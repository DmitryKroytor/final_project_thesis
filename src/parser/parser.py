import os
import traceback
import pandas as pd


RAW_MAPS_PATH = 'raw_data/maps'
PARSED_MAPS_PATH = 'parsed_data/maps'
RAW_VAC_PATH = 'raw_data/vac'
RAW_OLD_VAC_PATH = 'raw_data/old_vacs'
PARSED_VAC_PATH = 'parsed_data/vac'


def parse_row_data_from_txt_to_csv(data_type, input_path, output_path, column_names, number_of_ignore_lines=0):
    names = [name for name in os.listdir(input_path)]

    for name in names:
        try:
            title = process_title(data_type, name)
            with open(f"{input_path}/{name}", "r", encoding="utf-8") as infile, \
                    open(f"{output_path}/{title[:-4]}.csv", "w", encoding="utf-8") as outfile:
                outfile.write(column_names + "\n")

                if number_of_ignore_lines > 0:
                    for _ in range(number_of_ignore_lines):
                        next(infile, None)
                if data_type == 'vacs':
                    for line in infile:
                        line = line.replace(",", ".")
                        line = line.replace("	", ",")
                        outfile.write(line)
                if data_type == 'maps' or data_type == 'old_vacs':
                    for line in infile:
                        line = line.replace("	", ",")
                        outfile.write(line)
        except Exception as e:
            print(f"Error with file {name}: {str(e)}")
            traceback.print_exc()


def clear_maps():
    names = [name for name in os.listdir(PARSED_MAPS_PATH)]

    for name in names:
        df = pd.read_csv(f'{PARSED_MAPS_PATH}/{name}')
        df.drop(columns=["delme"], inplace=True)
        df['title'] = name[:-4]
        df.to_csv(f'{PARSED_MAPS_PATH}/{name}', index=False)


def clear_vacs():
    names = [name for name in os.listdir(PARSED_VAC_PATH)]

    for name in names:
        df = pd.read_csv(f'{PARSED_VAC_PATH}/{name}')
        df.drop(columns=["delme"], inplace=True)
        if "empty" and "index" in df.columns:
            df.drop(columns=["empty", "index"], inplace=True)
        df['title'] = name[:-4]
        if not (name.startswith('128') or name.startswith('129')):
            df['U'] = df['U'] * -1
            df['U'] = df['U'] * 1e-6
        df.to_csv(f'{PARSED_VAC_PATH}/{name}', index=False)


def process_title(data_type, title):
    if data_type == 'maps':
        return process_map_title(title)
    if data_type == 'vacs':
        return process_vac_title(title)
    if data_type == 'old_vacs':
        return process_old_vac_title(title)
    return title


def process_map_title(title):
    if title.startswith('2024'):
        return title[-11:]
    else:
        return title.split()[-1]


def process_vac_title(title):
    if 'N' in title:
        return title.split('N', 1)[1]
    elif '№' in title:
        return title.split('№', 1)[1]
    return title


def process_old_vac_title(title):
    parts = title.split('_')
    if len(parts) >= 4:
        return parts[3] + '.txt'
    return title

parse_row_data_from_txt_to_csv(
    "maps",
    RAW_MAPS_PATH,
    PARSED_MAPS_PATH,
    "x,y,delme,B",
    5
)
clear_maps()

parse_row_data_from_txt_to_csv(
    "vacs",
    RAW_VAC_PATH,
    PARSED_VAC_PATH,
    "index,I,U,delme,empty",
    4
)
parse_row_data_from_txt_to_csv(
    "old_vacs",
    RAW_OLD_VAC_PATH,
    PARSED_VAC_PATH,
    "I,U,delme"
)
clear_vacs()