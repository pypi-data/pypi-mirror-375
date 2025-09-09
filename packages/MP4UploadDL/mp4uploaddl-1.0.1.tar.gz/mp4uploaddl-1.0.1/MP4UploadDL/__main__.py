
import argparse
from .mp4upload import MP4UploadDL

def main():
    parser = argparse.ArgumentParser(
        description="MP4UploadDL For Download Files From MP4Upload Site without waiting - Made By: MrJo0x01")
    parser.add_argument(
        "source",
        help="MP4Upload URL or file containing links"
    )
    parser.add_argument(
        "-i", "--info-only",
        help="Don`t Download Just Show Info About Links",
        action='store_true'
    )
    parser.add_argument(
        "-o", "--output",
        help="Output directory to save files",
        default="downloads"
    )
    args = parser.parse_args()

    _info = MP4UploadDL(args.source).download(args.output,args.info_only)
    for _i in _info:
        print(f"From: {_i.url}")
        print(f"File: {_i.file_name}")
        print(f"File Size: {_i.fsize}")
        print(f"File Path: {_i.file_path}")
        print("="*40)

if __name__ == "__main__":
    main()
