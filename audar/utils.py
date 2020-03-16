import requests
from tqdm import tqdm


def download_file(url, output_dir="./"):
    output_file = output_dir + url.split("/")[-1]

    r = requests.get(url, stream=True)
    total_size = int(r.headers.get('content-length', 0))
    block_size = 1024 #1 Kibibyte
    t = tqdm(total=total_size, unit='iB', unit_scale=True)
    with open(output_file, 'wb') as f:
        for data in r.iter_content(block_size):
            t.update(len(data))
            f.write(data)