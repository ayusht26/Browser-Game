import os
import json
import struct
import gzip

WEB_DIR = r"d:\Coding\NFS-MW\gta-vc-web"
PRELOAD_LIST = os.path.join(WEB_DIR, "preload_files.list")
PACKS_DIR = os.path.join(WEB_DIR, "packs")
os.makedirs(PACKS_DIR, exist_ok=True)

# Read file list, excluding flash.adf
files = []
with open(PRELOAD_LIST, "r", encoding="utf-8") as f:
    for line in f:
        p = line.strip().replace("\\", "/")
        if not p or p.startswith("#"):
            continue
        if p.endswith("flash.adf"):
            continue
        files.append(p)

print(f"Total startup files to package: {len(files)}")

# Collect file sizes and paths
file_entries = []
missing = 0
for rel_path in files:
    abs_path = os.path.join(WEB_DIR, rel_path)
    if os.path.exists(abs_path):
        sz = os.path.getsize(abs_path)
        file_entries.append((rel_path, abs_path, sz))
    else:
        missing += 1

print(f"Found {len(file_entries)} files (Missing: {missing})")
total_raw_size = sum(sz for _, _, sz in file_entries)
print(f"Total uncompressed size: {total_raw_size / (1024*1024):.2f} MB")

# Split into 3 balanced packs
NUM_PACKS = 3
target_per_pack = total_raw_size / NUM_PACKS

packs = [[] for _ in range(NUM_PACKS)]
curr_pack = 0
curr_size = 0

for item in file_entries:
    packs[curr_pack].append(item)
    curr_size += item[2]
    if curr_size >= target_per_pack and curr_pack < NUM_PACKS - 1:
        curr_pack += 1
        curr_size = 0

manifest_packs = []

for idx, pack_items in enumerate(packs):
    pack_name = f"startup_{idx + 1}.pack.gz"
    pack_path = os.path.join(PACKS_DIR, pack_name)
    
    manifest = {}
    body = bytearray()
    for rel_path, abs_path, sz in pack_items:
        with open(abs_path, "rb") as f:
            content = f.read()
        offset = len(body)
        body.extend(content)
        manifest[rel_path] = [offset, len(content)]
        
    manifest_bytes = json.dumps(manifest).encode("utf-8")
    header = struct.pack("<I", len(manifest_bytes))
    raw_pack = header + manifest_bytes + bytes(body)
    
    compressed = gzip.compress(raw_pack, compresslevel=6)
    with open(pack_path, "wb") as f:
        f.write(compressed)
        
    gz_size = len(compressed)
    raw_size = len(raw_pack)
    print(f"[{pack_name}] {len(pack_items)} files | Raw: {raw_size/(1024*1024):.2f} MB | Compressed: {gz_size/(1024*1024):.2f} MB")
    
    manifest_packs.append({
        "file": pack_name,
        "files_count": len(pack_items),
        "raw_bytes": raw_size,
        "gz_bytes": gz_size
    })

meta_path = os.path.join(PACKS_DIR, "packs.json")
with open(meta_path, "w", encoding="utf-8") as f:
    json.dump({
        "packs": manifest_packs,
        "total_files": len(file_entries),
        "total_raw_bytes": total_raw_size,
        "total_gz_bytes": sum(p["gz_bytes"] for p in manifest_packs)
    }, f, indent=2)

print("\nPacks generation complete!")
