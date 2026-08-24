#!/usr/bin/env python3
"""
UNMIX - local stem separation.  ONE FILE. Just run it.

Splits any song into vocals / drums / bass / other (plus an instrumental), then
opens a mixing console in your browser so you can solo, mute, loop and export
any combination.

Windows : double-click this file.
Mac     : right-click -> Open With -> Python Launcher.  Or: python3 UNMIX.py
Linux   : python3 UNMIX.py

The first run installs what it needs (about 500 MB) and prints what it's doing.
Every run after that starts in a couple of seconds. Nothing is ever uploaded.
"""

from __future__ import annotations

import base64
import importlib
import io
import json
import os
import shutil
import subprocess
import sys
import threading
import time
import traceback
import uuid
import zipfile
from dataclasses import dataclass, field, asdict
from pathlib import Path

APP_FILE = Path(__file__).resolve()
APP_DIR = APP_FILE.parent


# ======================================================================================
#  Console that never disappears
# ======================================================================================

_INTERACTIVE = sys.stdin is not None and sys.stdin.isatty()


def hold(code: int = 0):
    """Stop the window vanishing before the person can read the error."""
    print()
    try:
        if _INTERACTIVE or os.name == "nt":
            input("Press Enter to close this window...")
    except Exception:
        pass
    sys.exit(code)


def banner(text: str) -> None:
    print()
    print("  " + "-" * 62)
    print("  " + text)
    print("  " + "-" * 62)
    print()


# ======================================================================================
#  Dependency bootstrap
# ======================================================================================

def _pip(*args: str) -> bool:
    cmd = [sys.executable, "-m", "pip", "install", "--disable-pip-version-check", *args]
    print("      pip install " + " ".join(a for a in args if not a.startswith("--index")))
    result = subprocess.run(cmd)
    if result.returncode != 0:
        # Some Linux distros refuse to touch the system Python without this flag
        print("      retrying...")
        result = subprocess.run(cmd + ["--break-system-packages"])
    return result.returncode == 0


def _have(module: str) -> bool:
    try:
        importlib.import_module(module)
        return True
    except Exception:
        return False


def ensure_deps() -> None:
    if sys.version_info < (3, 9):
        banner("Python 3.9 or newer is required.")
        print(f"  You're running {sys.version.split()[0]} from:")
        print(f"  {sys.executable}")
        print()
        print("  Install a current version from https://www.python.org/downloads/")
        hold(1)

    needs_torch = not _have("torch")
    rest = [
        (m, spec) for m, spec in [
            ("flask", "flask"),
            ("soundfile", "soundfile"),
            ("numpy", "numpy"),
            ("lameenc", "lameenc"),
            ("tqdm", "tqdm"),
            ("demucs.pretrained", "demucs==4.0.1"),
        ] if not _have(m)
    ]

    if not needs_torch and not rest:
        return

    banner("First run - installing what UNMIX needs. This takes a few minutes.")
    print("  It downloads roughly 500 MB, once. Leave this window open.")
    print(f"  Installing into: {sys.executable}")
    print()

    if not _have("pip"):
        print("  This Python has no pip, so nothing can be installed.")
        print("  Reinstall Python from python.org and keep the default options.")
        hold(1)

    _pip("--upgrade", "pip")

    if needs_torch:
        print()
        print("  [1/2] PyTorch - the big one. Go make a coffee.")
        if sys.platform == "darwin":
            ok = _pip("torch", "torchaudio")
        else:
            ok = _pip("torch", "torchaudio",
                      "--index-url", "https://download.pytorch.org/whl/cpu")
        if not ok:
            banner("PyTorch failed to install.")
            print("  Usually this is no internet, a proxy, or a firewall.")
            print("  The error is in the text above this message.")
            hold(1)

    if rest:
        print()
        print("  [2/2] Demucs and the audio bits.")
        if not _pip(*[spec for _, spec in rest]):
            banner("Some packages failed to install.")
            print("  The error is in the text above this message.")
            print("  If it mentions building a wheel, install Python 3.12 and retry.")
            hold(1)

    importlib.invalidate_caches()

    still_missing = [m for m in ("torch", "flask", "soundfile", "demucs.pretrained")
                     if not _have(m)]
    if still_missing:
        banner("Installed, but Python still can't see: " + ", ".join(still_missing))
        print("  Close this window and run the file again - that usually clears it.")
        hold(1)

    banner("Setup finished. Starting UNMIX.")

# ====================================================================================
#  The web interface, packed in so this stays a single file
# ====================================================================================

