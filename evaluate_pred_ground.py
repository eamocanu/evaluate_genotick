import os
import csv
import argparse
import itertools
import numpy as np
import matplotlib.pyplot as plt
from sklearn.calibration import calibration_curve
from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_curve
from sklearn.metrics import roc_auc_score

# condition = predicted
# data/class = actual (ground)

def main(pred_dir, ground_dir, start_point = None, end_point = None, instruments = [], mode = [], output_type = [], output_name=None, bins=5):
    ground_classes, pred_classes, scores = get_classes_scores_from_dir(pred_dir, ground_dir, start_point=start_point, end_point = end_point, instruments = instruments)

    print('Mode: {} | Instruments: {}'.format(','.join(mode) if len(mode) > 0 else 'All', ','.join(instruments) if len(instruments) > 0 else 'All'))

    output_file = len(output_type) > 0 and ('file' in output_type or 'image' in output_type or 'picture' in output_type or 'pic' in output_type or 'img' in output_type or 'png' in output_type)
    output_live = len(output_type) <= 0 or ('window' in output_type or 'console' in output_type or 'live' in output_type or 'view' in output_type or 'show' in output_type)

    get_metric_plots(ground_classes, pred_classes, scores, output_file, output_live)

def get_metric_plots(truth_classes, predicted_classes, scores, mode=[], output_file = False, output_live = True, output_name=None):
    # if len(mode) <= 0 or 'calibration' in mode:
    #     cal = calibration_curve(truth_classes, scores, n_bins=bins)
    #     plot_calibration(cal, predicted_classes, bins=bins, name='Genotick')
    #     if output_file: plt.savefig('{}_calibration.png'.format(output_name if not output_name is None and not len(output_name) <= 0 else 'output'))

    if len(mode) <= 0 or 'confusion' in mode or 'matrix' in mode:
        matrix = get_confusion_matrix(truth_classes, predicted_classes, scores)
        plot_confusion_matrix(matrix, ['Up', 'Down'], normalize=True)
        if output_file: plt.savefig('{}_confusion.png'.format(output_name if not output_name is None and not len(output_name) <= 0 else 'output'))

    if len(mode) <= 0 or 'roc' in mode:
        roc, auc = get_roc_auc(truth_classes, scores)
        plot_roc(roc, auc)
        if output_file: plt.savefig('{}_roc.png'.format(output_name if not output_name is None and not len(output_name) <= 0 else 'output'))

    if output_live: plt.show()

def plot_calibration(cal, prob_pos, bins=10, name=None):
    plt.figure()#figsize=(10, 10))
    ax1 = plt.subplot2grid((3, 1), (0, 0), rowspan=2)
    
    ax1.plot([0, 1], [0, 1], "k:", label="Perfectly calibrated")
    fraction_of_positives, mean_predicted_value = cal

    ax1.plot(mean_predicted_value, fraction_of_positives, "s-",
            label='%s' % (name, ))
    ax1.set_ylabel("Fraction of positives")
    ax1.set_ylim([-0.05, 1.05])
    ax1.legend(loc="lower right")
    ax1.set_title('Calibration plots  (reliability curve)')

    # todo: class probabilities need scores of all classes, not just the positive one

    # ax2 = plt.subplot2grid((3, 1), (2, 0))

    # ax2.hist(prob_pos, range=(0, 1), bins=bins, label=name,
    #     histtype="step", lw=2)

    # ax2.set_xlabel("Mean predicted value")
    # ax2.set_ylabel("Count")
    # ax2.legend(loc="upper center", ncol=2)

    plt.tight_layout()
    #return plt

def plot_roc(roc, auc, start_point = None, end_point = None):
    fpr, tpr, thresholds = roc
    plt.figure()
    lw = 2
    plt.plot(fpr, tpr, color='g',
            lw=lw, label='ROC (area = %0.8f)' % auc)
    plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver operating characteristic{}{}'.format(
        ' {}'.format(start_point) if not start_point is None else ''
        , ' - {}'.format(end_point) if not start_point is None and not end_point is None else ''
    ))
    plt.legend(loc="lower right")

    #return plt

def plot_confusion_matrix(cm, classes,
                          normalize=False,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        #print("Normalized confusion matrix")
    #else:
    #    print('Confusion matrix, without normalization')

    #print(cm)

    plt.figure()

    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, format(cm[i, j], fmt),
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')

    #return plt

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

def get_prediction_classes_scores_from_df_dict(predictions, truth_classes, drop_out_prediction = True):
    predicted_classes, scores = [], []

    for name in predictions:
        if name not in truth_classes: continue
        for index, row in predictions[name]:
            if index not in truth_classes[name].index: continue
            else:
                if drop_out_prediction and row['Prediction'] == 0: continue
                predicted_classes.append(row['Prediction'])
                scores.append(row['Score'])

    return predicted_classes, scores

def get_classes_scores_from_dir(pred_dir, ground_dir, start_point = None, end_point = None, instruments = [], drop_out_prediction = True, skip_reverse=False):
    ground_classes, pred_classes, scores = [], [], []
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

        new_ground_classes, new_pred_classes, new_scores = get_classes_scores_from_fn(fn, ground_fn, start_point, end_point, drop_out_prediction)
        ground_classes += new_ground_classes
        pred_classes += new_pred_classes
        scores += new_scores

        #print('True count: {} | Predicted count: {}'.format(len(ground_classes), len(pred_classes)))

        satisfied += 1
        if len(instruments) > 0 and satisfied >= len(instruments): break

    if len(pred_classes) == 0:
        raise ValueError('No predicted classes found')
    elif len(ground_classes) != len(pred_classes) or len(scores) != len(pred_classes):
        raise ValueError('Class and score counts are not equal: {}, {}, {}'.format(len(ground_classes), len(pred_classes), len(scores)))

    return ground_classes, pred_classes, scores

def get_classes_scores_from_fn(pred_fn, ground_fn, start_point=None, end_point=None, drop_out_prediction=True):
    if isinstance(start_point, str): start_point = int(start_point)
    if isinstance(end_point, str): end_point = int(end_point)
    col_pred_date, col_pred_class, col_pred_score = 0, 1, 2
    col_ground_date, col_ground_class = 0, 1
    ground_classes, pred_classes, scores = [], [], []

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
            scores.append(float(pred_row[col_pred_score]))

    return ground_classes, pred_classes, scores

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
