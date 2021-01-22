import sys
from setuptools import setup, find_packages
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    #     "packages": packages
}

# GUI applications require a different base on Windows (the default is for
# a console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"
    setup(
        name="premix",
        version="0.1.0",
        url="https://github.com/giftmischer69/premix",
        author="giftmischer69",
        author_email="giftmischer69@pm.me",
        description="phonk remix maker",
        packages=find_packages(),
        install_requires=[
            "python==3.7",
            "pyarrow",
            "streamlit",
            "spleeter",
            "librosa",
            "pytube",
            "sox",
        ],
        entry_points={
            'console_scripts': [
                'premix = run',
            ],
        },
        options={"build_exe": build_exe_options},
        executables=[Executable("run.py", base=base)]
    )