_PACKED = {
    "app.js":
        "LyogVU5NSVgg4oCUIGZyb250IGVuZC4KICAgVXBsb2FkIOKGkiBwb2xsIHRoZSByZW5kZXIg4oaSIGxvYWQgZXZlcnkgc3RlbSBp"
        "bnRvIFdlYiBBdWRpbyDihpIgbWl4LCBsb29wLCBleHBvcnQuICovCgpjb25zdCAkID0gKHMpID0+IGRvY3VtZW50LnF1ZXJ5U2Vs"
        "ZWN0b3Iocyk7CmNvbnN0ICQkID0gKHMpID0+IEFycmF5LmZyb20oZG9jdW1lbnQucXVlcnlTZWxlY3RvckFsbChzKSk7Cgpjb25z"
        "dCBTVEVNX05PVEUgPSB7CiAgdm9jYWxzOiAibGVhZCArIGJhY2tpbmcgdm9pY2UiLAogIGRydW1zOiAia2l0LCBwZXJjdXNzaW9u"
        "IiwKICBiYXNzOiAiYmFzcyBndWl0YXIsIHN1YiIsCiAgZ3VpdGFyOiAiZWxlY3RyaWMgKyBhY291c3RpYyIsCiAgcGlhbm86ICJr"
        "ZXlzIOKAlCBvZnRlbiBsZWFreSIsCiAgb3RoZXI6ICJzeW50aHMsIHN0cmluZ3MsIGV2ZXJ5dGhpbmcgZWxzZSIsCiAgaW5zdHJ1"
        "bWVudGFsOiAidGhlIHdob2xlIHRyYWNrIG1pbnVzIHZvY2FscyIsCn07Ci8qIHN0ZW1zIHRoYXQgYWxyZWFkeSBsaXZlIGluc2lk"
        "ZSAiaW5zdHJ1bWVudGFsIiDigJQgcGxheWluZyBib3RoIGRvdWJsZS1jb3VudHMgdGhlbSAqLwpjb25zdCBDT01QT05FTlRTID0g"
        "WyJkcnVtcyIsICJiYXNzIiwgIm90aGVyIiwgImd1aXRhciIsICJwaWFubyJdOwoKY29uc3Qgc3RhdGUgPSB7CiAgZW52OiBudWxs"
        "LAogIGpvYjogbnVsbCwKICBqb2JzOiBbXSwKICBwb2xsOiBudWxsLAogIGZtdDogIndhdiIsCiAgbG9vcDogZmFsc2UsCiAgcmVn"
        "aW9uOiBudWxsLCAgICAgICAgICAvLyB7c3RhcnQsIGVuZH0gaW4gc2Vjb25kcyAtIHRoZSBsb29wL3NlbGVjdGlvbiByYW5nZQog"
        "IHNlY3Rpb25zOiBbXSwgICAgICAgICAgLy8gW3tpZCwgbmFtZSwgc3RhcnQsIGVuZCwgZ2FpbnM6e30sIG11dGVzOnt9fV0KICBl"
        "bnZzOiBudWxsLCAgICAgICAgICAgIC8vIG5hbWUgLT4gZmxhdCBnYWluIHNlZ21lbnRzLCByZWJ1aWx0IG9uIGV2ZXJ5IGNoYW5n"
        "ZQogIGVkaXRpbmc6IG51bGwsICAgICAgICAgLy8gbnVsbCA9IHdob2xlIHRyYWNrLCBlbHNlIGEgc2VjdGlvbiBpZAogIGxhc3RQ"
        "b3M6IDAsCiAgcGxheWluZzogZmFsc2UsCiAgb2Zmc2V0OiAwLAogIHN0YXJ0ZWRBdDogMCwKICBkdXJhdGlvbjogMCwKICBwZWFr"
        "czogbnVsbCwKICBjaGFubmVsczogbmV3IE1hcCgpLCAgIC8vIG5hbWUgLT4ge2J1ZmZlciwgZ2FpbiwgYW5hbHlzZXIsIHNyYywg"
        "bXV0ZSwgc29sbywgcG9zLCBob2xkfQp9OwoKbGV0IEFDID0gbnVsbDsKbGV0IG1hc3RlciA9IG51bGw7CgpmdW5jdGlvbiBhdWRp"
        "bygpIHsKICBpZiAoIUFDKSB7CiAgICBBQyA9IG5ldyAod2luZG93LkF1ZGlvQ29udGV4dCB8fCB3aW5kb3cud2Via2l0QXVkaW9D"
        "b250ZXh0KSgpOwogICAgbWFzdGVyID0gQUMuY3JlYXRlR2FpbigpOwogICAgbWFzdGVyLmNvbm5lY3QoQUMuZGVzdGluYXRpb24p"
        "OwogIH0KICBpZiAoQUMuc3RhdGUgPT09ICJzdXNwZW5kZWQiKSBBQy5yZXN1bWUoKTsKICByZXR1cm4gQUM7Cn0KCi8qIOKUgOKU"
        "gCBmYWRlciBjdXJ2ZSDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDi"
        "lIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIAgKi8KY29u"
        "c3QgUFRTID0gW1swLjA2LCAtNjBdLCBbMC4yLCAtMzBdLCBbMC40LCAtMThdLCBbMC42LCAtOV0sIFswLjgsIDBdLCBbMSwgNl1d"
        "Owpjb25zdCBVTklUWSA9IDAuODsKCmZ1bmN0aW9uIHBvc1RvRGIocCkgewogIGlmIChwIDw9IFBUU1swXVswXSkgcmV0dXJuIC1J"
        "bmZpbml0eTsKICBmb3IgKGxldCBpID0gMTsgaSA8IFBUUy5sZW5ndGg7IGkrKykgewogICAgaWYgKHAgPD0gUFRTW2ldWzBdKSB7"
        "CiAgICAgIGNvbnN0IFtwMCwgZDBdID0gUFRTW2kgLSAxXSwgW3AxLCBkMV0gPSBQVFNbaV07CiAgICAgIHJldHVybiBkMCArIChk"
        "MSAtIGQwKSAqIChwIC0gcDApIC8gKHAxIC0gcDApOwogICAgfQogIH0KICByZXR1cm4gNjsKfQpmdW5jdGlvbiBkYlRvUG9zKGRi"
        "KSB7CiAgaWYgKGRiIDw9IFBUU1swXVsxXSkgcmV0dXJuIFBUU1swXVswXTsKICBmb3IgKGxldCBpID0gMTsgaSA8IFBUUy5sZW5n"
        "dGg7IGkrKykgewogICAgaWYgKGRiIDw9IFBUU1tpXVsxXSkgewogICAgICBjb25zdCBbcDAsIGQwXSA9IFBUU1tpIC0gMV0sIFtw"
        "MSwgZDFdID0gUFRTW2ldOwogICAgICByZXR1cm4gcDAgKyAocDEgLSBwMCkgKiAoZGIgLSBkMCkgLyAoZDEgLSBkMCk7CiAgICB9"
        "CiAgfQogIHJldHVybiAxOwp9CmNvbnN0IGRiVG9HYWluID0gKGRiKSA9PiAoZGIgPT09IC1JbmZpbml0eSA/IDAgOiBNYXRoLnBv"
        "dygxMCwgZGIgLyAyMCkpOwpjb25zdCBmbXREYiA9IChkYikgPT4gKGRiID09PSAtSW5maW5pdHkgPyAi4oiS4oieIiA6IChkYiA+"
        "IDAgPyAiKyIgOiAiIikgKyBkYi50b0ZpeGVkKDEpKTsKY29uc3QgY2xvY2sgPSAocykgPT4gewogIHMgPSBNYXRoLm1heCgwLCBz"
        "IHx8IDApOwogIHJldHVybiBNYXRoLmZsb29yKHMgLyA2MCkgKyAiOiIgKyBTdHJpbmcoTWF0aC5mbG9vcihzICUgNjApKS5wYWRT"
        "dGFydCgyLCAiMCIpOwp9OwoKZnVuY3Rpb24gdG9hc3QobXNnLCBiYWQpIHsKICBjb25zdCB0ID0gJCgiI3RvYXN0Iik7CiAgdC50"
        "ZXh0Q29udGVudCA9IG1zZzsKICB0LmNsYXNzTmFtZSA9ICJ0b2FzdCIgKyAoYmFkID8gIiBiYWQiIDogIiIpOwogIHQuaGlkZGVu"
        "ID0gZmFsc2U7CiAgY2xlYXJUaW1lb3V0KHRvYXN0Ll90KTsKICB0b2FzdC5fdCA9IHNldFRpbWVvdXQoKCkgPT4gKHQuaGlkZGVu"
        "ID0gdHJ1ZSksIGJhZCA/IDcwMDAgOiAzNjAwKTsKfQoKLyog4pSA4pSAIGJvb3Qg4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA"
        "4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA"
        "4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSAICovCmFzeW5jIGZ1bmN0aW9uIGJvb3QoKSB7"
        "CiAgdHJ5IHsKICAgIHN0YXRlLmVudiA9IGF3YWl0IChhd2FpdCBmZXRjaCgiL2FwaS9lbnYiKSkuanNvbigpOwogIH0gY2F0Y2gg"
        "ewogICAgdG9hc3QoIkNhbid0IHJlYWNoIHRoZSBhcHAncyBiYWNrZW5kLiBJcyB0aGUgdGVybWluYWwgd2luZG93IHN0aWxsIG9w"
        "ZW4/IiwgdHJ1ZSk7CiAgICByZXR1cm47CiAgfQogIGNvbnN0IGVudiA9IHN0YXRlLmVudjsKICAkKCIjcmlnIikuY2xhc3NMaXN0"
        "LmFkZCgibGl2ZSIpOwogICQoIiNyaWdUZXh0IikudGV4dENvbnRlbnQgPSBlbnYuZGV2aWNlX2xhYmVsICsgKGVudi5kZXZpY2Ug"
        "PT09ICJjcHUiID8gIiDigJQgc2xvd2VyLCBzdGlsbCBmaW5lIiA6ICIg4oCUIGZhc3QiKTsKICAkKCIjb3V0UGF0aCIpLnRleHRD"
        "b250ZW50ID0gZW52Lm91dHB1dF9kaXI7CgogIGNvbnN0IHNlbCA9ICQoIiNtb2RlbCIpOwogIGVudi5tb2RlbHMuZm9yRWFjaCgo"
        "bSkgPT4gewogICAgY29uc3QgbyA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoIm9wdGlvbiIpOwogICAgby52YWx1ZSA9IG0uaWQ7"
        "CiAgICBvLnRleHRDb250ZW50ID0gbS5uYW1lOwogICAgby5kYXRhc2V0LmRldGFpbCA9IG0uZGV0YWlsOwogICAgc2VsLmFwcGVu"
        "ZENoaWxkKG8pOwogIH0pOwogIGNvbnN0IGRlc2NyaWJlID0gKCkgPT4gKCQoIiNtb2RlbEhpbnQiKS50ZXh0Q29udGVudCA9IHNl"
        "bC5zZWxlY3RlZE9wdGlvbnNbMF0uZGF0YXNldC5kZXRhaWwpOwogIHNlbC5hZGRFdmVudExpc3RlbmVyKCJjaGFuZ2UiLCBkZXNj"
        "cmliZSk7CiAgZGVzY3JpYmUoKTsKCiAgaWYgKCFlbnYuZmZtcGVnKSB7CiAgICB0b2FzdCgiZmZtcGVnIGlzbid0IGluc3RhbGxl"
        "ZC4gV0FWIGFuZCBGTEFDIHdvcmsgbm93OyBpbnN0YWxsIGZmbXBlZyBmb3IgbXAzIGFuZCB2aWRlbyBmaWxlcy4iLCB0cnVlKTsK"
        "ICB9CiAgd2lyZUludGFrZSgpOwogIHdpcmVUcmFuc3BvcnQoKTsKICB3aXJlRXhwb3J0cygpOwogIGF3YWl0IHJlZnJlc2hKb2Jz"
        "KCk7Cn0KCi8qIOKUgOKUgCBpbnRha2Ug4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA"
        "4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA"
        "4pSA4pSA4pSA4pSA4pSA4pSAICovCmZ1bmN0aW9uIHdpcmVJbnRha2UoKSB7CiAgY29uc3QgZHJvcCA9ICQoIiNkcm9wIiksIGlu"
        "cHV0ID0gJCgiI2ZpbGUiKTsKICBkcm9wLmFkZEV2ZW50TGlzdGVuZXIoImNsaWNrIiwgKCkgPT4gaW5wdXQuY2xpY2soKSk7CiAg"
        "ZHJvcC5hZGRFdmVudExpc3RlbmVyKCJrZXlkb3duIiwgKGUpID0+IHsKICAgIGlmIChlLmtleSA9PT0gIkVudGVyIiB8fCBlLmtl"
        "eSA9PT0gIiAiKSB7IGUucHJldmVudERlZmF1bHQoKTsgaW5wdXQuY2xpY2soKTsgfQogIH0pOwogIGlucHV0LmFkZEV2ZW50TGlz"
        "dGVuZXIoImNoYW5nZSIsICgpID0+IGlucHV0LmZpbGVzWzBdICYmIHN1Ym1pdChpbnB1dC5maWxlc1swXSkpOwoKICBbImRyYWdl"
        "bnRlciIsICJkcmFnb3ZlciJdLmZvckVhY2goKGV2KSA9PgogICAgZHJvcC5hZGRFdmVudExpc3RlbmVyKGV2LCAoZSkgPT4geyBl"
        "LnByZXZlbnREZWZhdWx0KCk7IGRyb3AuY2xhc3NMaXN0LmFkZCgiaG90Iik7IH0pKTsKICBbImRyYWdsZWF2ZSIsICJkcm9wIl0u"
        "Zm9yRWFjaCgoZXYpID0+CiAgICBkcm9wLmFkZEV2ZW50TGlzdGVuZXIoZXYsIChlKSA9PiB7IGUucHJldmVudERlZmF1bHQoKTsg"
        "ZHJvcC5jbGFzc0xpc3QucmVtb3ZlKCJob3QiKTsgfSkpOwogIGRyb3AuYWRkRXZlbnRMaXN0ZW5lcigiZHJvcCIsIChlKSA9PiB7"
        "CiAgICBjb25zdCBmID0gZS5kYXRhVHJhbnNmZXIuZmlsZXNbMF07CiAgICBpZiAoZikgc3VibWl0KGYpOwogIH0pOwoKICAkKCIj"
        "Y2FuY2VsQnRuIikuYWRkRXZlbnRMaXN0ZW5lcigiY2xpY2siLCBhc3luYyAoKSA9PiB7CiAgICBpZiAoIXN0YXRlLmpvYikgcmV0"
        "dXJuOwogICAgYXdhaXQgZmV0Y2goYC9hcGkvam9icy8ke3N0YXRlLmpvYi5pZH0vY2FuY2VsYCwgeyBtZXRob2Q6ICJQT1NUIiB9"
        "KTsKICB9KTsKfQoKYXN5bmMgZnVuY3Rpb24gc3VibWl0KGZpbGUpIHsKICBzdG9wUGxheWJhY2soKTsKICBjb25zdCBib2R5ID0g"
        "bmV3IEZvcm1EYXRhKCk7CiAgYm9keS5hcHBlbmQoImZpbGUiLCBmaWxlKTsKICBib2R5LmFwcGVuZCgibW9kZWwiLCAkKCIjbW9k"
        "ZWwiKS52YWx1ZSk7CiAgYm9keS5hcHBlbmQoInBhc3NlcyIsICQoIiNwYXNzZXMiKS52YWx1ZSk7CgogIHNob3dXb3JraW5nKHsg"
        "dGl0bGU6IGZpbGUubmFtZS5yZXBsYWNlKC9cLlteLl0rJC8sICIiKSwgc3RhZ2U6ICJVcGxvYWRpbmciLCBwcm9ncmVzczogMCB9"
        "KTsKCiAgbGV0IGpvYjsKICB0cnkgewogICAgY29uc3QgcmVzID0gYXdhaXQgZmV0Y2goIi9hcGkvam9icyIsIHsgbWV0aG9kOiAi"
        "UE9TVCIsIGJvZHkgfSk7CiAgICBqb2IgPSBhd2FpdCByZXMuanNvbigpOwogICAgaWYgKCFyZXMub2spIHRocm93IG5ldyBFcnJv"
        "cihqb2IuZXJyb3IgfHwgIlVwbG9hZCBmYWlsZWQuIik7CiAgfSBjYXRjaCAoZXJyKSB7CiAgICAkKCIjd29ya2luZyIpLmhpZGRl"
        "biA9IHRydWU7CiAgICAkKCIjaW50YWtlIikuaGlkZGVuID0gZmFsc2U7CiAgICB0b2FzdChlcnIubWVzc2FnZSwgdHJ1ZSk7CiAg"
        "ICByZXR1cm47CiAgfQogIHN0YXRlLmpvYiA9IGpvYjsKICB3YXRjaChqb2IuaWQpOwogICQoIiNmaWxlIikudmFsdWUgPSAiIjsK"
        "fQoKZnVuY3Rpb24gc2hvd1dvcmtpbmcoaikgewogICQoIiNpbnRha2UiKS5oaWRkZW4gPSB0cnVlOwogICQoIiNjb25zb2xlIiku"
        "aGlkZGVuID0gdHJ1ZTsKICAkKCIjd29ya2luZyIpLmhpZGRlbiA9IGZhbHNlOwogICQoIiN3b3JrVGl0bGUiKS50ZXh0Q29udGVu"
        "dCA9IGoudGl0bGU7CiAgJCgiI3dvcmtTdGFnZSIpLnRleHRDb250ZW50ID0gai5zdGFnZTsKICBjb25zdCBwY3QgPSBNYXRoLnJv"
        "dW5kKChqLnByb2dyZXNzIHx8IDApICogMTAwKTsKICAkKCIjdGFwZUZpbGwiKS5zdHlsZS53aWR0aCA9IHBjdCArICIlIjsKICAk"
        "KCIjd29ya1BjdCIpLnRleHRDb250ZW50ID0gcGN0ICsgIiUiOwogICQoIiN0YXBlIikuc2V0QXR0cmlidXRlKCJhcmlhLXZhbHVl"
        "bm93IiwgcGN0KTsKfQoKZnVuY3Rpb24gd2F0Y2goaWQpIHsKICBjbGVhckludGVydmFsKHN0YXRlLnBvbGwpOwogIHN0YXRlLnBv"
        "bGwgPSBzZXRJbnRlcnZhbChhc3luYyAoKSA9PiB7CiAgICBsZXQgajsKICAgIHRyeSB7CiAgICAgIGogPSBhd2FpdCAoYXdhaXQg"
        "ZmV0Y2goYC9hcGkvam9icy8ke2lkfWApKS5qc29uKCk7CiAgICB9IGNhdGNoIHsgcmV0dXJuOyB9CiAgICBzdGF0ZS5qb2IgPSBq"
        "OwoKICAgIGlmIChqLnN0YXR1cyA9PT0gInJ1bm5pbmciIHx8IGouc3RhdHVzID09PSAicXVldWVkIikgewogICAgICBzaG93V29y"
        "a2luZyhqKTsKICAgICAgcmV0dXJuOwogICAgfQogICAgY2xlYXJJbnRlcnZhbChzdGF0ZS5wb2xsKTsKICAgIGF3YWl0IHJlZnJl"
        "c2hKb2JzKCk7CgogICAgaWYgKGouc3RhdHVzID09PSAiZG9uZSIpIHsKICAgICAgb3BlbkpvYihqKTsKICAgIH0gZWxzZSBpZiAo"
        "ai5zdGF0dXMgPT09ICJjYW5jZWxsZWQiKSB7CiAgICAgIHJlc2V0VG9JbnRha2UoKTsKICAgICAgdG9hc3QoIlN0b3BwZWQuIE5v"
        "dGhpbmcgd2FzIHNhdmVkLiIpOwogICAgfSBlbHNlIHsKICAgICAgcmVzZXRUb0ludGFrZSgpOwogICAgICB0b2FzdChqLmVycm9y"
        "IHx8ICJUaGUgcmVuZGVyIGZhaWxlZC4iLCB0cnVlKTsKICAgIH0KICB9LCA1MDApOwp9CgpmdW5jdGlvbiByZXNldFRvSW50YWtl"
        "KCkgewogICQoIiN3b3JraW5nIikuaGlkZGVuID0gdHJ1ZTsKICAkKCIjY29uc29sZSIpLmhpZGRlbiA9IHRydWU7CiAgJCgiI2lu"
        "dGFrZSIpLmhpZGRlbiA9IGZhbHNlOwp9CgovKiDilIDilIAgcmVjZW50cyDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDi"
        "lIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDi"
        "lIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIAgKi8KYXN5bmMgZnVuY3Rpb24gcmVmcmVzaEpvYnMoKSB7CiAgdHJ5"
        "IHsKICAgIHN0YXRlLmpvYnMgPSBhd2FpdCAoYXdhaXQgZmV0Y2goIi9hcGkvam9icyIpKS5qc29uKCk7CiAgfSBjYXRjaCB7IHJl"
        "dHVybjsgfQogIGNvbnN0IHdyYXAgPSAkKCIjY2hpcHMiKTsKICB3cmFwLmlubmVySFRNTCA9ICIiOwogIGNvbnN0IHVzYWJsZSA9"
        "IHN0YXRlLmpvYnMuZmlsdGVyKChqKSA9PiBqLnN0YXR1cyA9PT0gImRvbmUiIHx8IGouc3RhdHVzID09PSAiZXJyb3IiKTsKICAk"
        "KCIjcmVjZW50cyIpLmhpZGRlbiA9IHVzYWJsZS5sZW5ndGggPT09IDA7CgogIHVzYWJsZS5zbGljZSgwLCAxMikuZm9yRWFjaCgo"
        "aikgPT4gewogICAgY29uc3QgY2hpcCA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImRpdiIpOwogICAgY2hpcC5jbGFzc05hbWUg"
        "PSAiY2hpcCIgKyAoc3RhdGUuam9iICYmIGouaWQgPT09IHN0YXRlLmpvYi5pZCA/ICIgYWN0aXZlIiA6ICIiKTsKICAgIGNvbnN0"
        "IGxhYmVsID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgic3BhbiIpOwogICAgbGFiZWwudGV4dENvbnRlbnQgPSBqLnRpdGxlOwog"
        "ICAgY2hpcC5hcHBlbmRDaGlsZChsYWJlbCk7CiAgICBpZiAoai5zdGF0dXMgPT09ICJlcnJvciIpIHsKICAgICAgY29uc3QgYmFk"
        "ID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgic3BhbiIpOwogICAgICBiYWQuY2xhc3NOYW1lID0gInN0YWxlIjsKICAgICAgYmFk"
        "LnRleHRDb250ZW50ID0gImZhaWxlZCI7CiAgICAgIGNoaXAuYXBwZW5kQ2hpbGQoYmFkKTsKICAgIH0gZWxzZSB7CiAgICAgIGxh"
        "YmVsLmFkZEV2ZW50TGlzdGVuZXIoImNsaWNrIiwgKCkgPT4gb3BlbkpvYihqKSk7CiAgICAgIGNoaXAuc3R5bGUuY3Vyc29yID0g"
        "InBvaW50ZXIiOwogICAgfQogICAgY29uc3QgeCA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImJ1dHRvbiIpOwogICAgeC5jbGFz"
        "c05hbWUgPSAieCI7CiAgICB4LnRpdGxlID0gIkRlbGV0ZSB0aGVzZSBzdGVtcyBmcm9tIGRpc2siOwogICAgeC50ZXh0Q29udGVu"
        "dCA9ICLDlyI7CiAgICB4LmFkZEV2ZW50TGlzdGVuZXIoImNsaWNrIiwgYXN5bmMgKGUpID0+IHsKICAgICAgZS5zdG9wUHJvcGFn"
        "YXRpb24oKTsKICAgICAgYXdhaXQgZmV0Y2goYC9hcGkvam9icy8ke2ouaWR9YCwgeyBtZXRob2Q6ICJERUxFVEUiIH0pOwogICAg"
        "ICBpZiAoc3RhdGUuam9iICYmIHN0YXRlLmpvYi5pZCA9PT0gai5pZCkgeyBzdG9wUGxheWJhY2soKTsgcmVzZXRUb0ludGFrZSgp"
        "OyBzdGF0ZS5qb2IgPSBudWxsOyB9CiAgICAgIHJlZnJlc2hKb2JzKCk7CiAgICB9KTsKICAgIGNoaXAuYXBwZW5kQ2hpbGQoeCk7"
        "CiAgICB3cmFwLmFwcGVuZENoaWxkKGNoaXApOwogIH0pOwp9CgovKiDilIDilIAgb3BlbiBhIGZpbmlzaGVkIGpvYiDilIDilIDi"
        "lIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDi"
        "lIDilIDilIDilIDilIDilIDilIDilIAgKi8KYXN5bmMgZnVuY3Rpb24gb3BlbkpvYihqb2IpIHsKICBzdG9wUGxheWJhY2soKTsK"
        "ICBzdGF0ZS5qb2IgPSBqb2I7CiAgc3RhdGUucmVnaW9uID0gbnVsbDsKICBzdGF0ZS5zZWN0aW9ucyA9IFtdOwogIHN0YXRlLmVk"
        "aXRpbmcgPSBudWxsOwogIHN0YXRlLmxhc3RQb3MgPSAwOwogIHN0YXRlLmxvb3AgPSBmYWxzZTsKICAkKCIjbG9vcEJ0biIpLnNl"
        "dEF0dHJpYnV0ZSgiYXJpYS1wcmVzc2VkIiwgImZhbHNlIik7CiAgJCgiI2xvb3BSZWdpb24iKS5oaWRkZW4gPSB0cnVlOwoKICAk"
        "KCIjaW50YWtlIikuaGlkZGVuID0gdHJ1ZTsKICAkKCIjd29ya2luZyIpLmhpZGRlbiA9IGZhbHNlOwogIHNob3dXb3JraW5nKHsg"
        "dGl0bGU6IGpvYi50aXRsZSwgc3RhZ2U6ICJMb2FkaW5nIHN0ZW1zIGludG8gdGhlIG1peGVyIiwgcHJvZ3Jlc3M6IDAuOTcgfSk7"
        "CiAgJCgiI3RyYWNrVGl0bGUiKS50ZXh0Q29udGVudCA9IGpvYi50aXRsZTsKCiAgYXVkaW8oKTsKICBzdGF0ZS5jaGFubmVscy5j"
        "bGVhcigpOwogICQoIiNzdHJpcHMiKS5pbm5lckhUTUwgPSAiIjsKCiAgdHJ5IHsKICAgIGF3YWl0IFByb21pc2UuYWxsKGpvYi5z"
        "dGVtcy5tYXAoYXN5bmMgKHMpID0+IHsKICAgICAgY29uc3QgcmVzID0gYXdhaXQgZmV0Y2goYC9hcGkvam9icy8ke2pvYi5pZH0v"
        "cHJldmlldy8ke3MubmFtZX1gKTsKICAgICAgY29uc3QgYnVmID0gYXdhaXQgYXVkaW8oKS5kZWNvZGVBdWRpb0RhdGEoYXdhaXQg"
        "cmVzLmFycmF5QnVmZmVyKCkpOwogICAgICBjb25zdCBnYWluID0gQUMuY3JlYXRlR2FpbigpOwogICAgICBjb25zdCBhbmFseXNl"
        "ciA9IEFDLmNyZWF0ZUFuYWx5c2VyKCk7CiAgICAgIGFuYWx5c2VyLmZmdFNpemUgPSAxMDI0OwogICAgICBhbmFseXNlci5zbW9v"
        "dGhpbmdUaW1lQ29uc3RhbnQgPSAwLjM1OwogICAgICBnYWluLmNvbm5lY3QoYW5hbHlzZXIpOwogICAgICBhbmFseXNlci5jb25u"
        "ZWN0KG1hc3Rlcik7CiAgICAgIHN0YXRlLmNoYW5uZWxzLnNldChzLm5hbWUsIHsKICAgICAgICBidWZmZXI6IGJ1ZiwgZ2Fpbiwg"
        "YW5hbHlzZXIsIHNyYzogbnVsbCwKICAgICAgICBtdXRlOiBzLm5hbWUgPT09ICJpbnN0cnVtZW50YWwiLCBzb2xvOiBmYWxzZSwK"
        "ICAgICAgICBwb3M6IFVOSVRZLCBob2xkOiAwLCBkZXJpdmVkOiAhIXMuZGVyaXZlZCwKICAgICAgICBkYXRhOiBuZXcgRmxvYXQz"
        "MkFycmF5KGFuYWx5c2VyLmZmdFNpemUpLAogICAgICB9KTsKICAgIH0pKTsKICB9IGNhdGNoIChlcnIpIHsKICAgIHJlc2V0VG9J"
        "bnRha2UoKTsKICAgIHRvYXN0KCJDb3VsZG4ndCBsb2FkIHRoZSBzdGVtcyBmb3IgcGxheWJhY2s6ICIgKyBlcnIubWVzc2FnZSwg"
        "dHJ1ZSk7CiAgICByZXR1cm47CiAgfQoKICBzdGF0ZS5kdXJhdGlvbiA9IE1hdGgubWF4KC4uLlsuLi5zdGF0ZS5jaGFubmVscy52"
        "YWx1ZXMoKV0ubWFwKChjKSA9PiBjLmJ1ZmZlci5kdXJhdGlvbikpOwogIHN0YXRlLm9mZnNldCA9IDA7CiAgJCgiI3RpbWVFbmQi"
        "KS50ZXh0Q29udGVudCA9IGNsb2NrKHN0YXRlLmR1cmF0aW9uKTsKICAkKCIjdGltZU5vdyIpLnRleHRDb250ZW50ID0gIjA6MDAi"
        "OwoKICBqb2Iuc3RlbXMuZm9yRWFjaCgocykgPT4gJCgiI3N0cmlwcyIpLmFwcGVuZENoaWxkKGJ1aWxkU3RyaXAocy5uYW1lKSkp"
        "OwogIGFwcGx5R2FpbnMoKTsKICBidWlsZFBlYWtzKCk7CgogICQoIiN3b3JraW5nIikuaGlkZGVuID0gdHJ1ZTsKICAkKCIjY29u"
        "c29sZSIpLmhpZGRlbiA9IGZhbHNlOwogIGRyYXdXYXZlKCk7CiAgcmVuZGVyTGFuZSgpOwogIHJlbmRlckVkaXRCYXIoKTsKICBy"
        "ZWZyZXNoSm9icygpOwogIHJlcXVlc3RBbmltYXRpb25GcmFtZSh0aWNrKTsKfQoKLyog4pSA4pSAIG9uZSBjaGFubmVsIHN0cmlw"
        "IOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKU"
        "gOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgCAqLwpjb25zdCBUSUNLUyA9IFtbNiwgIis2Il0sIFswLCAiMCJd"
        "LCBbLTksICItOSJdLCBbLTE4LCAiLTE4Il0sIFstMzAsICItMzAiXSwgWy02MCwgIi1cdTIyMWUiXV0KICAubWFwKChbZGIsIGxh"
        "YmVsXSkgPT4gYDxzcGFuIHN0eWxlPSJib3R0b206JHsoZGJUb1BvcyhkYikgKiAxMDApLnRvRml4ZWQoMil9JSI+JHtsYWJlbH08"
        "L3NwYW4+YCkKICAuam9pbigiIik7CgpmdW5jdGlvbiBidWlsZFN0cmlwKG5hbWUpIHsKICBjb25zdCBjaCA9IHN0YXRlLmNoYW5u"
        "ZWxzLmdldChuYW1lKTsKICBjb25zdCBlbCA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImRpdiIpOwogIGVsLmNsYXNzTmFtZSA9"
        "ICJzdHJpcCIgKyAoY2guZGVyaXZlZCA/ICIgZGVyaXZlZCIgOiAiIikgKyAoY2gubXV0ZSA/ICIgbXV0ZWQiIDogIiIpOwogIGVs"
        "LnN0eWxlLnNldFByb3BlcnR5KCItLWMiLCBgdmFyKC0tYy0ke25hbWV9LCB2YXIoLS1kaW0pKWApOwogIGVsLmRhdGFzZXQuc3Rl"
        "bSA9IG5hbWU7CgogIGVsLmlubmVySFRNTCA9IGAKICAgIDxkaXYgY2xhc3M9InN0cmlwLW5hbWUiPiR7bmFtZX08L2Rpdj4KICAg"
        "IDxkaXYgY2xhc3M9InN0cmlwLW5vdGUiPiR7U1RFTV9OT1RFW25hbWVdIHx8ICIifTwvZGl2PgogICAgPGRpdiBjbGFzcz0ic3Ry"
        "aXAtYm9keSI+CiAgICAgIDxkaXYgY2xhc3M9Im1ldGVyIj4keyc8aSBjbGFzcz0ic2VnIj48L2k+Jy5yZXBlYXQoMTQpfTwvZGl2"
        "PgogICAgICA8ZGl2IGNsYXNzPSJmYWRlciI+CiAgICAgICAgPGRpdiBjbGFzcz0iZmFkZXItc2xvdCI+PGRpdiBjbGFzcz0iZmFk"
        "ZXItZmlsbCI+PC9kaXY+PC9kaXY+CiAgICAgICAgPGRpdiBjbGFzcz0iZmFkZXItc2NhbGUiPiR7VElDS1N9PC9kaXY+CiAgICAg"
        "ICAgPGRpdiBjbGFzcz0iZmFkZXItY2FwIiB0YWJpbmRleD0iMCIgcm9sZT0ic2xpZGVyIiBhcmlhLWxhYmVsPSIke25hbWV9IGxl"
        "dmVsIgogICAgICAgICAgICAgYXJpYS12YWx1ZW1pbj0iLTYwIiBhcmlhLXZhbHVlbWF4PSI2IiBhcmlhLXZhbHVlbm93PSIwIj48"
        "L2Rpdj4KICAgICAgPC9kaXY+CiAgICA8L2Rpdj4KICAgIDxkaXYgY2xhc3M9InN0cmlwLXJlYWQiPgogICAgICA8c3BhbiBjbGFz"
        "cz0ic2lsayI+TGV2ZWw8L3NwYW4+PHNwYW4gY2xhc3M9ImRiIj4wLjAgZEI8L3NwYW4+CiAgICA8L2Rpdj4KICAgIDxkaXYgY2xh"
        "c3M9InN0cmlwLWJ0bnMiPgogICAgICA8YnV0dG9uIGNsYXNzPSJtaW5pIiBkYXRhLXJvbGU9Im11dGUiPk08L2J1dHRvbj4KICAg"
        "ICAgPGJ1dHRvbiBjbGFzcz0ibWluaSIgZGF0YS1yb2xlPSJzb2xvIj5TPC9idXR0b24+CiAgICAgIDxidXR0b24gY2xhc3M9Im1p"
        "bmkgZ3JhYiIgZGF0YS1yb2xlPSJzYXZlIiB0aXRsZT0iRG93bmxvYWQgdGhpcyBzdGVtIj4KICAgICAgICA8c3ZnIHZpZXdCb3g9"
        "IjAgMCAyNCAyNCI+PHBhdGggZD0iTTEyIDN2MTAuMmwzLjYtMy42IDEuNCAxLjQtNiA2LTYtNiAxLjQtMS40IDMuNiAzLjZWM3pN"
        "NCAxOWgxNnYySDR6Ii8+PC9zdmc+CiAgICAgIDwvYnV0dG9uPgogICAgPC9kaXY+YDsKCiAgY29uc3QgY2FwID0gZWwucXVlcnlT"
        "ZWxlY3RvcigiLmZhZGVyLWNhcCIpOwogIGNvbnN0IGZpbGwgPSBlbC5xdWVyeVNlbGVjdG9yKCIuZmFkZXItZmlsbCIpOwogIGNv"
        "bnN0IHNsb3QgPSBlbC5xdWVyeVNlbGVjdG9yKCIuZmFkZXItc2xvdCIpOwogIGNvbnN0IHJlYWQgPSBlbC5xdWVyeVNlbGVjdG9y"
        "KCIuZGIiKTsKCiAgZnVuY3Rpb24gcGFpbnQoKSB7CiAgICBjb25zdCBwb3MgPSBnZXRQb3MobmFtZSk7CiAgICBjb25zdCBkYiA9"
        "IHBvc1RvRGIocG9zKTsKICAgIGNvbnN0IGRyb3AgPSAxIC0gcG9zOwogICAgY2FwLnN0eWxlLnRvcCA9IGBjYWxjKDhweCArICR7"
        "KGRyb3AgKiAxMDApLnRvRml4ZWQoMyl9JSAtICR7KGRyb3AgKiAxNikudG9GaXhlZCgyKX1weClgOwogICAgZmlsbC5zdHlsZS5o"
        "ZWlnaHQgPSBwb3MgKiAxMDAgKyAiJSI7CiAgICByZWFkLnRleHRDb250ZW50ID0gZm10RGIoZGIpICsgIiBkQiI7CiAgICBjYXAu"
        "c2V0QXR0cmlidXRlKCJhcmlhLXZhbHVlbm93IiwgZGIgPT09IC1JbmZpbml0eSA/IC02MCA6IGRiLnRvRml4ZWQoMSkpOwogIH0K"
        "ICBjaC5wYWludCA9IHBhaW50OwogIHBhaW50KCk7CgogIGxldCBkcmFnZ2luZyA9IGZhbHNlOwogIGNvbnN0IHNldEZyb21ZID0g"
        "KGNsaWVudFkpID0+IHsKICAgIGNvbnN0IHIgPSBzbG90LmdldEJvdW5kaW5nQ2xpZW50UmVjdCgpOwogICAgc2V0UG9zKG5hbWUs"
        "IE1hdGgubWF4KDAsIE1hdGgubWluKDEsIDEgLSAoY2xpZW50WSAtIHIudG9wKSAvIHIuaGVpZ2h0KSkpOwogICAgcGFpbnQoKTsK"
        "ICAgIGFwcGx5R2FpbnMoKTsKICB9OwogIGNhcC5hZGRFdmVudExpc3RlbmVyKCJwb2ludGVyZG93biIsIChlKSA9PiB7CiAgICBk"
        "cmFnZ2luZyA9IHRydWU7IGNhcC5zZXRQb2ludGVyQ2FwdHVyZShlLnBvaW50ZXJJZCk7IGUucHJldmVudERlZmF1bHQoKTsKICB9"
        "KTsKICBjYXAuYWRkRXZlbnRMaXN0ZW5lcigicG9pbnRlcm1vdmUiLCAoZSkgPT4gZHJhZ2dpbmcgJiYgc2V0RnJvbVkoZS5jbGll"
        "bnRZKSk7CiAgY2FwLmFkZEV2ZW50TGlzdGVuZXIoInBvaW50ZXJ1cCIsICgpID0+IChkcmFnZ2luZyA9IGZhbHNlKSk7CiAgY2Fw"
        "LmFkZEV2ZW50TGlzdGVuZXIoImRibGNsaWNrIiwgKCkgPT4geyBzZXRQb3MobmFtZSwgVU5JVFkpOyBwYWludCgpOyBhcHBseUdh"
        "aW5zKCk7IH0pOwogIHNsb3QucGFyZW50RWxlbWVudC5hZGRFdmVudExpc3RlbmVyKCJwb2ludGVyZG93biIsIChlKSA9PiB7CiAg"
        "ICBpZiAoZS50YXJnZXQgPT09IGNhcCkgcmV0dXJuOwogICAgc2V0RnJvbVkoZS5jbGllbnRZKTsKICB9KTsKICBjYXAuYWRkRXZl"
        "bnRMaXN0ZW5lcigia2V5ZG93biIsIChlKSA9PiB7CiAgICBjb25zdCBzdGVwID0gZS5zaGlmdEtleSA/IDAuMDEgOiAwLjA0Owog"
        "ICAgaWYgKGUua2V5ID09PSAiQXJyb3dVcCIpIHNldFBvcyhuYW1lLCBNYXRoLm1pbigxLCBnZXRQb3MobmFtZSkgKyBzdGVwKSk7"
        "CiAgICBlbHNlIGlmIChlLmtleSA9PT0gIkFycm93RG93biIpIHNldFBvcyhuYW1lLCBNYXRoLm1heCgwLCBnZXRQb3MobmFtZSkg"
        "LSBzdGVwKSk7CiAgICBlbHNlIHJldHVybjsKICAgIGUucHJldmVudERlZmF1bHQoKTsgcGFpbnQoKTsgYXBwbHlHYWlucygpOwog"
        "IH0pOwoKICBlbC5xdWVyeVNlbGVjdG9yQWxsKCIubWluaSIpLmZvckVhY2goKGIpID0+IHsKICAgIGIuYWRkRXZlbnRMaXN0ZW5l"
        "cigiY2xpY2siLCAoKSA9PiB7CiAgICAgIGNvbnN0IHJvbGUgPSBiLmRhdGFzZXQucm9sZTsKICAgICAgaWYgKHJvbGUgPT09ICJz"
        "YXZlIikgcmV0dXJuIGRvd25sb2FkKG5hbWUpOwogICAgICBpZiAocm9sZSA9PT0gIm11dGUiKSB7CiAgICAgICAgc2V0TXV0ZShu"
        "YW1lLCAhZ2V0TXV0ZShuYW1lKSk7CiAgICAgICAgaWYgKCFnZXRNdXRlKG5hbWUpKSByZXNvbHZlT3ZlcmxhcChuYW1lKTsKICAg"
        "ICAgfSBlbHNlIHsKICAgICAgICBjaC5zb2xvID0gIWNoLnNvbG87CiAgICAgIH0KICAgICAgYXBwbHlHYWlucygpOwogICAgfSk7"
        "CiAgfSk7CgogIGNoLmVsID0gZWw7CiAgcmV0dXJuIGVsOwp9CgovKiBpbnN0cnVtZW50YWwgYWxyZWFkeSBjb250YWlucyBkcnVt"
        "cy9iYXNzL290aGVyIOKAlCBuZXZlciBwbGF5IGJvdGggKi8KZnVuY3Rpb24gcmVzb2x2ZU92ZXJsYXAoanVzdFVubXV0ZWQpIHsK"
        "ICBpZiAoIXN0YXRlLmNoYW5uZWxzLmhhcygiaW5zdHJ1bWVudGFsIikpIHJldHVybjsKICBpZiAoanVzdFVubXV0ZWQgPT09ICJp"
        "bnN0cnVtZW50YWwiKSB7CiAgICBDT01QT05FTlRTLmZvckVhY2goKG4pID0+IHN0YXRlLmNoYW5uZWxzLmhhcyhuKSAmJiBzZXRN"
        "dXRlKG4sIHRydWUpKTsKICB9IGVsc2UgaWYgKENPTVBPTkVOVFMuaW5jbHVkZXMoanVzdFVubXV0ZWQpKSB7CiAgICBzZXRNdXRl"
        "KCJpbnN0cnVtZW50YWwiLCB0cnVlKTsKICB9Cn0KCi8qIOKUgOKUgCB3aGljaCBtaXggYXJlIHdlIGVkaXRpbmc6IHRoZSB3aG9s"
        "ZSB0cmFjaywgb3Igb25lIHNlY3Rpb24/IOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgCAqLwpmdW5jdGlvbiB0YXJnZXQoKSB7CiAg"
        "cmV0dXJuIHN0YXRlLmVkaXRpbmcgPyBzdGF0ZS5zZWN0aW9ucy5maW5kKChzKSA9PiBzLmlkID09PSBzdGF0ZS5lZGl0aW5nKSB8"
        "fCBudWxsIDogbnVsbDsKfQpmdW5jdGlvbiBnZXRQb3MobmFtZSkgewogIGNvbnN0IHQgPSB0YXJnZXQoKTsKICBjb25zdCBjID0g"
        "c3RhdGUuY2hhbm5lbHMuZ2V0KG5hbWUpOwogIHJldHVybiB0ID8gKHQuZ2FpbnNbbmFtZV0gIT09IHVuZGVmaW5lZCA/IHQuZ2Fp"
        "bnNbbmFtZV0gOiBjLnBvcykgOiBjLnBvczsKfQpmdW5jdGlvbiBzZXRQb3MobmFtZSwgcCkgewogIGNvbnN0IHQgPSB0YXJnZXQo"
        "KTsKICBpZiAodCkgdC5nYWluc1tuYW1lXSA9IHA7CiAgZWxzZSBzdGF0ZS5jaGFubmVscy5nZXQobmFtZSkucG9zID0gcDsKfQpm"
        "dW5jdGlvbiBnZXRNdXRlKG5hbWUpIHsKICBjb25zdCB0ID0gdGFyZ2V0KCk7CiAgY29uc3QgYyA9IHN0YXRlLmNoYW5uZWxzLmdl"
        "dChuYW1lKTsKICByZXR1cm4gdCA/ICh0Lm11dGVzW25hbWVdICE9PSB1bmRlZmluZWQgPyB0Lm11dGVzW25hbWVdIDogYy5tdXRl"
        "KSA6IGMubXV0ZTsKfQpmdW5jdGlvbiBzZXRNdXRlKG5hbWUsIHYpIHsKICBjb25zdCB0ID0gdGFyZ2V0KCk7CiAgaWYgKHQpIHQu"
        "bXV0ZXNbbmFtZV0gPSB2OwogIGVsc2Ugc3RhdGUuY2hhbm5lbHMuZ2V0KG5hbWUpLm11dGUgPSB2Owp9CgpmdW5jdGlvbiBzZWN0"
        "aW9uQXQodCkgewogIHJldHVybiBzdGF0ZS5zZWN0aW9ucy5maW5kKChzKSA9PiB0ID49IHMuc3RhcnQgJiYgdCA8IHMuZW5kKSB8"
        "fCBudWxsOwp9CgovKiBHYWluIGZvciBvbmUgc3RlbSBhY3Jvc3MgdGhlIHdob2xlIHNvbmcsIGFzIGZsYXQgc2VnbWVudHMuCiAg"
        "IFNvbG8gaXMgYSBtb25pdG9yaW5nIG92ZXJyaWRlIGFuZCBzaXRzIG9uIHRvcCBvZiBldmVyeXRoaW5nLiAqLwpmdW5jdGlvbiBz"
        "dGVtRW52ZWxvcGUobmFtZSkgewogIGNvbnN0IGR1ciA9IHN0YXRlLmR1cmF0aW9uIHx8IDA7CiAgY29uc3Qgc29sb2VkID0gWy4u"
        "LnN0YXRlLmNoYW5uZWxzLnZhbHVlcygpXS5zb21lKChjKSA9PiBjLnNvbG8pOwogIGlmIChzb2xvZWQgJiYgIXN0YXRlLmNoYW5u"
        "ZWxzLmdldChuYW1lKS5zb2xvKSByZXR1cm4gW3sgc3RhcnQ6IDAsIGVuZDogZHVyLCBnYWluOiAwIH1dOwoKICBjb25zdCBjID0g"
        "c3RhdGUuY2hhbm5lbHMuZ2V0KG5hbWUpOwogIGNvbnN0IGJhc2UgPSBjLm11dGUgPyAwIDogZGJUb0dhaW4ocG9zVG9EYihjLnBv"
        "cykpOwogIGNvbnN0IHNlY3MgPSBbLi4uc3RhdGUuc2VjdGlvbnNdLnNvcnQoKGEsIGIpID0+IGEuc3RhcnQgLSBiLnN0YXJ0KTsK"
        "CiAgY29uc3Qgb3V0ID0gW107CiAgbGV0IGN1cnNvciA9IDA7CiAgZm9yIChjb25zdCBzZWMgb2Ygc2VjcykgewogICAgaWYgKHNl"
        "Yy5zdGFydCA+IGN1cnNvcikgb3V0LnB1c2goeyBzdGFydDogY3Vyc29yLCBlbmQ6IHNlYy5zdGFydCwgZ2FpbjogYmFzZSB9KTsK"
        "ICAgIGNvbnN0IG11dGVkID0gc2VjLm11dGVzW25hbWVdICE9PSB1bmRlZmluZWQgPyBzZWMubXV0ZXNbbmFtZV0gOiBjLm11dGU7"
        "CiAgICBjb25zdCBwb3MgPSBzZWMuZ2FpbnNbbmFtZV0gIT09IHVuZGVmaW5lZCA/IHNlYy5nYWluc1tuYW1lXSA6IGMucG9zOwog"
        "ICAgb3V0LnB1c2goeyBzdGFydDogc2VjLnN0YXJ0LCBlbmQ6IHNlYy5lbmQsIGdhaW46IG11dGVkID8gMCA6IGRiVG9HYWluKHBv"
        "c1RvRGIocG9zKSkgfSk7CiAgICBjdXJzb3IgPSBzZWMuZW5kOwogIH0KICBpZiAoY3Vyc29yIDwgZHVyKSBvdXQucHVzaCh7IHN0"
        "YXJ0OiBjdXJzb3IsIGVuZDogZHVyLCBnYWluOiBiYXNlIH0pOwogIHJldHVybiBvdXQubGVuZ3RoID8gb3V0IDogW3sgc3RhcnQ6"
        "IDAsIGVuZDogZHVyLCBnYWluOiBiYXNlIH1dOwp9CgpmdW5jdGlvbiBlbnZBdChlbnYsIHQpIHsKICBmb3IgKGNvbnN0IHNlZyBv"
        "ZiBlbnYpIGlmICh0ID49IHNlZy5zdGFydCAmJiB0IDwgc2VnLmVuZCkgcmV0dXJuIHNlZy5nYWluOwogIHJldHVybiBlbnYubGVu"
        "Z3RoID8gZW52W2Vudi5sZW5ndGggLSAxXS5nYWluIDogMDsKfQoKZnVuY3Rpb24gYXVkaWJsZSgpIHsKICBjb25zdCBzb2xvZWQg"
        "PSBbLi4uc3RhdGUuY2hhbm5lbHMuZW50cmllcygpXS5maWx0ZXIoKFssIGNdKSA9PiBjLnNvbG8pLm1hcCgoW25dKSA9PiBuKTsK"
        "ICByZXR1cm4gWy4uLnN0YXRlLmNoYW5uZWxzLmtleXMoKV0uZmlsdGVyKChuKSA9PiB7CiAgICBjb25zdCBjID0gc3RhdGUuY2hh"
        "bm5lbHMuZ2V0KG4pOwogICAgcmV0dXJuIHNvbG9lZC5sZW5ndGggPyBjLnNvbG8gOiAhZ2V0TXV0ZShuKTsKICB9KTsKfQoKZnVu"
        "Y3Rpb24gYXBwbHlHYWlucygpIHsKICBjb25zdCBub3cgPSBBQyA/IEFDLmN1cnJlbnRUaW1lIDogMDsKICBjb25zdCBoZXJlID0g"
        "cG9zaXRpb24oKTsKICBjb25zdCBSQU1QID0gMC4wMjU7CgogIHN0YXRlLmVudnMgPSBuZXcgTWFwKCk7CiAgc3RhdGUuY2hhbm5l"
        "bHMuZm9yRWFjaCgoYywgbmFtZSkgPT4gewogICAgY29uc3QgZW52ID0gc3RlbUVudmVsb3BlKG5hbWUpOwogICAgc3RhdGUuZW52"
        "cy5zZXQobmFtZSwgZW52KTsKICAgIGNvbnN0IHN0YXJ0ID0gZW52QXQoZW52LCBoZXJlKTsKCiAgICBpZiAoYy5nYWluLmdhaW4u"
        "Y2FuY2VsQW5kSG9sZEF0VGltZSkgYy5nYWluLmdhaW4uY2FuY2VsQW5kSG9sZEF0VGltZShub3cpOwogICAgZWxzZSBjLmdhaW4u"
        "Z2Fpbi5jYW5jZWxTY2hlZHVsZWRWYWx1ZXMobm93KTsKICAgIGMuZ2Fpbi5nYWluLnNldFRhcmdldEF0VGltZShzdGFydCwgbm93"
        "LCAwLjAwOCk7CgogICAgaWYgKHN0YXRlLnBsYXlpbmcpIHsKICAgICAgbGV0IHByZXYgPSBzdGFydDsKICAgICAgZm9yIChjb25z"
        "dCBzZWcgb2YgZW52KSB7CiAgICAgICAgaWYgKHNlZy5lbmQgPD0gaGVyZSB8fCBzZWcuc3RhcnQgPD0gaGVyZSkgeyBpZiAoc2Vn"
        "LmVuZCA+IGhlcmUpIHByZXYgPSBzZWcuZ2FpbjsgY29udGludWU7IH0KICAgICAgICBjb25zdCB3aGVuID0gbm93ICsgKHNlZy5z"
        "dGFydCAtIGhlcmUpOwogICAgICAgIGMuZ2Fpbi5nYWluLnNldFZhbHVlQXRUaW1lKHByZXYsIHdoZW4pOwogICAgICAgIGMuZ2Fp"
        "bi5nYWluLmxpbmVhclJhbXBUb1ZhbHVlQXRUaW1lKHNlZy5nYWluLCB3aGVuICsgUkFNUCk7CiAgICAgICAgcHJldiA9IHNlZy5n"
        "YWluOwogICAgICB9CiAgICB9CgogICAgY29uc3QgbGl2ZSA9IHN0YXJ0ID4gMC4wMDAxOwogICAgaWYgKGMuZWwpIHsKICAgICAg"
        "Yy5lbC5jbGFzc0xpc3QudG9nZ2xlKCJtdXRlZCIsICFsaXZlKTsKICAgICAgYy5lbC5xdWVyeVNlbGVjdG9yQWxsKCIubWluaSIp"
        "LmZvckVhY2goKGIpID0+IHsKICAgICAgICBpZiAoYi5kYXRhc2V0LnJvbGUgPT09ICJtdXRlIikgYi5jbGFzc0xpc3QudG9nZ2xl"
        "KCJvbiIsIGdldE11dGUobmFtZSkpOwogICAgICAgIGlmIChiLmRhdGFzZXQucm9sZSA9PT0gInNvbG8iKSBiLmNsYXNzTGlzdC50"
        "b2dnbGUoIm9uIiwgYy5zb2xvKTsKICAgICAgfSk7CiAgICB9CiAgfSk7Cn0KCi8qIOKUgOKUgCBzZWN0aW9ucyDilIDilIDilIDi"
        "lIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDi"
        "lIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDi"
        "lIDilIDilIDilIDilIAgKi8KZnVuY3Rpb24gbWFrZVNlY3Rpb24ocmFuZ2UpIHsKICBjb25zdCBzdGFydCA9IE1hdGgubWF4KDAs"
        "IHJhbmdlLnN0YXJ0KTsKICBjb25zdCBlbmQgPSBNYXRoLm1pbihzdGF0ZS5kdXJhdGlvbiwgcmFuZ2UuZW5kKTsKICBpZiAoZW5k"
        "IC0gc3RhcnQgPCAwLjI1KSB7IHRvYXN0KCJUaGF0IHNlY3Rpb24gaXMgdG9vIHNob3J0IHRvIGJlIHVzZWZ1bC4iLCB0cnVlKTsg"
        "cmV0dXJuOyB9CiAgaWYgKHN0YXRlLnNlY3Rpb25zLnNvbWUoKHMpID0+IHN0YXJ0IDwgcy5lbmQgJiYgZW5kID4gcy5zdGFydCkp"
        "IHsKICAgIHRvYXN0KCJUaGF0IG92ZXJsYXBzIGEgc2VjdGlvbiB5b3UgYWxyZWFkeSBtYWRlLiIsIHRydWUpOwogICAgcmV0dXJu"
        "OwogIH0KICBjb25zdCBnYWlucyA9IHt9LCBtdXRlcyA9IHt9OwogIHN0YXRlLmNoYW5uZWxzLmZvckVhY2goKGMsIG5hbWUpID0+"
        "IHsgZ2FpbnNbbmFtZV0gPSBjLnBvczsgbXV0ZXNbbmFtZV0gPSBjLm11dGU7IH0pOwoKICBjb25zdCBzZWMgPSB7CiAgICBpZDog"
        "InMiICsgRGF0ZS5ub3coKS50b1N0cmluZygzNiksCiAgICBuYW1lOiAiU2VjdGlvbiAiICsgKHN0YXRlLnNlY3Rpb25zLmxlbmd0"
        "aCArIDEpLAogICAgc3RhcnQsIGVuZCwgZ2FpbnMsIG11dGVzLAogIH07CiAgc3RhdGUuc2VjdGlvbnMucHVzaChzZWMpOwogIHN0"
        "YXRlLnNlY3Rpb25zLnNvcnQoKGEsIGIpID0+IGEuc3RhcnQgLSBiLnN0YXJ0KTsKICBlZGl0U2VjdGlvbihzZWMuaWQpOwp9Cgpm"
        "dW5jdGlvbiBlZGl0U2VjdGlvbihpZCkgewogIHN0YXRlLmVkaXRpbmcgPSBpZDsKICBjb25zdCBzZWMgPSB0YXJnZXQoKTsKICBp"
        "ZiAoc2VjKSB7CiAgICBzdGF0ZS5yZWdpb24gPSB7IHN0YXJ0OiBzZWMuc3RhcnQsIGVuZDogc2VjLmVuZCB9OwogICAgc3RhdGUu"
        "bG9vcCA9IHRydWU7CiAgICAkKCIjbG9vcEJ0biIpLnNldEF0dHJpYnV0ZSgiYXJpYS1wcmVzc2VkIiwgInRydWUiKTsKICAgIHBh"
        "aW50UmVnaW9uKCk7CiAgICBzZWVrKHNlYy5zdGFydCk7CiAgfQogIHJlcGFpbnRTdHJpcHMoKTsKICByZW5kZXJMYW5lKCk7CiAg"
        "cmVuZGVyRWRpdEJhcigpOwogIGFwcGx5R2FpbnMoKTsKfQoKZnVuY3Rpb24gZWRpdFdob2xlVHJhY2tRdWlldCgpIHsKICBzdGF0"
        "ZS5lZGl0aW5nID0gbnVsbDsKICByZXBhaW50U3RyaXBzKCk7CiAgcmVuZGVyTGFuZSgpOwp9CgpmdW5jdGlvbiBlZGl0V2hvbGVU"
        "cmFjaygpIHsKICBzdGF0ZS5lZGl0aW5nID0gbnVsbDsKICBzdGF0ZS5yZWdpb24gPSBudWxsOwogIHN0YXRlLmxvb3AgPSBmYWxz"
        "ZTsKICAkKCIjbG9vcEJ0biIpLnNldEF0dHJpYnV0ZSgiYXJpYS1wcmVzc2VkIiwgImZhbHNlIik7CiAgcGFpbnRSZWdpb24oKTsK"
        "ICByZXBhaW50U3RyaXBzKCk7CiAgcmVuZGVyTGFuZSgpOwogIHJlbmRlckVkaXRCYXIoKTsKICBhcHBseUdhaW5zKCk7Cn0KCmZ1"
        "bmN0aW9uIGRlbGV0ZVNlY3Rpb24oaWQpIHsKICBzdGF0ZS5zZWN0aW9ucyA9IHN0YXRlLnNlY3Rpb25zLmZpbHRlcigocykgPT4g"
        "cy5pZCAhPT0gaWQpOwogIGVkaXRXaG9sZVRyYWNrKCk7Cn0KCmZ1bmN0aW9uIHJlcGFpbnRTdHJpcHMoKSB7CiAgc3RhdGUuY2hh"
        "bm5lbHMuZm9yRWFjaCgoYykgPT4gYy5wYWludCAmJiBjLnBhaW50KCkpOwogICQoIiNzdHJpcHMiKS5jbGFzc0xpc3QudG9nZ2xl"
        "KCJzY29wZWQiLCAhIXN0YXRlLmVkaXRpbmcpOwp9CgpmdW5jdGlvbiByZW5kZXJMYW5lKCkgewogIGNvbnN0IGxhbmUgPSAkKCIj"
        "bGFuZSIpOwogIGxhbmUuaW5uZXJIVE1MID0gIiI7CiAgaWYgKCFzdGF0ZS5kdXJhdGlvbikgcmV0dXJuOwogIHN0YXRlLnNlY3Rp"
        "b25zLmZvckVhY2goKHNlYykgPT4gewogICAgY29uc3QgYiA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImRpdiIpOwogICAgYi5j"
        "bGFzc05hbWUgPSAiYmxvY2siICsgKHNlYy5pZCA9PT0gc3RhdGUuZWRpdGluZyA/ICIgb24iIDogIiIpOwogICAgYi5zdHlsZS5s"
        "ZWZ0ID0gKHNlYy5zdGFydCAvIHN0YXRlLmR1cmF0aW9uKSAqIDEwMCArICIlIjsKICAgIGIuc3R5bGUud2lkdGggPSBNYXRoLm1h"
        "eCgxLjIsICgoc2VjLmVuZCAtIHNlYy5zdGFydCkgLyBzdGF0ZS5kdXJhdGlvbikgKiAxMDApICsgIiUiOwogICAgYi50ZXh0Q29u"
        "dGVudCA9IHNlYy5uYW1lOwogICAgYi50aXRsZSA9IGAke3NlYy5uYW1lfSDigJQgJHtjbG9jayhzZWMuc3RhcnQpfSB0byAke2Ns"
        "b2NrKHNlYy5lbmQpfWA7CiAgICBiLmFkZEV2ZW50TGlzdGVuZXIoImNsaWNrIiwgKCkgPT4gZWRpdFNlY3Rpb24oc2VjLmlkKSk7"
        "CiAgICBsYW5lLmFwcGVuZENoaWxkKGIpOwogIH0pOwp9CgpmdW5jdGlvbiByZW5kZXJFZGl0QmFyKCkgewogIGNvbnN0IHNlYyA9"
        "IHRhcmdldCgpOwogIGNvbnN0IGJhciA9ICQoIiNlZGl0YmFyIiksIHRvb2xzID0gJCgiI2VkaXRUb29scyIpOwogIHRvb2xzLmlu"
        "bmVySFRNTCA9ICIiOwogIGJhci5jbGFzc0xpc3QudG9nZ2xlKCJzY29wZWQiLCAhIXNlYyk7CgogIGlmIChzZWMpIHsKICAgICQo"
        "IiNlZGl0S2lja2VyIikudGV4dENvbnRlbnQgPSBgQWRqdXN0aW5nIGp1c3QgdGhpcyBwYXJ0IOKAlCAke2Nsb2NrKHNlYy5zdGFy"
        "dCl9IHRvICR7Y2xvY2soc2VjLmVuZCl9YDsKICAgICQoIiNlZGl0TmFtZSIpLnRleHRDb250ZW50ID0gc2VjLm5hbWU7CgogICAg"
        "Y29uc3QgbmFtZSA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoImlucHV0Iik7CiAgICBuYW1lLmNsYXNzTmFtZSA9ICJuYW1lLWlu"
        "cHV0IjsKICAgIG5hbWUudmFsdWUgPSBzZWMubmFtZTsKICAgIG5hbWUuc2V0QXR0cmlidXRlKCJhcmlhLWxhYmVsIiwgIlNlY3Rp"
        "b24gbmFtZSIpOwogICAgbmFtZS5hZGRFdmVudExpc3RlbmVyKCJpbnB1dCIsICgpID0+IHsKICAgICAgc2VjLm5hbWUgPSBuYW1l"
        "LnZhbHVlIHx8ICJTZWN0aW9uIjsKICAgICAgJCgiI2VkaXROYW1lIikudGV4dENvbnRlbnQgPSBzZWMubmFtZTsKICAgICAgcmVu"
        "ZGVyTGFuZSgpOwogICAgfSk7CiAgICB0b29scy5hcHBlbmRDaGlsZChuYW1lKTsKCiAgICB0b29scy5hcHBlbmRDaGlsZChidXR0"
        "b24oIkV4cG9ydCBqdXN0IHRoaXMgcGFydCIsICJnbyIsICgpID0+IGV4cG9ydE1peCh7IHJhbmdlOiBbc2VjLnN0YXJ0LCBzZWMu"
        "ZW5kXSwgbGFiZWw6IHNlYy5uYW1lIH0pKSk7CiAgICB0b29scy5hcHBlbmRDaGlsZChidXR0b24oIkRlbGV0ZSIsICJkYW5nZXIi"
        "LCAoKSA9PiBkZWxldGVTZWN0aW9uKHNlYy5pZCkpKTsKICAgIHRvb2xzLmFwcGVuZENoaWxkKGJ1dHRvbigiQmFjayB0byB3aG9s"
        "ZSB0cmFjayIsICIiLCBlZGl0V2hvbGVUcmFjaykpOwogICAgcmV0dXJuOwogIH0KCiAgJCgiI2VkaXRLaWNrZXIiKS50ZXh0Q29u"
        "dGVudCA9ICJBZGp1c3RpbmciOwogICQoIiNlZGl0TmFtZSIpLnRleHRDb250ZW50ID0gInRoZSB3aG9sZSB0cmFjayI7CgogIGlm"
        "IChzdGF0ZS5yZWdpb24gJiYgc3RhdGUucmVnaW9uLmVuZCAtIHN0YXRlLnJlZ2lvbi5zdGFydCA+IDAuMjUpIHsKICAgIGNvbnN0"
        "IHIgPSBzdGF0ZS5yZWdpb247CiAgICB0b29scy5hcHBlbmRDaGlsZChoaW50KGAke2Nsb2NrKHIuc3RhcnQpfSDigJMgJHtjbG9j"
        "ayhyLmVuZCl9IHNlbGVjdGVkYCkpOwogICAgdG9vbHMuYXBwZW5kQ2hpbGQoYnV0dG9uKCJBZGp1c3QganVzdCB0aGlzIHBhcnQi"
        "LCAiZ28iLCAoKSA9PiBtYWtlU2VjdGlvbihyKSkpOwogICAgdG9vbHMuYXBwZW5kQ2hpbGQoYnV0dG9uKCJDbGVhciIsICIiLCAo"
        "KSA9PiB7CiAgICAgIHN0YXRlLnJlZ2lvbiA9IG51bGw7IHN0YXRlLmxvb3AgPSBmYWxzZTsKICAgICAgJCgiI2xvb3BCdG4iKS5z"
        "ZXRBdHRyaWJ1dGUoImFyaWEtcHJlc3NlZCIsICJmYWxzZSIpOwogICAgICBwYWludFJlZ2lvbigpOyByZW5kZXJFZGl0QmFyKCk7"
        "CiAgICB9KSk7CiAgfSBlbHNlIGlmIChzdGF0ZS5zZWN0aW9ucy5sZW5ndGgpIHsKICAgIHRvb2xzLmFwcGVuZENoaWxkKGhpbnQo"
        "IkNsaWNrIGEgc2VjdGlvbiBiZWxvdyB0aGUgd2F2ZWZvcm0gdG8gYWRqdXN0IGl0IikpOwogIH0gZWxzZSB7CiAgICB0b29scy5h"
        "cHBlbmRDaGlsZChoaW50KCJEcmFnIGFjcm9zcyB0aGUgd2F2ZWZvcm0gdG8gcGljayBhIHBhcnQgb2YgdGhlIHNvbmciKSk7CiAg"
        "fQp9CgpmdW5jdGlvbiBidXR0b24obGFiZWwsIGNscywgZm4pIHsKICBjb25zdCBiID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgi"
        "YnV0dG9uIik7CiAgYi5jbGFzc05hbWUgPSAibWluaS1idG4iICsgKGNscyA/ICIgIiArIGNscyA6ICIiKTsKICBiLnRleHRDb250"
        "ZW50ID0gbGFiZWw7CiAgYi5hZGRFdmVudExpc3RlbmVyKCJjbGljayIsIGZuKTsKICByZXR1cm4gYjsKfQpmdW5jdGlvbiBoaW50"
        "KHRleHQpIHsKICBjb25zdCBzID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgic3BhbiIpOwogIHMuY2xhc3NOYW1lID0gImhpbnQi"
        "OwogIHMuc3R5bGUubWFyZ2luID0gIjAiOwogIHMudGV4dENvbnRlbnQgPSB0ZXh0OwogIHJldHVybiBzOwp9CgovKiDilIDilIAg"
        "dHJhbnNwb3J0IOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKU"
        "gOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgCAqLwpm"
        "dW5jdGlvbiB3aXJlVHJhbnNwb3J0KCkgewogICQoIiNwbGF5QnRuIikuYWRkRXZlbnRMaXN0ZW5lcigiY2xpY2siLCB0b2dnbGVQ"
        "bGF5KTsKICAkKCIjbG9vcEJ0biIpLmFkZEV2ZW50TGlzdGVuZXIoImNsaWNrIiwgKCkgPT4gewogICAgc3RhdGUubG9vcCA9ICFz"
        "dGF0ZS5sb29wOwogICAgJCgiI2xvb3BCdG4iKS5zZXRBdHRyaWJ1dGUoImFyaWEtcHJlc3NlZCIsIFN0cmluZyhzdGF0ZS5sb29w"
        "KSk7CiAgICBpZiAoc3RhdGUubG9vcCAmJiAhc3RhdGUucmVnaW9uKSBzdGF0ZS5yZWdpb24gPSB7IHN0YXJ0OiAwLCBlbmQ6IHN0"
        "YXRlLmR1cmF0aW9uIH07CiAgICBwYWludFJlZ2lvbigpOwogICAgaWYgKHN0YXRlLnBsYXlpbmcpIHN0YXJ0QXQocG9zaXRpb24o"
        "KSk7CiAgfSk7CgogIGNvbnN0IHdyYXAgPSAkKCIud2F2ZS13cmFwIik7CiAgbGV0IGRvd24gPSBudWxsOwogIHdyYXAuYWRkRXZl"
        "bnRMaXN0ZW5lcigicG9pbnRlcmRvd24iLCAoZSkgPT4gewogICAgY29uc3QgciA9IHdyYXAuZ2V0Qm91bmRpbmdDbGllbnRSZWN0"
        "KCk7CiAgICBkb3duID0geyB4OiBlLmNsaWVudFgsIHQ6ICgoZS5jbGllbnRYIC0gci5sZWZ0KSAvIHIud2lkdGgpICogc3RhdGUu"
        "ZHVyYXRpb24sIG1vdmVkOiBmYWxzZSB9OwogICAgd3JhcC5zZXRQb2ludGVyQ2FwdHVyZShlLnBvaW50ZXJJZCk7CiAgfSk7CiAg"
        "d3JhcC5hZGRFdmVudExpc3RlbmVyKCJwb2ludGVybW92ZSIsIChlKSA9PiB7CiAgICBpZiAoIWRvd24pIHJldHVybjsKICAgIGlm"
        "IChNYXRoLmFicyhlLmNsaWVudFggLSBkb3duLngpIDwgNSkgcmV0dXJuOwogICAgZG93bi5tb3ZlZCA9IHRydWU7CiAgICBpZiAo"
        "c3RhdGUuZWRpdGluZykgZWRpdFdob2xlVHJhY2tRdWlldCgpOwogICAgc3RhdGUubG9vcCA9IHRydWU7CiAgICAkKCIjbG9vcEJ0"
        "biIpLnNldEF0dHJpYnV0ZSgiYXJpYS1wcmVzc2VkIiwgInRydWUiKTsKICAgIGNvbnN0IHIgPSB3cmFwLmdldEJvdW5kaW5nQ2xp"
        "ZW50UmVjdCgpOwogICAgY29uc3QgdCA9ICgoZS5jbGllbnRYIC0gci5sZWZ0KSAvIHIud2lkdGgpICogc3RhdGUuZHVyYXRpb247"
        "CiAgICBzdGF0ZS5yZWdpb24gPSB7IHN0YXJ0OiBNYXRoLm1heCgwLCBNYXRoLm1pbihkb3duLnQsIHQpKSwgZW5kOiBNYXRoLm1p"
        "bihzdGF0ZS5kdXJhdGlvbiwgTWF0aC5tYXgoZG93bi50LCB0KSkgfTsKICAgIHBhaW50UmVnaW9uKCk7CiAgfSk7CiAgd3JhcC5h"
        "ZGRFdmVudExpc3RlbmVyKCJwb2ludGVydXAiLCAoKSA9PiB7CiAgICBpZiAoIWRvd24pIHJldHVybjsKICAgIGlmIChkb3duLm1v"
        "dmVkKSB7CiAgICAgIHN0YXRlLmxvb3AgPSB0cnVlOwogICAgICAkKCIjbG9vcEJ0biIpLnNldEF0dHJpYnV0ZSgiYXJpYS1wcmVz"
        "c2VkIiwgInRydWUiKTsKICAgICAgcmVuZGVyRWRpdEJhcigpOwogICAgICBzZWVrKHN0YXRlLnJlZ2lvbi5zdGFydCk7CiAgICB9"
        "IGVsc2UgewogICAgICBzdGF0ZS5yZWdpb24gPSBudWxsOwogICAgICBzdGF0ZS5sb29wID0gZmFsc2U7CiAgICAgICQoIiNsb29w"
        "QnRuIikuc2V0QXR0cmlidXRlKCJhcmlhLXByZXNzZWQiLCAiZmFsc2UiKTsKICAgICAgcGFpbnRSZWdpb24oKTsKICAgICAgcmVu"
        "ZGVyRWRpdEJhcigpOwogICAgICBzZWVrKGRvd24udCk7CiAgICB9CiAgICBkb3duID0gbnVsbDsKICB9KTsKCiAgd2luZG93LmFk"
        "ZEV2ZW50TGlzdGVuZXIoInJlc2l6ZSIsICgpID0+IHsgZHJhd1dhdmUoKTsgcGFpbnRSZWdpb24oKTsgcmVuZGVyTGFuZSgpOyB9"
        "KTsKICBkb2N1bWVudC5hZGRFdmVudExpc3RlbmVyKCJrZXlkb3duIiwgKGUpID0+IHsKICAgIGlmICgvaW5wdXR8c2VsZWN0fHRl"
        "eHRhcmVhL2kudGVzdChlLnRhcmdldC50YWdOYW1lKSkgcmV0dXJuOwogICAgaWYgKCQoIiNjb25zb2xlIikuaGlkZGVuKSByZXR1"
        "cm47CiAgICBpZiAoZS5jb2RlID09PSAiU3BhY2UiKSB7IGUucHJldmVudERlZmF1bHQoKTsgdG9nZ2xlUGxheSgpOyB9CiAgICBp"
        "ZiAoZS5rZXkudG9Mb3dlckNhc2UoKSA9PT0gImwiKSAkKCIjbG9vcEJ0biIpLmNsaWNrKCk7CiAgfSk7Cn0KCmZ1bmN0aW9uIHBv"
        "c2l0aW9uKCkgewogIGlmICghc3RhdGUucGxheWluZykgcmV0dXJuIHN0YXRlLm9mZnNldDsKICBsZXQgcCA9IEFDLmN1cnJlbnRU"
        "aW1lIC0gc3RhdGUuc3RhcnRlZEF0OwogIGlmIChzdGF0ZS5sb29wICYmIHN0YXRlLnJlZ2lvbikgewogICAgY29uc3QgbGVuID0g"
        "c3RhdGUucmVnaW9uLmVuZCAtIHN0YXRlLnJlZ2lvbi5zdGFydDsKICAgIGlmIChsZW4gPiAwLjA1ICYmIHAgPiBzdGF0ZS5yZWdp"
        "b24uZW5kKSBwID0gc3RhdGUucmVnaW9uLnN0YXJ0ICsgKChwIC0gc3RhdGUucmVnaW9uLnN0YXJ0KSAlIGxlbik7CiAgfQogIHJl"
        "dHVybiBwOwp9CgpmdW5jdGlvbiBzdG9wU291cmNlcygpIHsKICBzdGF0ZS5jaGFubmVscy5mb3JFYWNoKChjKSA9PiB7CiAgICBp"
        "ZiAoYy5zcmMpIHsgdHJ5IHsgYy5zcmMuc3RvcCgpOyB9IGNhdGNoIHt9IGMuc3JjLmRpc2Nvbm5lY3QoKTsgYy5zcmMgPSBudWxs"
        "OyB9CiAgfSk7Cn0KCmZ1bmN0aW9uIHN0YXJ0QXQob2Zmc2V0KSB7CiAgYXVkaW8oKTsKICBzdG9wU291cmNlcygpOwogIGNvbnN0"
        "IHVzZUxvb3AgPSBzdGF0ZS5sb29wICYmIHN0YXRlLnJlZ2lvbiAmJiBzdGF0ZS5yZWdpb24uZW5kIC0gc3RhdGUucmVnaW9uLnN0"
        "YXJ0ID4gMC4wNTsKICBpZiAodXNlTG9vcCkgb2Zmc2V0ID0gTWF0aC5tYXgoc3RhdGUucmVnaW9uLnN0YXJ0LCBNYXRoLm1pbihv"
        "ZmZzZXQsIHN0YXRlLnJlZ2lvbi5lbmQgLSAwLjAyKSk7CiAgb2Zmc2V0ID0gTWF0aC5tYXgoMCwgTWF0aC5taW4ob2Zmc2V0LCBN"
        "YXRoLm1heCgwLCBzdGF0ZS5kdXJhdGlvbiAtIDAuMDIpKSk7CgogIGNvbnN0IGF0ID0gQUMuY3VycmVudFRpbWUgKyAwLjA2Owog"
        "IHN0YXRlLmNoYW5uZWxzLmZvckVhY2goKGMpID0+IHsKICAgIGNvbnN0IHNyYyA9IEFDLmNyZWF0ZUJ1ZmZlclNvdXJjZSgpOwog"
        "ICAgc3JjLmJ1ZmZlciA9IGMuYnVmZmVyOwogICAgaWYgKHVzZUxvb3ApIHsgc3JjLmxvb3AgPSB0cnVlOyBzcmMubG9vcFN0YXJ0"
        "ID0gc3RhdGUucmVnaW9uLnN0YXJ0OyBzcmMubG9vcEVuZCA9IHN0YXRlLnJlZ2lvbi5lbmQ7IH0KICAgIHNyYy5jb25uZWN0KGMu"
        "Z2Fpbik7CiAgICBzcmMuc3RhcnQoYXQsIG9mZnNldCk7CiAgICBjLnNyYyA9IHNyYzsKICB9KTsKICBzdGF0ZS5zdGFydGVkQXQg"
        "PSBhdCAtIG9mZnNldDsKICBzdGF0ZS5wbGF5aW5nID0gdHJ1ZTsKICAkKCIjcGxheUJ0biIpLmNsYXNzTGlzdC5hZGQoInBsYXlp"
        "bmciKTsKICAkKCIjcGxheUJ0biIpLnNldEF0dHJpYnV0ZSgiYXJpYS1sYWJlbCIsICJQYXVzZSIpOwp9CgpmdW5jdGlvbiBzdG9w"
        "UGxheWJhY2soKSB7CiAgaWYgKCFBQykgcmV0dXJuOwogIHN0b3BTb3VyY2VzKCk7CiAgc3RhdGUucGxheWluZyA9IGZhbHNlOwog"
        "IGNvbnN0IGJ0biA9ICQoIiNwbGF5QnRuIik7CiAgaWYgKGJ0bikgeyBidG4uY2xhc3NMaXN0LnJlbW92ZSgicGxheWluZyIpOyBi"
        "dG4uc2V0QXR0cmlidXRlKCJhcmlhLWxhYmVsIiwgIlBsYXkiKTsgfQp9CgpmdW5jdGlvbiB0b2dnbGVQbGF5KCkgewogIGlmICgh"
        "c3RhdGUuY2hhbm5lbHMuc2l6ZSkgcmV0dXJuOwogIGlmIChzdGF0ZS5wbGF5aW5nKSB7CiAgICBzdGF0ZS5vZmZzZXQgPSBwb3Np"
        "dGlvbigpOwogICAgc3RvcFBsYXliYWNrKCk7CiAgfSBlbHNlIHsKICAgIHN0YXJ0QXQoc3RhdGUub2Zmc2V0KTsKICB9Cn0KCmZ1"
        "bmN0aW9uIHNlZWsodCkgewogIHN0YXRlLm9mZnNldCA9IE1hdGgubWF4KDAsIE1hdGgubWluKHQsIHN0YXRlLmR1cmF0aW9uKSk7"
        "CiAgaWYgKHN0YXRlLnBsYXlpbmcpIHN0YXJ0QXQoc3RhdGUub2Zmc2V0KTsKICBlbHNlIHBhaW50UGxheWhlYWQoc3RhdGUub2Zm"
        "c2V0KTsKfQoKLyog4pSA4pSAIHdhdmVmb3JtIOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKU"
        "gOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKU"
        "gOKUgOKUgOKUgOKUgOKUgCAqLwpmdW5jdGlvbiBidWlsZFBlYWtzKCkgewogIGNvbnN0IHNvdXJjZXMgPSBbLi4uc3RhdGUuY2hh"
        "bm5lbHMuZW50cmllcygpXS5maWx0ZXIoKFssIGNdKSA9PiAhYy5kZXJpdmVkKS5tYXAoKFssIGNdKSA9PiBjLmJ1ZmZlcik7CiAg"
        "aWYgKCFzb3VyY2VzLmxlbmd0aCkgeyBzdGF0ZS5wZWFrcyA9IG51bGw7IHJldHVybjsgfQogIGNvbnN0IE4gPSAxNDAwOwogIGNv"
        "bnN0IHBlYWtzID0gbmV3IEZsb2F0MzJBcnJheShOKTsKICBjb25zdCB0b3RhbCA9IE1hdGgubWF4KC4uLnNvdXJjZXMubWFwKChi"
        "KSA9PiBiLmxlbmd0aCkpOwogIGNvbnN0IHN0ZXAgPSBNYXRoLm1heCgxLCBNYXRoLmZsb29yKHRvdGFsIC8gTikpOwoKICBzb3Vy"
        "Y2VzLmZvckVhY2goKGJ1ZikgPT4gewogICAgY29uc3QgZGF0YSA9IGJ1Zi5nZXRDaGFubmVsRGF0YSgwKTsKICAgIGZvciAobGV0"
        "IGkgPSAwOyBpIDwgTjsgaSsrKSB7CiAgICAgIGxldCBtID0gMDsKICAgICAgY29uc3Qgc3RhcnQgPSBpICogc3RlcDsKICAgICAg"
        "Y29uc3QgZW5kID0gTWF0aC5taW4oZGF0YS5sZW5ndGgsIHN0YXJ0ICsgc3RlcCk7CiAgICAgIGZvciAobGV0IHMgPSBzdGFydDsg"
        "cyA8IGVuZDsgcyArPSA0KSB7CiAgICAgICAgY29uc3QgdiA9IE1hdGguYWJzKGRhdGFbc10pOwogICAgICAgIGlmICh2ID4gbSkg"
        "bSA9IHY7CiAgICAgIH0KICAgICAgcGVha3NbaV0gKz0gbTsKICAgIH0KICB9KTsKICBsZXQgbWF4ID0gMDsKICBmb3IgKGNvbnN0"
        "IHYgb2YgcGVha3MpIGlmICh2ID4gbWF4KSBtYXggPSB2OwogIGlmIChtYXggPiAwKSBmb3IgKGxldCBpID0gMDsgaSA8IE47IGkr"
        "KykgcGVha3NbaV0gLz0gbWF4OwogIHN0YXRlLnBlYWtzID0gcGVha3M7Cn0KCmZ1bmN0aW9uIGRyYXdXYXZlKCkgewogIGNvbnN0"
        "IGN2ID0gJCgiI3dhdmUiKTsKICBpZiAoIWN2IHx8ICFzdGF0ZS5wZWFrcykgcmV0dXJuOwogIGNvbnN0IGRwciA9IHdpbmRvdy5k"
        "ZXZpY2VQaXhlbFJhdGlvIHx8IDE7CiAgY29uc3QgdyA9IGN2LmNsaWVudFdpZHRoLCBoID0gY3YuY2xpZW50SGVpZ2h0OwogIGN2"
        "LndpZHRoID0gdyAqIGRwcjsgY3YuaGVpZ2h0ID0gaCAqIGRwcjsKICBjb25zdCBnID0gY3YuZ2V0Q29udGV4dCgiMmQiKTsKICBn"
        "LnNldFRyYW5zZm9ybShkcHIsIDAsIDAsIGRwciwgMCwgMCk7CiAgZy5jbGVhclJlY3QoMCwgMCwgdywgaCk7CgogIGNvbnN0IGJh"
        "cnMgPSBNYXRoLm1heCgxLCBNYXRoLmZsb29yKHcgLyAzKSk7CiAgY29uc3QgbWlkID0gaCAvIDI7CiAgZy5maWxsU3R5bGUgPSAi"
        "IzNkNDU1MCI7CiAgZm9yIChsZXQgaSA9IDA7IGkgPCBiYXJzOyBpKyspIHsKICAgIGNvbnN0IHAgPSBzdGF0ZS5wZWFrc1tNYXRo"
        "LmZsb29yKChpIC8gYmFycykgKiBzdGF0ZS5wZWFrcy5sZW5ndGgpXSB8fCAwOwogICAgY29uc3QgYmggPSBNYXRoLm1heCgxLjUs"
        "IHAgKiAoaCAtIDgpKTsKICAgIGcuZmlsbFJlY3QoaSAqIDMsIG1pZCAtIGJoIC8gMiwgMiwgYmgpOwogIH0KfQoKZnVuY3Rpb24g"
        "cGFpbnRSZWdpb24oKSB7CiAgY29uc3QgZWwgPSAkKCIjbG9vcFJlZ2lvbiIpOwogIGlmICghc3RhdGUucmVnaW9uIHx8ICFzdGF0"
        "ZS5sb29wIHx8ICFzdGF0ZS5kdXJhdGlvbikgeyBlbC5oaWRkZW4gPSB0cnVlOyByZXR1cm47IH0KICBlbC5oaWRkZW4gPSBmYWxz"
        "ZTsKICBlbC5zdHlsZS5sZWZ0ID0gKHN0YXRlLnJlZ2lvbi5zdGFydCAvIHN0YXRlLmR1cmF0aW9uKSAqIDEwMCArICIlIjsKICBl"
        "bC5zdHlsZS53aWR0aCA9ICgoc3RhdGUucmVnaW9uLmVuZCAtIHN0YXRlLnJlZ2lvbi5zdGFydCkgLyBzdGF0ZS5kdXJhdGlvbikg"
        "KiAxMDAgKyAiJSI7Cn0KCmZ1bmN0aW9uIHBhaW50UGxheWhlYWQodCkgewogICQoIiNwbGF5aGVhZCIpLnN0eWxlLmxlZnQgPSAo"
        "c3RhdGUuZHVyYXRpb24gPyAodCAvIHN0YXRlLmR1cmF0aW9uKSAqIDEwMCA6IDApICsgIiUiOwogICQoIiN0aW1lTm93IikudGV4"
        "dENvbnRlbnQgPSBjbG9jayh0KTsKfQoKLyog4pSA4pSAIG1ldGVycyArIHBsYXloZWFkIGxvb3Ag4pSA4pSA4pSA4pSA4pSA4pSA"
        "4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA"
        "4pSAICovCmZ1bmN0aW9uIHRpY2soKSB7CiAgaWYgKCQoIiNjb25zb2xlIikuaGlkZGVuKSByZXR1cm47CiAgY29uc3QgdCA9IHBv"
        "c2l0aW9uKCk7CiAgaWYgKHN0YXRlLnBsYXlpbmcgJiYgdCA8IHN0YXRlLmxhc3RQb3MgLSAwLjA1KSBhcHBseUdhaW5zKCk7ICAg"
        "Ly8gbG9vcCB3cmFwcGVkCiAgc3RhdGUubGFzdFBvcyA9IHQ7CgogIGlmIChzdGF0ZS5wbGF5aW5nICYmICFzdGF0ZS5sb29wICYm"
        "IHQgPj0gc3RhdGUuZHVyYXRpb24gLSAwLjAzKSB7CiAgICBzdG9wUGxheWJhY2soKTsKICAgIHN0YXRlLm9mZnNldCA9IDA7CiAg"
        "ICBwYWludFBsYXloZWFkKDApOwogIH0gZWxzZSB7CiAgICBwYWludFBsYXloZWFkKHQpOwogIH0KCiAgc3RhdGUuY2hhbm5lbHMu"
        "Zm9yRWFjaCgoYywgbmFtZSkgPT4gewogICAgaWYgKCFjLmVsKSByZXR1cm47CiAgICBpZiAoc3RhdGUuZW52cykgewogICAgICBj"
        "b25zdCBlbnYgPSBzdGF0ZS5lbnZzLmdldChuYW1lKTsKICAgICAgaWYgKGVudikgYy5lbC5jbGFzc0xpc3QudG9nZ2xlKCJtdXRl"
        "ZCIsIGVudkF0KGVudiwgdCkgPD0gMC4wMDAxKTsKICAgIH0KICAgIGxldCBsZXZlbCA9IDA7CiAgICBpZiAoc3RhdGUucGxheWlu"
        "ZykgewogICAgICBjLmFuYWx5c2VyLmdldEZsb2F0VGltZURvbWFpbkRhdGEoYy5kYXRhKTsKICAgICAgbGV0IHN1bSA9IDA7CiAg"
        "ICAgIGZvciAobGV0IGkgPSAwOyBpIDwgYy5kYXRhLmxlbmd0aDsgaSArPSAyKSBzdW0gKz0gYy5kYXRhW2ldICogYy5kYXRhW2ld"
        "OwogICAgICBjb25zdCBybXMgPSBNYXRoLnNxcnQoc3VtIC8gKGMuZGF0YS5sZW5ndGggLyAyKSk7CiAgICAgIGNvbnN0IGRiID0g"
        "MjAgKiBNYXRoLmxvZzEwKHJtcyArIDFlLTkpOwogICAgICBsZXZlbCA9IE1hdGgubWF4KDAsIE1hdGgubWluKDEsIChkYiArIDU0"
        "KSAvIDU0KSk7CiAgICB9CiAgICBjLmhvbGQgPSBNYXRoLm1heChsZXZlbCwgKGMuaG9sZCB8fCAwKSAtIDAuMDI4KTsKICAgIGNv"
        "bnN0IHNlZ3MgPSBjLmVsLnF1ZXJ5U2VsZWN0b3JBbGwoIi5zZWciKTsKICAgIGNvbnN0IGxpdCA9IE1hdGgucm91bmQoYy5ob2xk"
        "ICogc2Vncy5sZW5ndGgpOwogICAgc2Vncy5mb3JFYWNoKChzLCBpKSA9PiB7CiAgICAgIGlmIChpIDwgbGl0KSB7CiAgICAgICAg"
        "cy5zdHlsZS5iYWNrZ3JvdW5kID0gaSA+PSBzZWdzLmxlbmd0aCAtIDIgPyAiI2ZmNWE0NSIKICAgICAgICAgIDogaSA+PSBzZWdz"
        "Lmxlbmd0aCAtIDUgPyAiI2ZmYzQ0ZCIKICAgICAgICAgIDogYHZhcigtLWMtJHtjLmVsLmRhdGFzZXQuc3RlbX0sICM1ZmQzYjQp"
        "YDsKICAgICAgfSBlbHNlIHsKICAgICAgICBzLnN0eWxlLmJhY2tncm91bmQgPSAiIzFiMjAyNyI7CiAgICAgIH0KICAgIH0pOwog"
        "IH0pOwoKICByZXF1ZXN0QW5pbWF0aW9uRnJhbWUodGljayk7Cn0KCi8qIOKUgOKUgCBleHBvcnRzIOKUgOKUgOKUgOKUgOKUgOKU"
        "gOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKU"
        "gOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgCAqLwpmdW5jdGlvbiB3aXJlRXhwb3J0cygp"
        "IHsKICAkJCgiI2Zvcm1hdCBidXR0b24iKS5mb3JFYWNoKChiKSA9PiB7CiAgICBiLmFkZEV2ZW50TGlzdGVuZXIoImNsaWNrIiwg"
        "KCkgPT4gewogICAgICAkJCgiI2Zvcm1hdCBidXR0b24iKS5mb3JFYWNoKChvKSA9PiB7CiAgICAgICAgby5jbGFzc0xpc3QudG9n"
        "Z2xlKCJvbiIsIG8gPT09IGIpOwogICAgICAgIG8uc2V0QXR0cmlidXRlKCJhcmlhLWNoZWNrZWQiLCBTdHJpbmcobyA9PT0gYikp"
        "OwogICAgICB9KTsKICAgICAgc3RhdGUuZm10ID0gYi5kYXRhc2V0LmZtdDsKICAgIH0pOwogIH0pOwoKICAkKCIjZXhwb3J0TWl4"
        "QnRuIikuYWRkRXZlbnRMaXN0ZW5lcigiY2xpY2siLCAoKSA9PiBleHBvcnRNaXgoKSk7CiAgJCgiI3ppcEJ0biIpLmFkZEV2ZW50"
        "TGlzdGVuZXIoImNsaWNrIiwgKCkgPT4gewogICAgaWYgKCFzdGF0ZS5qb2IpIHJldHVybjsKICAgIHdpbmRvdy5sb2NhdGlvbiA9"
        "IGAvYXBpL2pvYnMvJHtzdGF0ZS5qb2IuaWR9L3ppcD9mb3JtYXQ9JHtzdGF0ZS5mbXR9YDsKICB9KTsKICAkKCIjZm9sZGVyQnRu"
        "IikuYWRkRXZlbnRMaXN0ZW5lcigiY2xpY2siLCBhc3luYyAoKSA9PiB7CiAgICBpZiAoIXN0YXRlLmpvYikgcmV0dXJuOwogICAg"
        "Y29uc3QgciA9IGF3YWl0IGZldGNoKGAvYXBpL3JldmVhbC8ke3N0YXRlLmpvYi5pZH1gLCB7IG1ldGhvZDogIlBPU1QiIH0pOwog"
        "ICAgaWYgKCFyLm9rKSB0b2FzdCgiQ291bGRuJ3Qgb3BlbiB0aGUgZm9sZGVyLiBJdCdzIGF0ICIgKyBzdGF0ZS5lbnYub3V0cHV0"
        "X2RpciwgdHJ1ZSk7CiAgfSk7Cn0KCmZ1bmN0aW9uIGRvd25sb2FkKHN0ZW0pIHsKICBpZiAoIXN0YXRlLmpvYikgcmV0dXJuOwog"
        "IHdpbmRvdy5sb2NhdGlvbiA9IGAvYXBpL2pvYnMvJHtzdGF0ZS5qb2IuaWR9L2Rvd25sb2FkLyR7c3RlbX0/Zm9ybWF0PSR7c3Rh"
        "dGUuZm10fWA7Cn0KCmFzeW5jIGZ1bmN0aW9uIGV4cG9ydE1peChvcHRzKSB7CiAgaWYgKCFzdGF0ZS5qb2IpIHJldHVybjsKICBv"
        "cHRzID0gb3B0cyB8fCB7fTsKCiAgY29uc3QgdHJhY2tzID0gW107CiAgc3RhdGUuY2hhbm5lbHMuZm9yRWFjaCgoYywgbmFtZSkg"
        "PT4gewogICAgY29uc3QgZW52ID0gc3RlbUVudmVsb3BlKG5hbWUpOwogICAgaWYgKGVudi5ldmVyeSgoc2VnKSA9PiBzZWcuZ2Fp"
        "biA8IDAuMDAwMSkpIHJldHVybjsKICAgIHRyYWNrcy5wdXNoKHsgbmFtZSwgc2VnbWVudHM6IGVudiB9KTsKICB9KTsKICBpZiAo"
        "IXRyYWNrcy5sZW5ndGgpIHsgdG9hc3QoIkV2ZXJ5dGhpbmcgaXMgc2lsZW50IC0gbm90aGluZyB0byBleHBvcnQuIiwgdHJ1ZSk7"
        "IHJldHVybjsgfQoKICBjb25zdCBoZWFyZCA9IGF1ZGlibGUoKTsKICBjb25zdCBsYWJlbCA9IG9wdHMubGFiZWwgfHwgKGhlYXJk"
        "Lmxlbmd0aCA9PT0gMSA/IGhlYXJkWzBdCiAgICA6IHN0YXRlLnNlY3Rpb25zLmxlbmd0aCA/ICJtaXgiIDogaGVhcmQuam9pbigi"
        "ICsgIikpOwoKICBjb25zdCBidG4gPSAkKCIjZXhwb3J0TWl4QnRuIik7CiAgY29uc3Qgb3JpZ2luYWwgPSBidG4udGV4dENvbnRl"
        "bnQ7CiAgYnRuLmRpc2FibGVkID0gdHJ1ZTsKICBidG4udGV4dENvbnRlbnQgPSAiQm91bmNpbmcuLi4iOwogIHRyeSB7CiAgICBj"
        "b25zdCByZXMgPSBhd2FpdCBmZXRjaChgL2FwaS9qb2JzLyR7c3RhdGUuam9iLmlkfS9taXhgLCB7CiAgICAgIG1ldGhvZDogIlBP"
        "U1QiLAogICAgICBoZWFkZXJzOiB7ICJDb250ZW50LVR5cGUiOiAiYXBwbGljYXRpb24vanNvbiIgfSwKICAgICAgYm9keTogSlNP"
        "Ti5zdHJpbmdpZnkoeyB0cmFja3MsIGZvcm1hdDogc3RhdGUuZm10LCBsYWJlbCwgcmFuZ2U6IG9wdHMucmFuZ2UgfHwgbnVsbCB9"
        "KSwKICAgIH0pOwogICAgaWYgKCFyZXMub2spIHRocm93IG5ldyBFcnJvcigoYXdhaXQgcmVzLmpzb24oKSkuZXJyb3IgfHwgIkV4"
        "cG9ydCBmYWlsZWQuIik7CiAgICBjb25zdCBibG9iID0gYXdhaXQgcmVzLmJsb2IoKTsKICAgIGNvbnN0IGEgPSBkb2N1bWVudC5j"
        "cmVhdGVFbGVtZW50KCJhIik7CiAgICBhLmhyZWYgPSBVUkwuY3JlYXRlT2JqZWN0VVJMKGJsb2IpOwogICAgYS5kb3dubG9hZCA9"
        "IGAke3N0YXRlLmpvYi50aXRsZX0gLSAke2xhYmVsfS4ke3N0YXRlLmZtdH1gOwogICAgYS5jbGljaygpOwogICAgc2V0VGltZW91"
        "dCgoKSA9PiBVUkwucmV2b2tlT2JqZWN0VVJMKGEuaHJlZiksIDQwMDApOwogICAgdG9hc3QoIlNhdmVkICIgKyBhLmRvd25sb2Fk"
        "KTsKICB9IGNhdGNoIChlcnIpIHsKICAgIHRvYXN0KGVyci5tZXNzYWdlLCB0cnVlKTsKICB9IGZpbmFsbHkgewogICAgYnRuLmRp"
        "c2FibGVkID0gZmFsc2U7CiAgICBidG4udGV4dENvbnRlbnQgPSBvcmlnaW5hbDsKICB9Cn0KCmJvb3QoKTsK"
    ,
    "index.html":
        "PCFET0NUWVBFIGh0bWw+CjxodG1sIGxhbmc9ImVuIj4KPGhlYWQ+CjxtZXRhIGNoYXJzZXQ9InV0Zi04Ij4KPG1ldGEgbmFtZT0i"
        "dmlld3BvcnQiIGNvbnRlbnQ9IndpZHRoPWRldmljZS13aWR0aCwgaW5pdGlhbC1zY2FsZT0xIj4KPHRpdGxlPlVOTUlYIOKAlCBs"
        "b2NhbCBzdGVtIHNlcGFyYXRpb248L3RpdGxlPgo8bGluayByZWw9InByZWNvbm5lY3QiIGhyZWY9Imh0dHBzOi8vZm9udHMuZ29v"
        "Z2xlYXBpcy5jb20iPgo8bGluayByZWw9InByZWNvbm5lY3QiIGhyZWY9Imh0dHBzOi8vZm9udHMuZ3N0YXRpYy5jb20iIGNyb3Nz"
        "b3JpZ2luPgo8bGluayBocmVmPSJodHRwczovL2ZvbnRzLmdvb2dsZWFwaXMuY29tL2NzczI/ZmFtaWx5PUJhcmxvdytDb25kZW5z"
        "ZWQ6d2dodEA1MDA7NjAwOzcwMCZmYW1pbHk9SW50ZXI6d2dodEA0MDA7NTAwOzYwMCZmYW1pbHk9SmV0QnJhaW5zK01vbm86d2do"
        "dEA0MDA7NTAwJmRpc3BsYXk9c3dhcCIgcmVsPSJzdHlsZXNoZWV0Ij4KPGxpbmsgcmVsPSJzdHlsZXNoZWV0IiBocmVmPSJzdHls"
        "ZS5jc3MiPgo8L2hlYWQ+Cjxib2R5PgoKPGhlYWRlciBjbGFzcz0iZGVjay1oZWFkIj4KICA8ZGl2IGNsYXNzPSJicmFuZCI+CiAg"
        "ICA8c3BhbiBjbGFzcz0iYnJhbmQtbWFyayIgYXJpYS1oaWRkZW49InRydWUiPjwvc3Bhbj4KICAgIDxzcGFuIGNsYXNzPSJicmFu"
        "ZC1uYW1lIj5VTk1JWDwvc3Bhbj4KICAgIDxzcGFuIGNsYXNzPSJicmFuZC1zdWIiPmxvY2FsIHN0ZW0gc2VwYXJhdGlvbjwvc3Bh"
        "bj4KICA8L2Rpdj4KICA8ZGl2IGNsYXNzPSJyaWciIGlkPSJyaWciPgogICAgPHNwYW4gY2xhc3M9InJpZy1kb3QiIGFyaWEtaGlk"
        "ZGVuPSJ0cnVlIj48L3NwYW4+CiAgICA8c3BhbiBpZD0icmlnVGV4dCI+Y2hlY2tpbmcgaGFyZHdhcmXigKY8L3NwYW4+CiAgPC9k"
        "aXY+CjwvaGVhZGVyPgoKPG1haW4gY2xhc3M9ImRlY2siPgoKICA8IS0tIOKUgOKUgCBpbnRha2Ug4pSA4pSA4pSA4pSA4pSA4pSA"
        "4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA"
        "4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSAIC0tPgogIDxzZWN0aW9uIGNsYXNzPSJwYW5l"
        "bCBpbnRha2UiIGlkPSJpbnRha2UiPgogICAgPGRpdiBjbGFzcz0iZHJvcCIgaWQ9ImRyb3AiIHRhYmluZGV4PSIwIiByb2xlPSJi"
        "dXR0b24iIGFyaWEtbGFiZWw9IkNob29zZSBhbiBhdWRpbyBmaWxlIHRvIHNwbGl0Ij4KICAgICAgPGRpdiBjbGFzcz0iZHJvcC1p"
        "bm5lciI+CiAgICAgICAgPGRpdiBjbGFzcz0iZHJvcC1nbHlwaCIgYXJpYS1oaWRkZW49InRydWUiPgogICAgICAgICAgPHNwYW4+"
        "PC9zcGFuPjxzcGFuPjwvc3Bhbj48c3Bhbj48L3NwYW4+PHNwYW4+PC9zcGFuPjxzcGFuPjwvc3Bhbj4KICAgICAgICA8L2Rpdj4K"
        "ICAgICAgICA8cCBjbGFzcz0iZHJvcC1sZWFkIj5Ecm9wIGEgdHJhY2sgaGVyZTwvcD4KICAgICAgICA8cCBjbGFzcz0iZHJvcC1z"
        "dWIiPm9yIDxzcGFuIGNsYXNzPSJsaW5rIj5icm93c2UgeW91ciBmaWxlczwvc3Bhbj4g4oCUIG1wMywgd2F2LCBmbGFjLCBtNGEs"
        "IG9yIGFueSB2aWRlbzwvcD4KICAgICAgPC9kaXY+CiAgICAgIDxpbnB1dCB0eXBlPSJmaWxlIiBpZD0iZmlsZSIgYWNjZXB0PSJh"
        "dWRpby8qLHZpZGVvLyoiIGhpZGRlbj4KICAgIDwvZGl2PgoKICAgIDxkaXYgY2xhc3M9InNldHRpbmdzIj4KICAgICAgPGRpdiBj"
        "bGFzcz0ic2V0dGluZyI+CiAgICAgICAgPGxhYmVsIGNsYXNzPSJzaWxrIiBmb3I9Im1vZGVsIj5Nb2RlbDwvbGFiZWw+CiAgICAg"
        "ICAgPHNlbGVjdCBpZD0ibW9kZWwiPjwvc2VsZWN0PgogICAgICAgIDxwIGNsYXNzPSJoaW50IiBpZD0ibW9kZWxIaW50Ij48L3A+"
        "CiAgICAgIDwvZGl2PgogICAgICA8ZGl2IGNsYXNzPSJzZXR0aW5nIj4KICAgICAgICA8bGFiZWwgY2xhc3M9InNpbGsiIGZvcj0i"
        "cGFzc2VzIj5FeHRyYSBwYXNzZXM8L2xhYmVsPgogICAgICAgIDxzZWxlY3QgaWQ9InBhc3NlcyI+CiAgICAgICAgICA8b3B0aW9u"
        "IHZhbHVlPSIwIiBzZWxlY3RlZD5Ob25lIOKAlCBmYXN0ZXN0PC9vcHRpb24+CiAgICAgICAgICA8b3B0aW9uIHZhbHVlPSIxIj4x"
        "IOKAlCBzbGlnaHRseSBjbGVhbmVyPC9vcHRpb24+CiAgICAgICAgICA8b3B0aW9uIHZhbHVlPSIyIj4yIOKAlCBjbGVhbmVzdCwg"
        "M8OXIHRoZSB0aW1lPC9vcHRpb24+CiAgICAgICAgPC9zZWxlY3Q+CiAgICAgICAgPHAgY2xhc3M9ImhpbnQiPlJ1bnMgdGhlIHRy"
        "YWNrIHRocm91Z2ggYWdhaW4gYXQgYSBzaGlmdGVkIG9mZnNldCBhbmQgYXZlcmFnZXMgdGhlIHJlc3VsdC48L3A+CiAgICAgIDwv"
        "ZGl2PgogICAgPC9kaXY+CiAgPC9zZWN0aW9uPgoKICA8IS0tIOKUgOKUgCByZW5kZXIgcHJvZ3Jlc3Mg4pSA4pSA4pSA4pSA4pSA"
        "4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA"
        "4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSAIC0tPgogIDxzZWN0aW9uIGNsYXNzPSJwYW5lbCB3b3JraW5nIiBpZD0id29ya2luZyIg"
        "aGlkZGVuPgogICAgPGRpdiBjbGFzcz0id29ya2luZy10b3AiPgogICAgICA8ZGl2PgogICAgICAgIDxwIGNsYXNzPSJzaWxrIj5O"
        "b3cgcmVuZGVyaW5nPC9wPgogICAgICAgIDxoMiBpZD0id29ya1RpdGxlIj7igJQ8L2gyPgogICAgICA8L2Rpdj4KICAgICAgPGJ1"
        "dHRvbiBjbGFzcz0iYnRuIGdob3N0IiBpZD0iY2FuY2VsQnRuIj5TdG9wPC9idXR0b24+CiAgICA8L2Rpdj4KICAgIDxkaXYgY2xh"
        "c3M9InRhcGUiIHJvbGU9InByb2dyZXNzYmFyIiBhcmlhLXZhbHVlbWluPSIwIiBhcmlhLXZhbHVlbWF4PSIxMDAiIGlkPSJ0YXBl"
        "Ij4KICAgICAgPGRpdiBjbGFzcz0idGFwZS1maWxsIiBpZD0idGFwZUZpbGwiPjwvZGl2PgogICAgPC9kaXY+CiAgICA8ZGl2IGNs"
        "YXNzPSJ3b3JraW5nLWZvb3QiPgogICAgICA8c3BhbiBpZD0id29ya1N0YWdlIiBjbGFzcz0ibW9ubyI+V2FpdGluZzwvc3Bhbj4K"
        "ICAgICAgPHNwYW4gaWQ9IndvcmtQY3QiIGNsYXNzPSJtb25vIj4wJTwvc3Bhbj4KICAgIDwvZGl2PgogIDwvc2VjdGlvbj4KCiAg"
        "PCEtLSDilIDilIAgY29uc29sZSDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDi"
        "lIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDi"
        "lIDilIDilIAgLS0+CiAgPHNlY3Rpb24gY2xhc3M9ImNvbnNvbGUiIGlkPSJjb25zb2xlIiBoaWRkZW4+CgogICAgPGRpdiBjbGFz"
        "cz0icGFuZWwgdHJhbnNwb3J0Ij4KICAgICAgPGRpdiBjbGFzcz0idHJhbnNwb3J0LXJvdyI+CiAgICAgICAgPGJ1dHRvbiBjbGFz"
        "cz0icGxheSIgaWQ9InBsYXlCdG4iIGFyaWEtbGFiZWw9IlBsYXkiPgogICAgICAgICAgPHN2ZyB2aWV3Qm94PSIwIDAgMjQgMjQi"
        "IGNsYXNzPSJpY28tcGxheSIgYXJpYS1oaWRkZW49InRydWUiPjxwYXRoIGQ9Ik04IDUuNXYxM2wxMS02LjV6Ii8+PC9zdmc+CiAg"
        "ICAgICAgICA8c3ZnIHZpZXdCb3g9IjAgMCAyNCAyNCIgY2xhc3M9Imljby1wYXVzZSIgYXJpYS1oaWRkZW49InRydWUiPjxwYXRo"
        "IGQ9Ik03LjUgNWgzLjJ2MTRINy41ek0xMy4zIDVoMy4ydjE0aC0zLjJ6Ii8+PC9zdmc+CiAgICAgICAgPC9idXR0b24+CiAgICAg"
        "ICAgPGRpdiBjbGFzcz0iY2xvY2siPgogICAgICAgICAgPHNwYW4gY2xhc3M9Im1vbm8gdGltZSIgaWQ9InRpbWVOb3ciPjA6MDA8"
        "L3NwYW4+CiAgICAgICAgICA8c3BhbiBjbGFzcz0ibW9ubyB0aW1lIGRpbSIgaWQ9InRpbWVFbmQiPjA6MDA8L3NwYW4+CiAgICAg"
        "ICAgPC9kaXY+CiAgICAgICAgPGRpdiBjbGFzcz0idGltZWxpbmUiPgogICAgICAgICAgPGRpdiBjbGFzcz0id2F2ZS13cmFwIj4K"
        "ICAgICAgICAgICAgPGNhbnZhcyBpZD0id2F2ZSIgY2xhc3M9IndhdmUiPjwvY2FudmFzPgogICAgICAgICAgICA8ZGl2IGNsYXNz"
        "PSJsb29wLXJlZ2lvbiIgaWQ9Imxvb3BSZWdpb24iIGhpZGRlbj48L2Rpdj4KICAgICAgICAgICAgPGRpdiBjbGFzcz0icGxheWhl"
        "YWQiIGlkPSJwbGF5aGVhZCI+PC9kaXY+CiAgICAgICAgICA8L2Rpdj4KICAgICAgICAgIDxkaXYgY2xhc3M9ImxhbmUiIGlkPSJs"
        "YW5lIiBhcmlhLWxhYmVsPSJTZWN0aW9ucyI+PC9kaXY+CiAgICAgICAgPC9kaXY+CiAgICAgICAgPGJ1dHRvbiBjbGFzcz0idG9n"
        "IiBpZD0ibG9vcEJ0biIgYXJpYS1wcmVzc2VkPSJmYWxzZSI+TG9vcDwvYnV0dG9uPgogICAgICAgIDxkaXYgY2xhc3M9InRyYWNr"
        "LWlkIj4KICAgICAgICAgIDxzcGFuIGNsYXNzPSJzaWxrIj5UcmFjazwvc3Bhbj4KICAgICAgICAgIDxzcGFuIGlkPSJ0cmFja1Rp"
        "dGxlIj7igJQ8L3NwYW4+CiAgICAgICAgPC9kaXY+CiAgICAgIDwvZGl2PgogICAgPC9kaXY+CgogICAgPGRpdiBjbGFzcz0icGFu"
        "ZWwgZWRpdGJhciIgaWQ9ImVkaXRiYXIiPgogICAgICA8ZGl2IGNsYXNzPSJlZGl0LXdoYXQiPgogICAgICAgIDxzcGFuIGNsYXNz"
        "PSJzaWxrIiBpZD0iZWRpdEtpY2tlciI+QWRqdXN0aW5nPC9zcGFuPgogICAgICAgIDxzcGFuIGNsYXNzPSJlZGl0LW5hbWUiIGlk"
        "PSJlZGl0TmFtZSI+dGhlIHdob2xlIHRyYWNrPC9zcGFuPgogICAgICA8L2Rpdj4KICAgICAgPGRpdiBjbGFzcz0iZWRpdC10b29s"
        "cyIgaWQ9ImVkaXRUb29scyI+PC9kaXY+CiAgICA8L2Rpdj4KCiAgICA8ZGl2IGNsYXNzPSJzdHJpcHMtc2Nyb2xsIj4KICAgICAg"
        "PGRpdiBjbGFzcz0ic3RyaXBzIiBpZD0ic3RyaXBzIj48L2Rpdj4KICAgIDwvZGl2PgoKICAgIDxkaXYgY2xhc3M9InBhbmVsIGV4"
        "cG9ydHMiPgogICAgICA8ZGl2IGNsYXNzPSJleHBvcnQtbGVmdCI+CiAgICAgICAgPHNwYW4gY2xhc3M9InNpbGsiPkV4cG9ydCBh"
        "czwvc3Bhbj4KICAgICAgICA8ZGl2IGNsYXNzPSJzZWdtZW50ZWQiIGlkPSJmb3JtYXQiIHJvbGU9InJhZGlvZ3JvdXAiIGFyaWEt"
        "bGFiZWw9IkV4cG9ydCBmb3JtYXQiPgogICAgICAgICAgPGJ1dHRvbiByb2xlPSJyYWRpbyIgYXJpYS1jaGVja2VkPSJ0cnVlIiBk"
        "YXRhLWZtdD0id2F2IiBjbGFzcz0ib24iPldBVjwvYnV0dG9uPgogICAgICAgICAgPGJ1dHRvbiByb2xlPSJyYWRpbyIgYXJpYS1j"
        "aGVja2VkPSJmYWxzZSIgZGF0YS1mbXQ9Im1wMyI+TVAzPC9idXR0b24+CiAgICAgICAgICA8YnV0dG9uIHJvbGU9InJhZGlvIiBh"
        "cmlhLWNoZWNrZWQ9ImZhbHNlIiBkYXRhLWZtdD0iZmxhYyI+RkxBQzwvYnV0dG9uPgogICAgICAgIDwvZGl2PgogICAgICA8L2Rp"
        "dj4KICAgICAgPGRpdiBjbGFzcz0iZXhwb3J0LXJpZ2h0Ij4KICAgICAgICA8YnV0dG9uIGNsYXNzPSJidG4iIGlkPSJleHBvcnRN"
        "aXhCdG4iPkV4cG9ydCB3aGF0IEknbSBoZWFyaW5nPC9idXR0b24+CiAgICAgICAgPGJ1dHRvbiBjbGFzcz0iYnRuIGdob3N0IiBp"
        "ZD0iemlwQnRuIj5BbGwgc3RlbXMgKC56aXApPC9idXR0b24+CiAgICAgICAgPGJ1dHRvbiBjbGFzcz0iYnRuIGdob3N0IiBpZD0i"
        "Zm9sZGVyQnRuIj5PcGVuIGZvbGRlcjwvYnV0dG9uPgogICAgICA8L2Rpdj4KICAgIDwvZGl2PgogIDwvc2VjdGlvbj4KCiAgPCEt"
        "LSDilIDilIAgcmVjZW50cyDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDi"
        "lIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDi"
        "lIDilIAgLS0+CiAgPHNlY3Rpb24gY2xhc3M9InJlY2VudHMiIGlkPSJyZWNlbnRzIiBoaWRkZW4+CiAgICA8cCBjbGFzcz0ic2ls"
        "ayI+UmVjZW50PC9wPgogICAgPGRpdiBjbGFzcz0iY2hpcHMiIGlkPSJjaGlwcyI+PC9kaXY+CiAgPC9zZWN0aW9uPgoKPC9tYWlu"
        "PgoKPGRpdiBjbGFzcz0idG9hc3QiIGlkPSJ0b2FzdCIgaGlkZGVuPjwvZGl2PgoKPGZvb3RlciBjbGFzcz0iZGVjay1mb290Ij4K"
        "ICA8c3Bhbj5FdmVyeXRoaW5nIHJ1bnMgb24gdGhpcyBtYWNoaW5lLiBOb3RoaW5nIGlzIHVwbG9hZGVkLjwvc3Bhbj4KICA8c3Bh"
        "biBjbGFzcz0ibW9ubyBkaW0iIGlkPSJvdXRQYXRoIj48L3NwYW4+CjwvZm9vdGVyPgoKPHNjcmlwdCBzcmM9ImFwcC5qcyI+PC9z"
        "Y3JpcHQ+CjwvYm9keT4KPC9odG1sPgo="
    ,
    "style.css":
        "Lyog4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA"
        "4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA"
        "4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSACiAgIFVOTUlYIOKAlCB0aGUgbG9vayBpcyBhIHNtYWxsIHN0dWRp"
        "byBjb25zb2xlOiBncmFwaGl0ZSBjaGFzc2lzLAogICBzaWxrc2NyZWVuZWQgbGFiZWxzLCBwYXRjaC1jYWJsZSBjb2xvdXIgY29k"
        "aW5nIHBlciBzdGVtLgogICDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDi"
        "lIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDi"
        "lIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIAgKi8KCjpyb290ewogIC0tY2hhc3Npczoj"
        "MTQxNjFhOwogIC0tcGFuZWw6IzFkMjEyODsKICAtLXBhbmVsLWhpOiMyNDI5MzI7CiAgLS1yYWlsOiMyYjMyM2M7CiAgLS1lZGdl"
        "OiMwZDBmMTI7CiAgLS1pbms6I2VjZWFlNDsKICAtLWRpbTojODI4Yjk2OwogIC0tZGltbWVyOiM1YjY0NzA7CiAgLS1zaWduYWw6"
        "I2ZmYjQ1NDsKICAtLXNvbG86I2ZmNWE0NTsKICAtLW9rOiM1ZmQzYjQ7CgogIC0tYy12b2NhbHM6I2ZmYzQ0ZDsKICAtLWMtZHJ1"
        "bXM6I2ZmNmI1YTsKICAtLWMtYmFzczojN2M5YmZmOwogIC0tYy1ndWl0YXI6I2M1OGJmZjsKICAtLWMtcGlhbm86I2Y0OWFjMjsK"
        "ICAtLWMtb3RoZXI6IzVmZDNiNDsKICAtLWMtaW5zdHJ1bWVudGFsOiM5YWE1YjE7CgogIC0tc2lsazogIkJhcmxvdyBDb25kZW5z"
        "ZWQiLCAiUm9ib3RvIENvbmRlbnNlZCIsICJBcmlhbCBOYXJyb3ciLCBzeXN0ZW0tdWksIHNhbnMtc2VyaWY7CiAgLS1ib2R5OiAi"
        "SW50ZXIiLCBzeXN0ZW0tdWksIC1hcHBsZS1zeXN0ZW0sICJTZWdvZSBVSSIsIHNhbnMtc2VyaWY7CiAgLS1tb25vOiAiSmV0QnJh"
        "aW5zIE1vbm8iLCB1aS1tb25vc3BhY2UsICJTRiBNb25vIiwgTWVubG8sIENvbnNvbGFzLCBtb25vc3BhY2U7CgogIC0tcjo2cHg7"
        "Cn0KCip7Ym94LXNpemluZzpib3JkZXItYm94fQpbaGlkZGVuXXtkaXNwbGF5Om5vbmUgIWltcG9ydGFudH0KCmh0bWwsYm9keXto"
        "ZWlnaHQ6MTAwJX0KCmJvZHl7CiAgbWFyZ2luOjA7CiAgYmFja2dyb3VuZDoKICAgIHJhZGlhbC1ncmFkaWVudCgxMjAlIDkwJSBh"
        "dCA1MCUgLTEwJSwgIzFiMWYyNiAwJSwgdmFyKC0tY2hhc3NpcykgNjAlKSwKICAgIHZhcigtLWNoYXNzaXMpOwogIGNvbG9yOnZh"
        "cigtLWluayk7CiAgZm9udC1mYW1pbHk6dmFyKC0tYm9keSk7CiAgZm9udC1zaXplOjE1cHg7CiAgbGluZS1oZWlnaHQ6MS41Owog"
        "IC13ZWJraXQtZm9udC1zbW9vdGhpbmc6YW50aWFsaWFzZWQ7CiAgZGlzcGxheTpmbGV4OwogIGZsZXgtZGlyZWN0aW9uOmNvbHVt"
        "bjsKfQoKLyogc2lsa3NjcmVlbiBsYWJlbCDigJQgdGhlIGNvbnNvbGUncyB2b2ljZSAqLwouc2lsa3sKICBmb250LWZhbWlseTp2"
        "YXIoLS1zaWxrKTsKICBmb250LXdlaWdodDo2MDA7CiAgZm9udC1zaXplOjEycHg7CiAgbGV0dGVyLXNwYWNpbmc6LjE2ZW07CiAg"
        "dGV4dC10cmFuc2Zvcm06dXBwZXJjYXNlOwogIGNvbG9yOnZhcigtLWRpbSk7CiAgZGlzcGxheTpibG9jazsKfQoKLm1vbm97Zm9u"
        "dC1mYW1pbHk6dmFyKC0tbW9ubyk7Zm9udC1zaXplOjEyLjVweDtmb250LXZhcmlhbnQtbnVtZXJpYzp0YWJ1bGFyLW51bXN9Ci5k"
        "aW17Y29sb3I6dmFyKC0tZGltKX0KLmxpbmt7Y29sb3I6dmFyKC0tc2lnbmFsKTt0ZXh0LWRlY29yYXRpb246dW5kZXJsaW5lO3Rl"
        "eHQtdW5kZXJsaW5lLW9mZnNldDozcHh9CgovKiDilIDilIAgaGVhZGVyIOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKU"
        "gOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKU"
        "gOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgCAqLwouZGVjay1oZWFkewogIGRpc3BsYXk6ZmxleDthbGlnbi1pdGVt"
        "czpjZW50ZXI7anVzdGlmeS1jb250ZW50OnNwYWNlLWJldHdlZW47CiAgZ2FwOjE2cHg7cGFkZGluZzoxNnB4IDI0cHg7CiAgYm9y"
        "ZGVyLWJvdHRvbToxcHggc29saWQgdmFyKC0tZWRnZSk7CiAgYmFja2dyb3VuZDpsaW5lYXItZ3JhZGllbnQoMTgwZGVnLCMxYTFl"
        "MjQsIzE1MTgxZCk7Cn0KLmJyYW5ke2Rpc3BsYXk6ZmxleDthbGlnbi1pdGVtczpiYXNlbGluZTtnYXA6MTJweH0KLmJyYW5kLW1h"
        "cmt7CiAgd2lkdGg6MTFweDtoZWlnaHQ6MTFweDtib3JkZXItcmFkaXVzOjJweDsKICBiYWNrZ3JvdW5kOnZhcigtLXNpZ25hbCk7"
        "CiAgYm94LXNoYWRvdzowIDAgMTJweCByZ2JhKDI1NSwxODAsODQsLjU1KTsKICBhbGlnbi1zZWxmOmNlbnRlcjsKfQouYnJhbmQt"
        "bmFtZXsKICBmb250LWZhbWlseTp2YXIoLS1zaWxrKTtmb250LXdlaWdodDo3MDA7Zm9udC1zaXplOjIzcHg7CiAgbGV0dGVyLXNw"
        "YWNpbmc6LjI4ZW07dGV4dC10cmFuc2Zvcm06dXBwZXJjYXNlOwp9Ci5icmFuZC1zdWJ7Zm9udC1zaXplOjEyLjVweDtjb2xvcjp2"
        "YXIoLS1kaW1tZXIpfQoucmlnewogIGRpc3BsYXk6ZmxleDthbGlnbi1pdGVtczpjZW50ZXI7Z2FwOjhweDsKICBmb250LWZhbWls"
        "eTp2YXIoLS1tb25vKTtmb250LXNpemU6MTJweDtjb2xvcjp2YXIoLS1kaW0pOwogIGJvcmRlcjoxcHggc29saWQgdmFyKC0tcmFp"
        "bCk7Ym9yZGVyLXJhZGl1czoxMDBweDsKICBwYWRkaW5nOjVweCAxM3B4O2JhY2tncm91bmQ6IzE4MWIyMTsKfQoucmlnLWRvdHt3"
        "aWR0aDo3cHg7aGVpZ2h0OjdweDtib3JkZXItcmFkaXVzOjUwJTtiYWNrZ3JvdW5kOnZhcigtLWRpbW1lcil9Ci5yaWcubGl2ZSAu"
        "cmlnLWRvdHtiYWNrZ3JvdW5kOnZhcigtLW9rKTtib3gtc2hhZG93OjAgMCA4cHggcmdiYSg5NSwyMTEsMTgwLC43KX0KCi8qIOKU"
        "gOKUgCBsYXlvdXQg4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA"
        "4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA"
        "4pSAICovCi5kZWNrewogIGZsZXg6MTt3aWR0aDoxMDAlO21heC13aWR0aDoxMjQwcHg7bWFyZ2luOjAgYXV0bzsKICBwYWRkaW5n"
        "OjI2cHggMjRweCA0MHB4OwogIGRpc3BsYXk6ZmxleDtmbGV4LWRpcmVjdGlvbjpjb2x1bW47Z2FwOjIwcHg7Cn0KLnBhbmVsewog"
        "IGJhY2tncm91bmQ6bGluZWFyLWdyYWRpZW50KDE4MGRlZyx2YXIoLS1wYW5lbC1oaSksdmFyKC0tcGFuZWwpKTsKICBib3JkZXI6"
        "MXB4IHNvbGlkIHZhcigtLXJhaWwpOwogIGJvcmRlci1yYWRpdXM6dmFyKC0tcik7CiAgYm94LXNoYWRvdzowIDFweCAwIHJnYmEo"
        "MjU1LDI1NSwyNTUsLjA0KSBpbnNldCwgMCAxMnB4IDMwcHggLTIycHggIzAwMDsKfQoKLyog4pSA4pSAIGludGFrZSDilIDilIDi"
        "lIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDi"
        "lIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIAgKi8KLmludGFrZXtwYWRk"
        "aW5nOjIycHg7ZGlzcGxheTpncmlkO2dyaWQtdGVtcGxhdGUtY29sdW1uczoxZnIgMzAwcHg7Z2FwOjIycHh9CgouZHJvcHsKICBi"
        "b3JkZXI6MS41cHggZGFzaGVkIHZhcigtLXJhaWwpOwogIGJvcmRlci1yYWRpdXM6dmFyKC0tcik7CiAgYmFja2dyb3VuZDojMTkx"
        "ZDIzOwogIG1pbi1oZWlnaHQ6MjMwcHg7CiAgZGlzcGxheTpncmlkO3BsYWNlLWl0ZW1zOmNlbnRlcjsKICBjdXJzb3I6cG9pbnRl"
        "cjsKICB0cmFuc2l0aW9uOmJvcmRlci1jb2xvciAuMThzLCBiYWNrZ3JvdW5kIC4xOHM7Cn0KLmRyb3A6aG92ZXIsLmRyb3A6Zm9j"
        "dXMtdmlzaWJsZXtib3JkZXItY29sb3I6dmFyKC0tc2lnbmFsKTtiYWNrZ3JvdW5kOiMxYzIwMjc7b3V0bGluZTpub25lfQouZHJv"
        "cC5ob3R7Ym9yZGVyLWNvbG9yOnZhcigtLXNpZ25hbCk7YmFja2dyb3VuZDojMjAyNDJiO2JvcmRlci1zdHlsZTpzb2xpZH0KLmRy"
        "b3AtaW5uZXJ7dGV4dC1hbGlnbjpjZW50ZXI7cGFkZGluZzoyNHB4fQouZHJvcC1sZWFke2ZvbnQtZmFtaWx5OnZhcigtLXNpbGsp"
        "O2ZvbnQtc2l6ZToyN3B4O2ZvbnQtd2VpZ2h0OjYwMDtsZXR0ZXItc3BhY2luZzouMDVlbTttYXJnaW46MTZweCAwIDRweH0KLmRy"
        "b3Atc3Vie21hcmdpbjowO2NvbG9yOnZhcigtLWRpbSk7Zm9udC1zaXplOjEzLjVweH0KCi8qIGZpdmUgYmFycyA9IHRoZSBmaXZl"
        "IHRoaW5ncyBpdCBwdWxscyBhcGFydCAqLwouZHJvcC1nbHlwaHtkaXNwbGF5OmZsZXg7YWxpZ24taXRlbXM6ZmxleC1lbmQ7anVz"
        "dGlmeS1jb250ZW50OmNlbnRlcjtnYXA6NXB4O2hlaWdodDo0NHB4fQouZHJvcC1nbHlwaCBzcGFue3dpZHRoOjVweDtib3JkZXIt"
        "cmFkaXVzOjJweDtiYWNrZ3JvdW5kOnZhcigtLXJhaWwpO2FuaW1hdGlvbjpib2IgMS45cyBlYXNlLWluLW91dCBpbmZpbml0ZX0K"
        "LmRyb3AtZ2x5cGggc3BhbjpudGgtY2hpbGQoMSl7aGVpZ2h0OjE2cHg7YmFja2dyb3VuZDp2YXIoLS1jLXZvY2Fscyk7YW5pbWF0"
        "aW9uLWRlbGF5OjBzfQouZHJvcC1nbHlwaCBzcGFuOm50aC1jaGlsZCgyKXtoZWlnaHQ6MzBweDtiYWNrZ3JvdW5kOnZhcigtLWMt"
        "ZHJ1bXMpO2FuaW1hdGlvbi1kZWxheTouMTRzfQouZHJvcC1nbHlwaCBzcGFuOm50aC1jaGlsZCgzKXtoZWlnaHQ6NDRweDtiYWNr"
        "Z3JvdW5kOnZhcigtLWMtYmFzcyk7YW5pbWF0aW9uLWRlbGF5Oi4yOHN9Ci5kcm9wLWdseXBoIHNwYW46bnRoLWNoaWxkKDQpe2hl"
        "aWdodDoyNnB4O2JhY2tncm91bmQ6dmFyKC0tYy1vdGhlcik7YW5pbWF0aW9uLWRlbGF5Oi40MnN9Ci5kcm9wLWdseXBoIHNwYW46"
        "bnRoLWNoaWxkKDUpe2hlaWdodDoxM3B4O2JhY2tncm91bmQ6dmFyKC0tYy1pbnN0cnVtZW50YWwpO2FuaW1hdGlvbi1kZWxheTou"
        "NTZzfQpAa2V5ZnJhbWVzIGJvYnswJSwxMDAle3RyYW5zZm9ybTpzY2FsZVkoMSl9NTAle3RyYW5zZm9ybTpzY2FsZVkoLjQ1KX19"
        "Cgouc2V0dGluZ3N7ZGlzcGxheTpmbGV4O2ZsZXgtZGlyZWN0aW9uOmNvbHVtbjtnYXA6MThweH0KLnNldHRpbmcgc2VsZWN0ewog"
        "IHdpZHRoOjEwMCU7bWFyZ2luLXRvcDo3cHg7CiAgYmFja2dyb3VuZDojMTYxYTFmO2NvbG9yOnZhcigtLWluayk7CiAgYm9yZGVy"
        "OjFweCBzb2xpZCB2YXIoLS1yYWlsKTtib3JkZXItcmFkaXVzOjRweDsKICBwYWRkaW5nOjlweCAxMHB4O2ZvbnQtZmFtaWx5OnZh"
        "cigtLWJvZHkpO2ZvbnQtc2l6ZToxMy41cHg7Cn0KLnNldHRpbmcgc2VsZWN0OmZvY3VzLXZpc2libGV7b3V0bGluZToycHggc29s"
        "aWQgdmFyKC0tc2lnbmFsKTtvdXRsaW5lLW9mZnNldDoxcHh9Ci5oaW50e21hcmdpbjo3cHggMCAwO2ZvbnQtc2l6ZToxMnB4O2Nv"
        "bG9yOnZhcigtLWRpbW1lcik7bGluZS1oZWlnaHQ6MS40NX0KCi8qIOKUgOKUgCByZW5kZXJpbmcg4pSA4pSA4pSA4pSA4pSA4pSA"
        "4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA"
        "4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSAICovCi53b3JraW5ne3BhZGRpbmc6MjBweCAyMnB4fQoud29y"
        "a2luZy10b3B7ZGlzcGxheTpmbGV4O2FsaWduLWl0ZW1zOmZsZXgtc3RhcnQ7anVzdGlmeS1jb250ZW50OnNwYWNlLWJldHdlZW47"
        "Z2FwOjE2cHh9Ci53b3JraW5nLXRvcCBoMnttYXJnaW46M3B4IDAgMDtmb250LXNpemU6MTlweDtmb250LXdlaWdodDo2MDB9Ci50"
        "YXBlewogIHBvc2l0aW9uOnJlbGF0aXZlO2hlaWdodDo5cHg7bWFyZ2luOjE4cHggMCAxMHB4OwogIGJhY2tncm91bmQ6IzEyMTUx"
        "YTtib3JkZXI6MXB4IHNvbGlkIHZhcigtLXJhaWwpO2JvcmRlci1yYWRpdXM6MTAwcHg7b3ZlcmZsb3c6aGlkZGVuOwp9Ci50YXBl"
        "LWZpbGx7CiAgaGVpZ2h0OjEwMCU7d2lkdGg6MCU7CiAgYmFja2dyb3VuZDpsaW5lYXItZ3JhZGllbnQoOTBkZWcsI2MyODAzYSx2"
        "YXIoLS1zaWduYWwpKTsKICB0cmFuc2l0aW9uOndpZHRoIC4zNXMgY3ViaWMtYmV6aWVyKC40LDAsLjIsMSk7Cn0KLndvcmtpbmct"
        "Zm9vdHtkaXNwbGF5OmZsZXg7anVzdGlmeS1jb250ZW50OnNwYWNlLWJldHdlZW47Y29sb3I6dmFyKC0tZGltKX0KCi8qIOKUgOKU"
        "gCB0cmFuc3BvcnQg4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA"
        "4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSAICovCi5j"
        "b25zb2xle2Rpc3BsYXk6ZmxleDtmbGV4LWRpcmVjdGlvbjpjb2x1bW47Z2FwOjE2cHh9Ci50cmFuc3BvcnR7cGFkZGluZzoxNHB4"
        "IDE4cHh9Ci50cmFuc3BvcnQtcm93e2Rpc3BsYXk6ZmxleDthbGlnbi1pdGVtczpjZW50ZXI7Z2FwOjE2cHh9CgoucGxheXsKICB3"
        "aWR0aDo0NnB4O2hlaWdodDo0NnB4O2ZsZXg6bm9uZTtib3JkZXItcmFkaXVzOjUwJTsKICBib3JkZXI6MXB4IHNvbGlkIHZhcigt"
        "LXJhaWwpO2JhY2tncm91bmQ6bGluZWFyLWdyYWRpZW50KDE4MGRlZywjMmMzMzNkLCMyMDI1MmMpOwogIGNvbG9yOnZhcigtLWlu"
        "ayk7ZGlzcGxheTpncmlkO3BsYWNlLWl0ZW1zOmNlbnRlcjtjdXJzb3I6cG9pbnRlcjsKICBib3gtc2hhZG93OjAgMnB4IDAgcmdi"
        "YSgwLDAsMCwuNSksIDAgMXB4IDAgcmdiYSgyNTUsMjU1LDI1NSwuMDYpIGluc2V0Owp9Ci5wbGF5OmhvdmVye2JvcmRlci1jb2xv"
        "cjp2YXIoLS1zaWduYWwpfQoucGxheTphY3RpdmV7dHJhbnNmb3JtOnRyYW5zbGF0ZVkoMXB4KX0KLnBsYXkgc3Zne3dpZHRoOjIy"
        "cHg7aGVpZ2h0OjIycHg7ZmlsbDpjdXJyZW50Q29sb3J9Ci5wbGF5IC5pY28tcGF1c2V7ZGlzcGxheTpub25lfQoucGxheS5wbGF5"
        "aW5nIC5pY28tcGxheXtkaXNwbGF5Om5vbmV9Ci5wbGF5LnBsYXlpbmcgLmljby1wYXVzZXtkaXNwbGF5OmJsb2NrfQoucGxheS5w"
        "bGF5aW5ne2NvbG9yOnZhcigtLXNpZ25hbCl9CgouY2xvY2t7ZGlzcGxheTpmbGV4O2ZsZXgtZGlyZWN0aW9uOmNvbHVtbjtsaW5l"
        "LWhlaWdodDoxLjI1O2ZsZXg6bm9uZTttaW4td2lkdGg6NTJweH0KLmNsb2NrIC50aW1le2ZvbnQtc2l6ZToxNHB4fQoKLndhdmUt"
        "d3JhcHsKICBwb3NpdGlvbjpyZWxhdGl2ZTtmbGV4OjE7aGVpZ2h0OjU2cHg7bWluLXdpZHRoOjEyMHB4OwogIGJhY2tncm91bmQ6"
        "IzEyMTUxYTtib3JkZXI6MXB4IHNvbGlkIHZhcigtLXJhaWwpO2JvcmRlci1yYWRpdXM6NHB4OwogIG92ZXJmbG93OmhpZGRlbjtj"
        "dXJzb3I6Y3Jvc3NoYWlyOwp9Ci53YXZle2Rpc3BsYXk6YmxvY2s7d2lkdGg6MTAwJTtoZWlnaHQ6MTAwJX0KLnBsYXloZWFkewog"
        "IHBvc2l0aW9uOmFic29sdXRlO3RvcDowO2JvdHRvbTowO3dpZHRoOjEuNXB4O2xlZnQ6MDsKICBiYWNrZ3JvdW5kOnZhcigtLXNp"
        "Z25hbCk7Ym94LXNoYWRvdzowIDAgOHB4IHJnYmEoMjU1LDE4MCw4NCwuOCk7CiAgcG9pbnRlci1ldmVudHM6bm9uZTsKfQoubG9v"
        "cC1yZWdpb257CiAgcG9zaXRpb246YWJzb2x1dGU7dG9wOjA7Ym90dG9tOjA7CiAgYmFja2dyb3VuZDpyZ2JhKDI1NSwxODAsODQs"
        "LjEzKTsKICBib3JkZXItbGVmdDoxcHggc29saWQgcmdiYSgyNTUsMTgwLDg0LC41KTsKICBib3JkZXItcmlnaHQ6MXB4IHNvbGlk"
        "IHJnYmEoMjU1LDE4MCw4NCwuNSk7CiAgcG9pbnRlci1ldmVudHM6bm9uZTsKfQoKLnRvZ3sKICBmb250LWZhbWlseTp2YXIoLS1z"
        "aWxrKTtmb250LXNpemU6MTIuNXB4O2xldHRlci1zcGFjaW5nOi4xNGVtO3RleHQtdHJhbnNmb3JtOnVwcGVyY2FzZTsKICBwYWRk"
        "aW5nOjlweCAxNHB4O2JvcmRlci1yYWRpdXM6NHB4O2N1cnNvcjpwb2ludGVyO2ZsZXg6bm9uZTsKICBiYWNrZ3JvdW5kOiMxODFj"
        "MjI7Ym9yZGVyOjFweCBzb2xpZCB2YXIoLS1yYWlsKTtjb2xvcjp2YXIoLS1kaW0pOwp9Ci50b2dbYXJpYS1wcmVzc2VkPSJ0cnVl"
        "Il17YmFja2dyb3VuZDpyZ2JhKDI1NSwxODAsODQsLjE0KTtib3JkZXItY29sb3I6dmFyKC0tc2lnbmFsKTtjb2xvcjp2YXIoLS1z"
        "aWduYWwpfQoKLnRyYWNrLWlke2ZsZXg6bm9uZTt0ZXh0LWFsaWduOnJpZ2h0O21heC13aWR0aDoxOTBweH0KLnRyYWNrLWlkIHNw"
        "YW46bGFzdC1jaGlsZHsKICBkaXNwbGF5OmJsb2NrO2ZvbnQtc2l6ZToxMy41cHg7d2hpdGUtc3BhY2U6bm93cmFwO292ZXJmbG93"
        "OmhpZGRlbjt0ZXh0LW92ZXJmbG93OmVsbGlwc2lzOwp9CgovKiDilIDilIAgY2hhbm5lbCBzdHJpcHMg4pSA4pSA4pSA4pSA4pSA"
        "4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA"
        "4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSAICovCi5zdHJpcHMtc2Nyb2xse292ZXJmbG93LXg6YXV0bztwYWRkaW5nLWJvdHRv"
        "bTo0cHh9Ci5zdHJpcHN7ZGlzcGxheTpmbGV4O2dhcDoxMnB4O21pbi13aWR0aDptaW4tY29udGVudH0KCi5zdHJpcHsKICAtLWM6"
        "dmFyKC0tZGltKTsKICBmbGV4OjEgMCAxMzJweDttYXgtd2lkdGg6MTkwcHg7CiAgYmFja2dyb3VuZDpsaW5lYXItZ3JhZGllbnQo"
        "MTgwZGVnLHZhcigtLXBhbmVsLWhpKSx2YXIoLS1wYW5lbCkpOwogIGJvcmRlcjoxcHggc29saWQgdmFyKC0tcmFpbCk7Ym9yZGVy"
        "LXRvcDoycHggc29saWQgdmFyKC0tYyk7CiAgYm9yZGVyLXJhZGl1czp2YXIoLS1yKTsKICBwYWRkaW5nOjEycHggMTJweCAxNHB4"
        "OwogIGRpc3BsYXk6ZmxleDtmbGV4LWRpcmVjdGlvbjpjb2x1bW47Z2FwOjExcHg7CiAgYm94LXNoYWRvdzowIDEycHggMzBweCAt"
        "MjJweCAjMDAwOwp9Ci5zdHJpcC5tdXRlZHtvcGFjaXR5Oi40Mn0KLnN0cmlwLmRlcml2ZWR7Ym9yZGVyLXN0eWxlOmRhc2hlZDti"
        "b3JkZXItdG9wLXN0eWxlOnNvbGlkfQoKLnN0cmlwLW5hbWV7CiAgZm9udC1mYW1pbHk6dmFyKC0tc2lsayk7Zm9udC13ZWlnaHQ6"
        "NzAwO2ZvbnQtc2l6ZToxNXB4OwogIGxldHRlci1zcGFjaW5nOi4xNWVtO3RleHQtdHJhbnNmb3JtOnVwcGVyY2FzZTtjb2xvcjp2"
        "YXIoLS1jKTsKfQouc3RyaXAtbm90ZXsKICBmb250LXNpemU6MTAuNXB4O2xpbmUtaGVpZ2h0OjEuMjU7aGVpZ2h0OjI2cHg7b3Zl"
        "cmZsb3c6aGlkZGVuOwogIGNvbG9yOnZhcigtLWRpbW1lcik7bWFyZ2luLXRvcDotOHB4O2xldHRlci1zcGFjaW5nOi4wMmVtOwp9"
        "CgovKiBtZXRlciArIGZhZGVyIHNpdCBzaWRlIGJ5IHNpZGUsIGxpa2UgYSByZWFsIHN0cmlwICovCi5zdHJpcC1ib2R5e2Rpc3Bs"
        "YXk6ZmxleDtnYXA6MTFweDtoZWlnaHQ6MTkwcHh9CgoubWV0ZXJ7CiAgd2lkdGg6MTRweDtmbGV4Om5vbmU7bWFyZ2luOjhweCAw"
        "OwogIGRpc3BsYXk6ZmxleDtmbGV4LWRpcmVjdGlvbjpjb2x1bW4tcmV2ZXJzZTtnYXA6MnB4OwogIGJhY2tncm91bmQ6IzEwMTMx"
        "Nztib3JkZXI6MXB4IHNvbGlkIHZhcigtLXJhaWwpO2JvcmRlci1yYWRpdXM6M3B4O3BhZGRpbmc6M3B4Owp9Ci5zZWd7ZmxleDox"
        "O2JvcmRlci1yYWRpdXM6MXB4O2JhY2tncm91bmQ6IzFiMjAyNzt0cmFuc2l0aW9uOmJhY2tncm91bmQgLjA1cyBsaW5lYXJ9Cgou"
        "ZmFkZXJ7cG9zaXRpb246cmVsYXRpdmU7ZmxleDoxO2Rpc3BsYXk6ZmxleDtqdXN0aWZ5LWNvbnRlbnQ6Y2VudGVyfQouZmFkZXIt"
        "c2xvdHsKICBwb3NpdGlvbjphYnNvbHV0ZTt0b3A6OHB4O2JvdHRvbTo4cHg7d2lkdGg6NnB4O2xlZnQ6NTAlO3RyYW5zZm9ybTp0"
        "cmFuc2xhdGVYKC01MCUpOwogIGJhY2tncm91bmQ6IzBmMTIxNjtib3JkZXItcmFkaXVzOjNweDsKICBib3gtc2hhZG93OjAgMXB4"
        "IDJweCByZ2JhKDAsMCwwLC44KSBpbnNldDsKfQouZmFkZXItZmlsbHtwb3NpdGlvbjphYnNvbHV0ZTtsZWZ0OjA7cmlnaHQ6MDti"
        "b3R0b206MDtiYWNrZ3JvdW5kOnZhcigtLWMpO29wYWNpdHk6LjQ1O2JvcmRlci1yYWRpdXM6M3B4fQouZmFkZXItY2FwewogIHBv"
        "c2l0aW9uOmFic29sdXRlO2xlZnQ6NTAlO3dpZHRoOjQwcHg7aGVpZ2h0OjE5cHg7bWFyZ2luLWxlZnQ6LTIwcHg7bWFyZ2luLXRv"
        "cDotOS41cHg7CiAgYmFja2dyb3VuZDpsaW5lYXItZ3JhZGllbnQoMTgwZGVnLCM0NTRkNTgsIzI3MmQzNSA0OCUsIzFiMjAyNyk7"
        "CiAgYm9yZGVyOjFweCBzb2xpZCAjMGMwZTExO2JvcmRlci1yYWRpdXM6M3B4O2N1cnNvcjpncmFiOwogIGJveC1zaGFkb3c6MCAy"
        "cHggNXB4IHJnYmEoMCwwLDAsLjYpLCAwIDFweCAwIHJnYmEoMjU1LDI1NSwyNTUsLjEzKSBpbnNldDsKfQouZmFkZXItY2FwOjph"
        "ZnRlcnsKICBjb250ZW50OiIiO3Bvc2l0aW9uOmFic29sdXRlO2xlZnQ6NXB4O3JpZ2h0OjVweDt0b3A6NTAlO2hlaWdodDoxLjVw"
        "eDttYXJnaW4tdG9wOi0uNzVweDsKICBiYWNrZ3JvdW5kOnZhcigtLWMpO2JvcmRlci1yYWRpdXM6MXB4O2JveC1zaGFkb3c6MCAw"
        "IDZweCB2YXIoLS1jKTsKfQouZmFkZXItY2FwOmFjdGl2ZXtjdXJzb3I6Z3JhYmJpbmd9Ci5mYWRlci1jYXA6Zm9jdXMtdmlzaWJs"
        "ZXtvdXRsaW5lOjJweCBzb2xpZCB2YXIoLS1zaWduYWwpO291dGxpbmUtb2Zmc2V0OjJweH0KLmZhZGVyLXNjYWxlewogIHBvc2l0"
        "aW9uOmFic29sdXRlO3JpZ2h0OjA7dG9wOjhweDtib3R0b206OHB4O3dpZHRoOjI0cHg7CiAgZm9udC1mYW1pbHk6dmFyKC0tbW9u"
        "byk7Zm9udC1zaXplOjguNXB4O2NvbG9yOnZhcigtLWRpbW1lcik7CiAgcG9pbnRlci1ldmVudHM6bm9uZTsKfQouZmFkZXItc2Nh"
        "bGUgc3BhbnsKICBwb3NpdGlvbjphYnNvbHV0ZTtyaWdodDowO3RyYW5zZm9ybTp0cmFuc2xhdGVZKDUwJSk7CiAgd2hpdGUtc3Bh"
        "Y2U6bm93cmFwOwp9Ci5mYWRlci1zY2FsZSBzcGFuOjpiZWZvcmV7CiAgY29udGVudDoiIjtwb3NpdGlvbjphYnNvbHV0ZTtyaWdo"
        "dDoxMDAlO3RvcDo1MCU7CiAgd2lkdGg6NXB4O2hlaWdodDoxcHg7bWFyZ2luLXJpZ2h0OjNweDtiYWNrZ3JvdW5kOnZhcigtLXJh"
        "aWwpOwp9Cgouc3RyaXAtcmVhZHtkaXNwbGF5OmZsZXg7anVzdGlmeS1jb250ZW50OnNwYWNlLWJldHdlZW47YWxpZ24taXRlbXM6"
        "YmFzZWxpbmV9Ci5zdHJpcC1yZWFkIC5kYntmb250LWZhbWlseTp2YXIoLS1tb25vKTtmb250LXNpemU6MTJweDtjb2xvcjp2YXIo"
        "LS1pbmspfQoKLnN0cmlwLWJ0bnN7ZGlzcGxheTpmbGV4O2dhcDo2cHh9Ci5taW5pewogIGZsZXg6MTtmb250LWZhbWlseTp2YXIo"
        "LS1zaWxrKTtmb250LXdlaWdodDo3MDA7Zm9udC1zaXplOjEycHg7bGV0dGVyLXNwYWNpbmc6LjEyZW07CiAgcGFkZGluZzo3cHgg"
        "MDtib3JkZXItcmFkaXVzOjNweDtjdXJzb3I6cG9pbnRlcjsKICBiYWNrZ3JvdW5kOiMxNjFhMWY7Ym9yZGVyOjFweCBzb2xpZCB2"
        "YXIoLS1yYWlsKTtjb2xvcjp2YXIoLS1kaW0pOwp9Ci5taW5pOmhvdmVye2NvbG9yOnZhcigtLWluayl9Ci5taW5pLm9uW2RhdGEt"
        "cm9sZT0ibXV0ZSJde2JhY2tncm91bmQ6cmdiYSgxMzAsMTM5LDE1MCwuMik7Ym9yZGVyLWNvbG9yOnZhcigtLWRpbSk7Y29sb3I6"
        "dmFyKC0taW5rKX0KLm1pbmkub25bZGF0YS1yb2xlPSJzb2xvIl17YmFja2dyb3VuZDpyZ2JhKDI1NSw5MCw2OSwuMTgpO2JvcmRl"
        "ci1jb2xvcjp2YXIoLS1zb2xvKTtjb2xvcjp2YXIoLS1zb2xvKX0KLm1pbmkuZ3JhYnsKICBmbGV4Om5vbmU7d2lkdGg6MzRweDtk"
        "aXNwbGF5OmdyaWQ7cGxhY2UtaXRlbXM6Y2VudGVyO3BhZGRpbmc6MDsKfQoubWluaS5ncmFiIHN2Z3t3aWR0aDoxNHB4O2hlaWdo"
        "dDoxNHB4O2ZpbGw6Y3VycmVudENvbG9yfQoKLyog4pSA4pSAIGV4cG9ydHMg4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA"
        "4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA"
        "4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSAICovCi5leHBvcnRzewogIHBhZGRpbmc6MTRweCAxOHB4O2Rpc3BsYXk6"
        "ZmxleDthbGlnbi1pdGVtczpjZW50ZXI7anVzdGlmeS1jb250ZW50OnNwYWNlLWJldHdlZW47CiAgZ2FwOjE2cHg7ZmxleC13cmFw"
        "OndyYXA7Cn0KLmV4cG9ydC1sZWZ0e2Rpc3BsYXk6ZmxleDthbGlnbi1pdGVtczpjZW50ZXI7Z2FwOjEycHh9Ci5leHBvcnQtcmln"
        "aHR7ZGlzcGxheTpmbGV4O2dhcDo5cHg7ZmxleC13cmFwOndyYXB9Cgouc2VnbWVudGVke2Rpc3BsYXk6ZmxleDtib3JkZXI6MXB4"
        "IHNvbGlkIHZhcigtLXJhaWwpO2JvcmRlci1yYWRpdXM6NHB4O292ZXJmbG93OmhpZGRlbn0KLnNlZ21lbnRlZCBidXR0b257CiAg"
        "Zm9udC1mYW1pbHk6dmFyKC0tc2lsayk7Zm9udC1zaXplOjEyLjVweDtsZXR0ZXItc3BhY2luZzouMTJlbTsKICBwYWRkaW5nOjhw"
        "eCAxNHB4O2JhY2tncm91bmQ6IzE2MWExZjtib3JkZXI6MDtib3JkZXItcmlnaHQ6MXB4IHNvbGlkIHZhcigtLXJhaWwpOwogIGNv"
        "bG9yOnZhcigtLWRpbSk7Y3Vyc29yOnBvaW50ZXI7Cn0KLnNlZ21lbnRlZCBidXR0b246bGFzdC1jaGlsZHtib3JkZXItcmlnaHQ6"
        "MH0KLnNlZ21lbnRlZCBidXR0b24ub257YmFja2dyb3VuZDpyZ2JhKDI1NSwxODAsODQsLjE1KTtjb2xvcjp2YXIoLS1zaWduYWwp"
        "fQoKLmJ0bnsKICBmb250LWZhbWlseTp2YXIoLS1ib2R5KTtmb250LXNpemU6MTMuNXB4O2ZvbnQtd2VpZ2h0OjUwMDsKICBwYWRk"
        "aW5nOjEwcHggMTdweDtib3JkZXItcmFkaXVzOjRweDtjdXJzb3I6cG9pbnRlcjsKICBiYWNrZ3JvdW5kOnZhcigtLXNpZ25hbCk7"
        "Ym9yZGVyOjFweCBzb2xpZCAjZDk5NDM2O2NvbG9yOiMyMjE4MGE7Cn0KLmJ0bjpob3ZlcntmaWx0ZXI6YnJpZ2h0bmVzcygxLjA3"
        "KX0KLmJ0bjphY3RpdmV7dHJhbnNmb3JtOnRyYW5zbGF0ZVkoMXB4KX0KLmJ0bi5naG9zdHtiYWNrZ3JvdW5kOiMxODFjMjI7Ym9y"
        "ZGVyLWNvbG9yOnZhcigtLXJhaWwpO2NvbG9yOnZhcigtLWluayl9Ci5idG4uZ2hvc3Q6aG92ZXJ7Ym9yZGVyLWNvbG9yOnZhcigt"
        "LWRpbSl9Ci5idG46ZGlzYWJsZWR7b3BhY2l0eTouNDU7Y3Vyc29yOmRlZmF1bHQ7dHJhbnNmb3JtOm5vbmU7ZmlsdGVyOm5vbmV9"
        "CgovKiDilIDilIAgcmVjZW50cyDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDi"
        "lIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDi"
        "lIDilIDilIAgKi8KLnJlY2VudHN7cGFkZGluZzoycHggMnB4IDB9Ci5jaGlwc3tkaXNwbGF5OmZsZXg7Z2FwOjhweDtmbGV4LXdy"
        "YXA6d3JhcDttYXJnaW4tdG9wOjlweH0KLmNoaXB7CiAgZGlzcGxheTpmbGV4O2FsaWduLWl0ZW1zOmNlbnRlcjtnYXA6OXB4Owog"
        "IGJhY2tncm91bmQ6IzE4MWMyMjtib3JkZXI6MXB4IHNvbGlkIHZhcigtLXJhaWwpO2JvcmRlci1yYWRpdXM6MTAwcHg7CiAgcGFk"
        "ZGluZzo2cHggN3B4IDZweCAxNHB4O2ZvbnQtc2l6ZToxM3B4O2NvbG9yOnZhcigtLWluayk7Y3Vyc29yOnBvaW50ZXI7Cn0KLmNo"
        "aXA6aG92ZXJ7Ym9yZGVyLWNvbG9yOnZhcigtLWRpbSl9Ci5jaGlwLmFjdGl2ZXtib3JkZXItY29sb3I6dmFyKC0tc2lnbmFsKTtj"
        "b2xvcjp2YXIoLS1zaWduYWwpfQouY2hpcCAueHsKICBib3JkZXI6MDtiYWNrZ3JvdW5kOnRyYW5zcGFyZW50O2NvbG9yOnZhcigt"
        "LWRpbW1lcik7Y3Vyc29yOnBvaW50ZXI7CiAgZm9udC1zaXplOjE2cHg7bGluZS1oZWlnaHQ6MTtwYWRkaW5nOjJweCA2cHg7Ym9y"
        "ZGVyLXJhZGl1czo1MCU7Cn0KLmNoaXAgLng6aG92ZXJ7Y29sb3I6dmFyKC0tc29sbyl9Ci5jaGlwIC5zdGFsZXtjb2xvcjp2YXIo"
        "LS1zb2xvKTtmb250LXNpemU6MTFweH0KCi8qIOKUgOKUgCBjaHJvbWUg4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA"
        "4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA"
        "4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSAICovCi5kZWNrLWZvb3R7CiAgZGlzcGxheTpmbGV4O2p1c3RpZnktY29u"
        "dGVudDpzcGFjZS1iZXR3ZWVuO2dhcDoxNnB4O2ZsZXgtd3JhcDp3cmFwOwogIHBhZGRpbmc6MTRweCAyNHB4O2JvcmRlci10b3A6"
        "MXB4IHNvbGlkIHZhcigtLWVkZ2UpOwogIGNvbG9yOnZhcigtLWRpbW1lcik7Zm9udC1zaXplOjEycHg7Cn0KLnRvYXN0ewogIHBv"
        "c2l0aW9uOmZpeGVkO2xlZnQ6NTAlO2JvdHRvbToyNnB4O3RyYW5zZm9ybTp0cmFuc2xhdGVYKC01MCUpOwogIGJhY2tncm91bmQ6"
        "IzIwMjUyYztib3JkZXI6MXB4IHNvbGlkIHZhcigtLXJhaWwpO2JvcmRlci1sZWZ0OjNweCBzb2xpZCB2YXIoLS1zaWduYWwpOwog"
        "IGJvcmRlci1yYWRpdXM6NHB4O3BhZGRpbmc6MTJweCAxOHB4O2ZvbnQtc2l6ZToxMy41cHg7bWF4LXdpZHRoOm1pbig1NjBweCw5"
        "MHZ3KTsKICBib3gtc2hhZG93OjAgMThweCA0MHB4IC0xOHB4ICMwMDA7ei1pbmRleDo0MDsKfQoudG9hc3QuYmFke2JvcmRlci1s"
        "ZWZ0LWNvbG9yOnZhcigtLXNvbG8pfQoKOjotd2Via2l0LXNjcm9sbGJhcntoZWlnaHQ6OXB4O3dpZHRoOjlweH0KOjotd2Via2l0"
        "LXNjcm9sbGJhci10cmFja3tiYWNrZ3JvdW5kOiMxMjE1MWF9Cjo6LXdlYmtpdC1zY3JvbGxiYXItdGh1bWJ7YmFja2dyb3VuZDp2"
        "YXIoLS1yYWlsKTtib3JkZXItcmFkaXVzOjEwMHB4fQoKQG1lZGlhIChtYXgtd2lkdGg6ODIwcHgpewogIC5pbnRha2V7Z3JpZC10"
        "ZW1wbGF0ZS1jb2x1bW5zOjFmcn0KICAudHJhbnNwb3J0LXJvd3tmbGV4LXdyYXA6d3JhcH0KICAud2F2ZS13cmFwe29yZGVyOjU7"
        "ZmxleC1iYXNpczoxMDAlfQogIC50cmFjay1pZHt0ZXh0LWFsaWduOmxlZnQ7bWF4LXdpZHRoOm5vbmV9CiAgLnN0cmlwe2ZsZXg6"
        "MCAwIDEyOHB4fQp9CgpAbWVkaWEgKHByZWZlcnMtcmVkdWNlZC1tb3Rpb246cmVkdWNlKXsKICAqe2FuaW1hdGlvbi1kdXJhdGlv"
        "bjouMDAxbXMgIWltcG9ydGFudDt0cmFuc2l0aW9uLWR1cmF0aW9uOi4wMDFtcyAhaW1wb3J0YW50fQp9CgovKiDilIDilIAgc2Vj"
        "dGlvbnMg4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA"
        "4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSAICovCi8qICBB"
        "IHNlY3Rpb24gaXMgYSBzbGljZSBvZiB0aGUgc29uZyB3aXRoIGl0cyBvd24gZmFkZXIgcG9zaXRpb25zLgogICAgVGhlIGxhbmUg"
        "dW5kZXIgdGhlIHdhdmVmb3JtIGlzIHdoZXJlIHRoZXkgbGl2ZS4gICAgICAgICAgICAgICAqLwoKLnRpbWVsaW5le2ZsZXg6MTtt"
        "aW4td2lkdGg6MTIwcHg7ZGlzcGxheTpmbGV4O2ZsZXgtZGlyZWN0aW9uOmNvbHVtbjtnYXA6M3B4fQovKiB0aGUgd2F2ZSBrZWVw"
        "cyBpdHMgZml4ZWQgaGVpZ2h0IGluc2lkZSB0aGUgY29sdW1uIC0gZG9uJ3QgbGV0IGl0IGZsZXgtZ3JvdyAqLwoudGltZWxpbmUg"
        "LndhdmUtd3JhcHtmbGV4OjAgMCBhdXRvO2hlaWdodDo1NnB4fQoKLmxhbmV7CiAgcG9zaXRpb246cmVsYXRpdmU7aGVpZ2h0OjIw"
        "cHg7CiAgYmFja2dyb3VuZDojMTAxMzE3O2JvcmRlcjoxcHggc29saWQgdmFyKC0tcmFpbCk7Ym9yZGVyLXJhZGl1czozcHg7CiAg"
        "b3ZlcmZsb3c6aGlkZGVuOwp9Ci5sYW5lOmVtcHR5OjphZnRlcnsKICBjb250ZW50OiJkcmFnIHRoZSB3YXZlZm9ybSB0byBwaWNr"
        "IGEgc2VjdGlvbiI7CiAgcG9zaXRpb246YWJzb2x1dGU7aW5zZXQ6MDtkaXNwbGF5OmdyaWQ7cGxhY2UtaXRlbXM6Y2VudGVyOwog"
        "IGZvbnQtc2l6ZToxMHB4O2xldHRlci1zcGFjaW5nOi4wNmVtO2NvbG9yOiM0YTUyNWQ7cG9pbnRlci1ldmVudHM6bm9uZTsKfQou"
        "YmxvY2t7CiAgcG9zaXRpb246YWJzb2x1dGU7dG9wOjJweDtib3R0b206MnB4OwogIGJhY2tncm91bmQ6cmdiYSgyNTUsMTgwLDg0"
        "LC4xNik7CiAgYm9yZGVyOjFweCBzb2xpZCByZ2JhKDI1NSwxODAsODQsLjQyKTsKICBib3JkZXItcmFkaXVzOjJweDtjdXJzb3I6"
        "cG9pbnRlcjsKICBkaXNwbGF5OmZsZXg7YWxpZ24taXRlbXM6Y2VudGVyO3BhZGRpbmc6MCA1cHg7b3ZlcmZsb3c6aGlkZGVuOwog"
        "IGZvbnQtZmFtaWx5OnZhcigtLXNpbGspO2ZvbnQtc2l6ZToxMXB4O2xldHRlci1zcGFjaW5nOi4wOGVtOwogIHRleHQtdHJhbnNm"
        "b3JtOnVwcGVyY2FzZTtjb2xvcjojZjBjOThhO3doaXRlLXNwYWNlOm5vd3JhcDsKfQouYmxvY2s6aG92ZXJ7YmFja2dyb3VuZDpy"
        "Z2JhKDI1NSwxODAsODQsLjI2KX0KLmJsb2NrLm9uewogIGJhY2tncm91bmQ6cmdiYSgyNTUsMTgwLDg0LC4zNCk7Ym9yZGVyLWNv"
        "bG9yOnZhcigtLXNpZ25hbCk7Y29sb3I6IzIyMTgwYTsKICBib3gtc2hhZG93OjAgMCAwIDFweCB2YXIoLS1zaWduYWwpIGluc2V0"
        "Owp9CgovKiDilIDilIAgZWRpdCBiYXIg4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA"
        "4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA"
        "4pSA4pSA4pSAICovCi5lZGl0YmFyewogIHBhZGRpbmc6MTFweCAxNnB4O2Rpc3BsYXk6ZmxleDthbGlnbi1pdGVtczpjZW50ZXI7"
        "anVzdGlmeS1jb250ZW50OnNwYWNlLWJldHdlZW47CiAgZ2FwOjE0cHg7ZmxleC13cmFwOndyYXA7Ym9yZGVyLWxlZnQ6M3B4IHNv"
        "bGlkIHZhcigtLXJhaWwpOwp9Ci5lZGl0YmFyLnNjb3BlZHtib3JkZXItbGVmdC1jb2xvcjp2YXIoLS1zaWduYWwpO2JhY2tncm91"
        "bmQ6bGluZWFyLWdyYWRpZW50KDE4MGRlZywjMmEyNjIwLCMyMjFmMWEpfQouZWRpdC13aGF0e2Rpc3BsYXk6ZmxleDtmbGV4LWRp"
        "cmVjdGlvbjpjb2x1bW47Z2FwOjFweDttaW4td2lkdGg6MH0KLmVkaXQtbmFtZXtmb250LXNpemU6MTVweDtmb250LXdlaWdodDo2"
        "MDA7d2hpdGUtc3BhY2U6bm93cmFwO292ZXJmbG93OmhpZGRlbjt0ZXh0LW92ZXJmbG93OmVsbGlwc2lzfQouZWRpdGJhci5zY29w"
        "ZWQgLmVkaXQtbmFtZXtjb2xvcjp2YXIoLS1zaWduYWwpfQouZWRpdC10b29sc3tkaXNwbGF5OmZsZXg7YWxpZ24taXRlbXM6Y2Vu"
        "dGVyO2dhcDo4cHg7ZmxleC13cmFwOndyYXB9CgoubWluaS1idG57CiAgZm9udC1mYW1pbHk6dmFyKC0tYm9keSk7Zm9udC1zaXpl"
        "OjEyLjVweDsKICBwYWRkaW5nOjdweCAxMnB4O2JvcmRlci1yYWRpdXM6NHB4O2N1cnNvcjpwb2ludGVyOwogIGJhY2tncm91bmQ6"
        "IzE4MWMyMjtib3JkZXI6MXB4IHNvbGlkIHZhcigtLXJhaWwpO2NvbG9yOnZhcigtLWluayk7Cn0KLm1pbmktYnRuOmhvdmVye2Jv"
        "cmRlci1jb2xvcjp2YXIoLS1kaW0pfQoubWluaS1idG4uZ297YmFja2dyb3VuZDp2YXIoLS1zaWduYWwpO2JvcmRlci1jb2xvcjoj"
        "ZDk5NDM2O2NvbG9yOiMyMjE4MGE7Zm9udC13ZWlnaHQ6NTAwfQoubWluaS1idG4uZGFuZ2VyOmhvdmVye2JvcmRlci1jb2xvcjp2"
        "YXIoLS1zb2xvKTtjb2xvcjp2YXIoLS1zb2xvKX0KCi5uYW1lLWlucHV0ewogIGZvbnQtZmFtaWx5OnZhcigtLWJvZHkpO2ZvbnQt"
        "c2l6ZToxM3B4O3dpZHRoOjEzMHB4OwogIGJhY2tncm91bmQ6IzEyMTUxYTtib3JkZXI6MXB4IHNvbGlkIHZhcigtLXJhaWwpO2Jv"
        "cmRlci1yYWRpdXM6NHB4OwogIHBhZGRpbmc6NnB4IDlweDtjb2xvcjp2YXIoLS1pbmspOwp9Ci5uYW1lLWlucHV0OmZvY3Vze291"
        "dGxpbmU6MnB4IHNvbGlkIHZhcigtLXNpZ25hbCk7b3V0bGluZS1vZmZzZXQ6MXB4O2JvcmRlci1jb2xvcjp0cmFuc3BhcmVudH0K"
        "Ci5zdHJpcHMuc2NvcGVkIC5zdHJpcHtib3JkZXItdG9wLXdpZHRoOjNweH0K"
    ,
}

