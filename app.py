from flask import Flask, jsonify, request, Response, send_from_directory
from flask_cors import CORS
import requests
import re
import json
from datetime import datetime
import os
from bs4 import BeautifulSoup
from urllib.parse import quote
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import base64
import sys

# 获取应用运行时的基础路径
if getattr(sys, 'frozen', False):
    # 如果是打包后的可执行文件
    base_dir = os.path.dirname(sys.executable)
    static_folder = os.path.join(base_dir, '_internal', 'static')
    data_dir = os.path.join(base_dir, '_internal', 'data')
    print(f"运行在打包环境中，数据目录: {data_dir}")
else:
    # 如果是开发环境
    base_dir = os.path.dirname(os.path.abspath(__file__))
    static_folder = os.path.join(base_dir, 'static')
    data_dir = os.path.join(base_dir, 'data')
    print(f"运行在开发环境中，数据目录: {data_dir}")

# 创建Flask应用
app = Flask(__name__, static_folder=static_folder, static_url_path='')
CORS(app)

# B站 cookie，需要替换成你的实际 cookie
BILIBILI_COOKIE = "SESSDATA=d1f5a129%2C1753873610%2C850f6%2A12CjD2z0U5j-OvZev3v42ovfmtRtUHtUzIJjrlY14wObWze2DErUJFAVAJWwyIjWy5iPASVjF5ejQxVlYzcTB3Y0RoRGhzV0JNSWd0cU9vVnhPSnhzN0NLMkhtdEZnRV9qRG1VU19Ca3BXbXJEUV9sa3RzOG54ZEhmNVFZdUdDSmtjcGtna3BQSUd3IIEC; bili_jct=2a507e83846687a75c856f59c0a37eae; buvid3=5CEDA6E7-3943-8604-BDB2-3F176527722A16138infoc"

BILIBILI_API = {
    'search': 'https://api.bilibili.com/x/web-interface/search/type',
    'video_info': 'https://api.bilibili.com/x/web-interface/view',
    'play_url': 'https://api.bilibili.com/x/player/playurl'
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Referer': 'https://www.bilibili.com',
    'Cookie': BILIBILI_COOKIE
}

# 修改数据目录的定义
DATA_DIR = data_dir
PLAYLISTS_FILE = os.path.join(DATA_DIR, 'playlists.json')
LYRICS_CACHE_FILE = os.path.join(DATA_DIR, 'lyrics_cache.json')

print(f"数据文件路径：")
print(f"播放列表文件: {PLAYLISTS_FILE}")
print(f"歌词缓存文件: {LYRICS_CACHE_FILE}")

# 确保数据目录存在
try:
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"创建数据目录: {DATA_DIR}")
except Exception as e:
    print(f"创建数据目录失败: {str(e)}")

# 确保文件存在并可写
def ensure_file_exists(file_path, default_content):
    try:
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(default_content, f, ensure_ascii=False)
            print(f"创建文件: {file_path}")
        else:
            # 测试文件是否可写
            with open(file_path, 'a', encoding='utf-8') as f:
                pass
            print(f"文件可访问: {file_path}")
    except Exception as e:
        print(f"文件操作失败 {file_path}: {str(e)}")

# 初始化文件
ensure_file_exists(PLAYLISTS_FILE, [])
ensure_file_exists(LYRICS_CACHE_FILE, {})

