import os
import argparse
from moviepy.editor import VideoFileClip

def convert_video_to_audio_moviepy(video_file, output_ext="wav"):
    """
    Converts video to audio 16KHz .wav using MoviePy library that uses `ffmpeg` under the hood.
    """
    filename, ext = os.path.splitext(video_file)
    clip = VideoFileClip(video_file)
    clip.audio.write_audiofile(f"{filename}.{output_ext}", codec='pcm_s16le', fps=16000)

if __name__=="__main__":
    parser = argparse.ArgumentParser(description="Extract mp3 from video.")
    parser.add_argument('-f', metavar='--FILE', help="Name of video file.", required=True)
    args = parser.parse_args()

    filename = args.f
    convert_video_to_audio_moviepy(filename)
