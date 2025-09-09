class Config:
    BASE_URL = "https://www.mp4upload.com/"
    INPUT_REGEX = r'<input type="hidden" name="([A-Za-z_]+)" value="(.*?)">'
    CHUNK_SIZE = 1 * 1024 * 1024  # 1 MB

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0.6422.78 Safari/537.36"
        ),
        "Referer": BASE_URL,
        "Origin": BASE_URL
    }

    Payload = {
        "d1": {
            "op": "",
            "usr_login": "",
            "id": "",
            "fname": "",
            "referer": "",
            "method_free": "Free Download"
        },
        "d2": {
            "op": "",
            "id": "",
            "rand": "",
            "referer": "",
            "method_free": "Free Download",
            "method_premium": ""
        }
    }

    def human_readable_size(size_bytes: int) -> str:
        """Convert bytes into a human-readable format."""
        if size_bytes == 0:
            return "0 B"
        units = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(units) - 1:
            size_bytes /= 1024.0
            i += 1
        return f"{size_bytes:.2f} {units[i]}"

