# yt-dlp-wrapper

This project provides a small Python helper script for `yt-dlp` that automatically tests different levels of fragment concurrency before performing a full download. By benchmarking several concurrent fragment counts against a short preview clip, it picks the fastest configuration and then downloads the requested video with that setting.

## Requirements

- Python 3.8 or newer
- [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) available on your `PATH`
- [`ffmpeg`](https://ffmpeg.org/) available on your `PATH` for stream merging/remuxing

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

The script automatically adjusts settings for known services (Solidsport/Handbollplay, C More, TV4 Play, YouTube, and more) so that the right headers and formats are used without extra effort. For YouTube, the Android player client is selected to avoid recent SABR streaming restrictions and signature issues.

## Development Notes

The benchmarking phase only downloads the first 20 seconds of the video to keep tests fast. Temporary files created during the benchmark are deleted automatically after each run.

Feel free to adjust the candidate fragment counts inside `download_best` if you need different levels of parallelism.

## Add More Domains

If a service needs custom headers, formats, or extra flags for `yt-dlp`, extend the `DOMAIN_PROFILES` dictionary in `adaptiv_downloader.py`:

1. Note the domain keyword that reliably appears in the video URL.
2. Determine which settings are required (headers, preferred format string, or extra yt-dlp flags).
3. Add an entry to `DOMAIN_PROFILES` with any of the keys `headers`, `format`, or `extra_args`. For example:

   ```python
   DOMAIN_PROFILES = {
       "example.com": {
           "headers": [("Referer", "https://example.com/")],
           "format": "bestvideo+bestaudio/best",
           "extra_args": ["--cookies-from-browser", "chrome"],
       },
   }
   ```

4. Test a download from that site to confirm the new profile works.

Feel free to open a pull request with your additions so others benefit too.
