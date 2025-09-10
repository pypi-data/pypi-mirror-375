#!/usr/bin/env python3


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


@mcp.tool()
def add_web_data_book(web_url: str, model: int = 2) -> str:
    """
    将网页内容添加到知识库

    参数:
    - web_url: 网页URL
    - model: 模型类型，默认为2

    返回:
    - API响应结果的字符串形式
    """
    import requests
    import time
    import os

    # 生成时间戳
    timestamp = int(time.time() * 1000)
    url = f'https://ask.fangcloud.com/kbase/book/addWebDataBook?_={timestamp}'

    headers = {
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Origin': 'https://ask.fangcloud.com',
        'Pragma': 'no-cache',
        'Priority': 'u=1, i',
        'Referer': 'https://ask.fangcloud.com/kbase-web/v4/index/kbase',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
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


    # 请求数据
    data = {
        "webUrl": web_url,
        "model": model,
        "libraryId": library_id
    }


    try:
        response = requests.post(url, headers=headers, cookies=cookies, json=data)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        return f"请求失败: {str(e)}"
    except Exception as e:
        return f"发生错误: {str(e)}"



def main():
    """启动MCP服务器"""
    mcp.run()


if __name__ == "__main__":
    main()