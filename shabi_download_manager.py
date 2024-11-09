import os
import threading
import requests
import argparse
import time
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from urllib.parse import quote, urlparse, parse_qs


def clean_filename(url):
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)
    return filename


def download_file(url, directory, progress_bar, resume=False, max_retries=3):
    local_filename = os.path.join(directory, clean_filename(url))
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    downloaded_size = 0
    
    # Check if part of the file already exists to resume download
    if resume and os.path.exists(local_filename):
        downloaded_size = os.path.getsize(local_filename)
        headers['Range'] = f'bytes={downloaded_size}-'
    
    for attempt in range(max_retries):
        try:
            with requests.get(url, headers=headers, stream=True) as response:
                response.raise_for_status()
                total_size = int(response.headers.get('content-length', 0)) + downloaded_size
                progress_bar.reset(total=total_size)
                
                print(f"Total file size to download: {total_size / (1024 * 1024):.2f} MB")

                with open(local_filename, 'ab') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:  # filter out keep-alive chunks
                            f.write(chunk)
                            downloaded_size += len(chunk)
                            progress_bar.update(len(chunk))
                            print(f"Downloaded: {downloaded_size / (1024 * 1024):.2f} MB of {total_size / (1024 * 1024):.2f} MB", end='\r')
                            progress_bar.set_postfix({"Downloaded": f"{downloaded_size / (1024 * 1024):.2f} MB / {total_size / (1024 * 1024):.2f} MB"})
                print(f"\nDownload completed: {local_filename}")
                return
        except requests.exceptions.RequestException as e:
            print(f"Error downloading {url} (attempt {attempt + 1} of {max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                print(f"Failed to download {url} after {max_retries} attempts.")


def download_files_concurrently(urls, directory, max_threads, resume):
    print(f"Starting download of {len(urls)} files...")
    with ThreadPoolExecutor(max_threads) as executor:
        with tqdm(total=len(urls), desc="Overall Progress", unit="file") as overall_progress:
            futures = []
            for url in urls:
                encoded_url = quote(url, safe=':/?&=')
                progress_bar = tqdm(total=0, unit='B', unit_scale=True, desc=f"Downloading {clean_filename(url)}")
                future = executor.submit(download_file, encoded_url, directory, progress_bar, resume)
                futures.append((future, progress_bar))

            for i, (future, progress_bar) in enumerate(futures):
                try:
                    print(f"Processing file {i + 1} of {len(urls)}")
                    future.result()
                except Exception as e:
                    print(f"Error processing file {i + 1}: {e}")
                finally:
                    progress_bar.close()
                    overall_progress.update(1)


def main():
    parser = argparse.ArgumentParser(description="Shabi Download manager.")
    parser.add_argument('mode', type=int, help="1 for single link, 2 for multiple links")
    parser.add_argument('--urls', type=str, nargs='+', help="URL(s) to download")
    parser.add_argument('--threads', type=int, default=4, help="Number of concurrent threads")
    parser.add_argument('--directory', type=str, default='downloads', help="Directory to save downloaded files")
    parser.add_argument('--resume', action='store_true', help="Resume the download if interrupted")

    args, unknown = parser.parse_known_args()
    if '--resume' in unknown:
        args.resume = True

    # Create download directory if not exists
    if not os.path.exists(args.directory):
        os.makedirs(args.directory)

    if args.mode == 1:
        if len(args.urls) != 1:
            print("Error: Please provide exactly one URL for single link mode.")
            return
        print("Starting download of 1 file...")
        encoded_url = quote(args.urls[0], safe=':/?&=')
        with tqdm(total=0, unit='B', unit_scale=True, desc=f"Downloading {clean_filename(args.urls[0])}") as progress_bar:
            download_file(encoded_url, args.directory, progress_bar, args.resume)
    elif args.mode == 2:
        if len(args.urls) < 1:
            print("Error: Please provide at least one URL for multiple link mode.")
            return
        download_files_concurrently(args.urls, args.directory, args.threads, args.resume)
    else:
        print("Error: Invalid mode. Use 1 for single link or 2 for multiple links.")


if __name__ == '__main__':
    main()
