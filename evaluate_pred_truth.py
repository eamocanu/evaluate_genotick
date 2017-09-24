import os
import csv
import argparse
import itertools
import matplotlib.pyplot as plt
import scikitplot as skplt

# condition = predicted
# data/class = actual (ground)

def main(pred_dir, ground_dir, start_point = None, end_point = None, instruments = [], mode = [], output_type = [], output_name=None, bins=5):
    ground_classes, pred_classes, scores, probas = get_classes_scores_from_dir(pred_dir, ground_dir, start_point=start_point, end_point = end_point, instruments = instruments)

    print('Mode: {} | Instruments: {}'.format(','.join(mode) if len(mode) > 0 else 'All', ','.join(instruments) if len(instruments) > 0 else 'All'))

    output_file = len(output_type) > 0 and ('file' in output_type or 'image' in output_type or 'picture' in output_type or 'pic' in output_type or 'img' in output_type or 'png' in output_type)
    output_live = len(output_type) <= 0 or ('window' in output_type or 'console' in output_type or 'live' in output_type or 'view' in output_type or 'show' in output_type)

    get_metric_plots(ground_classes, pred_classes, scores, probas, output_file, output_live)

def get_metric_plots(truth_classes, predicted_classes, scores, probas, mode=[], output_file = False, output_live = True, output_name=None):
    filename_suffix = output_name if not output_name is None and not len(output_name) <= 0 else 'output'

    if len(mode) <= 0 or 'confusion' in mode or 'matrix' in mode:
        # matrix = get_confusion_matrix(truth_classes, predicted_classes, scores)
        # plot_confusion_matrix(matrix, ['Up', 'Down'], normalize=True)
        skplt.metrics.plot_confusion_matrix(truth_classes, predicted_classes, normalize=True)
        if output_file: plt.savefig('{}_confusion.png'.format(filename_suffix))

    if len(mode) <= 0 or 'roc' in mode:
        # roc, auc = get_roc_auc(truth_classes, scores)
        # plot_roc(roc, auc)
        skplt.metrics.plot_roc_curve(truth_classes, probas)
        if output_file: plt.savefig('{}_roc.png'.format(filename_suffix))

    if len(mode) <= 0 or 'precision-recall' in mode or 'precision' in mode or 'recall' in mode:
        skplt.metrics.plot_precision_recall_curve(truth_classes, probas)
        if output_file: plt.savefig('{}_precision-recall.png'.format(filename_suffix))

    if len(mode) <= 0 or 'calibration' in mode:
        #cal = calibration_curve(truth_classes, scores, n_bins=bins)
        #plot_calibration(cal, predicted_classes, bins=bins, name='Genotick')
        skplt.metrics.plot_calibration_curve(truth_classes, probas_list=[probas], clf_names=['Genotick'])
        if output_file: plt.savefig('{}_calibration.png'.format(filename_suffix))

    # if len(mode) <= 0 or 'silhouette' in mode:
    #     skplt.metrics.plot_silhouette()

    if output_live: plt.show()

def get_roc_auc(ground_classes, scores):
    roc = roc_curve(ground_classes, scores)
    auc = roc_auc_score(ground_classes, scores)
    return roc, auc

def get_confusion_matrix(ground_classes, pred_classes, scores):
    if len(pred_classes) == 0:
        raise ValueError('No predicted classes found')
    elif len(ground_classes) != len(pred_classes) or len(scores) != len(pred_classes):
        raise ValueError('Class and score counts are not equal: {}, {}, {}'.format(len(ground_classes), len(pred_classes), len(scores)))

    matrix = confusion_matrix(ground_classes, pred_classes, [1,-1])
    return matrix

def get_classes_scores_from_df_dict(predict_dict, truth_dict, start_point = None, end_point = None, instruments = [], drop_out_prediction = True, skip_reverse=False, score_by_positive_class = False):
    truth_classes, predict_classes, scores, probas = [], [], [], []

    for name in predict_dict:
        if name not in truth_dict: continue
        if len(instruments) > 0 and name not in instruments: continue
        if skip_reverse and name.startswith('_reverse'): continue

        for index, row in predict_dict[name].iterrows():
            if (not start_point is None and int(index) < start_point) or (not end_point is None and int(index) > end_point): continue
            if drop_out_prediction and row['Prediction'] == 0: continue

            try: truth_row = truth_dict[name].loc[index]
            except: continue
            truth_class = 1 if truth_row['Class'] == 0 else truth_row['Class']

            truth_classes.append(truth_class)
            predict_classes.append(row['Prediction'])
            if score_by_positive_class:
                scores.append(row['Score'])
                probas.append([
                    row['Score'] if row['Prediction'] < 0 else 1-row['Score']
                    , row['Score'] if row['Prediction'] > 0 else 1-row['Score']
                ])
            else:
                scores.append(row['ScoreUp'])
                probas.append([row['ScoreDown'], row['ScoreUp']])

    return truth_classes, predict_classes, scores, probas

