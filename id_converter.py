#!/usr/bin/env python3

import csv
import sys
import argparse
import os
from collections import defaultdict
import pickle

ID_MAP_FILE = './id_mapping'

def read_id_mapping(map_path):
    id_maps = defaultdict(dict)
    if os.path.exists(map_path) == True:
        with open(map_path, 'rb') as f:
            id_maps = pickle.load(f)
    return id_maps

def write_id_mapping(id_maps, map_path):
    with open(map_path, 'wb') as f:
        pickle.dump(id_maps, f)

def check_input_csv(path, help):
    if os.path.exists(path) == False:
        print("\n" + "Could not find the file '{}'.".format(path) + "\n")
        help()
        sys.exit(1)
    else:
        path_parts = path.split('_')
        if len(path_parts) < 2:
            print("\n" + "The file name '{}' has no 'servername'.".format(path) + "\n")
            help()
            sys.exit(1)

def check_output_csv(path, help):
    if os.path.exists(path) == True:
        print("\n" + "The file, '{}', you specified exists.".format(path) + "\n")
        help()
        sys.exit(1)

def get_max_id(id_maps):
    if len(id_maps) == 0:
        return 1
    else:
        wk_max = -1
        for k, v in id_maps.items():
            wk_max = max(wk_max, max(v.values()))
        return wk_max + 1

def show_id_maps(id_maps):
    print("Current ID mapping is as follows.")
    for k, v in id_maps.items():
        print(k, v)

def convert_csv(in_path, out_path, column, id_maps, max_id):
    path_parts = in_path.split('_')
    server_name = path_parts[0]
    table_name = path_parts[1].split('.')[0]
    with open(in_path, "r") as in_f:
        reader = csv.reader(in_f)
        with open(out_path, "w") as out_f:
            writer = csv.writer(out_f)
            for row in reader:
                if len(row) != 0:
                    try:
                        new_id = id_maps[server_name][row[column]]
                    except:
                        new_id = max_id
                        id_maps[server_name][row[column]] = new_id
                        max_id += 1
                    row[column] = new_id
                    writer.writerow(row)

def main():
    parser = argparse.ArgumentParser(description = "Convert 'Local' ID to 'Global' unique ID in CSV.")
    parser.add_argument("input_csv",
        help = "Source CSV to be converted. It should be named 'servername_tablename.csv' format.")
    parser.add_argument("output_csv",
        help = "Target CSV as a result of converting.")
    parser.add_argument("--column", "-c",
        type = int,
        default = 0,
        help = "Column number of 'Local ID' (default: 0)")
    parser.add_argument("--map", "-m",
        type = str,
        default = ID_MAP_FILE,
        help = "ID mapping file (default: {})".format(ID_MAP_FILE))

    args = parser.parse_args()

    check_input_csv(args.input_csv, parser.print_help)
    check_output_csv(args.output_csv, parser.print_help)

    id_maps = read_id_mapping(args.map)
    max_id = get_max_id(id_maps)

    convert_csv(args.input_csv, args.output_csv, args.column, id_maps, max_id)

    write_id_mapping(id_maps, args.map)
    
    show_id_maps(id_maps)

if __name__ == "__main__":
    main()