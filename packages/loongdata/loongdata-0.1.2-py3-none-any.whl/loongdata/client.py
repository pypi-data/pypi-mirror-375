import requests


class Client:
    def __init__(self, ak, sk, host, max_workers=4):
        self.ak = ak
        self.sk = sk
        self.host = host
        self.max_workers = max_workers

    def get_url_list(self, dataset_id, page_num=1, page_size=10, task_id=None
                                       , min_size=None
                                       , max_size=None
                                       , min_duration=None
                                       , max_duration=None
                                       , audit_type=None):
        res = requests.request(
            method='POST',
            url=str(self.host) + '/data-miner/episode/download',
            json={  # 使用 json 参数自动设置 Content-Type 为 application/json
                "pageNum": page_num,
                "pageSize": page_size,
                "accessKey": self.ak,
                "secretKey": self.sk,
                "datasetId": dataset_id,
                "taskId": task_id,
                "minFileSize": min_size,
                "maxFileSize": max_size,
                "minFileDuration": min_duration,
                "maxFileDuration": max_duration,
                "dataAuditType": audit_type
            }
        )
        return res.json()