ASSETS = {k: base64.b64decode(v).decode('utf-8') for k, v in _PACKED.items()}

# ======================================================================================
#  Where things live
# ======================================================================================

OUTPUT_DIR = Path(os.environ.get("UNMIX_OUTPUT", APP_DIR / "output"))
UPLOAD_DIR = OUTPUT_DIR / "_incoming"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

AUDIO_EXTS = {".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg", ".opus", ".wma", ".aiff", ".aif", ".mp4", ".mov", ".mkv", ".webm"}

MODELS = [
    {
        "id": "htdemucs",
        "name": "Standard",
        "detail": "4 stems - fastest, very good",
        "stems": ["vocals", "drums", "bass", "other"],
        "speed": 1,
    },
    {
        "id": "htdemucs_ft",
        "name": "Best quality",
        "detail": "4 stems - fine-tuned, ~4x slower",
        "stems": ["vocals", "drums", "bass", "other"],
        "speed": 4,
    },
    {
        "id": "htdemucs_6s",
        "name": "Six stems",
        "detail": "adds guitar + piano, piano is rough",
        "stems": ["vocals", "drums", "bass", "guitar", "piano", "other"],
        "speed": 1.5,
    },
    {
        "id": "mdx_extra",
        "name": "Alternate",
        "detail": "4 stems - different character, try if one sounds off",
        "stems": ["vocals", "drums", "bass", "other"],
        "speed": 2,
    },
]
MODEL_IDS = {m["id"] for m in MODELS}

