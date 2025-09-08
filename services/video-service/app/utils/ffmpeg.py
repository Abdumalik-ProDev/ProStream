import subprocess
import shlex
from pathlib import Path
from app.core.config import settings

# Using system ffmpeg for workers. This is synchronous - run inside Celery workers (not FastAPI)
def transcode_to_hls(input_path: str, output_dir: str):
    """
    Produce multiple renditions and an HLS master playlist.
    output_dir should be local filesystem path (worker workspace).
    """
    # Example renditions (resolution, bitrate)
    renditions = [
        {"name": "1080p", "scale": "1920:1080", "vb": "5000k"},
        {"name": "720p", "scale": "1280:720", "vb": "3000k"},
        {"name": "480p", "scale": "854:480", "vb": "1500k"},
    ]

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Create a rendition-level HLS with variant playlists
    variant_playlist_lines = []

    for r in renditions:
        out_prefix = Path(output_dir) / r["name"]
        out_prefix.mkdir(parents=True, exist_ok=True)
        out_ts = str(out_prefix / "index.m3u8")
        cmd = (
            f'{settings.FFMPEG_PATH} -y -i "{input_path}" '
            f'-vf scale={r["scale"]} -c:a aac -ar 48000 -b:a 128k '
            f'-c:v h264 -profile:v main -crf 20 -g 48 -keyint_min 48 -sc_threshold 0 '
            f'-b:v {r["vb"]} -maxrate {r["vb"]} -bufsize 2M '
            f'-hls_time 6 -hls_playlist_type vod -hls_segment_filename "{out_prefix}/seg%03d.ts" '
            f'"{out_ts}"'
        )
        subprocess.check_call(shlex.split(cmd))
        # add to variant playlist
        variant_playlist_lines.append(f'#EXT-X-STREAM-INF:BANDWIDTH={int(r["vb"].replace("k",""))*1000},RESOLUTION={r["scale"]}\n{r["name"]}/index.m3u8')

    master_playlist = "#EXTM3U\n" + "\n".join(variant_playlist_lines)
    master_path = Path(output_dir) / "master.m3u8"
    master_path.write_text(master_playlist)
    return str(master_path)