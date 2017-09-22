import os
import csv
from collections import deque
import argparse
import pandas

# def main(working_dir = '.', price_col = 0, data_new_offset=2, data_old_offset=1):
#     for fn in os.listdir(working_dir):
#         if os.path.isdir(fn) and 'csv' in fn:
#             fn_type, fn_name = get_fn_pieces(fn)
#             if fn_type == 'data': get_truth_from_data(fn, new_offset=data_new_offset, old_offset=data_old_offset)
#             else: continue

def get_truth_from_data(data_dir, skip_reverse = False, price_col=0, new_offset=2, old_offset=1, save_dir=None, get_dataframe=True):
    price_col += 1 # skip date col
    new_offset, old_offset = abs(new_offset), abs(old_offset)
    rowset_len = max(new_offset, old_offset) + 1 # include current row
    save_output = not save_dir is None
    output = {}

    if save_output: os.makedirs(save_dir, exist_ok=True)

    for fn in os.listdir(data_dir):
        if skip_reverse and fn.lower().startswith('reverse_'): continue
        rowset = deque(maxlen=rowset_len)

        with open(os.path.join(data_dir, fn), 'r') as fr, open(os.path.join(save_dir, fn), 'w', newline='\n') if save_output else None as fw:
            csvr = csv.reader(fr)
            if save_output: csvw = csv.writer(fw)
            if get_dataframe: df = pandas.DataFrame(data=None, columns=['Class','Delta']) # Delta is unused in rest of project

            end = False
            while not end:
                for i in range(0, rowset_len if len(rowset) == 0 else 1):
                    try: 
                        rowset.append(next(csvr))
                    except Exception as e:
                        end = True
                        break

                if end: break

                delta = float(rowset[new_offset][price_col]) - float(rowset[old_offset][price_col])
                row = [
                    rowset[0][0].translate(rowset[0][0].maketrans('', '', 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_-`{|}~ \t\n\r\x0b\x0c')) #TimePoint, remove non-numeric chars
                    , 0 if delta == 0 else 1 if delta > 0 else -1
                    , delta
                ]
                if not save_dir is None: csvw.writerow(row)
                if get_dataframe: df = df.append(pandas.DataFrame([row[1:]], index=[row[0]], columns=['Class','Delta']))

            if get_dataframe: output[fn] = df

    if get_dataframe: return fn
    # else: return None

def read_truth_from_dir(truth_dir, skip_reverse = False):
    output = {}

    for fn in os.listdir(truth_dir):
        if skip_reverse and fn.lower().startswith('reverse_'): continue
        output[fn] = pandas.read_csv(os.path.join(truth_dir, fn), header=None, names=['TimePoint', 'Class'], index_col=0)

    return output

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--col', '-c', type=int, default=0
        , help='Price column starting after date')
    parser.add_argument('--newoffset', '-n', type=int, default=2)
    parser.add_argument('--oldoffset', '-o', type=int, default=1)
    parser.add_argument('--workingdir', '-w', type=str, default='.')
    return parser.parse_args()

# if __name__ == "__main__":
#     args = get_args()
#     main(working_dir=args.workingdir, price_col=args.col, data_new_offset=args.newoffset, data_old_offset=args.oldoffset)
