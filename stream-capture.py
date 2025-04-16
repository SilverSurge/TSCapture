# imports
import os
from urllib.parse import urlparse
import requests 
import subprocess

def download_file(url, save_path):
    """
    description:
        uses requests to download a file
    args:
        url: url to the file
        save_path: save path for the download file
    """
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        print(f"Downloaded: {save_path}")
    else:
        print(f"Failed to download. Status code: {response.status_code}")

def extract_links(input_path, links_file_path):
    """
    description:
        extract all the links from m3u8 file and save it to a file
    args:
        input_path: path to input m3u8 file
        links_file_path: path to file containing all links
    """
    with open(input_path, 'r') as f:
        lines = f.readlines()

    links = []
    for line in lines:
        stripped = line.strip()

        # Extract .ts segment URLs
        if stripped.startswith("http"):
            links.append(stripped)
        elif '#EXT-X-KEY' in stripped and 'URI="' in stripped:
            # Extract encryption key URL
            uri_start = stripped.find('URI="') + 5
            uri_end = stripped.find('"', uri_start)
            uri = stripped[uri_start:uri_end]
            links.append(uri)

    # Write all links to the output file
    with open(links_file_path, 'w') as f:
        for link in links:
            f.write(link + '\n')

    print(f"Links extracted and saved to: {links_file_path}")

def simplify_m3u8_file(original_path, save_path, prefix=""):
    """
    description:
        create another m3u8 files with url replaced with file names
    args:
        original_path: path to the original m3u8 file
        save_path: path to simplified m3u8 file
        prefix: prefix for the file names in the simplified m3u8
    """

    with open(original_path, 'r') as f:
        lines = f.readlines()

    simplified_lines = []
    for line in lines:
        stripped = line.strip()

        if stripped.startswith("http"):
            filename = os.path.basename(urlparse(stripped).path)
            simplified_lines.append(prefix + filename)
        elif '#EXT-X-KEY' in stripped and 'URI="' in stripped:
            # Handle encryption key
            uri_start = stripped.find('URI="') + 5
            uri_end = stripped.find('"', uri_start)
            uri = stripped[uri_start:uri_end]
            filename = os.path.basename(urlparse(uri).path)
            new_uri = prefix + filename
            simplified_line = stripped.replace(uri, new_uri)
            simplified_lines.append(simplified_line)
        else:
            simplified_lines.append(stripped)

    with open(save_path, 'w') as f:
        for line in simplified_lines:
            f.write(line + '\n')

    print(f"Simplified m3u8 file saved to: {save_path}")
    

def run_command(command):
    process = subprocess.Popen(
        command,
        shell=True,              # Allows command as a string
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True  # Auto-decode bytes to str
    )

    # Stream output line by line
    for line in process.stdout:
        print(line, end='')      # Already includes newline

    process.wait()
    print(f"Command exited with code: {process.returncode}")

if __name__ == '__main__':
    
    capture_name = 'capture_1'

    m3u8_url = "https://be4235.rcr32.ams02.cdn255.com/hls2/01/08764/cjk6te44q889_x/index-v1-a1.m3u8?t=lUYBWO8P7k2EYB081eeSpoX4fwKf3FnQw9U54ZjNN1A&s=1744784913&e=10800&f=43822852&srv=27&asn=212238&sp=5500&p="
    # setup capture directory
    os.makedirs(capture_name, exist_ok=True)

    # download m3u8 file
    download_file(m3u8_url, f"{capture_name}/original.m3u8")

    # extract links
    extract_links(f"{capture_name}/original.m3u8", f"{capture_name}/extracted_links.txt")

    # create modified m3u8
    simplify_m3u8_file(f"{capture_name}/original.m3u8", f"{capture_name}/simple.m3u8", prefix=f"{capture_name}/downloads/")

    # download all the links
    download_cmd = f"aria2c -i {capture_name}/extracted_links.txt -j 10 -d {capture_name}/downloads"

    # merge the segments
    merge_cmd = f"ffmpeg -allowed_extensions ALL -i {capture_name}/simple.m3u8 -c copy {capture_name}.ts"

    print("\nrun the following commands in order")
    print(f"command 1: {download_cmd}")
    print(f"command 2: {merge_cmd}")
    print("NOTE: command 1 may take more time depending on the network speed, it is recommened to use a VPN")
