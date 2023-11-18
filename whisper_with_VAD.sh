#!/bin/bash

usage() { printf "Usage: $(basename $0)\n [-f FILE_NAME]\n [-m MODEL_PATH]";}
f_flag=false
m_flag=false
while getopts ':f:m:h' opt; do
    case "$opt" in 
        f ) file_name="$OPTARG";;
        m ) model_path="$OPTARG";;
        h ) usage ; exit;;
        : ) echo "Option -$OPTARG requires an argument ">&2; exit 1;;
        \? ) echo "Invalid option: -$OPTARG" >&2; usage; exit 1;;
    esac
done

if ((OPTIND == 1))
then
    echo "No arguments specified";
    usage;
    exit;
fi

shift "$(($OPTIND -1))"

# Check if both arguments are provided
if [ -z "$file_name" ] || [ -z "$model_path" ]; then
  echo "Both -f and -m are required."
  exit 1
fi

#Make sure chunks folder exist or being empty.
folder_path=vad_chunks/
# Check if the chunks folder already exists
if [ -d "$folder_path" ]; then
    # Check if the folder is empty
    if [ -z "$(ls $folder_path)" ]; then
        echo "Chunks directory is empty."
    else
        # Clear the folder
        rm -rf $folder_path/*
        echo "Chunks directory cleared."
    fi
else
    # Create the folder
    mkdir -p "$folder_path"
    echo "Chunks directory created."
fi

#Run Silero-VAD and produce chunk files
python VAD_Whisper-cpp/runVAD.py -re -uo -f $file_name

#Passing all chunk files into whisper
files=""
# Iterate over files in the folder
for file in ./vad_chunks/*.wav; do
    # Add the file to the array
    files+="$file "
done

# Check if there are files to process
if [ ${#files[@]} -gt 0 ]; then
    ./whisper.cpp/main -m $model_path -l ja -tr -osrt -f $files 
    #echo $files
else
    echo "No files found in the folder. Exiting.";
    exit 1;
fi

# Extract the directory, filename, and extension of the input file
input_dir=$(dirname "$file_name")
input_base=$(basename "$file_name")
input_name="${input_base%.*}"
input_ext="${input_base##*.}"

#Create final subtitle
python VAD_Whisper-cpp/composeSub.py
output_name="${input_name}.srt"
mv VAD_used_subtitle.srt $output_name
rm -r vad_chunks
echo "Output subtitle: ${output_name}"
