import argparse
import os
import subprocess
import sys

def create_virtualenv(venv_path):
    if not os.path.exists(venv_path):
        print(f"Creating virtual environment at {venv_path}")
        subprocess.run([sys.executable, '-m', 'venv', venv_path])
    else:
        print(f"Virtual environment already exists at {venv_path}")

def install_packages(venv_path):
    pip_executable = os.path.join(venv_path, 'bin', 'pip') if os.name != 'nt' else os.path.join(venv_path, 'Scripts', 'pip.exe')
    print("Installing required packages...")
    subprocess.run([pip_executable, 'install', 'git+https://github.com/pytube/pytube'])

def download_video(url, output_path, venv_path):
    python_executable = os.path.join(venv_path, 'bin', 'python') if os.name != 'nt' else os.path.join(venv_path, 'Scripts', 'python.exe')
    download_script = f"""
import sys
from pytube import YouTube

def download_video(url, output_path):
    try:
        yt = YouTube(url)
        video = yt.streams.get_highest_resolution()
        video.download(output_path=output_path)
        print(f"Downloaded '{{yt.title}}' successfully!")
    except Exception as e:
        print(f"An error occurred: {{e}}")

if __name__ == "__main__":
    url = sys.argv[1]
    output_path = sys.argv[2]
    download_video(url, output_path)
"""
    with open("download_script.py", "w") as f:
        f.write(download_script)
    subprocess.run([python_executable, "download_script.py", url, output_path])
    os.remove("download_script.py")

def main(url, output_path):
    venv_path = os.path.join(output_path, 'venv')
    create_virtualenv(venv_path)
    install_packages(venv_path)
    download_video(url, output_path, venv_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YouTube Video Downloader with Virtual Environment")
    parser.add_argument("url", help="URL of the YouTube video")
    parser.add_argument("output_path", help="Path to save the downloaded video and create virtual environment")
    args = parser.parse_args()
    main(args.url, args.output_path)

