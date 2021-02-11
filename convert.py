import os
import subprocess
from typing import List
# Covert all files into html (store in html folder)


def find_all_md_files(in_dir: str) -> List[str]:

    # Check if the start dir exists
    if not os.path.isdir(in_dir):
        raise FileNotFoundError
    start_dir_path = os.path.abspath(in_dir)
    # Walk through the dir and create a list of all the exact paths to the files
    md_files = []
    for path, _, files in os.walk(start_dir_path):
        for file in files:
            full_path = os.path.join(path, file)
            # print(full_path)
            md_files.append(full_path)
    return md_files

def convert_file(filepath: str, outpath: str):
    # pandoc recovery.md -o recov.html  --template GitHub.html5
    command = f"pandoc {filepath} -o {outpath} --template GitHub.html5"
    print(f'Running command: {command}')
    try:
        subprocess.run(command,shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        print(f"Could not convert {filepath} into {outpath}")
        print(f"Error {e}")

if __name__ == "__main__":
    in_dir = 'test_docs'
    files = find_all_md_files(in_dir)
    out_dir = os.path.abspath('test')
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)
    for file_path in files:
        dir_path = file_path[len(os.path.abspath(in_dir)):]
        # TODO: Adapt for windows
        dirs = dir_path.split('/')[1:-1]
        cur_path = out_dir
        # Create all (sub) directories needed
        for d in dirs:
            cur_path = os.path.join(cur_path, d)
            if not os.path.isdir(cur_path):
                print(f"Making directory: {cur_path}")
                os.mkdir(cur_path)
        filename_with_ext = file_path.split('/')[-1]
        filename = filename_with_ext.replace('.md', '.html')
        print(f'Filename: {filename}')
        out_file_path = os.path.join(cur_path, filename)
        print(f'Converting {file_path} to {out_file_path}')
        convert_file(file_path, out_file_path)
    # convert_file(os.path.abspath('testfile.md'), 'test.html')

