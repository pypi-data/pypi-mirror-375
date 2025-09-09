<p align="left">
  <a href="https://github.com/Jo0X01/MP4UploadDL">
    <img src="MP4UploadDL.ico" alt="MP4UploadDL">
  </a>
</p>
<p align="left">
  <a href="https://pypi.org/project/MP4UploadDL/">
    <img src="https://img.shields.io/badge/-PyPi-blue.svg?logo=pypi&labelColor=555555&style=for-the-badge" alt="PyPi">
  </a>
  <a href="https://github.com/Jo0X01/MP4UploadDL">
    <img src="https://img.shields.io/badge/license-MIT-blue.svg?style=for-the-badge" alt="License: MIT">
  </a>
</p>



# MP4Upload Downloader

A Python script to download videos from **MP4Upload** using the free download method without waiting.

## Features
- Download single video or multiple from a list
- Human-readable progress (MB/GB)
- Works on Windows, Linux, macOS
- Command-line interface (CLI)
- Supports direct URL or a `.txt` file with multiple links

## Installation

install via `Pypi`:

```bash
pip install MP4UploadDL
```


via `source`:

Clone the repository and install dependencies:

```bash
git clone https://github.com/jo0x01/mp4uploaddl.git
cd mp4uploaddl
pip install -r requirements.txt
pip install .
```


## Usage

```bash
mp4upload-dl <URL or file> -o downloads/ --info-only
```

### Single link:
```bash
python mp4upload_downloader.py https://www.mp4upload.com/abcd1234
```

### From a file:
```bash
python mp4upload_downloader.py links.txt
```

Each line in `links.txt` should contain a single MP4Upload link.

### Custom output folder:
```bash
python mp4upload_downloader.py links.txt -o my_videos/
```

## Requirements
- Python 3.0+
- Libraries: `requests`, `certifi`, `urllib3`

Install them via:
```bash
pip install -r requirements.txt
```
## Python Code
```python

from MP4UpoadDL import MP4UploadDL

source = " https://www.mp4upload.com/abcd1234"
source = [" https://www.mp4upload.com/abcd1234"," https://www.mp4upload.com/abcd1234"," https://www.mp4upload.com/abcd1234"]
source = "links.txt"

mp4upload = MP4UploadDL(source)
_info = mp4upload.download(output_dir=".",info_only=True)
for _i in _info:
    print(f"From: {_i.url}")
    print(f"File: {_i.file_name}")
    print(f"File Size: {_i.fsize}")
    print(f"File Path: {_i.file_path}")
    print("="*40)

```
## License
MIT License