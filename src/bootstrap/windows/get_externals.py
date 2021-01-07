import sys
import os

# Append previous folder to path
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append("..")
sys.path.append(
    THIS_DIR + "/../"
)

# Import mmv, get interface
import mmv
interface = mmv.MMVPackageInterface()

comment = {
    "ffmpeg": "It should work as expected, downloads and extracts to the externals folder",
    "mpv": "It should work as expected, downloads and extracts to the externals folder",
    "musescore": "It should work as expected, downloads and extracts to the externals folder",
    "golang": "Consider restarting the shell after installing golang so it finds the go.exe binary",
    "shady": "This will most likely fail for running the next level MMVShaders, find a way to install egl and pkg-config for Windows.. I couldn't.",
}

# Testing
for external in ["ffmpeg", "mpv", "musescore", "golang", "shady"]:
    c = comment[external]
    print(f"\n{c}\n")
    interface.check_download_externals(target_externals = external)
