#!/usr/bin/env python3
import os
import re
import certifi
import requests
import urllib3
from typing import List
from MP4UploadDL.config import Config
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class MP4UploadDLURLInfo:
    url:str = None
    direct_url:str = None
    size:int = None
    fsize:str = None
    file_name:str = None
    file_path:str = None
    def __init__(self,url,durl,size,filename,file_path):
        self.url = url
        self.direct_url = durl
        self.size = size
        self.fsize = Config.human_readable_size(size)
        self.file_name = filename
        self.file_path = file_path

class MP4UploadDL:
    def __init__(self, urls: List[str]):
        if urls.startswith("http"):
            urls = [urls]
        elif os.path.isfile(urls):
            with open(urls, "r", encoding="utf-8") as f:
                urls = [line.strip() for line in f if line.strip()]
        else:
            print(f"[!] '{urls}' is not a valid file or URL.")
            urls = []
        if not urls:
            print("[x] No valid URLs found.")
            return
        self.urls = urls
        self.session = requests.Session()
        self.session.verify = certifi.where()
        self.session.headers.update(Config.HEADERS)

    def _parse_post_data(self, html: str, template: dict) -> dict:
        parsed = template | dict(re.findall(Config.INPUT_REGEX, html))
        key = "d1" if "fname" in template else "d2"
        Config.Payload[key] = parsed
        return parsed

    def _post(self, url: str, html: str, template: dict):
        return self.session.post(url, data=self._parse_post_data(html, template), allow_redirects=False)

    def _get(self, url: str) -> str:
        return self.session.get(url).text

    def _download(self, url: str, output_dir: str,info_only:bool=False):
        try:
            initial_html = self._get(url)
            html_after_post = self._post(url, initial_html, Config.Payload["d1"]).text
            download_req = self._post(Config.BASE_URL + "F1", html_after_post, Config.Payload["d2"])
            file_url = download_req.headers.get("Location")

            if not file_url:
                print(f"[!] Failed to get download link for: {url}")
                return

            response = self.session.get(file_url, stream=True, verify=False)
            total_size = int(response.headers.get("Content-Length", 0))
            filename = Config.Payload["d1"]["fname"] or os.path.basename(url)
            filename = filename.strip().replace(" ","_")
            filepath = os.path.join(output_dir, filename)
            _info_obj = MP4UploadDLURLInfo(url,file_url,total_size,filename,filepath)
            if not info_only:
                os.makedirs(output_dir, exist_ok=True)
                print(f"→ Downloading: {filename} ({Config.human_readable_size(total_size)})")
                
                downloaded = 0
                with open(filepath, "wb") as f:
                    for chunk in response.iter_content(chunk_size=Config.CHUNK_SIZE):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            progress = f"{Config.human_readable_size(downloaded)}/{Config.human_readable_size(total_size)}"
                            print(f"Progress: {progress}", end="\r")
                print(f"\n✓ Completed: {filename}")
            return _info_obj
        except Exception as e:
            print(f"[x] Error downloading {url}: {e}")

    def download(self, output_dir: str = ".",info_only:bool=False):
        _files:list[MP4UploadDLURLInfo] = []
        for url in self.urls:
            url = url.strip()
            if url.startswith("http"):
                _files.append(self._download(url, output_dir,info_only))
                print("-" * 50)
        return _files

