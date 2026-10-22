import os
import sys
import struct
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

INPUT_DIR = r"d:\Coding\NFS-MW\Games-folder\Grand Theft Auto Vice City"
OUTPUT_DIR = r"d:\Coding\NFS-MW\gta-vc-web"
REVCDOS_SRC = r"d:\Coding\NFS-MW\revcdos-repo\src"

FFMPEG_BIN_DIR = r"C:\Users\ayush\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin"
FFMPEG = os.path.join(FFMPEG_BIN_DIR, "ffmpeg.exe") if os.path.exists(os.path.join(FFMPEG_BIN_DIR, "ffmpeg.exe")) else "ffmpeg"
FFPROBE = os.path.join(FFMPEG_BIN_DIR, "ffprobe.exe") if os.path.exists(os.path.join(FFMPEG_BIN_DIR, "ffprobe.exe")) else "ffprobe"

ADF2MP3 = os.path.join(REVCDOS_SRC, "adf2mp3.exe")
FONT_FILE = os.path.join(REVCDOS_SRC, "sansation.ttf")
FRONTEN1_FILE = os.path.join(REVCDOS_SRC, "fronten1.txd")

if not os.path.exists(INPUT_DIR):
    print(f"Error: Input directory {INPUT_DIR} does not exist.")
    sys.exit(1)

assets_root = os.path.join(OUTPUT_DIR, "vc-assets", "local")
os.makedirs(assets_root, exist_ok=True)

freq_cache = {}
freq_lock = Lock()

def get_mp3_frequency(sample_freq, sample_mp3):
    with freq_lock:
        if sample_freq in freq_cache:
            return freq_cache[sample_freq]

    probe_out = subprocess.check_output([
        FFPROBE, "-v", "quiet", "-select_streams", "a:0",
        "-show_entries", "stream=sample_rate", "-of", "default=noprint_wrappers=1:nokey=1",
        sample_mp3
    ], text=True).strip()

    with freq_lock:
        freq_cache[sample_freq] = probe_out
    return probe_out

sizes_by_ext = {}
sizes_lock = Lock()

def process_file(src_path, dst_path):
    _, ext = os.path.splitext(dst_path)
    ext = ext.lower()

    # Skip files that should not be packaged
    if any(k in ext for k in [".git", ".exe", ".dll", ".mpg"]) or "temp.mp3" in src_path.lower():
        return
    
    # Skip sfx.sdt here because it will be generated and written by the .raw handler
    if src_path.lower().endswith("sfx.sdt"):
        return

    os.makedirs(os.path.dirname(dst_path), exist_ok=True)

    if ext == ".adf":
        print(f"[ADF] Minifying {os.path.basename(src_path)}")
        big_path = dst_path + ".big"
        subprocess.check_output([ADF2MP3, src_path, big_path], text=True)
        subprocess.check_output([
            FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-i", big_path,
            "-ar", "22050", "-ac", "2", "-f", "mp3", dst_path
        ], text=True)
        if os.path.exists(big_path):
            os.remove(big_path)

    elif ext == ".mp3":
        print(f"[MP3] Minifying {os.path.basename(src_path)}")
        subprocess.check_output([
            FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-i", src_path,
            "-ar", "22050", "-ac", "2", "-f", "mp3", dst_path
        ], text=True)

    elif ext == ".wav":
        print(f"[WAV] Converting {os.path.basename(src_path)}")
        subprocess.check_output([
            FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-i", src_path,
            "-ar", "22050", "-ac", "2", "-f", "mp3", dst_path
        ], text=True)

    elif ext == ".img":
        img_size = os.path.getsize(src_path)
        base, _ = os.path.splitext(src_path)
        dir_path = base + ".dir"
        if not os.path.exists(dir_path):
            dir_path = base + ".DIR"
        if not os.path.exists(dir_path):
            raise Exception(f"No matching .dir file found for {src_path}")

        print(f"[IMG] Extracting {os.path.basename(src_path)} -> {os.path.basename(dst_path)}")
        os.makedirs(dst_path, exist_ok=True)

        with open(dir_path, "rb") as dirf, open(src_path, "rb") as imgf:
            while True:
                entry = dirf.read(32)
                if len(entry) == 0:
                    break
                if len(entry) < 32:
                    break

                offset_sectors, size_sectors, name = struct.unpack("<II24s", entry)
                name = name.split(b"\0", 1)[0].decode("ascii", errors="ignore").lower()
                offset = offset_sectors * 2048
                size = size_sectors * 2048

                if offset + size > img_size:
                    continue

                imgf.seek(offset)
                data = imgf.read(size)
                out_path = os.path.join(dst_path, name)
                with open(out_path, "wb") as outf:
                    outf.write(data)
        return

    elif ext == ".raw":
        if src_path.lower().endswith("sfx.raw"):
            base_dir = os.path.dirname(src_path)
            sdt_path = os.path.join(base_dir, "sfx.SDT")
            if not os.path.exists(sdt_path):
                sdt_path = os.path.join(base_dir, "sfx.sdt")

            def_dst_path = os.path.join(os.path.dirname(dst_path), "sfx.sdt")

            print(f"[SFX] Parsing {os.path.basename(src_path)} & sfx.sdt...")
            with open(sdt_path, "rb") as deff, open(src_path, "rb") as sfxf:
                samples = []
                idx = 0
                while True:
                    sample_data = deff.read(20)
                    if not sample_data or len(sample_data) < 20:
                        break
                    offset, size, frequency, loop_start, loop_end = struct.unpack("<IIIIi", sample_data)
                    samples.append({
                        "index": idx,
                        "offset": offset,
                        "size": size,
                        "frequency": frequency,
                        "loop_start": loop_start,
                        "loop_end": loop_end,
                        "raw": sfxf.read(size)
                    })
                    idx += 1

            os.makedirs(dst_path, exist_ok=True)
            print(f"[SFX] Converting {len(samples)} samples to MP3 with 12 parallel workers...")

            def process_sample(sample):
                i = sample["index"]
                raw_file = os.path.join(dst_path, f"{i}.raw")
                mp3_file = os.path.join(dst_path, f"{i}.mp3")

                with open(raw_file, "wb") as rf:
                    rf.write(sample["raw"])

                subprocess.check_output([
                    FFMPEG, "-hide_banner", "-loglevel", "error", "-y",
                    "-f", "s16le", "-ar", str(sample["frequency"]),
                    "-i", raw_file, mp3_file
                ], text=True)

                sample["mp3_frequency"] = get_mp3_frequency(sample["frequency"], mp3_file)
                if os.path.exists(raw_file):
                    os.remove(raw_file)

            with ThreadPoolExecutor(max_workers=12) as sample_pool:
                futures = [sample_pool.submit(process_sample, s) for s in samples]
                for idx, f in enumerate(futures):
                    f.result()
                    if (idx + 1) % 1000 == 0 or (idx + 1) == len(samples):
                        print(f"      SFX progress: {idx + 1}/{len(samples)} samples converted")

            print("[SFX] Writing updated sfx.sdt table...")
            with open(def_dst_path, "wb") as out_sdt:
                for s in samples:
                    out_sdt.write(struct.pack(
                        "<IIIIi",
                        s["offset"],
                        s["size"],
                        int(s["mp3_frequency"]),
                        s["loop_start"],
                        s["loop_end"]
                    ))
            print("[SFX] Sound effects conversion finished!")
            return

    else:
        shutil.copy2(src_path, dst_path)

    with sizes_lock:
        if os.path.exists(dst_path):
            sizes_by_ext[ext] = sizes_by_ext.get(ext, 0) + os.path.getsize(dst_path)

