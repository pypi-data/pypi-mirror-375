import os
import requests
from tqdm import tqdm
from urllib.parse import unquote
import time
import random


def download_file_with_progress(url, save_path=None, final_path=None, chunk_size=8192, max_retries=3):
    """
    下载文件并显示进度条，避免403 Forbidden错误

    :param url: 文件URL
    :param save_path: 保存路径（可选）
    :param chunk_size: 下载块大小（字节）
    :param max_retries: 最大重试次数
    :return: 下载的文件路径
    """
    try:
        # 创建会话对象
        session = requests.Session()

        # 设置浏览器级别的请求头 - 这是避免403错误的关键
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://www.google.com/',
        }

        # 尝试多次请求
        for attempt in range(max_retries):
            try:
                # 发送HEAD请求获取文件信息
                response = session.head(
                    url,
                    headers=headers,
                    allow_redirects=True,
                    timeout=10
                )

                # 如果HEAD请求被拒绝，尝试GET请求
                if response.status_code in [403, 405]:
                    response = session.get(
                        url,
                        headers=headers,
                        stream=True,
                        timeout=10
                    )
                    response.raise_for_status()
                    file_size = int(response.headers.get('Content-Length', 0))
                else:
                    response.raise_for_status()
                    file_size = int(response.headers.get('Content-Length', 0))

                break  # 成功获取信息，跳出重试循环

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 403 and attempt < max_retries - 1:
                    print(f"403错误，尝试第 {attempt + 1}/{max_retries} 次重试...")
                    # 随机等待时间避免被识别为爬虫
                    time.sleep(random.uniform(1, 3))
                    # 更新Referer头
                    headers['Referer'] = url
                    continue
                else:
                    raise

        # 获取文件名
        content_disposition = response.headers.get('Content-Disposition', '')
        if 'filename=' in content_disposition:
            filename = unquote(content_disposition.split('filename=')[1].strip('"'))
        else:
            filename = unquote(url.split('/')[-1].split('?')[0])

        # 设置保存路径
        if not save_path:
            save_path = filename

        # 检查文件是否已存在
        if os.path.exists(final_path):
            file_size_local = os.path.getsize(final_path)
            if file_size > 0 and file_size_local == file_size:
                print(f"文件已存在且完整: {final_path}")
                return final_path

        # 发送GET请求下载文件
        response = session.get(
            url,
            headers=headers,
            stream=True,
            timeout=30
        )
        response.raise_for_status()

        # 如果之前HEAD请求失败，现在获取实际文件大小
        if file_size == 0:
            file_size = int(response.headers.get('Content-Length', 0))

        # 创建进度条
        progress_bar = tqdm(
            total=file_size,
            unit='iB',
            unit_scale=True,
            desc=f"下载 {filename}",
            ascii=True,
            ncols=100,
            disable=file_size == 0  # 文件大小未知时禁用进度条
        )

        # 下载并写入文件
        downloaded_size = 0
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:  # 过滤掉保持连接的新块
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    if file_size > 0:
                        progress_bar.update(len(chunk))

        if file_size > 0:
            progress_bar.close()

        # 验证下载完整性
        if file_size > 0 and downloaded_size != file_size:
            os.remove(save_path)
            raise IOError(f"下载不完整: 预期 {file_size} 字节, 实际 {downloaded_size} 字节")

        # 重命名文件到最终路径
        if final_path:
            os.rename(save_path, final_path)
        print(f"\n文件下载成功: {final_path}")
        print(f"大小: {format_file_size(downloaded_size)}")
        return final_path

    except requests.exceptions.RequestException as e:
        print(f"下载失败: {str(e)}")
        return None
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return None


def format_file_size(size_bytes):
    """格式化文件大小显示"""
    if size_bytes < 1024:
        return f"{size_bytes} bytes"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / (1024 ** 2):.2f} MB"
    else:
        return f"{size_bytes / (1024 ** 3):.2f} GB"


# 使用示例
if __name__ == "__main__":
    # 示例URL（替换为实际下载链接）
    file_url = "https://openloong-apps-dev-private.obs.cn-east-3.myhuaweicloud.com/data-collector-svc/raw/da154076ac834f7aaad9c1a80a327e69/645b20d8a1ef4e0286f473cd138a0a4b/%E6%96%AF%E5%A1%94%E5%85%8B111_645b20d8a1ef4e0286f473cd138a0a4b.tar?AccessKeyId=HPUATWPNH6CPOZKR2MCL&Expires=1757042193&Signature=m%2FekOgPDEqazLbVq2ooQ%2FjY%2Brhs%3D"

    # 下载文件
    downloaded_file = download_file_with_progress(
        url=file_url,
        save_path="downloaded_file.tar",
        chunk_size=1024 * 1024,
        max_retries=5
    )

    if downloaded_file:
        print(f"文件已保存至: {os.path.abspath(downloaded_file)}")