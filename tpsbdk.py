import requests
import json
import os
import mimetypes

def upload_file(file_path, user):
    upload_url = "http://34.70.196.96/v1/files/upload"
    headers = {
        "Authorization": "Bearer app-Z2uoOcA7WBvpT3JzRrCZAczy",
    }

    try:
        print("上传文件中...")
        with open(file_path, 'rb') as file:
            mime_type, _ = mimetypes.guess_type(file_path)
            files = {'file': (file_path, file, mime_type or 'application/octet-stream')}

            data = {
                "user": user,
                "type": "IMAGE"
            }

            response = requests.post(upload_url, headers=headers, files=files, data=data)
            print("response:", response.json())
            if response.status_code == 201:
                print("文件上传成功")
                try:
                    return response.json().get("id")
                except ValueError:
                    print("解析响应JSON失败")
                    print(f"原始响应: {response.text}")
                    return None
            else:
                print(f"文件上传失败，状态码: {response.status_code}")
                print(f"响应内容: {response.text}")
                return None
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return None  


def send_api_request(image_path):
    # 首先上传文件
    uploaded_url = upload_file(image_path,"abc-123")
    if not uploaded_url:
        print(f"跳过处理 {image_path} 因为文件上传失败")
        return

    print(f"文件上传成功，文件ID：{uploaded_url}")
        
    # 1. 设置API端点
    url = 'http://34.70.196.96/v1/chat-messages'
    
    # 2. 设置请求头
    headers = {
        'Authorization': 'Bearer app-NBFWxqs199P7LcG5iCmyrnSh',
        'Content-Type': 'application/json'
    }
    
    # 3. 准备请求数据
    payload = {
        'inputs': {},
        'query': 'What are the specs of the iPhone 13 Pro Max?',
        'response_mode': 'streaming',
        'conversation_id': '',
        'user': 'abc-123',
        'files': [
            {
                'type': 'image',
                'transfer_method': 'local_file',
                "upload_file_id":  uploaded_url
            }
        ]
    }
    
    try:
        # 4. 发送POST请求
        response = requests.post(url, headers=headers, json=payload)
        
        # 5. 处理响应数据
        # print(f'\nProcessing image: {image_path}')
        print('Status Code:', response.text)
        
        # 6. 解析响应内容
        for line in response.text.split('\n'):
            if line.startswith('data: '):
                try:
                    # 去掉'data: '前缀并解析JSON
                    json_data = json.loads(line[6:])
                    
                    # 检查是否是workflow_finished事件
                    if json_data.get('event') == 'workflow_finished':
                        print('\nFound workflow_finished event:')
                        print('Answer:', json_data['data']['outputs']['answer'])
                        print('Elapsed time:', json_data['data']['elapsed_time'])
                        print('Status:', json_data['data']['status'])
                except json.JSONDecodeError:
                    continue
                except KeyError:
                    continue
        
    except requests.exceptions.RequestException as e:
        print(f'Error occurred: {e}')

def process_image_directory(directory_path):
    """处理指定目录下的所有图片"""
    # 支持的图片格式
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')
    
    # 遍历目录
    for filename in os.listdir(directory_path):
        if filename.lower().endswith(image_extensions):
            image_path = os.path.join(directory_path, filename)
            send_api_request(image_path)

if __name__ == '__main__':
    # 指定要处理的图片目录
    image_dir = input("请输入图片目录路径: ")
    if os.path.isdir(image_dir):
        process_image_directory(image_dir)
    else:
        print("无效的目录路径！")

    # send_api_request("")
