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
    activate_script = os.path.join(venv_path, 'bin', 'activate_this.py') if os.name != 'nt' else os.path.join(venv_path, 'Scripts', 'activate_this.py')
    with open(activate_script) as file_:
        exec(file_.read(), dict(__file__=activate_script))

    from pytube import YouTube  # Import here after activating the virtual environment

    try:
        yt = YouTube(url)
        video = yt.streams.get_highest_resolution()
        output_file = video.download(output_path=output_path)
        print(f"Downloaded '{yt.title}' successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")

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

