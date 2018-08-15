import numpy as np
import argparse
from pathlib import Path
import csv

ACCEPTED_TYPES = ["TTP", "CDA"]

#########################################################################
# Calculations
#########################################################################

# Returns a 3d array of the summary statistics of the input data with d1=label, d2=data, d3=formatting
def getStats(data, TCID):

    # get the number of measurements for each minute
    minute_number_for_each_row = (data[:, 0] / 60).astype(np.int)
    measures_per_min = np.histogram(minute_number_for_each_row, np.arange(0, np.max(minute_number_for_each_row) + 2))[0]

    # Create the Summary Statistics
    return [
        ["TCID", TCID, "{}"],
        ["TotalSCRs", data.shape[0], "{}"],
        ["SCRAmpMean", np.mean(data[:, 1]), "{:.10f}"],
        ["SCRAmpSD", np.std(data[:, 1]), "{:.10f}"],
        ["FileMin", np.max(minute_number_for_each_row) + 1, "{}"],
        ["SCRPerMinMean", np.mean(measures_per_min), "{:.10f}"],
        ["SCRPerMinSD", np.std(measures_per_min), "{:.10f}"],
        ["SCRPerMinMinimum", np.min(measures_per_min), "{}"],
        ["SCRPerMinMaximum", np.max(measures_per_min), "{}"]
    ]


#########################################################################
# File and Argument Manipulation
#########################################################################

## Parses the command line arguments, performs preliminary error checking, and returns the flags and Python file
## descriptors
def getArguments():
    
    #Parser configuration
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", nargs='+', help="a space-delineated list of paths to files to read raw data from (e.g., 'input.csv').")
    parser.add_argument("output_directory", help="path to save extracted data")
    parser.add_argument("-s", "--skip-errors", help="use flag to skip files with errors (rather than immediately terminating program)", action='store_true')
    args = parser.parse_args()

    SKIP = args.skip_errors
    FILES = args.input_file
    TCIDs = []
    TYPEs = []
    FILEs = []

    for FILE_STRING in FILES:

        # Input File Checks
        FILE = Path(FILE_STRING)
        error = validateFile(FILE, throwError=not SKIP)


        # Print Warning
        if error:
            print("[Skipping ", FILE, "] Warning:", error)

        # Add to the list of files (and metadata) to be processed
        else:
            name_parts = FILE.name.split("_")
            TCIDs.append(name_parts[1])
            TYPEs.append(name_parts[3].split(".")[0])
            FILEs.append(FILE)

    
    #Output File Mapping
    OUTPUT_FILEs = {}
    OUTPUT_FILEs["TTP"] = Path(args.output_directory, 'SCRSummary_TTP.txt')
    OUTPUT_FILEs["CDA"] = Path(args.output_directory, 'SCRSummary_CDA.txt')

    #Check for duplicate TCIDs
    toRemove = []
    for outputFileType, outputFile in OUTPUT_FILEs.items():
        if(outputFile.exists()):
            existingTCIDs = np.loadtxt(outputFile, delimiter=",", skiprows=1, usecols=(0), dtype=np.str)
            for i, TCID in enumerate(TCIDs):
                if TYPEs[i] == outputFileType and TCID in existingTCIDs:
                    error = "Trying to parse file for TCID " + str(TCID) + " but this TCID is aleady present in the output file (" +  str(outputFile) + ")."
                    if(SKIP):
                        print("[Skipping TCID =", TCID, "] Warning:", error)
                        toRemove.append(i)
                    else:
                        print("Error:", error)
                        exit(1)
    for i in sorted(toRemove, reverse=True):
        del FILEs[i]
        del TYPEs[i]
        del TCIDs[i]

    return FILEs, TCIDs, TYPEs, OUTPUT_FILEs, SKIP


## Validates that the input files follow appropriate naming conventions
def validateFile(file, throwError=True):
    if (not file.is_file()):
        error = "'" + str(file) + "' does not exist!"
        if(throwError):
            print("Error:", error)
            exit(1)
        else:
            return error

    name_parts = file.name.split("_")
    if (not name_parts[0] == "p" or not name_parts[1].replace('.', '', 1).isdigit() or not name_parts[2].lower() == "scrlist" or not
    name_parts[3].split(".")[0] in ACCEPTED_TYPES):

        error = "Expected filename that looks like 'p_[#]_scrlist_[TPP/CDA].txt'; given: " + str(file.name)

        if(throwError):
            print("Error:", error)
            exit(1)
        else:
            return error

    elif (not file.suffix == ".txt"):

        error = "Expected a .txt file; given a " + str(file.suffix) + " file."

        if(throwError):
            print("Error:", error)
            exit(1)
        else:
            return error


## Loads the raw input data into a numpy array
def loadRawData(inputFile, throwError=True):
    
    #load input data in (row, column) index form
    #Col 1: TTP.SCR-Onset	Col 2: TTP.SCR-Amplitude
    RAW_DATA = None
    try:
        RAW_DATA = np.loadtxt(inputFile, skiprows=1, delimiter="\t")
    except Exception as e:
        error = "Unable to read the file (" + str(inputFile) + "). Make sure it is a 2 column txt file with tab delimiters."

        if(throwError):
            print("Error:", error)
            exit(1)
        else:
            print("[Skipping", inputFile, "]:", error)
            return None

    if not RAW_DATA.shape[1] == 2:
        error = "Expected 2 columns in the input data (" +  str(inputFile) + "). Columns should represent SCR-Onset and SCR-Amplitude. Given " + str(RAW_DATA.shape[1]) + " columns."

        if(throwError):
            print("Error:", error)
            exit(1)
        else:
            print("[Skipping ", inputFile, "]:", error)
            return None
        
    return RAW_DATA


## Saves the output data either by creating a new file or appending to an existing one
def saveData(outputFile, output):
    toSave = [option[2].format(option[1]) for option in output]
    if(outputFile.exists()):
        with open(outputFile, 'a') as file:
            writer = csv.writer(file, quoting=csv.QUOTE_NONE)
            writer.writerow(toSave)
    else:
        with open(outputFile, 'a') as file:
            writer=csv.writer(file, quoting=csv.QUOTE_NONE)
            writer.writerow([[col[1] for col in output]])
            writer.writerow(toSave)




#########################################################################
# Driver
#########################################################################

if __name__ == "__main__":

    FILEs, TCIDs, TYPEs, OUTPUT_FILEs, SKIP = getArguments()
    for FILE, TCID, TYPE in zip(FILEs, TCIDs, TYPEs):
        data = loadRawData(FILE, throwError=not SKIP)
        if data is not None:
            OUTPUT = getStats(data, TCID)
            saveData(OUTPUT_FILEs[TYPE], OUTPUT)





    
    

    
    
    

        

