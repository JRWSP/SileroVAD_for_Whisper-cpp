# runSileroVAD
Scripts for filter silence periods in audio file by calling Silero-VAD. 
Suppose to use for prepare file in foreign langauge before passing into Whisper or any voice-to-text model to transcibe and make subtitle file.

# Dependecy

- pytorch (cpu-only)
- argparse
- ffmpeg
- json
- moviepy
- srt
- pysrt

# Usage
Just using using video should be fine. Otherwise, audio can be extracted by 
```
python convert_video_to_audio.py VIDEO_FILE.mp4
```
Then, filter the file with Silero-VAD by simply call 
```
python runVAD.py -f INPUT_FILE.mp3
```
or, for the first time, you might need to download VAD model first. This can be done by simply add force_reload argument
```
python runVAD.py -f INPUT_FILE.mp3 -re
```
Then in folder `vad_chunks` The script will produce 
1. chunk.wav : audios file that contain voices.
2. chunk_timestamps.json : data of original timestamp for reconstruct srt file.

Passing those .wav files into Whisper or any voice-to-text model to generate srt of those chunks. I prefer using [SubtitleEdit](https://github.com/SubtitleEdit/subtitleedit) for it simplicity.
Assume the srt files being in 'vad_chunks' folder and having same name as .wav files. Calling 
```
python composeSub.py -o OUTPUT_NAME
```
to compose the final subtitle. ENJOY!!! :) 

## Support
If this project help you reduce time to develop, you can give me a cup of coffee, or some beers so I can code more :)

<a href="https://www.buymeacoffee.com/jrwsp" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 30px !important;width: 108px !important;" ></a>
<a href='https://ko-fi.com/R5R5R7C6Y' target='_blank'><img height='30' style='border:0px;height:30px;' src='https://storage.ko-fi.com/cdn/kofi2.png?v=3' border='0' alt='Buy Me a Coffee at ko-fi.com' /></a>