def load_playlists():
    try:
        with open(PLAYLISTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_playlists(playlists):
    with open(PLAYLISTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(playlists, f, ensure_ascii=False, indent=2)

def load_lyrics_cache():
    try:
        if not os.path.exists(LYRICS_CACHE_FILE):
            print(f"歌词缓存文件不存在: {LYRICS_CACHE_FILE}")
            return {}
        with open(LYRICS_CACHE_FILE, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                print("歌词缓存文件为空")
                return {}
            cache = json.load(f)
            print(f"成功加载歌词缓存，包含 {len(cache)} 条记录")
            return cache
    except Exception as e:
        print(f"加载歌词缓存出错: {str(e)}")
        # 如果文件损坏，创建新的
        try:
            with open(LYRICS_CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False)
            print("重新创建了空的歌词缓存文件")
        except Exception as write_error:
            print(f"重新创建歌词缓存文件失败: {str(write_error)}")
        return {}

def save_lyrics_cache(cache):
    try:
        temp_file = LYRICS_CACHE_FILE + '.tmp'
        # 先写入临时文件
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
        # 然后替换原文件
        os.replace(temp_file, LYRICS_CACHE_FILE)
        print(f"成功保存歌词缓存，共 {len(cache)} 条记录")
    except Exception as e:
        print(f"保存歌词缓存出错: {str(e)}")
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass

@app.route('/api/playlists', methods=['GET'])
def get_playlists():
    playlists = load_playlists()
    return jsonify(playlists)

@app.route('/api/playlists', methods=['POST'])
def create_playlist():
    data = request.json
    if not data or 'name' not in data:
        return jsonify({'code': -1, 'message': '缺少必要参数'}), 400
    
    playlists = load_playlists()
    new_playlist = {
        'id': str(len(playlists) + 1),
        'name': data['name'],
        'description': data.get('description', ''),
        'tracks': [],
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
    
    playlists.append(new_playlist)
    save_playlists(playlists)
    
    return jsonify({'code': 0, 'data': new_playlist})

@app.route('/api/search')
def search():
    keyword = request.args.get('keyword', '')
    try:
        response = requests.get(
            BILIBILI_API['search'],
            params={
                'keyword': keyword,
                'search_type': 'video',
                'order': 'totalrank',
                'duration': 1,  # 仅搜索6分钟以下的视频
                'tids': 3,  # 音乐分区
            },
            headers=HEADERS
        )
        data = response.json()
        
        if data['code'] == 0 and 'result' in data.get('data', {}):
            videos = []
            for item in data['data']['result'][:20]:  # 限制返回20个结果
                videos.append({
                    'bvid': item['bvid'],
                    'title': re.sub(r'<[^>]+>', '', item['title']),  # 移除HTML标签
                    'author': item['author'],
                    'pic': item['pic'],
                    'play': item.get('play', '0'),
                    'danmaku': item.get('video_review', '0')
                })
            return jsonify({'code': 0, 'data': videos})
        return jsonify({'code': -1, 'message': '搜索失败', 'raw_response': data})
    except Exception as e:
        return jsonify({'code': -1, 'message': str(e)})

@app.route('/api/audio/<bvid>')
def get_audio_url(bvid):
    try:
        # 获取视频信息
        video_info = requests.get(
            BILIBILI_API['video_info'],
            params={'bvid': bvid},
            headers=HEADERS
        ).json()
        
        if video_info['code'] != 0:
            return jsonify({'code': -1, 'message': '获取视频信息失败'})
        
        # 获取音频URL
        play_info = requests.get(
            BILIBILI_API['play_url'],
            params={
                'bvid': bvid,
                'cid': video_info['data']['cid'],
                'fnval': 16  # 请求音频流
            },
            headers=HEADERS
        ).json()
        
        if play_info['code'] == 0 and play_info['data']['dash']['audio']:
            audio_url = play_info['data']['dash']['audio'][0]['baseUrl']
            return jsonify({'code': 0, 'url': audio_url})
        
        return jsonify({'code': -1, 'message': '获取音频URL失败'})
    except Exception as e:
        return jsonify({'code': -1, 'message': str(e)})

@app.route('/api/proxy/image')
def proxy_image():
    url = request.args.get('url', '')
    if not url:
        return jsonify({'code': -1, 'message': '缺少图片URL'})
    
    # 确保 URL 有正确的协议
    if url.startswith('//'):
        url = 'https:' + url
    elif not url.startswith('http'):
        url = 'https://' + url
    
    try:
        response = requests.get(url, headers={
            'User-Agent': HEADERS['User-Agent'],
            'Referer': 'https://www.bilibili.com'
        })
        
        if response.status_code != 200:
            return jsonify({
                'code': -1, 
                'message': f'图片请求失败: {response.status_code}'
            })
        
        # 获取正确的 content-type，默认为 image/jpeg
        content_type = response.headers.get('content-type', 'image/jpeg')
        
        # 创建响应对象
        resp = Response(response.content, content_type=content_type)
        
        # 添加 CORS 头
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        resp.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With'
        resp.headers['Cache-Control'] = 'public, max-age=31536000'
        
        return resp
        
    except Exception as e:
        print(f"Error proxying image: {str(e)}")
        return jsonify({'code': -1, 'message': str(e)})

@app.route('/api/playlists/<playlist_id>', methods=['GET'])
def get_playlist(playlist_id):
    playlists = load_playlists()
    playlist = next((p for p in playlists if p['id'] == playlist_id), None)
    
    if playlist is None:
        return jsonify({'code': -1, 'message': '专辑不存在'}), 404
        
    return jsonify(playlist)

@app.route('/api/playlists/<playlist_id>', methods=['DELETE'])
def delete_playlist(playlist_id):
    playlists = load_playlists()
    playlist_index = next((i for i, p in enumerate(playlists) if p['id'] == playlist_id), -1)
    
    if playlist_index == -1:
        return jsonify({'code': -1, 'message': '专辑不存在'}), 404
        
    playlists.pop(playlist_index)
    save_playlists(playlists)
    
    return jsonify({'code': 0, 'message': '删除成功'})

@app.route('/api/playlists/<playlist_id>/tracks', methods=['POST'])
def add_track_to_playlist(playlist_id):
    data = request.json
    if not data or 'track' not in data:
        return jsonify({'code': -1, 'message': '缺少歌曲信息'}), 400
        
    playlists = load_playlists()
    playlist = next((p for p in playlists if p['id'] == playlist_id), None)
    
    if playlist is None:
        return jsonify({'code': -1, 'message': '专辑不存在'}), 404
    
    # 检查歌曲是否已存在
    if any(t['bvid'] == data['track']['bvid'] for t in playlist['tracks']):
        return jsonify({'code': -1, 'message': '歌曲已存在于专辑中'}), 400
        
    # 添加歌曲
    track = {
        'bvid': data['track']['bvid'],
        'title': data['track']['title'],
        'author': data['track']['author'],
        'pic': data['track']['pic'],
        'added_at': datetime.now().isoformat()
    }
    playlist['tracks'].append(track)
    playlist['updated_at'] = datetime.now().isoformat()
    
    save_playlists(playlists)
    return jsonify({'code': 0, 'message': '添加成功', 'data': playlist})

@app.route('/api/playlists/<playlist_id>/tracks/<bvid>', methods=['DELETE'])
def delete_track_from_playlist(playlist_id, bvid):
    playlists = load_playlists()
    playlist = next((p for p in playlists if p['id'] == playlist_id), None)
    
    if playlist is None:
        return jsonify({'code': -1, 'message': '专辑不存在'}), 404
        
    # 找到要删除的歌曲索引
    track_index = next((i for i, t in enumerate(playlist['tracks']) if t['bvid'] == bvid), -1)
    
    if track_index == -1:
        return jsonify({'code': -1, 'message': '歌曲不存在'}), 404
        
    # 删除歌曲
    playlist['tracks'].pop(track_index)
    playlist['updated_at'] = datetime.now().isoformat()
    
    save_playlists(playlists)
    return jsonify({'code': 0, 'message': '删除成功'})

def get_search_results(url):
    print(f"开始请求URL: {url}")
    session = requests.Session()
    
    # 设置请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache'
    }
    
    try:
        response = session.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        print(f"请求完成，状态码: {response.status_code}")
        print(f"实际URL: {response.url}")
        
        if response.status_code == 200:
            return response.text
        else:
            print(f"请求失败，状态码: {response.status_code}")
            return ""
            
    except Exception as e:
        print(f"请求失败: {str(e)}")
        return ""

@app.route('/api/lyrics', methods=['GET'])
def get_lyrics():
    title = request.args.get('title', '')
    bvid = request.args.get('bvid', '')
    if not title:
        return jsonify({'code': -1, 'message': '缺少歌曲名称'})
    if not bvid:
        return jsonify({'code': -1, 'message': '缺少视频ID'})
    
    try:
        # 清理歌曲名称
        clean_title = re.sub(r'【.*?】|\[.*?\]|《.*?》|\(.*?\)|（.*?）|Hi-Res|Hi-res|hi-res|HD|4K|\d+K|\s+', ' ', title)
        clean_title = re.sub(r'在.*?试听|在.*?听|在.*?播放|在.*?唱', '', clean_title)
        clean_title = clean_title.strip()
        if not clean_title:
            clean_title = title
            
        # 检查缓存
        lyrics_cache = load_lyrics_cache()
        if bvid in lyrics_cache:
            print(f"从缓存加载歌词: {clean_title}")
            return jsonify({
                'code': 0,
                'data': {
                    'lyrics': lyrics_cache[bvid]['lyrics'],
                    'from_cache': True
                }
            })
            
        # 第一步：搜索歌曲获取songmid
        search_url = 'https://c.y.qq.com/soso/fcgi-bin/client_search_cp'
        search_params = {
            'w': clean_title,
            'format': 'json',
            'p': 1,
            'n': 20,
            'aggr': 1,
            'lossless': 1,
            'cr': 1,
            'new_json': 1
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://y.qq.com'
        }
        
        print(f"搜索歌曲: {clean_title}")
        response = requests.get(search_url, params=search_params, headers=headers)
        
        if response.status_code != 200:
            return jsonify({'code': -1, 'message': '搜索失败'})
            
        # 解析搜索结果
        data = response.json()
        if not data.get('data', {}).get('song', {}).get('list'):
            return jsonify({'code': -1, 'message': '未找到歌曲'})
            
        # 获取第一个结果的songmid
        first_result = data['data']['song']['list'][0]
        songmid = first_result.get('mid')
        
        if not songmid:
            return jsonify({'code': -1, 'message': '未找到歌曲ID'})
            
        # 第二步：获取歌词
        lyric_url = 'https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_new.fcg'
        lyric_params = {
            'songmid': songmid,
            'g_tk': '5381',
            'format': 'json',
            'nobase64': 1
        }
        
        headers['Referer'] = 'https://y.qq.com/n/ryqq/songDetail/' + songmid
        
        lyric_response = requests.get(lyric_url, params=lyric_params, headers=headers)
        
        if lyric_response.status_code != 200:
            return jsonify({'code': -1, 'message': '获取歌词失败'})
            
        # 解析歌词
        lyric_data = lyric_response.json()
        if not lyric_data.get('lyric'):
            return jsonify({'code': -1, 'message': '未找到歌词'})
            
        lyrics_text = lyric_data['lyric']
        lyrics_lines = []
        
        for line in lyrics_text.split('\n'):
            line = line.strip()
            if line and '[' in line and ']' in line:
                time_str = re.findall(r'\[(.*?)\]', line)[0]
                text = re.sub(r'\[.*?\]', '', line).strip()
                if text and re.match(r'\d{2}:\d{2}.\d{2}', time_str):
                    minutes, seconds = time_str.split(':')
                    seconds = float(seconds)
                    time = int(float(minutes) * 60 + seconds)
                    lyrics_lines.append({
                        'time': time,
                        'text': text
                    })
        
        if lyrics_lines:
            # 保存到缓存
            lyrics_cache[bvid] = {
                'lyrics': lyrics_lines,
                'title': clean_title,
                'updated_at': datetime.now().isoformat()
            }
            save_lyrics_cache(lyrics_cache)
            
            print(f"保存歌词到缓存: {clean_title}")
            
            return jsonify({
                'code': 0,
                'data': {
                    'lyrics': lyrics_lines,
                    'from_cache': False
                }
            })
        
        return jsonify({'code': -1, 'message': '未找到歌词'})
        
    except Exception as e:
        print(f"获取歌词出错: {str(e)}")
        return jsonify({'code': -1, 'message': str(e)})

@app.route('/')
def index():
    return send_from_directory(static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(static_folder, path)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(static_folder, 'favicon.ico')

if __name__ == '__main__':
    app.run(debug=False, port=5000) 