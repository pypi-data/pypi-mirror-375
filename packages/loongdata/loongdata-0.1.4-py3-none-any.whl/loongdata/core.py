import csv
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from obs import ObsClient
from tqdm import tqdm


class Client:
    def __init__(self, obs_access_key, obs_secret_key, obs_endpoint, max_workers=4):
        self.obs_access_key = obs_access_key
        self.obs_secret_key = obs_secret_key
        self.obs_endpoint = obs_endpoint
        self.max_workers = max_workers
        self.obs_client = ObsClient(
            access_key_id=obs_access_key,
            secret_access_key=obs_secret_key,
            server=obs_endpoint
        )

    def _download_one(self, bucket, raw_path, output_dir, filename):
        filename = os.path.basename(raw_path) if filename is None else filename
        output_path = os.path.join(output_dir, filename)
        # 断点续传下载
        with tqdm(total=100, unit='MB', smoothing=1) as pbar:
            def cb(transferredAmount, totalAmount, totalSeconds):
                pbar.total = float(f"{totalAmount / 1024 / 1024:.1f}")
                pbar.n = float(f"{transferredAmount / 1024 / 1024:.1f}")
                pbar.refresh()
            resp = self.obs_client.downloadFile(
                bucketName=bucket,
                objectKey=raw_path,
                downloadFile=output_path,
                taskNum=4,  # 分段下载线程数
                enableCheckpoint=True,  # 断点续传
                progressCallback=cb
            )
        return resp

    def _download_one_by_path(self, csv_path, output_dir, path_key, suffix):
        os.makedirs(output_dir, exist_ok=True)
        # 读取csv
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            decomment = filter(lambda row: row[0]!='#', csvfile)
            reader = csv.DictReader(decomment)
            files = list(reader)
            for row in files:
                bucket = row['bucket']
                raw_path = row[path_key]
                basename = os.path.basename(row['rawPath']).split('.')[0]
                filename = basename + suffix
                if raw_path != None:
                    print('Downloading:', row['episodeId'], bucket, raw_path)
                    self._download_one(bucket, raw_path, output_dir, filename)
                else:
                    print(path_key, 'not exist:', row['episodeId'])


    def downloadRaw(self, csv_path, output_dir):
        self._download_one_by_path(csv_path, output_dir, 'rawPath', '.tar')
        
    def downloadNorm(self, csv_path, output_dir):
        self._download_one_by_path(csv_path, output_dir, 'normalizePath', '.h5')
