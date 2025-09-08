#!/usr/bin/env python3
"""
抖音无水印视频下载并提取文本的 MCP 服务器

该服务器提供以下功能：
1. 解析抖音分享链接获取无水印视频链接
2. 下载视频并提取音频
3. 从音频中提取文本内容
4. 自动清理中间文件
"""

import os
import time

from mcp.server.fastmcp import FastMCP


# 创建 MCP 服务器实例
mcp = FastMCP("kbase-mcp-server",
              dependencies=["requests", "ffmpeg-python", "tqdm", "dashscope"])





@mcp.tool()
def fetch_external_data(page_num: int = 1, page_size: int = 20) -> str:
    """
    获取外部数据
    
    参数:
    - page_num: 页码，默认为1
    - page_size: 每页数量，默认为20
    
    返回:
    - API响应结果的字符串形式
    """
    import requests
    
    url = f'https://v2.fangcloud.com/aiapi/knowledgeDataCollect/externaDataCollectpage?_={int(time.time()*1000)}'
    
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'zh-CN',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Origin': 'https://v2.fangcloud.com',
        'Pragma': 'no-cache',
        'Referer': 'https://v2.fangcloud.com/console/gather/external',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"'
    }

    # 从环境变量获取API密钥
    kbase_key = os.getenv('KBASE_KEY')
    if not kbase_key:
        raise ValueError("未设置环境变量 KBASE_KEY，请在配置中添加知识库密钥")

    if not isinstance(kbase_key, str):
        # 如果是集合或其他类型，转换为字符串
        kbase_key = str(kbase_key)

    cookies = {
        'cookie': kbase_key
    }
    
    data = {
        "pageNum": page_num,
        "pageSize": page_size
    }
    
    try:
        response = requests.post(url, headers=headers, cookies=cookies, json=data)
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"请求失败: {str(e)}"


@mcp.tool()
def push_ai_qa_to_library(question: str, content: str) -> str:
    """
    将AI问答内容推送到知识库

    参数:
    - question: 问题
    - content: 回答内容

    返回:
    - API响应结果的字符串形式
    """
    import requests
    import time

    url = f'https://ask.fangcloud.com/kbase/library/pushAiQaToLibrary?_={int(time.time() * 1000)}'

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json;charset=UTF-8',
        'Origin': 'https://ask.fangcloud.com',
        'Pragma': 'no-cache',
        'Priority': 'u=1, i',
        'Referer': 'https://ask.fangcloud.com/kbase-web/v4/index/kbase',
        'RequestToken': 'SMSPEwTv0TcWEP6z18EwiNInLrJcIAllygNad0Fp',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'X-XSRF-TOKEN': 'ewogICJpdiIgOiAiYm5Lc281MTVweHMwbGRoNFAzL0xFQT09IiwKICAidmFsdWUiIDogIndOellCeEFMMmRxOVN3TDhQNjVjQXAwZG9USnBzZ0RYd1RYRXVGU2FtN3lIaldodkVKVHRZcWlXRDBNdVdMQUlBbXk2QXhNTXdkVG5BYlhNSlpTN253PT0iLAogICJtYWMiIDogImI1Zjk1ZjhiMTc1ZjVkMzI0MjVmOTZhYWRjMzhjYTc1OGY1YWY3Yzc4N2QwNDQ5OTIzNzVlZTY4ZTk1MzI2MGIiCn0='
    }

    # 从环境变量获取API密钥
    kbase_key = os.getenv('KBASE_KEY')
    if not kbase_key:
        raise ValueError("未设置环境变量 KBASE_KEY，请在配置中添加知识库密钥")

    if not isinstance(kbase_key, str):
        # 如果是集合或其他类型，转换为字符串
        kbase_key = str(kbase_key)

    cookies = {
        'cookie': kbase_key
    }

    library_id = os.getenv('LIBRARY_ID')

    data = {
        "libraryId": library_id,
        "documentId": 0,
        "qaInfo": {
            "question": question,
            "content": content
        }
    }

    try:
        response = requests.post(url, headers=headers, cookies=cookies, json=data)
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"请求失败: {str(e)}"



@mcp.prompt()
def douyin_text_extraction_guide() -> str:
    """抖音视频文本提取使用指南"""
    return """
# 抖音视频文本提取使用指南

## 功能说明
这个MCP服务器可以从抖音分享链接中提取视频的文本内容，以及获取无水印下载链接。

## 环境变量配置
请确保设置了以下环境变量：
- `DASHSCOPE_API_KEY`: 阿里云百炼API密钥

## 使用步骤
1. 复制抖音视频的分享链接
2. 在Claude Desktop配置中设置环境变量 DASHSCOPE_API_KEY
3. 使用相应的工具进行操作

## 工具说明
- `extract_douyin_text`: 完整的文本提取流程（需要API密钥）
- `get_douyin_download_link`: 获取无水印视频下载链接（无需API密钥）
- `parse_douyin_video_info`: 仅解析视频基本信息
- `add_two_integers`: 计算两个整数的加法运算
- `fetch_external_data`: 获取外部数据（需要有效Cookie）
- `push_ai_qa_to_library`: 将AI问答内容推送到知识库（需要有效Cookie）
- `douyin://video/{video_id}`: 获取指定视频的详细信息

## Claude Desktop 配置示例
```json
{
  "mcpServers": {
    "douyin-mcp": {
      "command": "uvx",
      "args": ["kkse-mcp-server"],
      "env": {
        "DASHSCOPE_API_KEY": "your-dashscope-api-key-here"
      }
    }
  }
}
```

## 注意事项
- 需要提供有效的阿里云百炼API密钥（通过环境变量）
- 使用阿里云百炼的paraformer-v2模型进行语音识别
- 支持大部分抖音视频格式
- 获取下载链接无需API密钥
"""


def main():
    """启动MCP服务器"""
    mcp.run()


if __name__ == "__main__":
    main()