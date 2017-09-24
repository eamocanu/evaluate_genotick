import os
import csv
import argparse
import pandas

def main(working_dir='.', score_type='weight'):
    for fn in os.listdir(working_dir):
        if os.path.isfile(os.path.join(working_dir, fn)):
            fn_type, fn_name = get_fn_pieces(fn)
            if (fn_type == 'predictions' or fn_type == 'prediction') and 'csv' in fn:
                print('Processing {}'.format(fn))
                get_predictions_from_file(fn, working_dir=working_dir, score_type=score_type)
    print('Finished')

def get_predictions_from_file(fn, skip_reverse = False, col_prediction = 1, col_voteup = 4, col_votedown = 5, save_dir = None, score_by_positive_class = True, get_dataframe = True, format_is_tf_inst_time = False):
    col_prediction, col_voteup, col_votedown = col_prediction+1, col_voteup+1, col_votedown+1 # add for TimePoint
    if format_is_tf_inst_time: col_tf, col_inst, col_date = 0, 1, 2
    else: col_date, col_name = 0, 1
    save_output = not save_dir is None
    dest_files = {}
    output = {}

    if save_output: os.makedirs(save_dir, exist_ok=True)

    with open(fn, 'r') as fr:
        csvr = csv.reader(fr)
        for row in csvr:
            name = '{}_{}.csv'.format(row[col_inst], row[col_tf]) if format_is_tf_inst_time else os.path.basename(row[col_name])
            if skip_reverse and name.lower().startswith('reverse_'): continue

            if save_output:
                dest_fn = os.path.join(save_dir, name)
                if dest_fn in dest_files: dest_fw = dest_files[dest_fn]
                else:
                    dest_files[dest_fn] = open(dest_fn, 'w', newline='\n')
                    dest_fw = dest_files[dest_fn]
                csvw = csv.writer(dest_fw)

            if get_dataframe: 
                if not name in output: output[name] = []

            prediction = prediction_to_numeric(row[col_prediction])

            rowOut = [
                row[col_date]
                , prediction
            ]

            if prediction == 0: 
                rowOut += [0] if score_by_positive_class else [0,0]
            else:
                score_total = float(row[col_votedown]) + float(row[col_voteup])
                if score_by_positive_class:
                    rowOut += [float(row[col_voteup]) / score_total]
                else:
                    rowOut += [
                        float(row[col_votedown]) / score_total
                        , float(row[col_voteup]) / score_total
                    ]

            if save_output: csvw.writerow(rowOut)
            if get_dataframe: output[name].append(rowOut)

    if save_output: close_file_dict(dest_files)
    if get_dataframe: 
        for name in output:
            columns = ['TimePoint', 'Prediction','Score'] if score_by_positive_class else ['TimePoint','Prediction','ScoreDown','ScoreUp']
            output[name] = pandas.DataFrame(data=output[name], columns=columns)
            output[name].set_index('TimePoint', inplace=True)
        return output

def prediction_to_numeric(prediction):
    if prediction.isdigit(): return prediction
    elif prediction.upper() == 'UP': return 1
    elif prediction.upper() == 'DOWN': return -1
    else: return 0

def close_file_dict(file_dict):
    names = list(file_dict.keys())

    for fn in names:
        file_dict.pop(fn, None).close()

def get_fn_pieces(fn):
    pieces = fn.split('_', 1)
    return pieces[0], pieces[1] if len(pieces) > 1 else None

def read_predictions_from_dir(prediction_path, skip_reverse = False, score_by_positive_class=True):
    output = {}

    for fn in os.listdir(prediction_path):
        if skip_reverse and fn.lower().startswith('reverse_'): continue
        names = ['TimePoint', 'Prediction', 'Score'] if score_by_positive_class else ['TimePoint', 'Prediction', 'ScoreDown', 'ScoreUp']
        output[fn] = pandas.read_csv(os.path.join(prediction_path, fn), header=None, names=names, index_col=0)

    return output

def get_args():
    parser = argparse.ArgumentParser()
    #parser.add_argument('--col', '-c', type=int, default=0
    #    , help='Prediction column starting after date')
    parser.add_argument('--scoretype', '-t', type=str, default='weight_up'
        , help='Score method: weight, count, weight_up, weight_down, count_up, count_down')
    #parser.add_argument('--scoreoffset', '-k', type=int, default=6)
    parser.add_argument('--workingdir', '-w', type=str, default='.')
    return parser.parse_args()

if __name__ == "__main__":
    args = get_args()
    main(working_dir=args.workingdir, score_type=args.scoretype)
#       , prediction_col=args.col, score_offset=args.scoreoffset)
