# StreamShatter
Originally a very basic script for downloading files from servers with inconsistent connections, this project has been revisited and modernised to use https://github.com/jawah/niquests for multiplexing performance, both for private testing of niquests' stability, and for general improvements in functionality for those who still have use for such a tool.

StreamShatter takes advantage of the `Range` HTTP header to dynamically allocate multiple chunks, by starting with one streaming request and gradually bisecting it while bandwidth permits, all without restarting the download. This allows for single, large file downloads from hosts that, whether intentionally or unintentionally, have degraded throughputs. The individual chunks also serve as checkpoints for if/when connections are broken.

# Installation
- Install [python](https://www.python.org) and [pip](https://pip.pypa.io/en/stable/)
- Install StreamShatter as a package:
`pip install streamshatter`

## Usage
```ini
usage: streamshatter [-h] [-V] [-c CACHE_FOLDER] [-l LIMIT] url [filename]

Multiplexed chunked file downloader

positional arguments:
  url                   Target URL
  filename              Output filename

options:
  -h, --help            show this help message and exit
  -V, --version         show program's version number and exit
  -c, --cache-folder CACHE_FOLDER
                        Folder to store temporary files
  -l, --limit LIMIT     Limits the amount of chunks to download
```