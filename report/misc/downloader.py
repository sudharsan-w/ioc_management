import requests


def http_file_downloader(url: str, out_path):
    response = requests.get(url)
    with open(out_path, "wb") as file:
        file.write(response.content)
    return True


def get_file_size(url):
    try:
        response = requests.head(url, allow_redirects=True)
        if "Content-Length" in response.headers:
            return int(response.headers["Content-Length"])
        else:
            return None
    except Exception as e:
        print(url)
        print(f"Error: {e}")
