# shabi_download

Here is a Python script for a simple terminal-based download manager named Shabi Download Manager that can handle both single and multiple file downloads. It utilizes multithreading to increase download speed and provides a graphical progress bar in the terminal using the tqdm library.

## Features:

Single or Multiple Downloads: Choose to download either a *single* file or *multiple* files at once.

Multithreading: Increase download speeds by downloading multiple files concurrently.

Progress Visualization: Uses tqdm to show a progress bar for each file, as well as overall progress.


![Alt text](/img/logo.webp )

![Alt text](/img/sample.png )

### Requirements:

* Python 3.x

* requests library: For handling HTTP requests.

* tqdm library: For showing download progress in the terminal.

You can install the required libraries using:

```bash
pip install requests tqdm
```

### Usage:

This script can be run from the terminal with different modes:

#### To download a single file:

```
python3 shabi_download_manager.py 1 --urls https://example.com/file.zip --directory downloads
```
#### To download multiple files concurrently:

```bash
python3 shabi_download_manager.py 2 --urls https://example.com/file1.zip https://example.com/file2.zip --threads 8 --directory downloads
```

#### binary file
```bash
cp shabi_download /usr/bin/

shabi_download  -h
usage: shabi_download [-h] [--urls URLS [URLS ...]] [--threads THREADS] [--directory DIRECTORY] mode

Shabi Download manager.

positional arguments:
  mode                  1 for single link, 2 for multiple links

options:
  -h, --help            show this help message and exit
  --urls URLS [URLS ...]
                        URL(s) to download
  --threads THREADS     Number of concurrent threads
  --directory DIRECTORY
                        Directory to save downloaded files


```
Arguments:

* mode: Specify 1 for single link or 2 for multiple links.

* --urls: Provide the URL(s) to download.

* --threads: (Optional) Set the number of concurrent threads for multiple downloads (default is 4).

* --directory: (Optional) Directory to save downloaded files (default is downloads).

Feel free to use and modify it for your personal needs. If you have any questions or need further customization, let me know!

