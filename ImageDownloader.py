import random
import time

import requests
import os

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}

# from duckduckgo_search import ddg_images


def download(query: str, downloads_folder:str = "downloads", limit:int = 3, delay_min:float = 5, delay_max: float = 10):
    print('----')
    print(f'Starting search for {query}')

    delay = int(random.random()*(delay_max-delay_min)+delay_min)
    print(delay, "second delay")
    time.sleep(delay)
    print('Delay over')
    r = requests.get(f'https://search.brave.com/api/images?q={query}&source=web', headers=headers)
    print(r)
    print(r.headers)

    if r.status_code == 429:
        print("429 error, retrying after delay")
        r.close()
        download(query, downloads_folder=downloads_folder, limit=limit, delay_min = delay_min+60, delay_max=delay_max+60)
        return

    res = list(r.json()['results'])
    r.close()

    for i in range(limit):
        src = res[i]['thumbnail']['src']
        try:
            img = requests.get(src)
            os.makedirs(f"{downloads_folder}/{query}/", exist_ok=True)
            with open(f"{downloads_folder}/{query}/image_{i}.jpg", "wb") as f:
                f.write(img.content)
        except:
            print(f'Error downloading image from {src}')


if __name__ == '__main__':
    download("dogs")