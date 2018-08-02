# Installation

All of the logic is contained within ``SCRAnalyzer.py``. It can either be downloaded directly from https://github.com/jclangst/SCRAnalyzer
or cloned via ``git clone https://github.com/jclangst/SCRAnalyzer.git`` if you are familiar with git.

It has a single dependency, `numpy` that can be installed by running:

`pip install numpy`

or

`python -m pip install numpy` (if the above does not work)

# Running

Execute the file from a bash shell (terminal) as such:

``python SCRAnalyzer.py [input_files] [output_directory] [other_args]``

Running with `-h` or `--help` will show you the supported arguments and their functionality.

For example, if you wanted to process a single file `p_1_SCRlist_TTP.txt` and output the results to the
current directory, you would run the program as

``python SCRAnalyzer.py p_1_SCRlist_TTP.txt . ``

If you wanted to also process `p_2_SCRlist_TTP.txt`, you could execute

``python SCRAnalyzer.py p_1_SCRlist_TTP.txt p_2_SCRlist_TTP.txt . ``

If you wanted to process an entire directory of files, you could use the unix glob expander

``python SCRAnalyzer.py SOME_DIR/p_*_SCRlist_*.txt . ``

Note: There are many checks to ensure valid input data. By default the program will terminate
if it detects invalid input. You can override this behavior and simply skip the invalid input
(if processing multiple input files) by using the `-s` flag. However, warning messages will still
be displayed.


# Input and Output Format

### Input
The input file is expected to have the following parameters:

(1) The data is contained in a tab-delineated .txt file with two columns;

(2) The first column represents `SCR-Onset`	and the second represents `SCR-Amplitude`;

(3) The first row contains column headers and will be ignored;

(4) All subsequent rows contain the sampled data;

(5) The input files must be named according to this convention:

``p_[TCID #]_SCRlist_[Type].txt``

The TCID # and Type are extracted and used in the program, hence the strict naming
requirement. Currently, only ``CDA`` and ``TTP`` types are supported.

### Output

The output file will have the following format:

(1) The data will be contained in a comma-delineated txt file according to its `Type` (see above).
- `CDA` = `SCRSummary_CDA.txt`
- `TTP` = `SCRSummary_TTP.txt`

These files can be found in the directory specified as an input argument.

(2) The file will contain summary statistics about the input data underneath a header specifying
the summary statistics generated. If processing multiple files, each TCID will have a unique row.

(3) The program can be run multiple times and point to the same output files. New data will be appended
to the old output data. If output data with a particular TCID already exists, the program will
throw an error to ensure that the old TCID data is NOT overwritten.