# imports
import os
from urllib.parse import urlparse
import requests 
import subprocess
import argparse


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
    parser = argparse.ArgumentParser(description='📺 Capture and process transport streams from m3u8 links.')
    parser.add_argument('m3u8_url', type=str, help='🔗 URL to the .m3u8 file')
    parser.add_argument('capture_name', type=str, help='📁 Directory name for the capture')

    args = parser.parse_args()
    m3u8_url = args.m3u8_url
    capture_name = args.capture_name

    print("🚀 Starting capture process...")
    print(f"🔗 m3u8 URL: {m3u8_url}")
    print(f"📁 Capture Directory: {capture_name}\n")

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

    print("\n📥 Run the following commands to complete the process:")
    print(f"🔧 Step 1: {download_cmd}")
    print(f"🎞️  Step 2: {merge_cmd}")
    print("💡 NOTE: Step 1 may take time depending on your network speed. Using a VPN is recommended.")
