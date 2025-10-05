import subprocess
import tempfile
import os
import time
from datetime import datetime

# Domain-specific options applied to yt-dlp invocations.
DOMAIN_PROFILES = {
    "handbollplay": {
        "headers": [
            ("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"),
            ("Referer", "https://handbollplay.se/"),
        ],
    },
    "solidsport": {
        "headers": [
            ("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"),
            ("Referer", "https://solidsport.com/"),
        ],
    },
    "solidtango": {
        "headers": [
            ("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"),
            ("Referer", "https://handbollplay.se/"),
        ],
    },
    "cmore": {
        "headers": [
            ("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                           "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"),
            ("Referer", "https://www.cmore.se/"),
        ],
    },
    "tv4play": {
        "headers": [
            ("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                           "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"),
            ("Referer", "https://www.tv4play.se/"),
        ],
    },
    "youtube.com": {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best",
        "extra_args": ["--extractor-args", "youtube:player_client=android"],
    },
    "youtu.be": {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best",
        "extra_args": ["--extractor-args", "youtube:player_client=android"],
    },
}

DEFAULT_FORMAT = "best"


def resolve_domain_profile(url):
    profile = {
        "headers": [],
        "extra_args": [],
        "format": None,
        "matched": [],
    }
    for domain, options in DOMAIN_PROFILES.items():
        if domain in url:
            profile["matched"].append(domain)
            profile["headers"].extend(options.get("headers", []))
            profile["extra_args"].extend(options.get("extra_args", []))
            if profile["format"] is None and options.get("format"):
                profile["format"] = options["format"]
    return profile


def extend_command_with_profile(cmd, profile):
    for header_name, header_value in profile["headers"]:
        cmd += ["--add-header", f"{header_name}: {header_value}"]
    cmd += profile["extra_args"]
    return cmd


def test_speed(url, fragments, domain_profile):
    print(f"Testing with {fragments} parallel fragments ...")
    with tempfile.TemporaryDirectory() as temp_dir:
        output_template = os.path.join(temp_dir, "probe.%(ext)s")

        start_time = time.time()
        cmd = [
            "yt-dlp",
            url,
            "-f", domain_profile["format"] or DEFAULT_FORMAT,
            "--concurrent-fragments", str(fragments),
            "--no-part", "--no-overwrites",
            "--download-sections", "*00:00:00-00:00:20",
            "-o", output_template,
        ]
        cmd = extend_command_with_profile(cmd, domain_profile)
        result = subprocess.run(cmd, capture_output=True, text=True)
        elapsed = time.time() - start_time

        if result.returncode != 0:
            print(f"  Failed with {fragments} fragments")
            return 0

        downloaded_bytes = 0
        for root, _, files in os.walk(temp_dir):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                downloaded_bytes += os.path.getsize(file_path)

    print(f"  Completed in {elapsed:.1f}s")
    if elapsed <= 0 or downloaded_bytes == 0:
        return 0

    return (downloaded_bytes / 1024) / elapsed


def download_best(url):
    print("Smart yt-dlp downloader - testing optimal parallelism.\n")

    domain_profile = resolve_domain_profile(url)
    if domain_profile["matched"]:
        matched_domains = ", ".join(domain_profile["matched"])
        print(f"Detected {matched_domains} link - applying custom profile.\n")

    candidates = [5, 10, 15, 20]
    best_speed = 0
    best_fragments = 10

    for fragments in candidates:
        speed = test_speed(url, fragments, domain_profile)
        if speed > best_speed:
            best_speed = speed
            best_fragments = fragments

    print(f"\nBest result: {best_fragments} fragments (estimated speed: {best_speed:.1f} KB/s)\n")

    user_filename = input("Enter filename (without .mp4) or press Enter for the default name: ").strip()
    if user_filename == "":
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_name = f"video_{timestamp}.mp4"
    else:
        output_name = user_filename if user_filename.endswith(".mp4") else f"{user_filename}.mp4"

    cmd = [
        "yt-dlp",
        url,
        "-f", domain_profile["format"] or DEFAULT_FORMAT,
        "--concurrent-fragments", str(best_fragments),
        "--merge-output-format", "mp4",
        "-N", str(best_fragments),
        "--progress", "--newline", "--console-title",
        "--continue", "--no-overwrites",
        "-o", output_name,
    ]
    cmd = extend_command_with_profile(cmd, domain_profile)

    print(f"\nStarting download with {best_fragments} parallel fragments.\n")
    subprocess.run(cmd)


if __name__ == "__main__":
    url = input("Paste video URL: ").strip()
    download_best(url)
