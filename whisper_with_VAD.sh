#!/bin/bash
set -e  # Stop execution if any command fails

#Initialize Conda
eval "$(conda shell.bash hook)"

#Check if whisper environment is active.
ENV_NAME="whisper"
if [[ -z "$CONDA_DEFAULT_ENV" ]]; then
    echo "No Conda environment is currently active."
    exit 1
else
    if [[ "$CONDA_DEFAULT_ENV" == "$ENV_NAME" ]]; then
        echo "The Conda environment '$ENV_NAME' is currently active."
    else
        echo "Activate "$ENV_NAME" Conda environment."
        conda activate "$ENV_NAME"
    fi
fi

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

# Extract the directory, filename, and extension of the input file
input_dir=$(dirname "$file_name")
input_base=$(basename "$file_name")
input_name="${input_base%.*}"
input_ext="${input_base##*.}"
if [ -e "${input_dir}/${input_name}_output.srt" ]; then
    rm -r "${input_dir}/${input_name}_output.srt"
    echo "echo "Removed existing ${input_dir}/${input_name}_output.srt.";";
fi

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
python VAD_Whisper-cpp/runVAD.py -uo -f "${file_name}" -vt 0.6

#Passing all chunk files into whisper
files=""
# Iterate over files in the folder
cd vad_chunks/
for file in $(ls -v *.wav | sort -n); do
    # Add the file to the array
    files+="vad_chunks/$file "
done
cd ..

# Check if there are files to process
if [ ${#files[@]} -gt 0 ]; then
    # Run Whisper
    #./whisper.cpp/main -m $model_path -mc 5 -et 2.4 -osrt -pc -f $files -l ja -fa
    ### Switch to whisper-cli as the main whisper.cpp repo.
    ./whisper.cpp/build/bin/whisper-cli -m $model_path -osrt -pc -f $files -l ja -fa -mc 5 -et 2.4 #-tr #v3-turbo no traslation supported.
    #echo $files
else
    echo "No files found in the folder. Exiting.";
    exit 1;
fi

#Create final subtitle
output_name="${input_name}_output"
python VAD_Whisper-cpp/composeSub.py -o "${input_dir}/${output_name}"
if [ -e "${input_dir}/${output_name}.srt" ]; then
    rm -r vad_chunks
    echo "Output subtitle: ${input_dir}/${output_name}.srt";
else
    echo "${input_dir}/${output_name}.srt not found!";
    exit 1;
fi

#Translate the subtitle
INPUT_SRT="${input_dir}/${input_name}_output.srt"
OUTPUT_SRT="${input_dir}/${input_name}.srt"
DEST_LANG="en"
SRC_LANG="ja"
echo "Translating ${INPUT_SRT} from ${SRC_LANG} to ${DEST_LANG}..."
python VAD_Whisper-cpp/srt_translate.py -i "${INPUT_SRT}" -o "${OUTPUT_SRT}" -dest "${DEST_LANG}" -src "${SRC_LANG}"
# Check if the translation was successful
if [ -e "${OUTPUT_SRT}" ]; then
    rm -r "${INPUT_SRT}"
    echo "Translation completed. Output file: ${OUTPUT_SRT}"
else
    echo "Unable to translate the subtitle.;
    echo "Leaving the original file: ${INPUT_SRT}"."
    exit 1;
fi