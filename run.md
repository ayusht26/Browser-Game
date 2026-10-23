# How to Run Grand Theft Auto: Vice City (WebAssembly Browser Port)

This project runs **Grand Theft Auto: Vice City** natively in modern web browsers using WebAssembly (WASM), WebGL, and Emscripten.

---

## ⚡ Quick Start (Ready to Play)

All game assets are already compiled and ready inside `gta-vc-web/`. You only need **Python 3**.

### 1. Start the Local Server
Open a terminal (PowerShell, Command Prompt, or bash) in the project root (`d:\Coding\NFS-MW`) and run:

```bash
python serve.py
```

You should see output similar to:
```text
============================================================
   GRAND THEFT AUTO: VICE CITY - WEBASSEMBLY PORT
   Server running at: http://localhost:8080
   Serving directory: d:\Coding\NFS-MW\gta-vc-web
============================================================
```

> **Why `serve.py`?**  
> Do not use standard `python -m http.server` or open `index.html` directly via `file://`.  
> The WebAssembly engine requires specific HTTP response headers (`Cross-Origin-Opener-Policy: same-origin` and `Cross-Origin-Embedder-Policy: require-corp`) for high-performance memory isolation, as well as custom MIME types for `.wasm`, `.mp3`, `.dff`, and `.txd` game assets. `serve.py` handles all of this automatically.

### 2. Launch the Game
1. Open your browser (Google Chrome, Microsoft Edge, Brave, or Mozilla Firefox) and navigate to:
   ```text
   http://localhost:8080
   ```
2. Click the **"Launch Vice City"** button in the center overlay.
3. The virtual filesystem will mount and preload game assets.
4. Once the engine finishes loading, click into the game screen to lock mouse controls and enjoy!

---

## 🎮 Controls

### On-Foot Controls
| Action | Key / Input |
|---|---|
| **Move** | <kbd>W</kbd> <kbd>A</kbd> <kbd>S</kbd> <kbd>D</kbd> or Arrow Keys |
| **Look / Aim** | Mouse (pointer lock activates on click) |
| **Sprint** | Left <kbd>Shift</kbd> |
| **Jump** | <kbd>Space</kbd> |
| **Attack / Shoot** | Left Mouse Button or Left <kbd>Ctrl</kbd> |
| **Aim Weapon** | Right Mouse Button |
| **Enter / Exit Vehicle** | <kbd>F</kbd> or <kbd>Enter</kbd> |
| **Crouch** | <kbd>C</kbd> |
| **Cycle Weapon** | Mouse Wheel or <kbd>[ </kbd> / <kbd> ]</kbd> |
| **Pause / Menu** | <kbd>Esc</kbd> |

### Driving Controls
| Action | Key / Input |
|---|---|
| **Accelerate** | <kbd>W</kbd> or <kbd>Up Arrow</kbd> |
| **Brake / Reverse** | <kbd>S</kbd> or <kbd>Down Arrow</kbd> |
| **Steer** | <kbd>A</kbd> / <kbd>D</kbd> or Left / Right Arrows |
| **Handbrake** | <kbd>Space</kbd> |
| **Horn / Siren** | Left <kbd>Shift</kbd> |
| **Change Radio Station** | <kbd>Insert</kbd> / <kbd>Delete</kbd> or <kbd>1</kbd> / <kbd>2</kbd> |
| **Change Camera** | <kbd>V</kbd> |
| **Exit Vehicle** | <kbd>F</kbd> or <kbd>Enter</kbd> |

---

## ⌨️ Classic Cheat Codes

You can type these cheat codes directly on your keyboard at any time during gameplay:

- **Full Health:** `ASPIRINE`
- **Full Armor:** `PRECIOUSPROTECTION`
- **Weapons Set 1 (Thug Tools):** `THUGSTOOLS`
- **Weapons Set 2 (Professional Tools):** `PROFESSIONALTOOLS`
- **Weapons Set 3 (Heavy / Nutter Tools):** `NUTTERTOOLS`
- **Spawn Rhino Tank:** `PANZER`
- **Blow Up All Nearby Cars:** `BIGBANG`
- **Flying Cars:** `COMEFLYWITHME`
- **Faster Game Clock:** `LIFEISPASSINGMEBY`
- **Clear Wanted Level:** `LEAVEMEALONE`

---

## 💾 Save Games

- Save games are automatically persisted in your browser's **IndexedDB** virtual storage (`/vc-assets/local/userfiles`).
- When saving at any hideout (e.g. the Ocean View Hotel), your progress will remain saved across browser restarts on the same machine and browser profile.

---

## 🛠️ Advanced: Rebuilding Game Data (Optional)

You **do not** need to do this under normal circumstances because all game files are already processed in `gta-vc-web/vc-assets/local`.

However, if you wish to re-extract or update assets from a clean PC installation of GTA Vice City:

1. **Prerequisites**:
   - Python 3.x
   - [FFmpeg](https://ffmpeg.org/) installed and available in your `PATH` (or configured inside `build_vc_data.py`)
   - Original PC game folder placed in `Games-folder\Grand Theft Auto Vice City`
2. **Run compilation**:
   ```bash
   python build_vc_data.py
   ```
   This will unpack `.img` archives, convert `.raw` SFX to `.mp3`, encode audio streams, and output the optimized assets directly into `gta-vc-web/vc-assets/local`.

---

## ❓ Troubleshooting

- **Port 8080 in use?**
  Open `serve.py` and modify line 6:
  ```python
  PORT = 8081  # Or any open port
  ```
  Then navigate to `http://localhost:8081`.

- **Black screen or assets failing to load?**
  Ensure you are using `python serve.py` to launch the server, rather than opening `host.html` directly or using third-party static servers that do not inject the required `Cross-Origin-Opener-Policy` and `Cross-Origin-Embedder-Policy` headers.

- **Audio not playing?**
  Modern browsers block auto-playing audio until the user interacts with the page. Simply click anywhere on the game window to enable audio.

- **Mouse cursor leaving the window?**
  Click inside the game view to trigger the browser's pointer lock mode. Press <kbd>Esc</kbd> anytime to release the cursor.
