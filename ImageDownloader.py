import random
import time

import requests
import os


from duckduckgo_search import ddg_images


def download(query: str, downloads_folder:str = "downloads", limit:int = 3, delay_min:float = 5, delay_max: float = 10):
    r = ddg_images(query, safesearch='On', size=None, type_image=None, layout=None, license_image=None, max_results=300)


    for i in range(limit):
        src = r[i]['image']
        try:
            img = requests.get(src)
            os.makedirs(f"{downloads_folder}/{query}/", exist_ok=True)
            with open(f"{downloads_folder}/{query}/image_{i}.jpg", "wb") as f:
                f.write(img.content)
        except:
            print(f'Error downloading image from {src}')


if __name__ == '__main__':
    download("dogs")