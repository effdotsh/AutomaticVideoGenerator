import random
import time

import requests
import os

from duckduckgo_search import ddg_images


def download(query: str, downloads_folder: str = "downloads", limit: int = 3, delay_min: float = 5,
             delay_max: float = 10):
    r = ddg_images(query, safesearch='On', size=None, type_image=None, layout=None, license_image=None, max_results=300)

    for i in range(min(limit, len(r))):
        src = r[i]['image']
        path = f"{downloads_folder}/{query}/image_{i}.jpg"
        try:
            img = requests.get(src)
            if(img.status_code != 200):
                raise Exception(f"url had status code {img.status_code}")
            os.makedirs(f"{downloads_folder}/{query}/", exist_ok=True)
            BYTE_MINIMUM = 20_000
            if len(img.content) > BYTE_MINIMUM:
                with open(path, "wb") as f:
                    f.write(img.content)
            else:
                print(f'{src} did not meet the byte minimum')

        except:
            print(f'Error downloading image from {src} to {path}')
            if os.path.exists(path):
                os.remove(path)



if __name__ == '__main__':
    download("dogs")
