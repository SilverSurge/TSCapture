
# Transport Stream Capture Tool

This script simplifies the process of downloading and merging `.ts` video segments from a remote `.m3u8` playlist (HLS stream). It extracts URLs from the playlist, optionally simplifies the file paths, and generates commands to download and merge the segments locally.

---

## 🚀 Features

- 📥 Download `.m3u8` playlists directly from a URL
- 🔗 Extract `.ts` segment and encryption key links
- ✂️ Simplify `.m3u8` file with just file names (optionally with a prefix)
- ⚡ Generates `aria2c` and `ffmpeg` commands for fast downloading and merging
- ✅ Handles AES-128 encrypted streams

---

## 🔧 Requirements

- Python 3.x
- [aria2](https://aria2.github.io/) — for parallel downloading
- [ffmpeg](https://ffmpeg.org/) — for merging `.ts` files
- Python libraries:
  ```bash
  pip install requests
  ```

---

## 📂 Folder Structure

When you run the script, it creates a folder like this:

```
capture_1/
├── original.m3u8
├── extracted_links.txt
├── simple.m3u8
└── downloads/
    ├── seg-1-v1-a1.ts
    ├── seg-2-v1-a1.ts
    └── ...
```

---

## 📜 Usage

1. Update the `m3u8_url` and `capture_name` inside `main()` in the script.
2. Run the script:

   ```bash
   python capture.py
   ```

3. The script prints two commands:

   - One to download all the `.ts` files:
     ```bash
     aria2c -i capture_1/extracted_links.txt -j 10 -d capture_1/downloads
     ```

   - One to merge them using `ffmpeg`:
     ```bash
     ffmpeg -allowed_extensions ALL -i capture_1/simple.m3u8 -c copy capture_1.ts
     ```

4. **Important Note:** If the video is region-locked or protected, consider using a VPN while downloading.

---

## 📁 Optional Enhancements

- Handle decryption manually (if `ffmpeg` fails to auto-decrypt)
- Add CLI arguments using `argparse` for full automation
- Add auto-download and merge mode inside Python

---

## 📃 License

MIT License — feel free to fork, use, and contribute!

---
