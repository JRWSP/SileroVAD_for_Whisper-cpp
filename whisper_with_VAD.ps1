param (
    [string]$file_name,
    [string]$model_path
)

function usage {
    Write-Host "Usage: $((Get-Command $MyInvocation.InvocationName).Name) -f FILE_NAME -m MODEL_PATH"
}

$ErrorActionPreference = "Stop"

if (-not $file_name -or -not $model_path) {
    usage
    exit 1
}
$folder_path = "vad_chunks"

# Check if the chunks folder already exists
if (-not (Test-Path $folder_path)) {
    New-Item -ItemType Directory -Path $folder_path | Out-Null
    Write-Host "Chunks directory created."
} else {
    # Check if the folder is empty
    if (-not (Get-ChildItem $folder_path)) {
        Write-Host "Chunks directory is empty."
    } else {
        # Clear the folder
        Remove-Item "$folder_path\*" -Force
        Write-Host "Chunks directory cleared."
    }
}

# Run Silero-VAD and produce chunk files
python VAD_Whisper-cpp/runVAD.py -re -uo -f $file_name

# Passing all chunk files into whisper
$files = Get-ChildItem -Path $folder_path -Filter *.wav | Sort-Object { [int]$_.BaseName }

if ($files.Count -gt 0) {
    $files = $files | ForEach-Object { "vad_chunks\$($_.Name)" }
    .\Whisperer\main.exe -m $model_path -mc 0 -l ja -tr -osrt -f $files
} else {
    Write-Host "No files found in the folder. Exiting."
    exit 1
}

# Extract the directory, filename, and extension of the input file
$input_dir = Split-Path $file_name -Parent
$input_base = [System.IO.Path]::GetFileNameWithoutExtension($file_name)
$input_name = [System.IO.Path]::GetFileName($file_name)
$input_ext = [System.IO.Path]::GetExtension($file_name)


# Determine the output directory based on the input file
$output_dir = (Get-Item $file_name).Directory.FullName
$output_path = Join-Path $output_dir "output.srt"
# Create final subtitle
$output_name = [System.IO.Path]::GetFileNameWithoutExtension($file_name)
$output_path = Join-Path $output_dir "${output_name}_output.srt"
python VAD_Whisper-cpp/composeSub.py -o $output_path

Remove-Item -Path $folder_path -Recurse -Force
Write-Host "Output subtitle: $output_path"
