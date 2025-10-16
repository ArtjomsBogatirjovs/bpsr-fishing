
<div align="center">
  <h1 align="center">
    <img src="icons/airona.png" width="300"/>
    <br/>
    Blue protocol: Star Resonance AutoFisher
  </h1> 
<h3><i>Image-recognition-based automation for <b>Star Resonance</b>. Simulates user clicks via Windows API without reading game memory or modifying any game files or data.</i></h3>
</div>

![Static Badge](https://img.shields.io/badge/platform-Windows-blue?color=blue)

# Disclaimer

This software is an external tool designed to automate *Star Resonance* gameplay.
It interacts only through the visible user interface and complies with relevant laws and regulations.
The goal is to simplify player interaction without breaking game balance, providing unfair advantages, or modifying any files or code.

This project is open-source and free, intended **only for personal learning and communication**.
It must be used **only on personal accounts** and **not for commercial or profit-making purposes**.

All consequences arising from the use of this software are the user's responsibility.
If you discover anyone using this software for paid boosting services, that is their personal behavior — this project does **not** authorize such use.
We do **not** authorize anyone to sell this software.
Sold versions may include malicious code that could steal your account or system data — such cases are unrelated to this software.

### Highlights

1. Works under any **16:9 resolution** — windowed or fullscreen, scaling independent
2. Cannot run in the background
3. AI detects fish positions for precise casting

### Troubleshooting

If issues occur, please go through this checklist before reporting:

1. **Wrong fish direction:**
   In the fishing UI, press **O** to hide your and others’ character names. Make sure no boats are present — they can be mistaken for splashes.

2. **Slow pull or delayed response:**
   The script’s performance is limited. Lower game resolution to increase refresh rate.

3. **Extraction issues:**
   Extract the archive to a directory with **only English characters**.

4. **Antivirus interference:**
   Add the download and extraction folders to your **antivirus/Windows Defender whitelist**.

5. **Display settings:**
   Ensure the game runs at **16:9 resolution**, disable GPU filters and sharpening, use default brightness, and turn off on-screen FPS counters.

6. **Custom key bindings:**
   If you changed default keys, update them in the app. Keys not listed in settings are unsupported.

7. **Still having issues?**
   Submit a screenshot and log file from the moment the issue occurs.

---

### Running From Source

> Only supports **Python 3.12**

```bash
# CPU version, using OpenVINO
pip install -r requirements.txt --upgrade  # install/update dependencies; rerun after updates
python main.py        # run the release version
python main_debug.py  # run the debug version
```

---

### Acknowledgments

* This project is developed based on [ok-script](https://github.com/ok-oldking/ok-script).

