import argparse
import os
import sys
import srt
import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from googletrans import Translator

def translate_subtitle(subtitle, translator, target_lang:str='en', source_lang:str='auto'):
    """Helper function to translate a single subtitle."""
    subtitle.content = translator.translate(subtitle.content, dest=target_lang, src=source_lang).text
    return subtitle

def translate_srt(input_file, output_file, target_lang='en', source_lang='auto', max_threads=None):
    """
    Translates an SRT file and saves the translated version.

    Args:
        input_file (str): Path to the input SRT file.
        output_file (str): Path to save the translated SRT file.
        target_lang (str): Target language code (e.g., 'en', 'es').
        source_lang (str): Source language code (e.g., 'auto', 'ja').
        max_threads (int, optional): Maximum number of threads for translation. Defaults to None (auto-detect).
    """
    # Read SRT file
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            subtitles = list(srt.parse(f.read()))
    except UnicodeDecodeError:
        print(f"Error: Could not decode the input file '{input_file}' with UTF-8 encoding. Trying with 'latin-1'.")
        try:
            with open(input_file, 'r', encoding='latin-1') as f:
                subtitles = list(srt.parse(f.read()))
        except UnicodeDecodeError:
            print(f"Error: Could not decode the input file '{input_file}' with 'latin-1' encoding either. Please check the file encoding.")
            sys.exit(1)
    except Exception as e:
        print(f"Error reading input file '{input_file}': {e}")
        sys.exit(1)
    
    translator = Translator()
    results = [None] * len(subtitles)
    
    if max_threads is None:
        max_threads = min(32, (os.cpu_count()) + 4)  # Default: min(32, CPU cores + 4)
    
    progress_bar = tqdm.tqdm(total=len(subtitles), desc="Translating", unit="subtitle")
    
    with ThreadPoolExecutor(max_threads) as executor:
        future_to_index = {executor.submit(translate_subtitle, subtitle, translator, target_lang, source_lang): i for i, subtitle in enumerate(subtitles)}
        
        for future in as_completed(future_to_index):
            index = future_to_index[future]
            try:
                results[index] = future.result()
            except Exception as e:
                print(f"Error translating subtitle at index {index}: {e}")
                results[index] = subtitles[index] # keep original subtitle if translation failed.
            progress_bar.update(1)
    
    progress_bar.close()
    
    # Write translated subtitles to output file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            # Ensure proper reindexing before composing
            results = srt.sort_and_reindex(results)
            f.write(srt.compose(results))
    except Exception as e:
        print(f"Error writing to output file '{output_file}': {e}")
        sys.exit(1)
    
    print(f"Translation complete! Translated file saved as {output_file}")

if __name__ == "__main__":
    parse = argparse.ArgumentParser(description="Translate SRT files using Google Translate API.")
    parse.add_argument('-i', metavar="--input_file", help="Input SRT file to translate", required=True)
    parse.add_argument('-o', metavar="--output_file", help="Output SRT file for translated subtitles", required=False)
    parse.add_argument('-dest', metavar="--target_lang", default="en", help="Target language for translation (default: 'en')")
    parse.add_argument('-src', metavar="--source_lang", default="auto", help="Source language for translation (default: 'auto')")
    parse.add_argument('--mt', metavar="--max_threads", type=int, default=None, help="Maximum number of threads to use (default: None, auto-detect)")
    args = parse.parse_args()
    input_srt = args.i
    output_srt = args.o if args.o else input_srt
    target_lang = args.dest
    source_lang = args.src
    max_threads = args.mt
    if not os.path.exists(input_srt):
        print(f"Input file '{input_srt}' does not exist.")
        sys.exit(1)
    if not os.path.isfile(input_srt):
        print(f"Input file '{input_srt}' is not a valid file.")
        sys.exit(1)
    if not input_srt.endswith('.srt'):
        print(f"Input file '{input_srt}' is not a valid SRT file.")
        sys.exit(1)
    if not output_srt.endswith('.srt'):
        print(f"Output file '{output_srt}' is not a valid SRT file.")
        sys.exit(1)
    
    translate_srt(input_srt, output_srt, target_lang, source_lang, max_threads)
