from os import listdir
from os.path import isfile, join
from pathlib import Path

file_path = 'server\\files'
files = [f for f in listdir(file_path) if isfile(join(file_path, f))]
size = [Path(join(file_path, f)).stat().st_size for f in files]
print(files)
print(size)
