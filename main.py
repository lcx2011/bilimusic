import webview
from app import app
import threading
import time

def start_server():
    app.run(host='127.0.0.1', port=5000)

def main():
    # 启动Flask服务器
    t = threading.Thread(target=start_server, daemon=True)
    t.start()
    
    # 等待服务器启动
    time.sleep(2)
    
    # 创建窗口
    window = webview.create_window(
        'BiliMusic', 
        'http://127.0.0.1:5000',
        width=1024,
        height=768,
        resizable=True,
        frameless=False,
        min_size=(800, 600)
    )
    webview.start()

if __name__ == '__main__':
    main() 