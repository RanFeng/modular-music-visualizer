@REM Download 7zip executable if it doesn't exist
if not exist "7z1900-x64.msi" (
    echo "Downloading 7zip installer executable"
    powershell -Command "Invoke-WebRequest https://www.7-zip.org/a/7z1900-x64.msi -OutFile 7z1900-x64.msi"
) else (
    echo "7zip installer already downloaded"
)

@REM Install 7zip
echo "Installing 7zip for decompressing some .7z files (you should use it as well, better than rar and is free)"
.\7z1900-x64.msi

python.exe -m venv mmv_python_virtual_env
source .\mmv_python_virtual_env\scripts\activate.bat

@REM Upgrade pip
echo "Upgrading Python's package manager PIP and wheel"
python.exe -m pip install --upgrade pip wheel --user

@REM If you have any troubles with lapack / blas with SciPy try removing the @REM on the next line..?
@REM python.exe -m pip install -U https://download.lfd.uci.edu/pythonlibs/z4tqcw5k/scipy-1.5.4-cp38-cp38-win_amd64.whl scipy

echo "Installing MMV Python dependencies"
python.exe -m pip install -r "..\..\mmv\requirements.txt" --user

echo "Installing every dependency we'll need. This will likely fail missing patool because pip just will refuse installing on C:\Program Files even with admin permissions when I tried, and Python installer just won't add the appdata local roaming python folder to PATH automatically since that is user stuff, hence why we use a virtualenv before. Consider also restarting the shell after installing Golang otherwise it will not find the go.exe binary. Oh, and also, can't isntall shady because installing egl is just pain and unstable even on msys2, cygwin and have to add and micro manage those on PATH for it to even find the stuff. For running MMVSkia only FFmpeg is required and you probably can skip this."
python.exe ".\get_externals.py"