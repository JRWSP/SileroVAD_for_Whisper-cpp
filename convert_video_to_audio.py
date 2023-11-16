import os
import argparse
from moviepy.editor import VideoFileClip

def convert_video_to_audio_moviepy(video_file, output_ext="mp3"):
    """Converts video to audio using MoviePy library
    that uses `ffmpeg` under the hood"""
    filename, ext = os.path.splitext(video_file)
    clip = VideoFileClip(video_file)
    clip.audio.write_audiofile(f"{filename}.{output_ext}")

if __name__=="__main__":
    parser = argparse.ArgumentParser(description="Extract mp3 from video.")
    parser.add_argument('-f', metavar='--FILE', help="Name of video file.", required=True)
    args = parser.parse_args()

    filename = args.f
    convert_video_to_audio_moviepy(filename)