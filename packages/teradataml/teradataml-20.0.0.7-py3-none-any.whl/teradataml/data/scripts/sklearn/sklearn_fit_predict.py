import sys
import numpy as np
import pickle
import math
import os
from contextlib import contextmanager

DELIMITER = '\t'

@contextmanager
def suppress_stderr():
    """
    Function to suppress the warnings(lake systems treats warnings as errors).
    """
    with open(os.devnull, "w") as devnull:
        old_stderr = sys.stderr
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stderr = old_stderr

## On Lake system warnings raised by script are treated as a errors. 
## Hence, to suppress it putting the under suppress_stderr().
with suppress_stderr():
    def get_values_list(values, types):
        ret_vals = []
        for i, val in enumerate(values):
            ret_vals.append(convert_to_type(val, types[i]))
        return ret_vals

    def convert_to_type(val, typee):
        if typee == 'int':
            return int(val) if val != "" else np.nan
        if typee == 'float':
            if isinstance(val, str):
                val = val.replace(' ', '')
            return float(val) if val != "" else np.nan
        if typee == 'bool':
            return eval(val) if val != "" else None
        return str(val) if val != "" else None

    def splitter(strr, delim=",", convert_to="str"):
        """
        Split the string based on delimiter and convert to the type specified.
        """
        if strr == "None":
            return []
        return [convert_to_type(i, convert_to) for i in strr.split(delim)]

    # Arguments to the Script
    if len(sys.argv) != 7:
        # 6 arguments command line arguments should be passed to this file.
        # 1: file to be run
        # 2. No of feature columns.
        # 3. No of class labels.
        # 4. Comma separated indices of partition columns.
        # 5. Comma separated types of all the data columns.
        # 6. Model file prefix to generated model file using partition columns.
        # 7. Flag to check the system type. True, means Lake, Enterprise otherwise.
        sys.exit("7 arguments should be passed to this file - file to be run, "\
                 "no of feature columns, no of class labels, comma separated indices of partition "
                 "columns, comma separated types of all columns, model file prefix to generate model "
                 "file using partition columns and flag to check lake or enterprise.")

    is_lake_system = eval(sys.argv[6])
    if not is_lake_system:
        db = sys.argv[0].split("/")[1]
    n_f_cols = int(sys.argv[1])
    n_c_labels = int(sys.argv[2])
    model_file_prefix = sys.argv[5]
    data_column_types = splitter(sys.argv[4], delim="--")
    data_partition_column_indices = splitter(sys.argv[3], convert_to="int") # indices are integers.

    data_partition_column_types = [data_column_types[idx] for idx in data_partition_column_indices]

    model = None

    # Data Format (n_features, k_labels, one data_partition_columns):
    # feature1, feature2, ..., featuren, label1, label2, ... labelk, data_partition_column1, ...,
    # data_partition_columnn.
    # There can be no labels also.

    # Read data from table through STO and build features and labels.
    features = []
    labels = []
    data_partition_column_values = []


    while 1:
        try:
            line = input()
            if line == '':  # Exit if user provides blank line
                break
            else:
                values = line.split(DELIMITER)
                values = get_values_list(values, data_column_types)
                features.append(values[:n_f_cols])
                if n_c_labels > 0:
                    labels.append(values[n_f_cols:(n_f_cols+n_c_labels)])
                if not data_partition_column_values:
                    # Partition column values is same for all rows. Hence, only read once.
                    for i, val in enumerate(data_partition_column_indices):
                        data_partition_column_values.append(
                            convert_to_type(values[val], typee=data_partition_column_types[i])
                            )

                    # Prepare the corresponding model file name and extract model.
                    partition_join = "_".join([str(x) for x in data_partition_column_values])
                    # Replace '-' with '_' as '-' because partition_columns can be negative.
                    partition_join = partition_join.replace("-", "_")

                    model_file_path = f"{model_file_prefix}_{partition_join}" \
                        if is_lake_system else \
                        f"./{db}/{model_file_prefix}_{partition_join}"

                    with open(model_file_path, "rb") as fp:
                        model = pickle.loads(fp.read())

                    if model is None:
                        sys.exit("Model file is not installed in Vantage.")

        except EOFError:  # Exit if reached EOF or CTRL-D
            break

    if not len(features):
        sys.exit(0)

    # write code to call fit_predict with features and labels when n_c_labels > 0
    model_name = model.__class__.__name__
    if n_c_labels > 0:
        if model_name in ["SelectFromModel"]:
            labels = np.array(labels).ravel()
        predictions = model.fit_predict(features, labels)
    else:
        predictions = model.fit_predict(features)

    # Export results to to the Databse through standard output
    for i in range(len(predictions)):
        if n_c_labels > 0:
            # Add labels into output, if user passes it.
            result_list = features[i] + labels[i] + [predictions[i]]
        else:
            result_list = features[i] + [predictions[i]]
        print(*(data_partition_column_values +
                ['' if (val is None or (not isinstance(val, str) and (math.isnan(val) or math.isinf(val))))
                 else val for val in result_list]),
                 sep= DELIMITER)
