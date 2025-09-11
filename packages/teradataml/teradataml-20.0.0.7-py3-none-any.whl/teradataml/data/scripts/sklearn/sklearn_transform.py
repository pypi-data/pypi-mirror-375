import pickle
import math
import os
import sys
import numpy as np

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

def should_convert(t_val, py_type):
    """
    Function to check type of value and whether value is nan and infinity.
    """
    return not isinstance(t_val, eval(py_type)) and not math.isinf(t_val) and not math.isnan(t_val)

def convert_value(t_val, py_type):
    """
    Function to convert value to specified python type.
    """
    return convert_to_type(t_val, py_type) if should_convert(t_val, py_type) else t_val

# Process output returned by sklearn function.
def get_output_data(trans_values, func_name, model_obj, n_c_labels, n_out_columns):
    # Converting    sparse matrix to dense array as sparse matrices are NOT
    # supported in Vantage.
    module_name = model_obj.__module__.split("._")[0]

    # Converting the translated values into corresponding the return column's 
    # python type.
    if (func_name == "decision_path" or return_columns_python_types is None \
            or not isinstance(trans_values, np.ndarray)):
        trans_values_list = trans_values
    else:
        # Conversion.....
        trans_values_list = []
        for trans_value in trans_values.tolist():
            if not isinstance(trans_value, list):
                trans_value = [trans_value]

            converted_list = []
            if len(return_columns_python_types) == len(trans_value):
                for t_val, py_type in zip(trans_value, return_columns_python_types):
                    converted_list.append(convert_value(t_val, py_type))
            ## transform() is having only 1 python return type, But it actually returns more than 1 column  
            else:
                for t_val in trans_value:
                    converted_list.append(convert_value(t_val, "".join(return_columns_python_types)))

            trans_values_list.append(converted_list)

    if type(trans_values_list).__name__ in ["csr_matrix", "csc_matrix"]:
        trans_values_list = trans_values_list.toarray()

    if module_name == "sklearn.cross_decomposition" and n_c_labels > 0 and func_name == "transform":
        # For cross_decomposition, output is a tuple of arrays when label columns are provided
        # along with feature columns for transform function. In this case, concatenate the
        # arrays and return the combined values.
        if isinstance(trans_values_list, tuple):
            return np.concatenate(trans_values_list, axis=1).tolist()[0]

    if isinstance(trans_values_list[0], np.ndarray) \
            or isinstance(trans_values_list[0], list) \
            or isinstance(trans_values_list[0], tuple):
        # Here, the value returned by sklearn function is list type.
        opt_list = list(trans_values_list[0])

        if len(opt_list) < n_out_columns:
            # If the output list is less than the required number of columns, append
            # empty strings to the list.
            opt_list += [""] * (n_out_columns - len(opt_list))

        if func_name == "inverse_transform" and type(model_obj).__name__ == "MultiLabelBinarizer":
            # output array "trans_values[0]" may not be of same size. It should be of
            # maximum size of `model.classes_`
            # Append None to last elements.
            if len(opt_list) < len(model_obj.classes_):
                opt_list += [""] * (len(model_obj.classes_) - len(opt_list))

        return opt_list

    # Only one element is returned by the function.
    return [trans_values_list[0]]

# Arguments to the Script
if len(sys.argv) != 10:
    # 10 arguments command line arguments should be passed to this file.
    # 1: file to be run
    # 2. function name (Eg. predict, fit etc)
    # 3. No of feature columns.
    # 4. No of class labels.
    # 5. Comma separated indices of partition columns.
    # 6. Comma separated types of all the data columns.
    # 7. Model file prefix to generated model file using partition columns.
    # 8. Number of columns to be returned by the sklearn's transform function.
    # 9. Flag to check the system type. True, means Lake, Enterprise otherwise.
    # 10. Python types of returned/transfromed columns.
    sys.exit("10 arguments should be passed to this file - file to be run, function name, "\
                 "no of feature columns, no of class labels, comma separated indices of partition "\
                 "columns, comma separated types of all columns, model file prefix to generate model "\
                 "file using partition columns, number of columns to be returnd by sklearn's "\
                 "transform function, flag to check lake or enterprise and Python types of "\
                 "returned/transfromed columns.")

is_lake_system = eval(sys.argv[8])
if not is_lake_system:
    db = sys.argv[0].split("/")[1]
func_name = sys.argv[1]
n_f_cols = int(sys.argv[2])
n_c_labels = int(sys.argv[3])
data_column_types = splitter(sys.argv[5], delim="--")
data_partition_column_indices = splitter(sys.argv[4], convert_to="int") # indices are integers.
model_file_prefix = sys.argv[6]
# sys.argv[9] will contain a string of python datatypes with '--'
# separator OR a single datatype OR None in string format.
ret_col_argv = sys.argv[9]
if ret_col_argv == "None":
    return_columns_python_types = eval(ret_col_argv)
else:
    return_columns_python_types = splitter(ret_col_argv, delim="--")

no_of_output_columns = int(sys.argv[7])

data_partition_column_types = [data_column_types[idx] for idx in data_partition_column_indices]

model = None
data_partition_column_values = []

all_rows_input = []

# Data Format:
# feature1, feature2, ..., featuren, label1, label2, ... labelk, data_partition_column1, ..., 
# data_partition_columnn.
# label is optional (it is present when label_exists is not "None")