STEM_ORDER = ["vocals", "drums", "bass", "guitar", "piano", "other", "instrumental"]


# --------------------------------------------------------------------------------------
# device / environment
# --------------------------------------------------------------------------------------

def pick_device() -> str:
    forced = os.environ.get("UNMIX_DEVICE")
    if forced:
        return forced
    try:
        import torch
    except Exception:
        return "cpu"
    try:
        if torch.cuda.is_available():
            return "cuda"
    except Exception:
        pass
    try:
        if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
            return "mps"
    except Exception:
        pass
    return "cpu"


def device_label(dev: str) -> str:
    if dev.startswith("cuda"):
        try:
            import torch
            return torch.cuda.get_device_name(0)
        except Exception:
            return "NVIDIA GPU"
    if dev == "mps":
        return "Apple Silicon GPU"
    return "CPU"


def have_ffmpeg() -> bool:
    return shutil.which("ffmpeg") is not None


# --------------------------------------------------------------------------------------
# jobs
# --------------------------------------------------------------------------------------

class Cancelled(Exception):
    pass


@dataclass
class Job:
    id: str
    title: str
    model: str
    passes: int
    status: str = "queued"        # queued | running | done | error | cancelled
    stage: str = "Waiting"
    progress: float = 0.0
    duration: float = 0.0
    created: float = field(default_factory=time.time)
    elapsed: float = 0.0
    error: str = ""
    stems: list = field(default_factory=list)
    source_name: str = ""

    def dir(self) -> Path:
        return OUTPUT_DIR / self.id

    def public(self) -> dict:
        d = asdict(self)
        d["progress"] = round(self.progress, 4)
        return d


