import subprocess
import tempfile
import os
import time
from datetime import datetime

# Mapping of domain keywords to required request headers for yt-dlp.
HEADER_PROFILES = {
    "handbollplay": [
        ("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"),
        ("Referer", "https://handbollplay.se/"),
    ],
    "solidsport": [
        ("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"),
        ("Referer", "https://solidsport.com/"),
    ],
    "solidtango": [
        ("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"),
        ("Referer", "https://handbollplay.se/"),
    ],
    "cmore": [
        ("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"),
        ("Referer", "https://www.cmore.se/"),
    ],
    "tv4play": [
        ("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"),
        ("Referer", "https://www.tv4play.se/"),
    ],
}

def test_speed(url, fragments):
    print(f"Testing with {fragments} parallel fragments ...")
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_name = temp_file.name
    temp_file.close()

    start_time = time.time()
    cmd = [
        "yt-dlp",
        url,
        "-f", "best",
        "--concurrent-fragments", str(fragments),
        "--no-part", "--no-overwrites",
        "--download-sections", "*00:00:00-00:00:20",  # download only 20 seconds for testing
        "-o", temp_name
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = time.time() - start_time

    # Remove temporary file
    if os.path.exists(temp_name):
        os.remove(temp_name)

    # Verify that the command succeeded
    if result.returncode != 0:
        print(f"  Failed with {fragments} fragments")
        return 0

    size_kb = 0
    for line in result.stdout.splitlines():
        if "of" in line and "at" in line:
            try:
                parts = line.split("at")[1].strip().split()
                size_kb = float(parts[0].replace("KiB/s", "").replace("MiB/s", "")) * (1024 if "MiB" in parts[0] else 1)
            except Exception:
                pass

    print(f"  Completed in {elapsed:.1f}s")
    return size_kb / elapsed if elapsed > 0 else 0


def download_best(url):
    print("Smart yt-dlp downloader - testing optimal parallelism.\n")

    candidates = [5, 10, 15, 20]
    best_speed = 0
    best_fragments = 10

    # Run tests for each candidate level
    for fragments in candidates:
        speed = test_speed(url, fragments)
        if speed > best_speed:
            best_speed = speed
            best_fragments = fragments

    print(f"\nBest result: {best_fragments} fragments (estimated speed: {best_speed:.1f} KB/s)\n")

    # Ask for a custom file name
    user_filename = input("Enter filename (without .mp4) or press Enter for the default name: ").strip()
    if user_filename == "":
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_name = f"video_{timestamp}.mp4"
    else:
        output_name = user_filename if user_filename.endswith(".mp4") else f"{user_filename}.mp4"

    cmd = [
        "yt-dlp",
        url,
        "-f", "best",
        "--concurrent-fragments", str(best_fragments),
        "--merge-output-format", "mp4",
        "-N", str(best_fragments),
        "--progress", "--newline", "--console-title",
        "--continue", "--no-overwrites",
        "-o", output_name,
    ]

    for domain, headers in HEADER_PROFILES.items():
        if domain in url:
            print(f"Detected {domain} link - adding custom headers.")
            for header_name, header_value in headers:
                cmd += ["--add-header", f"{header_name}: {header_value}"]

    print(f"\nStarting download with {best_fragments} parallel fragments.\n")
    subprocess.run(cmd)


if __name__ == "__main__":
    url = input("Paste video URL: ").strip()
    download_best(url)
