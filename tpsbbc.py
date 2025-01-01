import requests
import json
import os
import mimetypes
import pandas as pd
from datetime import datetime

def upload_file(file_path, user, max_retries=3):
    upload_url = "http://34.70.196.96/v1/files/upload"
    headers = {
        "Authorization": "Bearer app-Z2uoOcA7WBvpT3JzRrCZAczy",
    }

    retries = 0
    while retries < max_retries:
        try:
            print("准备上传文件...")
            print("上传文件中...")
            with open(file_path, 'rb') as file:
                mime_type, _ = mimetypes.guess_type(file_path)
                files = {'file': (file_path, file, mime_type or 'application/octet-stream')}

                data = {
                    "user": user,
                    "type": "IMAGE"
                }

                response = requests.post(upload_url, headers=headers, files=files, data=data)
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
        except Exception as e:
            print(f"发生错误: {str(e)}")
        
        retries += 1
        print(f"重试上传 ({retries}/{max_retries})...")

    print("文件上传失败，超过最大重试次数")
    return None

def send_api_request(image_path):
    # 首先上传文件
    uploaded_url = upload_file(image_path, "abc-123")
    if not uploaded_url:
        print(f"跳过处理 {image_path} 因为文件上传失败")
        return None

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
        'query': '识别图片',
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
        print('Status Code:', response.status_code)
        
        return response.text
        
    except requests.exceptions.RequestException as e:
        print(f'Error occurred: {e}')
        return None

def process_image_directory(directory_path):
    """处理指定目录下的所有图片并保存结果到Excel"""
    # 支持的图片格式
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')
    
    # 创建用于存储结果的列表
    results = []
    
    # 遍历目录
    for filename in os.listdir(directory_path):
        if filename.lower().endswith(image_extensions):
            image_path = os.path.join(directory_path, filename)
            print(f"\n处理图片: {filename}")
            
            # 发送API请求并获取响应
            response_text = send_api_request(image_path)
            
            result_data = {
                '文件名': filename,
                '识别结果': ''
            }
            
            if response_text:
                for line in response_text.split('\n'):
                    if line.startswith('data: '):
                        try:
                            json_data = json.loads(line[6:])
                            if json_data.get('event') == 'workflow_finished':
                                result_data['识别结果'] = json_data['data']['outputs']['answer']
                        except (json.JSONDecodeError, KeyError):
                            continue
            
            results.append(result_data)
    
    # 创建DataFrame并保存到Excel
    if results:
        df = pd.DataFrame(results)
        excel_path = os.path.join(directory_path, '1.xlsm')
        df.to_excel(excel_path, index=False)
        print(f"\n结果已保存到: {excel_path}")

if __name__ == '__main__':
    # 指定要处理的图片目录
    image_dir = "C:/Users/Administrator/Desktop/TP"
    if os.path.isdir(image_dir):
        process_image_directory(image_dir)
    else:
        print("无效的目录路径！")