JOBS: dict[str, Job] = {}
CANCEL: dict[str, bool] = {}
LOCK = threading.Lock()
RUN_LOCK = threading.Lock()   # one separation at a time - they are memory hungry


def save_job(job: Job) -> None:
    try:
        job.dir().mkdir(parents=True, exist_ok=True)
        (job.dir() / "job.json").write_text(json.dumps(job.public(), indent=2))
    except Exception:
        pass


def load_jobs() -> None:
    for meta in sorted(OUTPUT_DIR.glob("*/job.json")):
        try:
            data = json.loads(meta.read_text())
            data.pop("progress", None)
            job = Job(
                id=data["id"],
                title=data.get("title", "Untitled"),
                model=data.get("model", "htdemucs"),
                passes=int(data.get("passes", 0)),
                status=data.get("status", "done"),
                stage=data.get("stage", ""),
                duration=float(data.get("duration", 0)),
                created=float(data.get("created", meta.stat().st_mtime)),
                elapsed=float(data.get("elapsed", 0)),
                stems=data.get("stems", []),
                source_name=data.get("source_name", ""),
            )
            if job.status == "cancelled":
                continue
            if job.status == "running" or job.status == "queued":
                job.status = "error"
                job.error = "Interrupted - the app was closed mid-render."
            job.progress = 1.0 if job.status == "done" else 0.0
            JOBS[job.id] = job
        except Exception:
            continue


