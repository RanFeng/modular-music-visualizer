This documentation needs some reviewing but should still be functional

# Running MMV on Windows

This project isn't extensively tested on Windows, feedback appreciated.

<hr>
<p align="center">
  <i>Prepare your disks and patience!!</i>
</p>
<hr>

Any easier steps for Windows are welcome specially for external installs other than Python that are needed.

##### Vanilla Python (discouraged somehow, high entropy)

Don't be afraid to search how / why stuff broke because it will at some point.

You can run the file `/src/bootstrap/windows/install_python.bat` and it should™ work.

Head over to [Python Releases for Windows](https://www.python.org/downloads/windows/), download a _"Windows x86-64 executable installer"_ (I currently use Python 3.8), install it (be sure to check _"ADD PYTHON TO PATH"_ option on the installer).

### Important: extra step for an automatic installation of dependencies

Either run `/src/bootstrap/windows/install_dependencies.bat` or continue reading. You'll mostly like only need FFmpeg from the Externals as the MMVSkia sub package is the only one that works consistently on Windows as far as I know, I'd say run this just in case but don't hesitate in skipping and manually moving stuff..

Go to [7-zip downloads](https://www.7-zip.org/download.html) website, download the `7-Zip for 64-bit Windows x64 (Intel 64 or AMD64)` executable if you don't have it already installed, run it and extract the files on the default path.

This step is required to extract the video encoder (FFmpeg) compressed files if you don't want to do this by hand.

### Virtual environment for isolating Python packages

Open a shell on the downloaded and extracted folder

On Windows you can right click an empty spot on the Windows File Manager app while holding the shift key for a option to "Open PowerShell" here to appear.

Change the working directory of the shell to the folder `.\src` (or just execute the previous step on that folder which contains the file `base_video.py`)

This step is not required but good to do so, create an virtual environment (venv) and activate it:

- `python.exe -m venv mmv-venv`

- `source .\venv-path\Scripts\activate.bat`

You'd then have to source the `activate.bat` every time you wish to run MMV again, just point it to the right directory relative on where your shell is opened..

#### Automatic installation and running

Install Python dependencies with `pip install -r .\mmv\requirements.txt`

When you run `python .\base_video.py` it should take care of downloading and moving FFmpeg, mpv and musescore as needed by working on the externals folders, moving the binary to the right place.

If this process doesn't work (dead links for example), report any issue you had. You can also continue reading this for manual instructions.

#### Manual FFmpeg and Python deps installation

Download a compiled FFmpeg [build](https://ffmpeg.org/download.html#build-windows), the binary named `ffmpeg.exe` must be on the directory `ROOT/mmv_skia/mmv/externals/ffmpeg.exe`.

Install Python dependencies with `pip install -r .\mmv\requirements.txt`

Run MMV with `python .\base_video.py`

# Post processing

You can't render videos out of this but only visualize real time

Edit the file `post_processing.py` then run it. Don't set a target output video, comment the line by adding a # at the beginning.

Head back to the original [RUNNING.md](RUNNING.md) for instructions on configuring your own stuff

# MMVShaderShady

Find a way to install polyfloyd's [Shady](https://github.com/polyfloyd/shady) project on Windows then report back.. couldn't make `pkg-config` of Cygwin to find `egl`.
