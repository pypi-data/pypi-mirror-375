import pickle
import math
import sys
import numpy as np
import base64
from contextlib import contextmanager
import os

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
    if len(sys.argv) != 9:
        # 9 arguments command line arguments should be passed to this file.
        # 1: file to be run
        # 2. function name
        # 3. No of feature columns.
        # 4. No of class labels.
        # 5. No of group columns.
        # 6. Comma separated indices of partition columns.
        # 7. Comma separated types of all the data columns.
        # 8. Model file prefix to generated model file using partition columns.
        # 9. Flag to check the system type. True, means Lake, Enterprise otherwise.
        sys.exit("9 arguments command line arguments should be passed: file to be run,"
                 " function name, no of feature columns, no of class labels, no of group columns,"
                 " comma separated indices of partition columns, comma separated types of all columns,"
                 " model file prefix to generated model file using partition columns and flag to check"
                 " lake or enterprise.")


    is_lake_system = eval(sys.argv[8])
    if not is_lake_system:
        db = sys.argv[0].split("/")[1]
    function_name = sys.argv[1]
    n_f_cols = int(sys.argv[2])
    n_c_labels = int(sys.argv[3])
    n_g_cols = int(sys.argv[4])
    data_column_types = splitter(sys.argv[6], delim="--")
    data_partition_column_indices = splitter(sys.argv[5], convert_to="int") # indices are integers.
    model_file_prefix = sys.argv[7]

    data_partition_column_types = [data_column_types[idx] for idx in data_partition_column_indices]

    model = None
    data_partition_column_values = []

    # Data Format (n_features, k_labels, one data_partition_column):
    # feature1, feature2, ..., featuren, label1, label2, ... labelk, data_partition_column1, ...,
    # data_partition_columnn.
    # labels are optional.

    features = []
    labels = []
    groups = []
    while 1:
        try:
            line = input()
            if line == '':  # Exit if user provides blank line
                break
            else:
                values = line.split(DELIMITER)
                values = get_values_list(values, data_column_types)
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

                    if not model:
                        sys.exit("Model file is not installed in Vantage.")

                start = 0
                if n_f_cols > 0:
                    features.append(values[:n_f_cols])
                    start = start + n_f_cols
                if n_c_labels > 0:
                    labels.append(values[start:(start+n_c_labels)])
                    start = start + n_c_labels
                if n_g_cols > 0:
                    groups.append(values[start:(start+n_g_cols)])

        except EOFError:  # Exit if reached EOF or CTRL-D
            break

    if len(features) == 0:
        sys.exit(0)

    features = np.array(features) if len(features) > 0 else None
    labels = np.array(labels).flatten() if len(labels) > 0 else None
    groups = np.array(groups).flatten() if len(groups) > 0 else None

    if function_name == "split":
        # Printing both train and test data instead of just indices unlike sklearn.
        # Generator is created based on split_id and type of split (train/test) in client.
        split_id = 1
        for train_idx, test_idx in model.split(features, labels, groups):
            X_train, X_test = features[train_idx], features[test_idx]
            y_train, y_test = labels[train_idx], labels[test_idx]
            for X, y in zip(X_train, y_train):
                print(*(data_partition_column_values + [split_id, "train"] +
                        ['' if (val is None or (not isinstance(val, str) and (math.isnan(val) or math.isinf(val)))) else val
                         for val in X] + [y]
                        ), sep=DELIMITER)
            for X, y in zip(X_test, y_test):
                print(*(data_partition_column_values + [split_id, "test"] +
                        ['' if (val is None or (not isinstance(val, str) and (math.isnan(val) or math.isinf(val)))) else val
                         for val in X] + [y]
                        ), sep=DELIMITER)
            split_id += 1
    else:
        val = getattr(model, function_name)(features, labels, groups)
        print(*(data_partition_column_values + [val]), sep=DELIMITER)
