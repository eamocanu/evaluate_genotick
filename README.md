# evaluate_genotick
Generate machine learning metrics from Genotick outputs. Tested on Python 3.6. Requires CSV output from latest Genotick on Github.

Depends (run `pip install` or use Anaconda3 distro):
* `pandas`
* `numpy`
* `scikit-learn`
* `matplotlib`

Drop files in a directory and run main.py:

```
usage: main.py [-h] [--data DATA] [--predictions PREDICTIONS] [--start START]
               [--end END] [--skipreverse] [--mode MODE [MODE ...]]
               [--suppressdisplay] [--outputfiles] [--pricecol PRICECOL]
               [--newpricerow NEWPRICEROW] [--oldpricerow OLDPRICEROW]
               [--predictioncol PREDICTIONCOL] [--weightupcol WEIGHTUPCOL]
               [--weightdowncol WEIGHTDOWNCOL]
               predictdir truthdir

Generate machine learning metrics from Genotick predictions.
You need a predictions_x.csv and the original data/ directory.

Suggested use, first time (to generate market readings):

    main.py "./predict" "./truth" --data "./data"
        --predictions "predictions_x.csv" --start 20170101
        --skipreverse --outputfiles

Suggested use, with already-generated market readings:

    main.py "./predict" "./truth" --start 20170101
        --skipreverse --outputfiles

positional arguments:
  predictdir            Directory with predicted market readings. If
                        --predictions is passed, generate and save the
                        readings to this dir. Else, read the readings.
  truthdir              Directory with actual market readings. If --data is
                        passed, generate and save the readings. Else, read the
                        readings.

optional arguments:
  -h, --help            show this help message and exit
  --data DATA, -d DATA  Data directory to generate market readings.
  --predictions PREDICTIONS, -c PREDICTIONS
                        File to generate predicted market readings.
  --start START, -s START
                        Starting TimePoint, inclusive. default: earliest
  --end END, -e END     Ending TimePoint, inclusive. default: latest
  --skipreverse, -k     Skip reverse data.
  --mode MODE [MODE ...], -m MODE [MODE ...]
                        List of metrics to process, space-separated. choices:
                        confusion, roc. default: all
  --suppressdisplay, -b
                        Do not display evaluation metrics upon completion
  --outputfiles, -o     Output evaluation metrics as image files
  --pricecol PRICECOL, -p PRICECOL
                        In data files, price column index to determine market
                        direction. Index does not include TimePoint column
                        (i.e., open = 0). default: 3 (close)
  --newpricerow NEWPRICEROW, -n NEWPRICEROW
                        In data files, new price row to determine market
                        direction, relative to TimePoint. default: 1 (next
                        future TimePoint)
  --oldpricerow OLDPRICEROW, -l OLDPRICEROW
                        In data files, old price row to determine market
                        direction, relative to TimePoint. default: 0 (current
                        TimePoint)
  --predictioncol PREDICTIONCOL, -r PREDICTIONCOL
                        In prediction file, prediction column index. Index
                        does not include TimePoint column. default: 1
  --weightupcol WEIGHTUPCOL, -u WEIGHTUPCOL
                        In prediction file, vote weight up column index. Index
                        does not include TimePoint column. default: 4
  --weightdowncol WEIGHTDOWNCOL, -w WEIGHTDOWNCOL
                        In prediction file, vote weight up column index. Index
                        does not include TimePoint column. default: 5

Column and row defaults (--pricecol, --newpricerow, etc.) should already work
for Genotick. Use these settings only if you have differently formatted CSV files.
```