def collect_all_files(src_root, dst_root):
    file_pairs = []
    for root, dirs, files in os.walk(src_root):
        rel_path = os.path.relpath(root, src_root)
        if rel_path == ".":
            target_dir = dst_root
        else:
            target_dir = os.path.join(dst_root, rel_path.lower())

        for file in files:
            src_f = os.path.join(root, file)
            dst_f = os.path.join(target_dir, file.lower())
            file_pairs.append((src_f, dst_f))
    return file_pairs

def main():
    print("=== Starting GTA Vice City Browser Asset Compilation ===")
    print(f"Input: {INPUT_DIR}")
    print(f"Output: {assets_root}")

    all_files = collect_all_files(INPUT_DIR, assets_root)
    print(f"Collected {len(all_files)} files to process.")

    # Process files
    # Note: process heavy archives and sound files, while copying rest
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(process_file, s, d) for s, d in all_files]
        for idx, f in enumerate(futures):
            f.result()
            if (idx + 1) % 50 == 0 or (idx + 1) == len(all_files):
                print(f"File progress: {idx + 1}/{len(all_files)} files processed")

    # Fonts and Frontend textures
    fonts_dir = os.path.join(assets_root, "fonts")
    os.makedirs(fonts_dir, exist_ok=True)
    if os.path.exists(FONT_FILE):
        print("Copying sansation.ttf font...")
        shutil.copy2(FONT_FILE, os.path.join(fonts_dir, os.path.basename(FONT_FILE).lower()))

    models_dir = os.path.join(assets_root, "models")
    os.makedirs(models_dir, exist_ok=True)
    if os.path.exists(FRONTEN1_FILE):
        print("Copying fronten1.txd frontend model...")
        shutil.copy2(FRONTEN1_FILE, os.path.join(models_dir, os.path.basename(FRONTEN1_FILE).lower()))

    print("\n=== Asset compilation finished successfully! ===")
    print("Asset sizes by extension:")
    for ext, sz in sorted(sizes_by_ext.items(), key=lambda x: x[1], reverse=True):
        if sz >= 1024 * 1024:
            print(f"  {ext}: {sz / (1024*1024):.2f} MB")

if __name__ == "__main__":
    main()
