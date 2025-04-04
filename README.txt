1) Convert to wav file with 16kHz.
ffmpeg -i 111.mp3 -acodec pcm_s16le -ac 1 -ar 16000 out.wav
2) Run Whisper
./whisper.cpp-master/main -m whisper.cpp-master/models/ggml-small.bin -f ssis388.wav

Cut using a specific time
$ ffmpeg -i input.mp4 -ss 00:05:10 -to 00:15:30 -c:v copy -c:a copy output2.mp4

filter-subtitles.py -s files/GHNU-10_part3_16kHz_output.srt