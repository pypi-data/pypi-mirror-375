import sys
import numpy as np
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
import base64, pickle

DELIMITER = "\t"

def get_value(value):
    ret_val = value
    try:
        ret_val = float(value.replace(' ', ''))
    except Exception as ex:
        # If the value can't be converted to float, then it is string.
        pass
    return ret_val


def get_values_list(values, ignore_none=True):
    ret_vals = []
    for val in values:
        if val == "" and ignore_none:
            # Empty cell value in the database table.
            continue
        ret_vals.append(get_value(val))

    return ret_vals

if len(sys.argv) != 2:
    sys.exit("Script command format: python deploy_script.py <enterprise/lake>")

vantage_type = sys.argv[1]

data_partition_column_values = []
data_partition_column_indices = [5, 6]

features = []
labels = []

while 1:
    try:
        line = input()
        if line == '':  # Exit if user provides blank line
            break
        else:
            values = line.split(DELIMITER)
            
            features.append(get_values_list(values[:4]))
            labels.append(get_values_list([values[4]]))
            if not data_partition_column_values:
                # Partition column values is same for all rows. Hence, only read once.
                for i, val in enumerate(data_partition_column_indices):
                    data_partition_column_values.append(int(values[val]))

    except EOFError:  # Exit if reached EOF or CTRL-D
        break

if not len(features):
    sys.exit(0)

X = np.array(features)
y = np.array(labels).ravel()

clf = make_pipeline(StandardScaler(), SVC(gamma='auto'))
clf.fit(X, y)

model_str = pickle.dumps(clf)

# Prepare the corresponding model file name and extract model.
partition_join = "_".join([str(x) for x in data_partition_column_values])
# Replace '-' with '_' as '-' because partition_columns can be negative.
partition_join = partition_join.replace("-", "_")

if vantage_type == "lake":
    model = f"/tmp/sklearn_model_{partition_join}.pickle"
    with open(model, "wb") as fp:
        fp.write(model_str)
elif vantage_type == "enterprise":
    model = base64.b64encode(model_str)
else:
    sys.exit("Invalid vantage type. Use either 'lake' or 'enterprise'.")

print(*(data_partition_column_values + [model]), sep=DELIMITER)