#!/usr/bin/env python3

import sys
import argparse
from cb_bsdl_parser.cb_bsdl import CBBsdl


def print_bsr_table(bsdl, bsdl_file):
    print(f'BSDL file: {bsdl_file}')
    bsdl.print_bsr_table()

def print_cell_info(bsdl, cell):
    print(f'Information for cell: {cell}')
    try:
        print(f'  data_cell:  {bsdl.get_bsr_data_cell(cell)}')
        print(f'  cell_type: {bsdl.get_bsr_cell_type(cell)}')
        print(f'  cell_desc: {bsdl.get_bsr_cell_desc(cell)}')
        print(f'  cell_func: {bsdl.get_bsr_cell_func(cell)}')
        print(f'  cell_val:  {bsdl.get_bsr_cell_val(cell)}')
        print(f'  ctrl_cell: {bsdl.get_bsr_ctrl_cell(cell)}')
    except Exception as e:
        print(f'Error retrieving information for cell {cell}: {e}')

def main():
    parser = argparse.ArgumentParser(description='Process a BSDL file.', usage='%(prog)s <bsdl_file> [--cell CELL] [--print-bsr-table]')
    parser.add_argument('bsdl_file', type=str, help='Path to the BSDL file')
    parser.add_argument('-c', '--cell', type=str, default=None, help='Cell name to query')
    parser.add_argument('-p', '--print-bsr-table', action='store_true', help='Print the BSR table')

    if len(sys.argv) == 1:
        parser.print_usage()
        sys.exit(1)


    args = parser.parse_args()

    bsdl = CBBsdl(args.bsdl_file)

    if args.print_bsr_table:
        print_bsr_table(bsdl, args.bsdl_file)

    if args.cell is not None:
        print_cell_info(bsdl, args.cell)

if __name__ == '__main__':
    main()