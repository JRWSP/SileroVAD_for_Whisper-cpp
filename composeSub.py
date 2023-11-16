import pysrt
import srt
import os
import json
import argparse

def load_chunk_timestamps(path):
    """
    Load timestamp file of chunks that saved from VAD.
    """
    print("Started loading timestamps from a json file")
    with open(path, "r") as fp:
        timestamps = json.load(fp)
        print("Done loading timestamps from .json file")
        return timestamps
    
def srt_parse_reader(path):
    """
    Script to load not-yet-reindex srt file that saved from pysrt.
    """
    with open(path, 'r') as f:
        sub =  f.read()
    return sub

def combine_naively_srt(chunk_timestamps):
    for chunk in range(len(chunk_timestamps)):
        if chunk==0:
            srt_name = f'./vad_chunks/{chunk}.srt'
            sub = pysrt.open(srt_name)
            os.remove(srt_name)
        else:
            srt_name = f'./vad_chunks/{chunk}.srt'
            sub_to_merge = pysrt.open(srt_name)
            offset = chunk_timestamps[chunk][0]['offset']
            sub_to_merge.shift(seconds=offset)
            sub += sub_to_merge
            os.remove(srt_name)
    return sub

def write_composed_srt(file, sub):
    """
    Script to recomposed srt file using srt package. """
    print("Begin writing a composed sub.")
    sub = srt.sort_and_reindex(sub)
    sub = srt.compose(sub)
    with open(file, 'w') as f:
        f.writelines(sub)
    print("Done writing a composed sub.")

if __name__=="__main__":
    parser = argparse.ArgumentParser(description="Combine srt files of VAD chunks and save as a completely composed subtitle.")
    parser.add_argument('-o', metavar='--OUTPUT', default="VAD_used_subtitle", help="Name of output srt file. Default: VAD_used_subtitle", required=False)
    args = parser.parse_args()
    output = args.o
    
    chunk_timestamps = load_chunk_timestamps('./vad_chunks/chunk_timestamps.json')
    sub = combine_naively_srt(chunk_timestamps)
    sub.save("sub_temp.srt")
    sub = srt.parse(srt_parse_reader('sub_temp.srt'))
    write_composed_srt(f"{output}.srt", sub) #save srt file by path name without type.
    os.remove("sub_temp.srt")