def get_classes_scores_from_dir(pred_dir, ground_dir, start_point = None, end_point = None, instruments = [], drop_out_prediction = True, skip_reverse=False, score_by_positive_class = False):
    ground_classes, pred_classes, scores, probas = [], [], [], []
    satisfied = 0
    for fn in os.listdir(pred_dir):
        fn_instrument = fn.split('_', 1)[0]
        if len(instruments) > 0 and fn_instrument not in instruments: continue
        elif '.csv' not in fn: continue
        elif skip_reverse and fn.startswith('reverse_'): continue

        ground_fn = find_ground_fn(ground_dir, fn)
        if ground_fn is None: continue
        else: fn, ground_fn = os.path.join(pred_dir, fn), os.path.join(ground_dir, ground_fn)

        #print('Processing {} | {}'.format(fn, ground_fn))
        print('Processing {}'.format(fn))

        new_ground_classes, new_pred_classes, new_scores, new_probas = get_classes_scores_from_fn(fn, ground_fn, start_point, end_point, drop_out_prediction, score_by_positive_class)
        ground_classes += new_ground_classes
        pred_classes += new_pred_classes
        scores += new_scores
        probas += new_probas

        #print('True count: {} | Predicted count: {}'.format(len(ground_classes), len(pred_classes)))

        satisfied += 1
        if len(instruments) > 0 and satisfied >= len(instruments): break

    if len(pred_classes) == 0:
        raise ValueError('No predicted classes found')
    elif len(ground_classes) != len(pred_classes) or len(scores) != len(pred_classes):
        raise ValueError('Class and score counts are not equal: {}, {}, {}'.format(len(ground_classes), len(pred_classes), len(scores)))

    return ground_classes, pred_classes, scores, probas

def get_classes_scores_from_fn(pred_fn, ground_fn, start_point=None, end_point=None, drop_out_prediction=True, score_by_positive_class = False):
    if isinstance(start_point, str): start_point = int(start_point)
    if isinstance(end_point, str): end_point = int(end_point)
    col_pred_date, col_pred_class, col_pred_score = 0, 1, 2
    col_pred_scoredown, col_pred_scoreup = 2, 3
    col_ground_date, col_ground_class = 0, 1
    ground_classes, pred_classes, scores, probas = [], [], [], []

    with open(pred_fn, 'r') as pred_fr, open(ground_fn, 'r') as ground_fr:
        pred_csvr = csv.reader(pred_fr)
        ground_csvr = csv.reader(ground_fr)
        ground_comparerow = []

        for pred_row in pred_csvr:
            pred_point = int(pred_row[col_pred_date])
            if not end_point is None and end_point > -1 and pred_point > end_point: break
            if not start_point is None and start_point > -1 and pred_point < start_point: continue

            pred_class = int(pred_row[col_pred_class])
            if drop_out_prediction and pred_class == 0: continue

            skip = False
            if len(ground_comparerow) <= col_ground_date or int(ground_comparerow[col_ground_date]) != pred_point:
                ground_comparerow = []
                for ground_row in ground_csvr:
                    ground_point = int(ground_row[col_ground_date])
                    if ground_point < pred_point: continue
                    skip = ground_point > pred_point
                    ground_comparerow = ground_row
                    break

            if skip or len(ground_comparerow) <= col_ground_date: continue
            compare_point = int(ground_comparerow[col_ground_date])
            if compare_point != pred_point: continue

            ground_class = 1 if int(ground_comparerow[col_ground_class]) == 0 else int(ground_comparerow[col_ground_class])
            ground_classes.append(ground_class)
            pred_classes.append(pred_class)
            if score_by_positive_class:
                scores.append(float(pred_row[col_pred_score]))
                probas.append([
                    int(pred_row[col_pred_score]) if pred_class < 0 else 1-float(pred_row[col_pred_score])
                    , int(pred_row[col_pred_score]) if pred_class > 0 else 1-float(pred_row[col_pred_score])
                ])
            else:
                scores.append(float(pred_row[col_pred_scoreup]))
                probas.append([float(pred_row[col_pred_scoredown]), float(pred_row[col_pred_scoreup])])

    return ground_classes, pred_classes, scores, probas

def find_ground_fn(ground_dir, pred_fn):
    pred_fn = pred_fn.replace('.csv', '')

    for fn in os.listdir(ground_dir):
        if fn.startswith(pred_fn): return fn

    print('Could not find data file for {}'.format(pred_fn))
    return None

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('preddir', type=str)
    parser.add_argument('grounddir', type=str)
    parser.add_argument('--start', '-s', type=int, default=None)
    parser.add_argument('--end', '-e', type=int, default=None)
    parser.add_argument('--instruments', '-i', type=str, nargs='+', default=[])
    parser.add_argument('--mode', '-m', type=str, nargs='+', default=[], help='Modes (default all): confusion, roc')
    parser.add_argument('--output', '-o', type=str, nargs='+', default=[])
    parser.add_argument('--outputname', '-n', type=str, default=None, help='Name to output plot images')
    return parser.parse_args()

if __name__ == "__main__":
    args = get_args()
    main(args.preddir, args.grounddir, start_point=args.start, end_point=args.end, instruments=args.instruments, mode=args.mode,              output_type=args.output, output_name=args.outputname)