# --------------------------------------------------------------------------------------
# audio in / out
#
# Deliberately does NOT use torchaudio's load/save or demucs.audio.save_audio: those move
# around between versions and are the usual reason a setup like this breaks six months
# later. soundfile + lameenc + ffmpeg are stable and do the whole job.
# --------------------------------------------------------------------------------------

class UnreadableAudio(Exception):
    pass


def read_audio(path: Path):
    """Return (float32 tensor [channels, samples], samplerate) for any file we can open."""
    import numpy as np
    import soundfile as sf
    import torch

    try:
        data, sr = sf.read(str(path), dtype="float32", always_2d=True)
    except Exception as first:
        if not have_ffmpeg():
            raise UnreadableAudio(
                f"Can't read {path.name}. Install ffmpeg to open mp3, m4a and video files."
            ) from first
        tmp = path.with_name(path.stem + "__decoded.wav")
        try:
            subprocess.run(
                ["ffmpeg", "-y", "-loglevel", "error", "-i", str(path),
                 "-vn", "-acodec", "pcm_s16le", str(tmp)],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
            )
            data, sr = sf.read(str(tmp), dtype="float32", always_2d=True)
        except subprocess.CalledProcessError as exc:
            detail = (exc.stderr or b"").decode("utf8", "ignore").strip().splitlines()[-1:]
            raise UnreadableAudio(
                f"ffmpeg couldn't read {path.name}. {' '.join(detail)}"
            ) from exc
        finally:
            tmp.unlink(missing_ok=True)

    return torch.from_numpy(np.ascontiguousarray(data.T)), sr


