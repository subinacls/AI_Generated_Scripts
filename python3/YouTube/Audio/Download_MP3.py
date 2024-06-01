import argparse
import subprocess
import sys
import os
import json

def check_ffmpeg():
    try:
        subprocess.run(['ffmpeg', '-version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("ffmpeg is installed.")
    except subprocess.CalledProcessError:
        print("ffmpeg is not installed or not found in PATH.")
        sys.exit(1)

def create_virtualenv(venv_path):
    if not os.path.exists(venv_path):
        print(f"Creating virtual environment at {venv_path}")
        subprocess.run([sys.executable, '-m', 'venv', venv_path])
    else:
        print(f"Virtual environment already exists at {venv_path}")

def install_packages(venv_path):
    pip_executable = os.path.join(venv_path, 'bin', 'pip') if os.name != 'nt' else os.path.join(venv_path, 'Scripts', 'pip.exe')
    print("Installing required packages...")
    subprocess.run([pip_executable, 'install', 'git+https://github.com/pytube/pytube', 'pydub', 'mutagen'])

def download_video(url, output_path):
    from pytube import YouTube
    yt = YouTube(url)
    video = yt.streams.filter(only_audio=True).first()
    downloaded_file = video.download(output_path=output_path)
    return downloaded_file, yt

def convert_to_mp3(input_file, output_file, metadata):
    from pydub import AudioSegment
    from mutagen.easyid3 import EasyID3
    audio = AudioSegment.from_file(input_file)
    audio.export(output_file, format="mp3")
    os.remove(input_file)
    audio_file = EasyID3(output_file)
    audio_file['title'] = metadata.get('title', 'Unknown Title')
    audio_file['artist'] = metadata.get('author', 'Unknown Artist')
    audio_file['album'] = metadata.get('title', 'Unknown Album')
    audio_file['genre'] = metadata.get('category', 'Unknown Genre')
    audio_file['date'] = metadata.get('publish_date', 'Unknown Date')
    audio_file.save()

def save_metadata(metadata, output_path):
    metadata_file = os.path.join(output_path, "metadata.json")
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=4)
    print(f"Metadata saved to {metadata_file}")

def main(url, output_path):
    check_ffmpeg()
    venv_path = os.path.join(output_path, 'venv')
    create_virtualenv(venv_path)
    install_packages(venv_path)
    python_executable = os.path.join(venv_path, 'bin', 'python') if os.name != 'nt' else os.path.join(venv_path, 'Scripts', 'python.exe')
    download_script = f"""
import sys
from pytube import YouTube
from pydub import AudioSegment
from mutagen.easyid3 import EasyID3
import os
import json

def download_video(url, output_path):
    yt = YouTube(url)
    video = yt.streams.filter(only_audio=True).first()
    downloaded_file = video.download(output_path=output_path)
    return downloaded_file, yt

def convert_to_mp3(input_file, output_file, metadata):
    audio = AudioSegment.from_file(input_file)
    audio.export(output_file, format="mp3")
    os.remove(input_file)

    audio_file = EasyID3(output_file)
    audio_file['title'] = metadata.get('title', 'Unknown Title')
    audio_file['artist'] = metadata.get('author', 'Unknown Artist')
    audio_file['album'] = metadata.get('title', 'Unknown Album')
    audio_file['genre'] = metadata.get('category', 'Unknown Genre')
    audio_file['date'] = metadata.get('publish_date', 'Unknown Date')
    audio_file.save()

def save_metadata(metadata, output_path):
    metadata_file = os.path.join(output_path, "metadata.json")
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=4)
    print(f"Metadata saved to {{metadata_file}}")

def main(url, output_path):
    print(f"Downloading video from {{url}}")
    downloaded_file, yt = download_video(url, output_path)
    base, ext = os.path.splitext(downloaded_file)
    output_file = base + '.mp3'
    metadata = {{
        'title': yt.title,
        'author': yt.author,
        'category': yt.channel_id,
        'publish_date': yt.publish_date.strftime('%Y-%m-%d'),
        'description': yt.description,
        'views': yt.views,
        'length': yt.length
    }}
    save_metadata(metadata, output_path)
    print(f"Converting {{downloaded_file}} to {{output_file}}")
    convert_to_mp3(downloaded_file, output_file, metadata)
    print(f"MP3 file saved to {{output_file}}")

if __name__ == "__main__":
    url = sys.argv[1]
    output_path = sys.argv[2]
    main(url, output_path)
"""
    script_path = os.path.join(output_path, 'download_script.py')
    with open(script_path, 'w') as f:
        f.write(download_script)
    subprocess.run([python_executable, script_path, url, output_path])
    os.remove(script_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YouTube to MP3 Converter with Virtual Environment")
    parser.add_argument("url", help="URL of the YouTube video")
    parser.add_argument("output_path", help="Path to save the MP3 file and metadata")
    args = parser.parse_args()
    main(args.url, args.output_path)
