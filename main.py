import argparse
import os
import data_to_ground as d2g
import predictions_to_pred as p2p
import evaluate_pred_ground as epg
import matplotlib.pyplot as plt

def main(predict_dir, truth_dir \
        , data_dir = None \
        , predictions_file = None \
        , start_point = None \
        , end_point = None \
        # , truth_save_dir = None \
        , skip_reverse = False \
        , mode = [] \
        , suppress_display = False \
        , output_files = False \
        , output_name = None \
        , price_col = 3 \
        , new_price_row = 1 \
        , old_price_row = 0 \
        , prediction_col = 1 \
        , weight_up_col = 4 \
        , weight_down_col = 5 \
):
    if not data_dir is None and os.path.isdir(data_dir): # process data
        d2g.get_truth_from_data(data_dir = data_dir, skip_reverse = skip_reverse, price_col = price_col, new_offset = new_price_row, old_offset = old_price_row, save_dir = truth_dir, get_dataframe=False)

    if not predictions_file is None and os.path.isfile(predictions_file): # process predictions
        p2p.get_predictions_from_file(predictions_file, skip_reverse = skip_reverse, col_prediction = prediction_col, col_voteup = weight_up_col, col_votedown = weight_down_col, save_dir = predict_dir, get_dataframe = False)

    truth_classes, predicted_classes, scores = epg.get_classes_scores_from_dir(predict_dir, truth_dir, start_point = start_point, end_point = end_point, skip_reverse = skip_reverse)

    epg.get_metric_plots(truth_classes, predicted_classes, scores, mode = [], output_file = output_files, output_live = not suppress_display)

    print('Finished')

def get_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description='''Generate machine learning metrics from Genotick predictions.
You need a predictions_x.csv and the original data/ directory.

Suggested use, first time (to generate market readings):

    main.py "./predict" "./truth" --data "./data" 
        --predictions "predictions_x.csv" --start 20170101 
        --skipreverse --outputfiles

Suggested use, with already-generated market readings:

    main.py "./predict" "./truth" --start 20170101 
        --skipreverse --outputfiles

''', epilog='''Column and row defaults (--pricecol, --newpricerow, etc.) should already work
for Genotick. Use these settings only if you have differently formatted CSV files.''')
    parser.add_argument('predictdir', type=str
        , help='Directory with predicted market readings. If --predictions is passed, generate and save the readings to this dir. Else, read the readings.')
    parser.add_argument('truthdir', type=str
        , help='Directory with actual market readings. If --data is passed, generate and save the readings. Else, read the readings.')
    parser.add_argument('--data', '-d', type=str, default=None
        , help='Data directory to generate market readings.')
    parser.add_argument('--predictions', '-c', type=str, default=None
        , help='File to generate predicted market readings.')
    parser.add_argument('--start', '-s', type=int, default=None
        , help='Starting TimePoint, inclusive. default: earliest')
    parser.add_argument('--end', '-e', type=int, default=None
        , help='Ending TimePoint, inclusive. default: latest')
    # parser.add_argument('--readtruth', '-t', type=str, default=None
    #     , help='Directory to read actual market readings. If this is specified, program will use these readings instead of generating them from data. Expected column layout is TimePoint,Direction[,Delta (is ignored)].')
    # parser.add_argument('--savetruth', '-s', type=str, default=None
    #     , help='Specify a directory if you want to save actual market readings.')
    # parser.add_argument('--savepredicted', '-c', type=str, default=None
    #     , help='Specify a directory if you want to save predicted market readings.')
    parser.add_argument('--skipreverse', '-k', action='store_true', default=False
        , help='Skip reverse data.')
    parser.add_argument('--mode', '-m', type=str, nargs='+', default=[]
        , help='List of metrics to process, space-separated. choices: confusion, roc. default: all')
    parser.add_argument('--suppressdisplay', '-b', action='store_true', default=False
        , help='Do not display evaluation metrics upon completion')
    parser.add_argument('--outputfiles', '-o', action='store_true', default=False
        , help='Output evaluation metrics as image files')
    parser.add_argument('--pricecol', '-p', type=int, default=3
        , help='In data files, price column index to determine market direction. Index does not include TimePoint column (i.e., open = 0). default: 3 (close)')
    parser.add_argument('--newpricerow', '-n', type=int, default=1
        , help='In data files, new price row to determine market direction, relative to TimePoint. default: 1 (next future TimePoint)')
    parser.add_argument('--oldpricerow', '-l', type=int, default=0
        , help='In data files, old price row to determine market direction, relative to TimePoint. default: 0 (current TimePoint)')
    parser.add_argument('--predictioncol', '-r', type=int, default=1
        , help='In prediction file, prediction column index. Index does not include TimePoint column. default: 1')
    parser.add_argument('--weightupcol', '-u', type=int, default=4
        , help='In prediction file, vote weight up column index. Index does not include TimePoint column. default: 4')
    parser.add_argument('--weightdowncol', '-w', type=int, default=5
        , help='In prediction file, vote weight up column index. Index does not include TimePoint column. default: 5')
    

    return parser.parse_args()

if __name__ == '__main__':
    args = get_args()
    main(args.predictdir, args.truthdir \
        , data_dir = args.data \
        , predictions_file = args.predictions \
        , start_point = args.start \
        , end_point = args.end \
        # , truth_dir = args.readtruth \
        # , truth_save_dir = args.savetruth \
        # , predicted_save_dir = args.savepredicted \
        , skip_reverse = args.skipreverse \
        , mode = args.mode \
        , suppress_display = args.suppressdisplay \
        , output_files = args.outputfiles \
        # output_name = None
        , price_col = args.pricecol \
        , new_price_row = args.newpricerow \
        , old_price_row = args.oldpricerow \
        , prediction_col = args.predictioncol \
        , weight_up_col = args.weightupcol \
        , weight_down_col = args.weightdowncol
    )
