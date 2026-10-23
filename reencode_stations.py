import os
import subprocess
import time

AUDIO_DIR = r"d:\Coding\NFS-MW\gta-vc-web\vc-assets\local\audio"

STATIONS = {
    "kchat.adf":   {"ac": "1", "b": "28k"},   # 104 mins -> ~21 MB
    "vcpr.adf":    {"ac": "1", "b": "32k"},   # 86.4 mins -> ~20 MB
    "vrock.adf":   {"ac": "2", "b": "36k"},   # 77.4 mins -> ~20 MB
    "wild.adf":    {"ac": "2", "b": "40k"},   # 68.5 mins -> ~20 MB
    "wave.adf":    {"ac": "2", "b": "40k"},   # 66.1 mins -> ~19 MB
    "fever.adf":   {"ac": "2", "b": "44k"},   # 63.2 mins -> ~20 MB
    "espant.adf":  {"ac": "2", "b": "44k"},   # 61.6 mins -> ~20 MB
    "flash.adf":   {"ac": "2", "b": "44k"},   # 59.8 mins -> ~19 MB
    "emotion.adf": {"ac": "2", "b": "44k"},   # 59.1 mins -> ~19 MB
}

def main():
    print("Starting audio re-encoding for Cloudflare 25 MB limit...")
    start_total = time.time()
    for filename, cfg in STATIONS.items():
        filepath = os.path.join(AUDIO_DIR, filename)
        if not os.path.exists(filepath):
            print(f"[SKIP] {filename} not found.")
            continue

        original_size = os.path.getsize(filepath) / (1024 * 1024)
        temp_out = filepath + ".tmp.mp3"
        print(f"\n[ENCODING] {filename} ({original_size:.2f} MB) -> Channels: {cfg['ac']}, Bitrate: {cfg['b']}...")

        cmd = [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-i", filepath,
            "-ar", "22050",
            "-ac", cfg["ac"],
            "-b:a", cfg["b"],
            "-f", "mp3",
            temp_out
        ]
        t0 = time.time()
        subprocess.check_call(cmd)
        elapsed = time.time() - t0

        new_size = os.path.getsize(temp_out) / (1024 * 1024)
        print(f"  Done in {elapsed:.1f}s: {original_size:.2f} MB -> {new_size:.2f} MB")

        # Replace original file
        os.replace(temp_out, filepath)

    total_time = time.time() - start_total
    print(f"\nAll 9 radio stations successfully re-encoded in {total_time:.1f}s!")

if __name__ == "__main__":
    main()
