# BiliMusic - B站音乐播放器

BiliMusic 是一个基于 B站 视频的音乐播放器，让您可以轻松地收听和管理 B站 上的音乐视频。

## 功能特点

- 🎵 搜索 B站 音乐视频
- 📝 创建和管理播放列表
- 🎶 自动提取和显示歌词
- 💾 本地缓存歌词，提高加载速度
- 🎨 美观的用户界面
- 🚀 快速响应的播放控制

## 安装说明

### 方式一：直接运行可执行文件

1. 从 [Releases](https://github.com/lcx2011/bilinew/releases) 页面下载最新版本
2. 解压下载的文件
3. 运行 `BiliMusic.exe`

### 方式二：从源码运行

1. 克隆仓库
```bash
git clone https://github.com/lcx2011/bilinew.git
cd bilinew/backend
```

2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 运行应用
```bash
python main.py
```

## 使用方法

1. 启动应用后，在浏览器中访问 `http://localhost:5000`
2. 在搜索框中输入想要收听的音乐
3. 点击搜索结果中的音乐开始播放
4. 可以创建播放列表来保存喜欢的音乐

## 配置说明

### Cookie 设置

为了获取更好的播放体验，建议设置您的 B站 Cookie：

1. 登录 B站 网站
2. 获取 Cookie 中的 `SESSDATA` 值
3. 在 `app.py` 中更新 `BILIBILI_COOKIE` 变量

## 技术栈

- 后端：Python + Flask
- 前端：Vue.js + Element Plus
- 打包工具：PyInstaller

## 注意事项

- 本应用仅用于学习和个人使用
- 请遵守 B站 的使用条款
- 音频内容版权归原作者所有

## 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进这个项目！

## 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。 