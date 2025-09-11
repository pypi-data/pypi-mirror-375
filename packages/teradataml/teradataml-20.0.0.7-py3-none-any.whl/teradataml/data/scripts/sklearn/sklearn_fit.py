import sys
import numpy as np
import pickle
import base64
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
    def get_values_list(values, types, model_obj):
        ret_vals = []
        for i, val in enumerate(values):
            if type(model_obj).__name__ == "MultiLabelBinarizer" and val == "":
                continue
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

    def get_classes_as_list(classes, actual_type):
        if classes == "None":
            return None
        if actual_type == "None":
            sys.exit("type of class elements is None where class elements exists.")

        # separated by '--'
        classes = classes.split("--")

        for idx, cls in enumerate(classes):
            classes[idx] = convert_to_type(cls, actual_type)

        return classes


    def splitter(strr, delim=",", convert_to="str"):
        """
        Split the string based on delimiter and convert to the type specified.
        """
        if strr == "None":
            return []
        return [convert_to_type(i, convert_to) for i in strr.split(delim)]

    # Arguments to the Script
    if len(sys.argv) != 10:
        # 10 arguments command line arguments should be passed to this file.
        # 1: file to be run
        # 2. function name
        # 3. No of feature columns.
        # 4. No of class labels.
        # 5. Comma separated indices of partition columns.
        # 6. Comma separated types of all the data columns.
        # 7. Model file prefix to generated model file using partition columns.
        # 8. classes (separated by '--') - should be converted to list. "None" if no classes exists.
        # 9. type of elements in passed in classes. "None" if no classes exists.
        # 10. Flag to check the system type. True, means Lake, Enterprise otherwise
        sys.exit("10 arguments command line arguments should be passed: file to be run,"
                 " function name, no of feature columns, no of class labels, comma separated indices"
                 " of partition columns, comma separated types of all columns, model file prefix ,"
                 " classes, type of elements in classes and flag to check lake or enterprise.")

    is_lake_system = eval(sys.argv[9])
    if not is_lake_system:
        db = sys.argv[0].split("/")[1]
    function_name = sys.argv[1]
    n_f_cols = int(sys.argv[2])
    n_c_labels = int(sys.argv[3])
    data_column_types = splitter(sys.argv[5], delim="--")
    data_partition_column_indices = splitter(sys.argv[4], convert_to="int") # indices are integers.
    model_file_prefix = sys.argv[6]
    class_type = sys.argv[8]
    classes = get_classes_as_list(sys.argv[7], class_type)

    data_partition_column_types = [data_column_types[idx] for idx in data_partition_column_indices]

    model = None

    # Data Format (n_features, k_labels, one data_partition_column):
    # feature1, feature2, ..., featuren, label1, label2, ... labelk, data_partition_column1, ...,
    # data_partition_columnn
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

                    model_file_path = f"{model_file_prefix}_{partition_join}"\
                        if is_lake_system else \
                        f"./{db}/{model_file_prefix}_{partition_join}"

                    with open(model_file_path, "rb") as fp:
                        model = pickle.loads(fp.read())

                    if model is None:
                        sys.exit("Model file is not installed in Vantage.")

                values = get_values_list(values, data_column_types, model)
                values = values[:-len(data_partition_column_indices)] # Already processed partition columns.
                features.append(values[:n_f_cols])
                if n_c_labels > 0:
                    labels.append(values[n_f_cols:(n_f_cols+n_c_labels)])


        except EOFError:  # Exit if reached EOF or CTRL-D
            break

    if not len(features):
        sys.exit(0)

    # Fit/partial_fit the model to the data.
    model_name = model.__class__.__name__
    if function_name == "partial_fit":
        if labels and classes:
            if model_name == "SelectFromModel":
               features = np.array(features)
               classes = np.array(classes)
               labels = np.array(labels).ravel()
            model.partial_fit(features, labels, classes=classes)
        elif labels:
            model.partial_fit(features, labels)
        elif classes:
            model.partial_fit(features, classes=classes)
        else:
            model.partial_fit(features)
    elif function_name == "fit":
        np_func_list = ["OneVsRestClassifier", "LabelBinarizer", "TSNE"]
        if labels:
            # For IsotonicRegression, fit() accepts training target as
            # y: array-like of shape (n_samples,).
            if model_name in ["CalibratedClassifierCV", "GaussianProcessClassifier", "GenericUnivariateSelect",
                              "IsotonicRegression", "LinearSVC", "GridSearchCV", "LinearDiscriminantAnalysis", "RFECV",
                              "RFE", "RandomizedSearchCV", "SelectFdr", "SelectFpr", "SelectFromModel", "SelectFwe",
                              "SelectKBest", "SelectPercentile", "SequentialFeatureSelector", "GaussianNB",
                              "QuadraticDiscriminantAnalysis"]:
                labels = np.array(labels).reshape(-1)
            if model_name in np_func_list:
                labels = np.array(labels)
                features = np.array(features)
            model.fit(features, labels)
        else:
            if model_name in np_func_list:
                features = np.array(features)
            model.fit(features)

    model_str = pickle.dumps(model)

    if is_lake_system:
        model_file_path = f"/tmp/{model_file_prefix}_{partition_join}.pickle"

    # Write to file in Vantage, to be used in predict/scoring.
    with open(model_file_path, "wb") as fp:
        fp.write(model_str)

    model_data = model_file_path if is_lake_system \
        else base64.b64encode(model_str)

    # Print the model to be read from script.
    print(*(data_partition_column_values + [model_data]), sep=DELIMITER)
