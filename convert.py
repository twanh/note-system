import os
import sys
import subprocess
from typing import List
import argparse

from tqdm import tqdm
from termcolor import colored

VERBOSE = False


def find_all_md_files(in_dir: str) -> List[str]:
    # puts(colored.blue(f"[INFO] Searching for markdown files in '{in_dir}'", ))
    print(
        colored("[INFO]", "blue", attrs=["bold"])
        + colored(f' Searching for files in "{in_dir}".', "blue")
    )
    # Check if the start dir exists
    if not os.path.isdir(in_dir):
        print(
            colored("[ERROR]", "red", attrs=["bold"])
            + colored(
                f"{in_dir} does not exist. Please provide a valid input directory."
            )
        )
        sys.exit(1)

    start_dir_path = os.path.abspath(in_dir)
    # Walk through the dir and create a list of all the exact paths to the files
    md_files = []
    for path, _, files in os.walk(start_dir_path):
        for file in files:
            full_path = os.path.join(path, file)
            if VERBOSE:
                print(
                    colored("[VEROSE] ", "yellow", attrs=["bold"])
                    + colored(f"found file: {file}", "yellow")
                )
                # with indent(4):
                # puts(colored.blue('Found file:') + colored.blue(full_path))
            md_files.append(full_path)

    print(
        colored("[INFO] ", "blue", attrs=["bold"])
        + colored(f"found {len(md_files)} files to convert.", "blue")
    )

    return md_files


def convert_file(in_file: str, out_file: str):
    # pandoc {infile} -o recov.html  --template GitHub.html5
    command = f"pandoc {in_file} -o {out_file} --template GitHub.html5"
    try:
        if VERBOSE:
            tqdm.write(
                colored("[VEROSE] ", "yellow", attrs=["bold"])
                + colored("Converted ", "yellow")
                + colored(in_file, "yellow")
                + colored(" ➜  ", "yellow", attrs=["bold"])
                + colored(out_file, "yellow")
            )
        subprocess.run(
            command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError as e:
        tqdm.write(colored("[ERROR] ", 'red', attrs=['bold']) + colored(f"Could not convert {in_file} into {out_file}", 'red'))
        if VERBOSE:
            tqdm.write(colored('[VERBOSE] ', 'yellow', attrs=['bold']) + colored(f"Error {e}", 'yellow'))


### DEFINE THE ARGUMENTS
ap = argparse.ArgumentParser()
ap.add_argument("indir", help="The input directory")
ap.add_argument("outdir", help="The output directory")
ap.add_argument("--verbose", help="Enable verbose mode", action="store_true")

# Covert all files into html (store in html folder)

if __name__ == "__main__":

    # Handle input arguments
    args = ap.parse_args()
    in_dir = args.indir
    out_dir = args.outdir
    VERBOSE = args.verbose

    files = find_all_md_files(in_dir)

    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)
    out_dir = os.path.abspath(out_dir)

    print(colored('[INFO] ', 'blue', attrs=['bold']) + colored('Starting conversion.', 'blue'))
    print('')
    # Loop over all the files that need to be converted, using tqdm for progress bar
    for file_path in tqdm(files, desc="Converting", ascii=True, colour="blue"):
        dir_path = file_path[len(os.path.abspath(in_dir)) :]
        # TODO: Adapt for windows
        dirs = dir_path.split("/")[1:-1]
        cur_path = out_dir
        # Create all (sub) directories needed
        for d in dirs:
            cur_path = os.path.join(cur_path, d)
            if not os.path.isdir(cur_path):
                if VERBOSE:
                    print(colored('[VEROSE] ', 'yellow', attrs=['bold']) + colored(f'Making new directory: {cur_path}'))
                os.mkdir(cur_path)
        filename_with_ext = file_path.split("/")[-1]
        filename = filename_with_ext.replace(".md", ".html")
        out_file_path = os.path.join(cur_path, filename)
        convert_file(file_path, out_file_path)