def _as_frames(wav, scale: float = 1.0):
    """torch [channels, samples] -> numpy [samples, channels], safely inside +/-1."""
    import numpy as np

    data = wav.detach().cpu().numpy() if hasattr(wav, "detach") else np.asarray(wav)
    data = np.asarray(data, dtype="float32")
    if data.ndim == 1:
        data = data[None, :]
    data = data.T * float(scale)
    return np.clip(data, -1.0, 1.0)


def write_audio(wav, path: Path, samplerate: int, fmt: str = "wav",
                scale: float = 1.0, bitrate: int = 320) -> Path:
    import soundfile as sf

    path = path.with_suffix("." + fmt)
    frames = _as_frames(wav, scale)

    if fmt == "mp3":
        import lameenc
        import numpy as np

        pcm = (frames * 32767.0).astype("<i2")
        enc = lameenc.Encoder()
        enc.set_bit_rate(bitrate)
        enc.set_in_sample_rate(int(samplerate))
        enc.set_channels(pcm.shape[1])
        enc.set_quality(2)
        blob = enc.encode(np.ascontiguousarray(pcm).tobytes())
        blob += enc.flush()
        path.write_bytes(blob)
        return path

    subtype = "PCM_24" if fmt in ("wav", "flac") else None
    sf.write(str(path), frames, int(samplerate), subtype=subtype)
    return path


