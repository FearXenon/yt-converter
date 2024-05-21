import argparse
import re
import os
from pytube import YouTube

def sanitize_filename(filename):
    filename = re.sub(r'\s', '_', filename)
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def progress_callback(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    progress = (bytes_downloaded / total_size) * 100
    print(f"Downloaded: {progress:.2f}% ({bytes_downloaded / (1024 * 1024):.2f}/{total_size / (1024 * 1024):.2f} MB)", end='\r')

# Create the parser
parser = argparse.ArgumentParser(description='Download a YouTube video.')

# Add the `url` argument
parser.add_argument('url', type=str, help='The URL of the YouTube video to download')

# Add the `only_audio` argument
parser.add_argument('--only-audio', action='store_true', help='Only download the audio')

# Add the `destination_path` argument
parser.add_argument('--destination-path', default='downloads', type=str, help='The destination path for the downloaded file')

# Add the `start` and `end` arguments
parser.add_argument('--start', default=0, type=int, help='The start time of the section to download (in seconds)')
parser.add_argument('--end', default=-1, type=int, help='The end time of the section to download (in seconds)')

# Add the `max_length` argument
parser.add_argument('--max-length', default=-1, type=int, help='The maximum length of the video to download (in seconds)')

# Parse the arguments
args = parser.parse_args()

# Create a YouTube object
yt = YouTube(args.url, on_progress_callback=progress_callback)

length = int(yt.length)

if args.max_length == -1:
    args.max_length = length

if args.end != -1:
    end = args.start + args.max_length

print(yt.title)
print(f"Loaded video is {length} seconds.")

# If the `only_audio` argument is set, filter the streams to only include audio-only streams
if args.only_audio:
    stream = yt.streams.filter(only_audio=True).first()
else:
    # Otherwise, get the first stream (this will be the highest resolution video and audio)
    stream = yt.streams.get_highest_resolution()

print(f"Started download of video with size of {stream.filesize_mb}MB.")

# If the `start` and `end` arguments are set, use the `start` and `end` parameters of the `download` method
filename = sanitize_filename(yt.title)

if args.only_audio:
    filename += '.mp3'
else:    
    filename += '.mp4'

# Ensure the destination path exists
if not os.path.exists(args.destination_path):
    os.makedirs(args.destination_path)

# Download the stream with progress callback
stream.download(output_path=args.destination_path, filename=filename)
