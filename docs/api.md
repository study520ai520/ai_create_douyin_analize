# 抖音视频下载工具 API 文档

## API 基本信息

- 基础URL: `http://localhost:5000/api/v1`
- 所有请求和响应均使用 JSON 格式
- 所有响应都包含 `code` 和 `message` 字段
- 时间格式统一使用 ISO 8601 格式

## 通用响应格式

### 成功响应
```json
{
    "code": 200,
    "message": "success",
    "data": {
        // 具体的响应数据
    }
}
```

### 错误响应
```json
{
    "code": 400,  // 或其他错误码
    "message": "错误信息描述"
}
```

## 错误码说明

- 200: 请求成功
- 400: 请求参数错误
- 404: 资源不存在
- 500: 服务器内部错误

## API 接口列表

### 1. 解析抖音用户URL

解析抖音用户主页URL，支持标准链接和短链接。

- **接口**: `/parse`
- **方法**: `POST`
- **请求体**:
```json
{
    "url": "https://www.douyin.com/user/MS4wLjABAAAAKqxCy6CqgBOqf_Gc3W8_pKrwfqkWaK9PNy_RzHiXpKI"
}
```
- **响应示例**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "url": "https://www.douyin.com/user/MS4wLjABAAAAKqxCy6CqgBOqf_Gc3W8_pKrwfqkWaK9PNy_RzHiXpKI"
    }
}
```

### 2. 获取用户信息

获取抖音用户的基本信息。

- **接口**: `/user/<user_id>`
- **方法**: `GET`
- **参数**: 
  - `user_id`: 用户ID（路径参数）
- **响应示例**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "user_id": "MS4wLjABAAAAKqxCy6CqgBOqf_Gc3W8_pKrwfqkWaK9PNy_RzHiXpKI",
        "nickname": "用户昵称",
        "avatar": "头像URL",
        "signature": "个性签名",
        "following_count": 100,
        "follower_count": 1000,
        "liked_count": 10000
    }
}
```

### 3. 获取用户视频列表

获取用户发布的视频列表，支持分页。

- **接口**: `/user/<user_id>/videos`
- **方法**: `GET`
- **参数**: 
  - `user_id`: 用户ID（路径参数）
  - `cursor`: 分页游标（查询参数，可选）
  - `count`: 每页数量（查询参数，可选，默认20）
- **响应示例**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "videos": [
            {
                "video_id": "7123456789",
                "title": "视频标题",
                "cover": "封面URL",
                "play_url": "播放URL",
                "duration": 15,
                "create_time": "2024-01-07T12:00:00Z",
                "like_count": 1000,
                "comment_count": 100,
                "share_count": 50
            }
        ],
        "has_more": true,
        "cursor": "next_page_cursor"
    }
}
```

### 4. 下载视频

提交视频下载任务。

- **接口**: `/download`
- **方法**: `POST`
- **请求体**:
```json
{
    "video_id": "7123456789",
    "save_path": "optional/path/to/save"  // 可选
}
```
- **响应示例**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "task_id": "download_task_123",
        "status": "pending"
    }
}
```

## 使用示例

### Python 示例

```python
import requests

# 配置
BASE_URL = 'http://localhost:5000/api/v1'
headers = {
    'Content-Type': 'application/json'
}

# 1. 解析用户URL
def parse_user_url(url):
    response = requests.post(f'{BASE_URL}/parse', json={'url': url}, headers=headers)
    return response.json()

# 2. 获取用户信息
def get_user_info(user_id):
    response = requests.get(f'{BASE_URL}/user/{user_id}', headers=headers)
    return response.json()

# 3. 获取视频列表
def get_user_videos(user_id, cursor=None):
    params = {'cursor': cursor} if cursor else {}
    response = requests.get(f'{BASE_URL}/user/{user_id}/videos', params=params, headers=headers)
    return response.json()

# 4. 下载视频
def download_video(video_id, save_path=None):
    data = {'video_id': video_id}
    if save_path:
        data['save_path'] = save_path
    response = requests.post(f'{BASE_URL}/download', json=data, headers=headers)
    return response.json()

# 使用示例
if __name__ == '__main__':
    # 解析用户URL
    url = 'https://www.douyin.com/user/MS4wLjABAAAAKqxCy6CqgBOqf_Gc3W8_pKrwfqkWaK9PNy_RzHiXpKI'
    result = parse_user_url(url)
    print('解析结果:', result)

    # 获取用户信息
    user_id = result['data']['url'].split('/')[-1]
    user_info = get_user_info(user_id)
    print('用户信息:', user_info)

    # 获取视频列表
    videos = get_user_videos(user_id)
    print('视频列表:', videos)

    # 下载第一个视频
    if videos['data']['videos']:
        video_id = videos['data']['videos'][0]['video_id']
        download_result = download_video(video_id)
        print('下载任务:', download_result)
```

### cURL 示例

1. 解析用户URL:
```bash
curl -X POST http://localhost:5000/api/v1/parse \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.douyin.com/user/MS4wLjABAAAAKqxCy6CqgBOqf_Gc3W8_pKrwfqkWaK9PNy_RzHiXpKI"}'
```

2. 获取用户信息:
```bash
curl http://localhost:5000/api/v1/user/MS4wLjABAAAAKqxCy6CqgBOqf_Gc3W8_pKrwfqkWaK9PNy_RzHiXpKI
```

3. 获取视频列表:
```bash
curl http://localhost:5000/api/v1/user/MS4wLjABAAAAKqxCy6CqgBOqf_Gc3W8_pKrwfqkWaK9PNy_RzHiXpKI/videos
```

4. 下载视频:
```bash
curl -X POST http://localhost:5000/api/v1/download \
  -H "Content-Type: application/json" \
  -d '{"video_id": "7123456789"}'
``` 