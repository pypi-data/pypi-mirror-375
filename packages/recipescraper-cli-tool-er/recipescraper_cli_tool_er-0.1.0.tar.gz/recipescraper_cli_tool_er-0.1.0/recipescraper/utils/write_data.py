from pathlib import Path

def write_data(arr, file_name):
    current_dir = Path.cwd()
    file_path = Path(f'{current_dir}/{file_name}.txt')
         
    if file_path.exists():
     print(f'\nTxt file of the {file_name} recipe already exist.\n')
    else:
     for val in arr:
        with open(f'{file_name}.txt', 'a') as f:
            f.write(f'{val}\n')
                    