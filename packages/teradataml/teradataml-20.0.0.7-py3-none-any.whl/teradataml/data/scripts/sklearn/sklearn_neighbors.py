import pickle
import math
import sys
import numpy as np

# The below import is needed to convert sparse matrix to dense array as sparse matrices are NOT
# supported in Vantage.
# This is in scipy 1.6.x. Might vary based on scipy version.
from scipy.sparse.csr import csr_matrix


DELIMITER = '\t'


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
if len(sys.argv) < 7:
    # At least 7 arguments command line arguments should be passed to this file.
    # 1: file to be run
    # 2. function name.
    # 3. No of feature columns.
    # 4. Comma separated indices of partition columns.
    # 5. Comma separated types of all the data columns.
    # 6. Model file prefix to generate model file using partition columns.
    # 7. Flag to check the system type. True, means Lake, Enterprise otherwise.
    # 8. OPTIONAL - Arguments in string format like "return_distance True-bool",
    #    "n_neighbors 3-int", "radius 3.4-float" etc.
    sys.exit("At least 7 arguments should be passed to this file - file to be run, function name, "\
             "no of feature columns, comma separated indices of partition columns, comma "\
             "separated types of all columns, model file prefix to generate model file using "\
             "partition columns, flag to check lake or enterprise and optional arguments in string format.")

convert_to_int = lambda x: int(x) if x != "None" else None

is_lake_system = eval(sys.argv[6])
if not is_lake_system:
    db = sys.argv[0].split("/")[1]
func_name = sys.argv[1]
n_f_cols = convert_to_int(sys.argv[2])
data_column_types = splitter(sys.argv[4], delim="--")
data_partition_column_indices = splitter(sys.argv[3], convert_to="int") # indices are integers.
model_file_prefix = sys.argv[5]
# Extract arguments from string.
arguments = {}
for i in range(7, len(sys.argv), 2):
    value = sys.argv[i + 1].split("-", 1)
    arguments[sys.argv[i]] = convert_to_type(value[0], value[1])

data_partition_column_types = [data_column_types[idx] for idx in data_partition_column_indices]

model = None
data_partition_column_values = []

# Data Format:
# feature1, feature2, ..., featuren, label1, label2, ... labelk, data_partition_column1, ..., 
# data_partition_columnn.
# label is optional (it is present when label_exists is not "None")

# `return_distance` is needed as the result is a tuple of two arrays when it is True.
return_distance = arguments.get("return_distance", True) # Default value is True.

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

            f_ = values[:n_f_cols]
            if f_:
                output = getattr(model, func_name)([f_], **arguments)
            else:
                output = getattr(model, func_name)(**arguments)
            result_list = f_

            if func_name in ['kneighbors', 'radius_neighbors']:
                if return_distance:
                    result_list += [str(output[0][0].tolist()), str(output[1][0].tolist())]
                else:
                    result_list += [str(output[0].tolist())]
            else:
                # cases like 'kneighbors_graph', 'radius_neighbors_graph' and other functions.
                if isinstance(output, csr_matrix):
                    # 'kneighbors_graph', 'radius_neighbors_graph' return sparse matrix.
                    output = output.toarray()
                result_list += [str(output[0].tolist())]

            print(*(data_partition_column_values +
                    ['' if (val is None or (not isinstance(val, str) and
                                            (math.isnan(val) or math.isinf(val))))
                        else val
                    for val in result_list]), sep=DELIMITER)

    except EOFError:  # Exit if reached EOF or CTRL-D
        break
