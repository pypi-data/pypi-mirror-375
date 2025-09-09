import argparse
from .client import Client
from .download import download_file_with_progress
import os

def main():
    parser = argparse.ArgumentParser(description="Loongdata Open Source Data Client")
    parser.add_argument("action", default="download", help="data action", choices=["download"])
    parser.add_argument("--dataset", required=True, help="Dataset id in loong data platform")
    parser.add_argument("--ak", help="Loongdata access key, or setup by env variable loongdata_access_key")
    parser.add_argument("--sk", help="Loongdata secret key, or setup by env variable loongdata_secret_key")
    parser.add_argument("--host", default="https://dev-dojo-api.openloong.org.cn", help="Loongdata host")
    parser.add_argument("--endpoint", default="https://obs.cn-east-3.myhuaweicloud.com", help="Obs endpoint, or setup by env variable obs_endpoint")
    parser.add_argument("--max-workers", type=int, default=4, help="Max download threads")
    parser.add_argument("--task", help="Loongdata task id")
    parser.add_argument("--min-size", type=int, help="Loongdata filter argument: episode min size")
    parser.add_argument("--max-size", type=int, help="Loongdata filter argument: episode max size")
    parser.add_argument("--min-duration", type=int, help="Loongdata filter argument: episode min duration")
    parser.add_argument("--max-duration", type=int, help="Loongdata filter argument: episode max duration")
    parser.add_argument("--audit-type", help="Loongdata filter argument: data audit type")

    args = parser.parse_args()

    ak = args.ak if args.ak else os.getenv("loongdata_access_key")
    sk = args.sk if args.sk else os.getenv("loongdata_secret_key")
    host = args.host if args.host else os.getenv("loongdata_host")
    # 逐行读取csv，bucket字段由csv决定
    client = Client(ak, sk, host)
    if args.action == "download":
        # 获取下载任务的csv路径
        url_list = client.get_url_list(dataset_id=args.dataset, page_num=1, page_size=1000
                                       , task_id=args.task
                                       , min_size=args.min_size
                                       , max_size=args.max_size
                                       , min_duration=args.min_duration
                                       , max_duration=args.max_duration
                                       , audit_type=args.audit_type)
        if not url_list['success']:
            print(url_list.get('msg', '未知错误'))
            return
        output_dir = f"./{args.dataset}"
        os.makedirs(output_dir, exist_ok=True)
        for episode in url_list['data']:
            url = episode['downloadUrl']
            tid = episode['taskId']
            eid = episode['episodeId']
            path = os.path.join(output_dir, tid, str(eid) + '.downloading')
            final_path = os.path.join(output_dir, tid, str(eid) + '.h5')
            os.makedirs(os.path.dirname(path), exist_ok=True)
            download_file_with_progress(url, save_path=path, final_path=final_path, chunk_size=1024*1024, max_retries=3)