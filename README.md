# yt-dlp-wrapper

This project provides a small Python helper script for `yt-dlp` that automatically tests different levels of fragment concurrency before performing a full download. By benchmarking several concurrent fragment counts against a short preview clip, it picks the fastest configuration and then downloads the requested video with that setting.

## Requirements

- Python 3.8 or newer
- [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) available on your `PATH`

Install `yt-dlp` with pip if needed:

```bash
pip install yt-dlp
```

## Usage

Run the script directly with Python:

```bash
python adaptiv_downloader.py
```

1. Paste the video URL when prompted.
2. Wait while the script tests a handful of `--concurrent-fragments` values.
3. Choose an output filename (or press Enter to auto-generate one).
4. The script downloads the best-quality stream using the fastest-performing concurrency.

The script automatically adds Solidsport/Handbollplay headers when those domains are detected so that downloads succeed for those services.

## Development Notes

The benchmarking phase only downloads the first 20 seconds of the video to keep tests fast. Temporary files created during the benchmark are deleted automatically after each run.

Feel free to adjust the candidate fragment counts inside `download_best` if you need different levels of parallelism.

## Add More Domains

If a service requires extra request headers for `yt-dlp` to work, add it to the `HEADER_PROFILES` dictionary in `adaptiv_downloader.py`:

1. Note the domain keyword that reliably appears in the video URL.
2. Determine which headers are needed (e.g., User-Agent, Referer, cookies).
3. Add an entry to `HEADER_PROFILES` with the keyword and a list of `(header, value)` tuples.
4. Test a download from that site to confirm the new profile works.

Feel free to open a pull request with your additions so others benefit too.
