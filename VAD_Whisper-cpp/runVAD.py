import torch
import argparse
import os
import ffmpeg
import json
import time


torch.set_num_threads(1)

def runVAD(audio_path, force_reload=False, USE_ONNX=False, vad_threshold:float=0.4, chunk_threshold:float=0.3):
    """
    Main function of running VAD.
    """

    # Configuration
    assert vad_threshold >= 0.01
    assert chunk_threshold >= 0.1
    assert audio_path != ""

    print("Encoding audio...")
    if not os.path.exists("vad_chunks"):
        os.mkdir("vad_chunks")
    ffmpeg.input(audio_path).output(
        "vad_chunks/silero_temp.wav",
        ar=str(SAMPLING_RATE),
        ac="1",
        acodec="pcm_s16le",
        map_metadata="-1",
        fflags="+bitexact",
    ).overwrite_output().run(quiet=True)

    """
    USE_ONNX = False # change this to True if you want to test onnx model
    if USE_ONNX:
        !pip install -q onnxruntime
    """
    print("Running VAD...")
    model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad',
                                model='silero_vad',
                                force_reload=force_reload,
                                onnx=USE_ONNX)

    (get_speech_timestamps,
    save_audio,
    read_audio,
    VADIterator,
    collect_chunks) = utils

    out_path = os.path.splitext(audio_path)[0] + ".srt"

    # Generate VAD timestamps
    VAD_SR = SAMPLING_RATE
    wav = read_audio("vad_chunks/silero_temp.wav", sampling_rate=VAD_SR)
    t = get_speech_timestamps(wav, model, sampling_rate=VAD_SR, threshold=vad_threshold)

    # Add a bit of padding, and remove small gaps
    for i in range(len(t)):
        t[i]["start"] = max(0, t[i]["start"] - 3200)  # 0.2s head
        t[i]["end"] = min(wav.shape[0] - 16, t[i]["end"] + 20800)  # 1.3s tail
        if i > 0 and t[i]["start"] < t[i - 1]["end"]:
            t[i]["start"] = t[i - 1]["end"]  # Remove overlap

    # If breaks are longer than chunk_threshold seconds, split into a new audio file
    # This'll effectively turn long transcriptions into many shorter ones
    u = [[]]
    for i in range(len(t)):
        if i > 0 and t[i]["start"] > t[i - 1]["end"] + (chunk_threshold * VAD_SR):
            u.append([])
        u[-1].append(t[i])

    # Merge speech chunks
    for i in range(len(u)):
        save_audio(
            "vad_chunks/" + str(i) + ".wav",
            collect_chunks(u[i], wav),
            sampling_rate=VAD_SR,
        )
    # Convert timestamps to seconds
    for i in range(len(u)):
        time = 0.0
        offset = 0.0
        for j in range(len(u[i])):
            u[i][j]["start"] /= VAD_SR
            u[i][j]["end"] /= VAD_SR
            u[i][j]["chunk_start"] = time
            time += u[i][j]["end"] - u[i][j]["start"]
            u[i][j]["chunk_end"] = time
            if j == 0:
                offset += u[i][j]["start"]
            else:
                offset += u[i][j]["start"] - u[i][j - 1]["end"]
            u[i][j]["offset"] = offset
    write_timestamps(u, "vad_chunks/chunk_timestamps.json")
    os.remove("vad_chunks/silero_temp.wav")

#J.S.: Save VAD timestamps to json file.
def write_timestamps(a_list, name):
    print("Started writing list data into a json file")
    with open(f"{name}", "w") as fp:
        json.dump(a_list, fp, indent = 2)
        print("Done writing JSON data into .json file")

if __name__=="__main__":
    # Initialize parser
    parser = argparse.ArgumentParser(description="Read audio file name pass it to silero-VAD.")
    parser.add_argument('-f', metavar='--AUDIO_FILE', help="Name of audio file.", required=True)
    parser.add_argument("-re", action='store_true', help = "[Default:False] Force reload VAD model from hub before run.", required=False)
    parser.add_argument("-uo", action='store_true', help = "[Default:False] Use onnx model.", required=False)
    parser.add_argument("-vt", metavar='--VAD_THRESHOLD', default=0.4, type=float, help = "[Default:0.4] param type:number.", required=False)
    parser.add_argument("-ct", metavar='--CHUNK_THRESHOLD', default=0.3, type=float, help = "[Default:0.3] param type:number.", required=False)
    parser.add_argument("-mt", action='store_true', help = "[Default:False] Measure VAD running time.", required=False)

    SAMPLING_RATE = 16000
    # Read arguments from command line
    args = parser.parse_args()

    # Required settings:
    audio_path = args.f # @param {type:"string"}

    # @markdown Advanced settings:
    FORCE_RELOAD = args.re
    USE_ONNX = args.uo
    vad_threshold = args.vt
    chunk_threshold = args.ct
    meas_time = args.mt
    print(audio_path)
    print("FORCE_RELOAD: ", FORCE_RELOAD)
    print("USE_ONNX: ", USE_ONNX)
    if meas_time:
        start_time = time.time()
    runVAD(audio_path, force_reload=FORCE_RELOAD, USE_ONNX=USE_ONNX, 
           vad_threshold=vad_threshold, chunk_threshold=chunk_threshold)
    if meas_time:
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time: {execution_time} seconds")