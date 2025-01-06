# 抖音视频下载工具使用说明

## 简介

这是一个基于Python开发的抖音视频批量下载工具，可以通过输入抖音用户主页URL，自动获取并下载该用户的所有视频内容。本工具提供了RESTful API接口，方便集成到其他应用中。

## 功能特点

- 支持解析标准抖音用户主页URL和短链接
- 自动获取用户基本信息和视频列表
- 支持批量下载视频
- 提供断点续传功能
- 支持自定义保存路径
- 完整的API接口
- 详细的日志记录

## 环境要求

- Python 3.8+
- 操作系统：Windows/Linux/MacOS

## 安装步骤

1. 克隆项目
```bash
git clone https://github.com/your-username/douyin-downloader.git
cd douyin-downloader
```

2. 创建虚拟环境（推荐）
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/MacOS
python3 -m venv venv
source venv/bin/activate
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

## 配置说明

1. 环境变量配置（可选）
创建 `.env` 文件：
```bash
FLASK_ENV=development  # 开发环境
# FLASK_ENV=production  # 生产环境
SECRET_KEY=your-secret-key
```

2. 下载目录配置
默认下载目录为 `data/downloads`，可以在 `app/config/settings.py` 中修改：
```python
DOWNLOAD_DIR = BASE_DIR / 'data' / 'downloads'
```

## 运行服务

1. 开发环境运行
```bash
python main.py
```

2. 生产环境运行（使用gunicorn，仅支持Linux/MacOS）
```bash
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

3. 使用Docker运行（待实现）
```bash
docker build -t douyin-downloader .
docker run -p 5000:5000 douyin-downloader
```

## 使用方法

### 1. 通过API使用

详细的API文档请参考 [API文档](api.md)

### 2. 通过Python脚本使用

```python
import requests

# 配置
BASE_URL = 'http://localhost:5000/api/v1'

# 下载用户视频
def download_user_videos(user_url):
    # 1. 解析用户URL
    response = requests.post(f'{BASE_URL}/parse', json={'url': user_url})
    if response.status_code != 200:
        print('URL解析失败')
        return
    
    user_id = response.json()['data']['url'].split('/')[-1]
    
    # 2. 获取视频列表
    response = requests.get(f'{BASE_URL}/user/{user_id}/videos')
    if response.status_code != 200:
        print('获取视频列表失败')
        return
    
    videos = response.json()['data']['videos']
    
    # 3. 下载视频
    for video in videos:
        response = requests.post(f'{BASE_URL}/download', json={
            'video_id': video['video_id']
        })
        if response.status_code == 200:
            print(f'视频 {video["title"]} 开始下载')
        else:
            print(f'视频 {video["title"]} 下载失败')

# 使用示例
if __name__ == '__main__':
    user_url = 'https://www.douyin.com/user/MS4wLjABAAAAKqxCy6CqgBOqf_Gc3W8_pKrwfqkWaK9PNy_RzHiXpKI'
    download_user_videos(user_url)
```

## 常见问题

1. 如何修改下载并发数？
在 `app/config/settings.py` 中修改 `MAX_CONCURRENT_DOWNLOADS` 值。

2. 下载失败怎么办？
- 检查网络连接
- 检查用户URL是否有效
- 查看日志文件 `data/logs/app.log`

3. 如何自定义保存路径？
在调用下载接口时指定 `save_path` 参数：
```python
response = requests.post(f'{BASE_URL}/download', json={
    'video_id': 'xxx',
    'save_path': 'custom/path'
})
```

## 注意事项

1. 请遵守抖音平台的使用规则
2. 建议设置合理的下载间隔，避免频繁请求
3. 下载的视频仅供个人学习使用
4. 注意遵守相关法律法规
5. 尊重创作者的知识产权

## 更新日志

### v1.0.0 (2024-01-07)
- 初始版本发布
- 实现基本的下载功能
- 提供RESTful API接口

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 发起 Pull Request

## 许可证

MIT License 