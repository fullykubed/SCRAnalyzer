import numpy as np
import argparse
from pathlib import Path

#TODO validate input file format
ACCEPTED_TYPES = ["TTP", "CDA"]

if __name__ == "__main__":

    #Parser configuration
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="path to file to read raw data from (e.g., 'input.csv')")
    parser.add_argument("-o", "--output", help="path to save extracted data (e.g., 'output.csv')")
    parser.add_argument("-nh", "--no-header", help="use if the input data has no headers",action='store_true')
    args = parser.parse_args()

    #Input File Checks
    FILE = Path(args.input_file)
    if(not FILE.is_file()):
        print("Error: '",FILE,"' does not exist!")
        exit(1)

    name_parts = FILE.name.split("_")
    if(not name_parts[0] == "p" or not name_parts[1].isdigit() or not name_parts[2].lower() == "scrlist" or not name_parts[3].split(".")[0] in ACCEPTED_TYPES):
        print("Error: Expected filename that looks like 'p_[#]_scrlist_[TPP/CDA].txt'; given: ", FILE.name)
        exit(1)
    elif(not FILE.suffix == ".txt"):
        print("Error: Expected a .txt file; given:", FILE.suffix, " file.")
        exit(1)

    TCID = int(name_parts[1])
    TYPE = name_parts[3]

    #Output File Check
    OUTPUT_FILE = None
    if(not args.output):
        OUTPUT_FILE = Path(args.output) if args.output else FILE.parent.joinpath(
            FILE.name.split(".")[0] + "-out.csv")
    else:
        OUTPUT_FILE = Path(args.output)

    if(not OUTPUT_FILE.suffix in [".csv", ".txt"]):
        print("Error: Output file must either be of .txt or .csv format!")
        exit(1)


    #load input data in (row, column) index form
    #Col 1: TTP.SCR-Onset	Col 2: TTP.SCR-Amplitude
    RAW_DATA = None
    try:
        RAW_DATA = np.loadtxt(FILE, skiprows=0 if args.no_header else 1, delimiter="\t")
    except Exception as e:
        print("Error: Unable to read the file. Make sure it is a 2 column txt file with tab delimiters.")
        print(e)
        exit(1)

    if not RAW_DATA.shape[1] == 2:
        print("Error: Expected 2 columns in the input data. Columns should represent SCR-Onset and SCR-Amplitude. Given", RAW_DATA.shape[1], "columns.")
        exit(1)



    #get the number of measurements for each minute
    minute_number_for_each_row = (RAW_DATA[:, 0] / 60).astype(np.int)
    measures_per_min = np.histogram(minute_number_for_each_row, np.arange(0, np.max(minute_number_for_each_row) + 1))[0]

    #Create the Summary Statistics
    output = [
        ["TCID", TCID,  "%d"]       ,
        ["TotalSCRs", RAW_DATA.shape[0], "%d"]   ,
        ["SCRAmpMean", np.mean(RAW_DATA[:, 1]), "%.10f"],
        ["SCRAmpSD", np.std(RAW_DATA[:, 1]), "%.10f"],
        ["FileMin", np.max(minute_number_for_each_row) + 1, "%d"],
        ["SCRPerMinMean", np.mean(measures_per_min), "%.10f"],
        ["SCRPerMinSD", np.std(measures_per_min), "%.10f"],
        ["SCRPerMinMinimum", np.min(measures_per_min), "%d"],
        ["SCRPerMinMaximum", np.max(measures_per_min), "%d"]
    ]

    np.savetxt(OUTPUT_FILE,
               [[col[1] for col in output]],
               delimiter=",",
               header=','.join([col[0] for col in output]),
               fmt=[col[2] for col in output])




    
    

    
    
    

        

