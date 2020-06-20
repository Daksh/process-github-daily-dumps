# Process GitHub Daily Dumps

Simply  run the `python3 script.py > std_out.txt 2>std_err.txt` in Python 3.x

## Output
1. `output` directory contains all the CSV files
2. `script.log` log file from python's logging module
3. `std_err.txt`, `std_out.txt` any text which would have been displayed on your terminal screen gets redirected to these two files instead.

## Requirements: 
1. `MongoDB`
2. python package: `pymongo`
