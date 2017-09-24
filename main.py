import argparse
import os
import data_to_truth as d2t
import predictions_to_pred as p2p
import evaluate_pred_truth as ept

def main(data_gen = None, predict_gen = None \
        , data_out = None, predict_out = None \
        , data_in = None, predict_in = None \
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
    if not data_gen is None and predict_gen is None \
        or not predict_gen is None and data_gen is None \
    :
        raise ValueError('Both --datagen and --predictgen must be specified')
    elif not data_in is None and predict_in is None \
        or not predict_in is None and data_in is None \
    :
        raise ValueError('Both --datain and --predictin must be specified')
    elif data_in is None and predict_in is None and data_gen is None and predict_gen is None:
        raise ValueError('Either --datagen and --predictgen, or --datain and --predictin, must be specified. See --help')

    if not data_gen is None: # process data
        print('Generating truth classes from {}'.format(data_gen))
        truth = d2t.get_truth_from_data(data_dir = data_gen, skip_reverse = skip_reverse, price_col = price_col, new_offset = new_price_row, old_offset = old_price_row, save_dir = data_out, get_dataframe=True)
    # elif not data_in is None and os.path.isdir(data_in):
    #     print('Reading predicted classes from {}'.format(data_in))
    #     truth = d2t.read_truth_from_dir(data_in, skip_reverse = skip_reverse)

    if not predict_gen is None: # process predictions
        print('Generating predicted classes from {}'.format(predict_gen))
        predict = p2p.get_predictions_from_file(predict_gen, skip_reverse = skip_reverse, col_prediction = prediction_col, col_voteup = weight_up_col, col_votedown = weight_down_col, save_dir = predict_out, get_dataframe=True, score_by_positive_class=False)
    # elif not predict_in is None and os.path.isdir(predict_in):
    #     print('Reading predicted classes from {}'.format(predict_in))
    #     predict = p2p.read_predictions_from_dir(predict_in, skip_reverse = skip_reverse, score_by_positive_class=False)

    # if truth is None:
    #     raise ValueError('Missing truth classes: make sure --data_gen or --data_in is specified.')
    # elif predict is None:
    #     raise ValueError('Missing predicted classes: make sure --predict_gen or --predict_in is specified.')

    print('Retrieving classes and scores')
    if (not data_in is None or not data_out is None) and (not predict_in is None or not predict_out is None):
        data_dir = data_in if not data_in is None else data_out
        predict_dir = predict_in if not predict_in is None else predict_out
        truth_classes, predicted_classes, scores, probas = ept.get_classes_scores_from_dir(predict_dir, data_dir, start_point = start_point, end_point = end_point, skip_reverse = skip_reverse, score_by_positive_class=False)
    else: # do in memory, todo: very slow looping through pandas dataframe
        truth_classes, predicted_classes, scores, probas = ept.get_classes_scores_from_df_dict(predict, truth, start_point = start_point, end_point = end_point, skip_reverse = skip_reverse, score_by_positive_class=False)

    print('Drawing metrics')
    ept.get_metric_plots(truth_classes, predicted_classes, scores, probas, mode = [], output_file = output_files, output_live = not suppress_display)

    print('Finished')

def get_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description='''Generate machine learning metrics from Genotick predictions.
You need a predictions_x.csv and the original data/ directory.

--datagen and --predictgen, or --datain and --predictin, must
be specified. --dataout and --predictout are optional.

*gen commands generate readings from Genotick outputs and
*in commands read already-generated readings saved from *out.

Suggested use, first time (to generate market readings):

  %s --datagen "./data" --predictgen "predictions_x.csv" 
    --dataout "./truth" --predictout "./predict" 
    --start 20170101 --skipreverse --outputfiles

Suggested use, with already-generated market readings:

  %s --datain "./truth" --predictin "./predict" 
    --start 20170101 --skipreverse --outputfiles

''' % (os.path.basename(__file__), os.path.basename(__file__)), epilog='''Column and row defaults (--pricecol, --newpricerow, etc.) should already work
for Genotick. Use these settings only if you have differently formatted CSV files.''')
    parser.add_argument('--datagen', '-dg', type=str, default=None
        , help='Original data directory, to generate actual market readings.')
    parser.add_argument('--predictgen', '-cg', type=str, default=None
        , help='Original predictions file, to generate predicted readings.')
    parser.add_argument('--dataout', '-do', type=str, default=None
        , help='Output directory to save actual readings.')
    parser.add_argument('--predictout', '-co', type=str, default=None
        , help='Output directory to save predicted readings.')
    parser.add_argument('--datain', '-di', type=str, default=None
        , help='Directory to use already-generated actual readings.')
    parser.add_argument('--predictin', '-ci', type=str, default=None
        , help='Directory to use already-generated predicted readings. ')
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
    main(data_gen = args.datagen, predict_gen = args.predictgen \
        , data_out = args.dataout, predict_out = args.predictout \
        , data_in = args.datain, predict_in = args.predictin \
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
