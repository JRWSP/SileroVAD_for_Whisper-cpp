# Manual implementation
Just using video should be fine. Otherwise, audio can be extracted by 
```
python convert_video_to_audio.py VIDEO_FILE.mp4
```
Then, filter the file with Silero-VAD by simply call 
```
python runVAD.py -f INPUT_FILE
```
or, for the first run, you might need to download VAD model first. This can be done by simply add force_reload argument
```
python runVAD.py -f INPUT_FILE -re
```
*** Running with the bash file will use force_reload everytime. If this annoys you, consider turning it off.

Then in folder `vad_chunks` The script will produce 
1. chunk.wav : audios file that contain voices.
2. chunk_timestamps.json : data of original timestamp for reconstruct srt file.

Passing those .wav files into Whisper or any voice-to-text model to generate srt of those chunks. I prefer using [SubtitleEdit](https://github.com/SubtitleEdit/subtitleedit) or [Whisperer](https://github.com/tigros/Whisperer) for batch transcription.

Assume the srt files being in 'vad_chunks' folder and having same name as .wav files. Calling 
```
python composeSub.py -o OUTPUT_NAME
```
to compose the final subtitle. ENJOY!!! :) 