def write_preview(wav, path: Path, samplerate: int, scale: float = 1.0) -> Path | None:
    """Something small the browser can decode fast. mp3 if lame is around, else 16-bit wav."""
    import soundfile as sf

    try:
        return write_audio(wav, path, samplerate, "mp3", scale, bitrate=192)
    except Exception:
        pass
    try:
        target = path.with_suffix(".wav")
        sf.write(str(target), _as_frames(wav, scale), int(samplerate), subtype="PCM_16")
        return target
    except Exception:
        return None


# --------------------------------------------------------------------------------------
# the separation worker
# --------------------------------------------------------------------------------------

class _ProgressBars:
    """demucs 4.0.1 has no progress callback - it just wraps its chunk loop in tqdm.
    We stand in for tqdm so we can report real progress and honour Stop."""

    def __init__(self, report, total_passes):
        self.report = report
        self.total_passes = max(1, total_passes)
        self.done_passes = 0
        self.per_pass = None

    def tqdm(self, iterable, **_kw):
        items = list(iterable)
        if self.per_pass is None:
            self.per_pass = max(1, len(items))
        for i, item in enumerate(items):
            self.report((self.done_passes * self.per_pass + i) /
                        (self.total_passes * self.per_pass), self.done_passes)
            yield item
        self.done_passes += 1
        self.report(self.done_passes / self.total_passes, self.done_passes)


def friendly_error(exc: Exception) -> str:
    text = f"{exc}"
    low = text.lower()
    if isinstance(exc, UnreadableAudio):
        return text
    if any(k in low for k in ("urlopen", "connection", "resolve", "download", "certificate", "http")):
        return ("Couldn't download the model weights. The first run of each model needs "
                "internet; after that it's fully offline. Check your connection and retry.")
    if "out of memory" in low or "cuda oom" in low:
        return ("Ran out of memory on this track. Try the Standard model with no extra "
                "passes, or close other heavy apps.")
    return f"{type(exc).__name__}: {text}"


def run_job(job_id: str, source: Path) -> None:
    job = JOBS[job_id]
    started = time.time()

    with RUN_LOCK:
        if CANCEL.get(job_id):
            job.status = "cancelled"
            job.stage = "Cancelled"
            save_job(job)
            return
        try:
            job.status = "running"
            job.stage = "Loading model"
            job.progress = 0.01
            save_job(job)

            import torch
            import demucs.apply as demucs_apply
            from demucs.apply import apply_model, BagOfModels
            from demucs.audio import convert_audio
            from demucs.pretrained import get_model

            device = pick_device()
            model = get_model(job.model)
            model.cpu()
            model.eval()

            job.stage = "Reading audio"
            job.progress = 0.02
            save_job(job)

            wav, sr = read_audio(source)
            wav = convert_audio(wav, sr, model.samplerate, model.audio_channels)
            job.duration = float(wav.shape[-1]) / model.samplerate

            if CANCEL.get(job_id):
                raise Cancelled()

            n_models = len(model.models) if isinstance(model, BagOfModels) else 1
            total_passes = n_models * max(1, job.passes)

            def report(frac, pass_index):
                if CANCEL.get(job_id):
                    raise Cancelled()
                job.progress = 0.03 + 0.88 * max(0.0, min(1.0, frac))
                job.stage = (f"Separating - pass {min(pass_index + 1, total_passes)} of {total_passes}"
                             if total_passes > 1 else "Separating")

            # demucs normalises against the mix before inference and undoes it after
            ref = wav.mean(0)
            wav = (wav - ref.mean()) / ref.std()

            bars = _ProgressBars(report, total_passes)
            original_tqdm = demucs_apply.tqdm
            demucs_apply.tqdm = bars
            try:
                sources = apply_model(
                    model, wav[None],
                    device=device,
                    shifts=job.passes,
                    split=True,
                    overlap=0.25,
                    progress=True,
                    num_workers=0,
                )[0]
            finally:
                demucs_apply.tqdm = original_tqdm

            sources = sources * ref.std() + ref.mean()

            job.stage = "Writing stems"
            job.progress = 0.92
            save_job(job)

            named = {name: sources[i] for i, name in enumerate(model.sources)}

            # instrumental = the whole track minus the vocal
            if "vocals" in named and len(named) > 1:
                inst = None
                for key, part in named.items():
                    if key == "vocals":
                        continue
                    inst = part.clone() if inst is None else inst + part
                named["instrumental"] = inst

            # one shared scale factor, so the stems still balance against each other
            peak = max(float(torch.max(torch.abs(part))) for part in named.values())
            scale = 0.999 / peak if peak > 0.999 else 1.0

            stems_dir = job.dir() / "stems"
            prev_dir = job.dir() / "preview"
            stems_dir.mkdir(parents=True, exist_ok=True)
            prev_dir.mkdir(parents=True, exist_ok=True)

            ordered = ([k for k in STEM_ORDER if k in named] +
                       [k for k in named if k not in STEM_ORDER])
            out = []
            for i, key in enumerate(ordered):
                part = named[key]
                master = write_audio(part, stems_dir / key, model.samplerate, "wav", scale)
                preview = write_preview(part, prev_dir / key, model.samplerate, scale)
                out.append({
                    "name": key,
                    "file": master.name,
                    "preview": preview.name if preview else master.name,
                    "derived": key == "instrumental",
                })
                job.progress = 0.92 + 0.07 * ((i + 1) / len(ordered))

            job.stems = out
            job.status = "done"
            job.stage = "Ready"
            job.progress = 1.0
            job.elapsed = time.time() - started

            del sources, named, wav
            try:
                if device.startswith("cuda"):
                    torch.cuda.empty_cache()
            except Exception:
                pass

        except Cancelled:
            job.status = "cancelled"
            job.stage = "Cancelled"
        except Exception as exc:
            job.status = "error"
            job.stage = "Failed"
            job.error = friendly_error(exc)
            traceback.print_exc()
        finally:
            CANCEL.pop(job_id, None)
            try:
                source.unlink(missing_ok=True)
            except Exception:
                pass
            if job.status == "cancelled":
                # leave nothing behind, including the metadata file
                shutil.rmtree(job.dir(), ignore_errors=True)
                with LOCK:
                    JOBS.pop(job_id, None)
            else:
                save_job(job)


# --------------------------------------------------------------------------------------
# web app
# --------------------------------------------------------------------------------------


def build_app():
    from flask import Flask, Response, jsonify, request, send_file
    from werkzeug.utils import secure_filename

    app = Flask(__name__, static_folder=None)
    app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024 * 1024  # 2 GB


    @app.after_request
    def no_cache(resp: Response) -> Response:
        if request.path.startswith("/api/") or request.path == "/":
            resp.headers["Cache-Control"] = "no-store"
        return resp


    @app.route("/")
    def index():
        return Response(ASSETS["index.html"], mimetype="text/html")


    @app.route("/<path:filename>")
    def assets(filename: str):
        blob = ASSETS.get(filename)
        if blob is None:
            return jsonify({"error": "Not found."}), 404
        kind = ("text/css" if filename.endswith(".css")
                else "text/javascript" if filename.endswith(".js")
                else "text/html")
        return Response(blob, mimetype=kind)


    @app.route("/api/env")
    def api_env():
        dev = pick_device()
        try:
            import torch
            torch_version = torch.__version__
        except Exception:
            torch_version = None
        return jsonify({
            "device": dev,
            "device_label": device_label(dev),
            "ffmpeg": have_ffmpeg(),
            "torch": torch_version,
            "models": MODELS,
            "output_dir": str(OUTPUT_DIR),
        })


    @app.route("/api/jobs", methods=["GET"])
    def api_jobs():
        with LOCK:
            jobs = sorted(JOBS.values(), key=lambda j: j.created, reverse=True)
            return jsonify([j.public() for j in jobs])


    @app.route("/api/jobs", methods=["POST"])
    def api_create():
        upload = request.files.get("file")
        if upload is None or not upload.filename:
            return jsonify({"error": "No file was attached."}), 400

        name = secure_filename(upload.filename) or "track"
        ext = Path(name).suffix.lower()
        if ext and ext not in AUDIO_EXTS:
            return jsonify({"error": f"{ext} isn't a supported audio or video file."}), 400

        model = request.form.get("model", "htdemucs")
        if model not in MODEL_IDS:
            return jsonify({"error": "Unknown model."}), 400
        passes = max(0, min(3, int(request.form.get("passes", 0) or 0)))

        job_id = uuid.uuid4().hex[:12]
        staged = UPLOAD_DIR / f"{job_id}{ext or '.audio'}"
        upload.save(staged)

        job = Job(
            id=job_id,
            title=Path(upload.filename).stem,
            model=model,
            passes=passes,
            source_name=upload.filename,
        )
        with LOCK:
            JOBS[job_id] = job
        save_job(job)

        threading.Thread(target=run_job, args=(job_id, staged), daemon=True).start()
        return jsonify(job.public()), 201


    @app.route("/api/jobs/<job_id>", methods=["GET"])
    def api_job(job_id: str):
        job = JOBS.get(job_id)
        if not job:
            return jsonify({"error": "No such job."}), 404
        return jsonify(job.public())


    @app.route("/api/jobs/<job_id>", methods=["DELETE"])
    def api_delete(job_id: str):
        job = JOBS.get(job_id)
        if not job:
            return jsonify({"error": "No such job."}), 404
        CANCEL[job_id] = True
        time.sleep(0.05)
        shutil.rmtree(job.dir(), ignore_errors=True)
        with LOCK:
            JOBS.pop(job_id, None)
        return jsonify({"ok": True})


    @app.route("/api/jobs/<job_id>/cancel", methods=["POST"])
    def api_cancel(job_id: str):
        if job_id not in JOBS:
            return jsonify({"error": "No such job."}), 404
        CANCEL[job_id] = True
        return jsonify({"ok": True})


    def _stem_entry(job: Job, stem: str) -> dict | None:
        for s in job.stems:
            if s["name"] == stem:
                return s
        return None


    @app.route("/api/jobs/<job_id>/preview/<stem>")
    def api_preview(job_id: str, stem: str):
        job = JOBS.get(job_id)
        entry = _stem_entry(job, stem) if job else None
        if not entry:
            return jsonify({"error": "No such stem."}), 404
        path = job.dir() / "preview" / entry["preview"]
        if not path.exists():
            path = job.dir() / "stems" / entry["file"]
        return send_file(path, conditional=True)


    @app.route("/api/jobs/<job_id>/download/<stem>")
    def api_download(job_id: str, stem: str):
        job = JOBS.get(job_id)
        entry = _stem_entry(job, stem) if job else None
        if not entry:
            return jsonify({"error": "No such stem."}), 404
        fmt = request.args.get("format", "wav").lower()
        master = job.dir() / "stems" / entry["file"]

        if fmt == "wav":
            return send_file(master, as_attachment=True, download_name=f"{job.title} - {stem}.wav")

        wav, sr = read_audio(master)
        tmp = job.dir() / "exports"
        tmp.mkdir(exist_ok=True)
        out = write_audio(wav, tmp / f"{stem}", sr, fmt)
        return send_file(out, as_attachment=True, download_name=f"{job.title} - {stem}.{fmt}")


    def _build_envelope(segments, n, sr, ramp_ms=25):
        """Piecewise-constant gain over time, with short ramps so section edges don't click."""
        import numpy as np

        env = np.zeros(n, dtype="float32")
        for seg in segments:
            a = max(0, int(float(seg.get("start", 0)) * sr))
            b = min(n, int(float(seg.get("end", 0)) * sr))
            if b > a:
                env[a:b] = float(seg.get("gain", 0.0))

        w = max(1, int(sr * ramp_ms / 1000.0))
        if w > 1:
            win = np.hanning(2 * w + 1).astype("float32")
            win /= win.sum()
            padded = np.pad(env, w, mode="edge")
            env = np.convolve(padded, win, mode="same")[w:w + n]
        return env


    @app.route("/api/jobs/<job_id>/mix", methods=["POST"])
    def api_mix(job_id: str):
        """Sum stems into one file.

        Two shapes accepted:
          {"stems": [...], "gains": {...}}                        - flat, whole track
          {"tracks": [{"name": ..., "segments": [...]}, ...]}     - per-section automation
        Optional "range": [start, end] trims the result to just that slice.
        """
        job = JOBS.get(job_id)
        if not job or job.status != "done":
            return jsonify({"error": "That track isn't ready."}), 404

        import numpy as np
        import torch

        body = request.get_json(force=True, silent=True) or {}
        fmt = (body.get("format") or "wav").lower()
        label = body.get("label") or "mix"
        trim = body.get("range")

        tracks = body.get("tracks")
        if not tracks:
            tracks = [{"name": n, "segments": None, "flat": float((body.get("gains") or {}).get(n, 1.0))}
                      for n in (body.get("stems") or [])]
        if not tracks:
            return jsonify({"error": "Pick at least one stem to export."}), 400

        total = None
        sr = 44100
        for entry in tracks:
            name = entry.get("name")
            stem = _stem_entry(job, name)
            if not stem:
                continue
            wav, sr = read_audio(job.dir() / "stems" / stem["file"])
            part = wav.numpy() if hasattr(wav, "numpy") else np.asarray(wav)
            n = part.shape[-1]

            segments = entry.get("segments")
            if segments:
                if all(float(s.get("gain", 0)) == 0 for s in segments):
                    continue
                part = part * _build_envelope(segments, n, sr)[None, :]
            else:
                part = part * float(entry.get("flat", 1.0))

            if total is None:
                total = part
            else:
                m = min(total.shape[-1], part.shape[-1])
                total = total[..., :m] + part[..., :m]

        if total is None:
            return jsonify({"error": "Everything is silent - nothing to export."}), 400

        if trim and len(trim) == 2:
            a = max(0, int(float(trim[0]) * sr))
            b = min(total.shape[-1], int(float(trim[1]) * sr))
            if b - a > sr // 100:
                total = total[..., a:b]

        peak = float(np.max(np.abs(total)))
        if peak > 0.999:
            total = total * (0.999 / peak)

        exports = job.dir() / "exports"
        exports.mkdir(exist_ok=True)
        safe = secure_filename(label) or "mix"
        out = write_audio(torch.from_numpy(np.ascontiguousarray(total)), exports / safe, sr, fmt)
        return send_file(out, as_attachment=True, download_name=f"{job.title} - {label}.{fmt}")


    @app.route("/api/jobs/<job_id>/zip")
    def api_zip(job_id: str):
        job = JOBS.get(job_id)
        if not job or job.status != "done":
            return jsonify({"error": "That track isn't ready."}), 404
        fmt = request.args.get("format", "wav").lower()

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_STORED) as zf:
            for entry in job.stems:
                master = job.dir() / "stems" / entry["file"]
                if fmt == "wav":
                    zf.write(master, f"{job.title}/{entry['name']}.wav")
                else:
                    wav, sr = read_audio(master)
                    tmp = job.dir() / "exports"
                    tmp.mkdir(exist_ok=True)
                    out = write_audio(wav, tmp / entry["name"], sr, fmt)
                    zf.write(out, f"{job.title}/{entry['name']}.{fmt}")
        buf.seek(0)
        return send_file(buf, mimetype="application/zip", as_attachment=True,
                         download_name=f"{job.title} - stems.zip")


    @app.route("/api/reveal/<job_id>", methods=["POST"])
    def api_reveal(job_id: str):
        """Open the job folder in Explorer / Finder / the desktop file manager."""
        job = JOBS.get(job_id)
        if not job:
            return jsonify({"error": "No such job."}), 404
        path = str(job.dir() / "stems")
        try:
            if sys.platform.startswith("win"):
                os.startfile(path)  # noqa: S606
            elif sys.platform == "darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])
            return jsonify({"ok": True})
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    return app

def main() -> None:
    port = 7860
    host = "127.0.0.1"
    open_browser = True
    args = sys.argv[1:]
    for i, a in enumerate(args):
        if a == "--port" and i + 1 < len(args):
            port = int(args[i + 1])
        elif a == "--no-browser":
            open_browser = False

    ensure_deps()

    load_jobs()
    app = build_app()

    dev = pick_device()
    banner("UNMIX - local stem separation")
    print(f"  Running on {device_label(dev)}")
    if dev == "cpu":
        print("  A 4 minute song takes roughly 2-5 minutes on CPU.")
    if not have_ffmpeg():
        print("  ffmpeg not found - wav and flac work now; install ffmpeg for mp3/m4a/video.")
    print(f"  Stems are saved in: {OUTPUT_DIR}")
    print()
    print(f"  >>> Open this in your browser:  http://{host}:{port}")
    print()
    print("  Leave this window open while you use it. Close it to quit.")
    print()

    if open_browser:
        def pop():
            time.sleep(1.5)
            try:
                import webbrowser
                webbrowser.open(f"http://{host}:{port}")
            except Exception:
                pass
        threading.Thread(target=pop, daemon=True).start()

    try:
        app.run(host=host, port=port, threaded=True, debug=False)
    except OSError as exc:
        if "address already in use" in str(exc).lower() or getattr(exc, "errno", None) in (48, 98, 10048):
            banner(f"Port {port} is already busy.")
            print("  UNMIX may already be running in another window.")
            print(f"  Try: open http://{host}:{port} first.")
            print(f"  Or start it on a different port:  python UNMIX.py --port {port + 1}")
            hold(1)
        raise


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n  Stopped.")
    except SystemExit:
        raise
    except Exception:
        banner("UNMIX hit an error and stopped.")
        traceback.print_exc()
        print()
        print("  Copy everything above and send it over - that's enough to fix it.")
        hold(1)
