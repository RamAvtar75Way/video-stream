import os
import subprocess

def encode_to_hls(input_path: str, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)

    output_playlist = os.path.join(output_dir, "index.m3u8")

    command = [
        "ffmpeg",
        "-i", input_path,
        "-profile:v", "baseline",
        "-level", "3.0",
        "-start_number", "0",
        "-hls_time", "10",
        "-hls_list_size", "0",
        "-f", "hls",
        output_playlist
    ]

    subprocess.run(command, check=True)

    return output_playlist
