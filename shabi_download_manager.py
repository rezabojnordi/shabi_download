import os
import threading
import requests
import argparse
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

def download_file(url, directory, progress_bar):
    local_filename = os.path.join(directory, url.split('/')[-1])
    try:
        with requests.get(url, stream=True) as response:
            response.raise_for_status()
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            with open(local_filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    progress_bar.update(len(chunk))
        print(f"\nDownload completed: {local_filename}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")

def download_files_concurrently(urls, directory, max_threads):
    print(f"Starting download of {len(urls)} files...")
    with ThreadPoolExecutor(max_threads) as executor:
        with tqdm(total=len(urls), desc="Overall Progress", unit="file") as overall_progress:
            futures = []
            for url in urls:
                progress_bar = tqdm(total=0, unit='B', unit_scale=True, desc=f"Downloading {url.split('/')[-1]}")
                future = executor.submit(download_file, url, directory, progress_bar)
                futures.append((future, progress_bar))

            for i, (future, progress_bar) in enumerate(futures):
                print(f"Processing file {i + 1} of {len(urls)}")
                future.result()
                progress_bar.close()
                overall_progress.update(1)

def main():
    parser = argparse.ArgumentParser(description="Shabi Download manager.")
    parser.add_argument('mode', type=int, help="1 for single link, 2 for multiple links")
    parser.add_argument('--urls', type=str, nargs='+', help="URL(s) to download")
    parser.add_argument('--threads', type=int, default=4, help="Number of concurrent threads")
    parser.add_argument('--directory', type=str, default='downloads', help="Directory to save downloaded files")

    args = parser.parse_args()

    # Create download directory if not exists
    if not os.path.exists(args.directory):
        os.makedirs(args.directory)

    if args.mode == 1:
        if len(args.urls) != 1:
            print("Error: Please provide exactly one URL for single link mode.")
            return
        print("Starting download of 1 file...")
        with tqdm(total=0, unit='B', unit_scale=True, desc=f"Downloading {args.urls[0].split('/')[-1]}") as progress_bar:
            download_file(args.urls[0], args.directory, progress_bar)
    elif args.mode == 2:
        if len(args.urls) < 1:
            print("Error: Please provide at least one URL for multiple link mode.")
            return
        download_files_concurrently(args.urls, args.directory, args.threads)
    else:
        print("Error: Invalid mode. Use 1 for single link or 2 for multiple links.")

if __name__ == '__main__':
    main()

