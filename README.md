If this project help you reduce time to develop, you can give me a cup of coffee, or some beers so I can code more :)

BTC: bc1q2zpmmlz7ujwx2ghsgw5j7umv8wmpchplemvhtu <br>
ETH: 0x80e98FcfED62970e35a57d2F1fefed7C89d5DaF4

<a href="https://www.buymeacoffee.com/jrwsp" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 30px !important;width: 108px !important;" ></a>
# SileroVAD for Whisper-cpp

For CUDA-available devices, running Whisper with Silero-VAD is easily implemented by using [Faster-Whisper](https://github.com/guillaumekln/faster-whisper). [Whisper.cpp](https://github.com/ggerganov/whisper.cpp) is an alternative to run Whisper on AMD gpu but it does not implement any-VAD. 

This repo conatins python script for pre-processing input file with Silero-VAD and split it into chunks before passing them into any voice-to-text model. Then re-construct the full transcription from the chunk's results.  

# Dependecy
- pytorch (only cpu needed for VAD.)
- onnxruntime
- argparse
- ffmpeg
- json
- moviepy
- srt
- pysrt

# Installation
To use with bash script, need Whisper.cpp to be installed.
1) For Mac/Linux, download [Whisper.cpp](https://github.com/ggerganov/whisper.cpp) and make it executable. For Windows, download CLI version of [Whisperer](https://github.com/tigros/Whisperer)
2) Put it in the same directory with `VAD_Whisper-cpp` and `whisper_with_VAD.sh` (or `whisper_with_VAD.ps1`).
3) Make the script executable by typing `chmod +x whisper_with_VAD.sh`.

If you don't want to use script, look at [manually implementation](https://github.com/JRWSP/SileroVAD_for_Whisper-cpp/tree/main/VAD_Whisper-cpp).

# Usage
 For Mac/Linux user that can use Shell Script, simply run
   ```
./whisper_with_VAD.sh -f INPUT_FILE.mp4 -m MODEL_PATH
   ```
For example, if you want to use `small` model then replace `MODEL_PATH` with `whisper.cpp/models/ggml-small.bin`.

 For Windows user, I find it is convenient to use GPU-ready version through [Whisperer](https://github.com/tigros/Whisperer). Download its CLI version and use script for PowerShell.
 ```
.\whisper_with_VAD.ps1 -f INPUT_FILE.mp4 -m MODEL_PATH
 ```