model_name = ""
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

            model_name = model.__class__.__name__
            np_func_list = ["ClassifierChain", "EllipticEnvelope", "MinCovDet",  
                            "FeatureAgglomeration", "LabelBinarizer", "MultiLabelBinarizer",
                            "BernoulliRBM"]

            # MissingIndicator's transform() and SimpleImputer's inverse_transform() requires processing
            # the entire dataset simultaneously, rather than on a row-by-row basis.

            # Error getting during row-by-row processing of MissingIndicator - 
            # "ValueError: MissingIndicator does not support data with dtype <U13. 
            # Please provide either a numeric array (with a floating point or 
            # integer dtype) or categorical data represented ei

            # Error getting during row-by-row processing of SimpleImputer -
            # "IndexError: index 3 is out of bounds for axis 1 with size 3".
            if ((model_name == "MissingIndicator" and func_name == "transform") or \
                (model_name == "SimpleImputer" and func_name == "inverse_transform") or \
                    (model_name in ["EllipticEnvelope", "MinCovDet"]
                        and func_name == "correct_covariance")):
                all_rows_input.append(f_)
                continue

            f__ = np.array([f_]) if model_name in np_func_list else [f_]

            # transform() function in these functions generate different number of output columns and
            # NULLS/NaNs are appended to the end of the output.
            # If we run inverse_transform() on these models, it will take same number of input columns
            # with NULLs/NaNs but those NULLs/NaNs should be ignored while reading the input to 
            # inverse_transform() function.
            models_with_all_null_in_last_cols = ["SelectFpr", "SelectFdr", "SelectFwe", "SelectFromModel", "RFECV"]
            if model_name in models_with_all_null_in_last_cols and func_name == "inverse_transform":
                # Remove NULLs/NaNs from the end of one input row.
                _f  = np.array([f_])
                _f = _f[~np.isnan(_f)]
                f__ = [_f.tolist()]

            if n_c_labels > 0:
                # Labels are present in last column.
                l_ = values[n_f_cols:n_f_cols+n_c_labels]

                l__ = np.array([l_]) if model_name in np_func_list else [l_]
                # predict() now takes 'y' also for it to return the labels from script. Skipping 'y'
                # in function call. Generally, 'y' is passed to return y along with actual output.
                try:
                    # cross_composition functions uses Y for labels.
                    # used 'in' in if constion, as model.__module__ is giving 
                    # 'sklearn.cross_decomposition._pls'.  
                    if "cross_decomposition" in model.__module__:
                        trans_values = getattr(model, func_name)(X=f__, Y=l__)
                    else:
                        trans_values = getattr(model, func_name)(X=f__, y=l__)

                except TypeError as ex:
                    # Function which does not accept 'y' like predict_proba() raises error like
                    # "TypeError: predict_proba() takes 2 positional arguments but 3 were given".
                    trans_values = getattr(model, func_name)(f__)
            else:
                # If class labels do not exist in data, don't read labels, read just features.
                trans_values = getattr(model, func_name)(f__)

            result_list = f_
            if n_c_labels > 0 and func_name in ["predict", "decision_function"]:
                result_list += l_
            result_list += get_output_data(trans_values=trans_values, func_name=func_name,
                                           model_obj=model, n_c_labels=n_c_labels,
                                           n_out_columns=no_of_output_columns)

            for i, val in enumerate(result_list):
                if (val is None or (not isinstance(val, str) and (math.isnan(val) or math.isinf(val)))):
                    result_list[i] = ""
                # MissingIndicator returns boolean values. Convert them to 0/1.
                elif val == False:
                    result_list[i] = 0
                elif val == True:
                    result_list[i] = 1

            print(*(data_partition_column_values + result_list), sep=DELIMITER)

    except EOFError:  # Exit if reached EOF or CTRL-D
        break


# MissingIndicator and SimpleImputer needs processing of all the dataset at the same time, instead of row by row. 
# Hence, handling it outside of the while loop
if model_name == "MissingIndicator" and func_name == "transform" or \
    (model_name == "SimpleImputer" and func_name == "inverse_transform"):
    if model_name == "SimpleImputer":
        all_rows_input = np.array(all_rows_input)
    m_out = getattr(model, func_name)(all_rows_input)

    if type(m_out).__name__ in ["csr_matrix", "csc_matrix"]:
        m_out = m_out.toarray()

    for j in range(len(all_rows_input)):
        m_out_list = get_output_data(trans_values=[m_out[j]], func_name=func_name,
                                     model_obj=model, n_c_labels=n_c_labels,
                                     n_out_columns=no_of_output_columns)

        result_list = list(all_rows_input[j]) + list(m_out_list)

        for i, val in enumerate(result_list):
            if (val is None or (not isinstance(val, str) and (math.isnan(val) or math.isinf(val)))):
                result_list[i] = ""
            # MissingIndicator returns boolean values. Convert them to 0/1.
            elif val == False:
                result_list[i] = 0
            elif val == True:
                result_list[i] = 1

        print(*(data_partition_column_values + result_list), sep=DELIMITER)

## correct_covariance() requires processing of all the input rows at the same time.
## It returns the output dataset  in (n_features, n_features) shape, i.e., based on
## no. of columns.
if model_name in ["EllipticEnvelope", "MinCovDet"] and func_name == "correct_covariance":
    result_list = model.correct_covariance(np.array(all_rows_input))
    for l, vals in enumerate(result_list):
        print(*(data_partition_column_values + vals.tolist()), sep=DELIMITER)
