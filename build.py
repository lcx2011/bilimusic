import os
import shutil
from pathlib import Path

def modify_index_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修改资源路径
    content = content.replace('href="/favicon.ico"', 'href="favicon.ico"')
    content = content.replace('src="/assets/', 'src="assets/')
    content = content.replace('href="/assets/', 'href="assets/')
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def prepare_dist():
    # 检查前端构建目录是否存在
    frontend_dist = Path('../frontend/dist')
    if not frontend_dist.exists():
        print("错误：前端构建目录不存在，请先运行 npm run build")
        return False
        
    # 创建目标目录
    dist_dir = Path('dist')
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(parents=True)
    
    # 创建数据目录
    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)
    
    # 创建初始数据文件
    with open(data_dir / 'playlists.json', 'w', encoding='utf-8') as f:
        f.write('[]')
    with open(data_dir / 'lyrics_cache.json', 'w', encoding='utf-8') as f:
        f.write('{}')
    
    # 创建静态目录并复制前端文件
    static_dir = Path('static')
    if static_dir.exists():
        shutil.rmtree(static_dir)
    shutil.copytree(frontend_dist, static_dir)
    
    # 修改index.html
    modify_index_html(static_dir / 'index.html')
            
    print("构建准备完成！")
    return True

if __name__ == "__main__":
    if prepare_dist():
        print("静态文件和数据目录已准备完成")
    else:
        print("构建准备失败") 