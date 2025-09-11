import re
from datetime import date
from teradataml.common.exceptions import TeradataMlException
from teradataml.common.messages import Messages, MessageCodes
from teradataml.common.utils import UtilFuncs
from teradataml.dataframe.dataframe import DataFrame
from teradataml.dataframe.dataframe_utils import DataFrameUtils as df_utils
from teradataml.utils.validators import _Validators
from teradataml.utils.dtypes import _SuppArgTypes, _DtypesMappers
from teradatasqlalchemy.types import BIGINT, BYTEINT, CHAR, DATE, DECIMAL, FLOAT, INTEGER, NUMBER, SMALLINT, TIME, \
                                    TIMESTAMP, VARCHAR


class _Transformations(object):
    """ Class to represent different transformation techniques. """

    def __init__(self, columns=None, out_columns=None, datatype=None,
                 columns_optional=True):
        """
        DESCRIPTION:
            Constructor for _Transformations.
            Note:
               It is intended to use as super() class for transformation techniques.

        PARAMETERS:
            columns:
                Optional Argument.
                Required when "out_columns" is used or "columns_optional" is False.
                Specifies the names of the columns.
                Types: str or list of str

            out_columns:
                Optional Argument.
                Specifies the names of the output columns.
                Notes:
                    1. "columns" argument must be used, when this argument is used.
                    2. Number of elements in "columns" and "out_columns" must be same.
                Types: str or list of str

            datatype:
                Optional Argument.
                Specifies the name of the intended datatype of the output column.
                Intended data types for the output column can be specified using either the
                teradatasqlalchemy types or the permitted strings mentioned below:
                 -------------------------------------------------------------------
                | If intended SQL Data Type is  | Permitted Value to be passed is   |
                |-------------------------------------------------------------------|
                | bigint                        | bigint                            |
                | byteint                       | byteint                           |
                | char(n)                       | char,n                            |
                | date                          | date                              |
                | decimal(m,n)                  | decimal,m,n                       |
                | float                         | float                             |
                | integer                       | integer                           |
                | number(*)                     | number                            |
                | number(n)                     | number,n                          |
                | number(*,n)                   | number,*,n                        |
                | number(n,n)                   | number,n,n                        |
                | smallint                      | smallint                          |
                | time(p)                       | time,p                            |
                | timestamp(p)                  | timestamp,p                       |
                | varchar(n)                    | varchar,n                         |
                --------------------------------------------------------------------
                Notes:
                    1. Argument is ignored if "columns" argument is not used.
                    2. char without a size is not supported.
                    3. number(*) does not include the * in its datatype format.
                Examples:
                    1. If intended datatype for the output column is "bigint", then
                       pass string "bigint" to the argument as shown below:
                       datatype="bigint"
                    2. If intended datatype for the output column is "decimal(3,5)", then
                       pass string "decimal,3,5" to the argument as shown below:
                       datatype="decimal,3,5"
                Types: str, BIGINT, BYTEINT, CHAR, DATE, DECIMAL, FLOAT, INTEGER, NUMBER, SMALLINT, TIME,
                       TIMESTAMP, VARCHAR.

            columns_optional:
                Optional Argument.
                Specifies whether to treat "columns" argument as required or optional.
                Default Value: True ("columns" is optional)
                Types: bool

        RETURNS:
            An instance of _Transformations class.

        RAISES:
            TeradataMlException, TypeError, ValueError

        EXAMPLE:
            _Transformations(columns="col1")
        """
        self.columns = columns
        self.out_columns = out_columns
        self.datatype = datatype

        # Validations
        arg_info_matrix = []
        arg_info_matrix.append(
            ["columns", self.columns, columns_optional, (str, list), True])
        arg_info_matrix.append(["out_columns", self.out_columns, True, (str, list), True])
        arg_info_matrix.append(["datatype", self.datatype, True, _SuppArgTypes.VAL_ARG_DATATYPE, True])

        # Validate for missing required arguments.
        _Validators._validate_missing_required_arguments(arg_info_matrix)

        # Argument validations.
        _Validators._validate_function_arguments(arg_info_matrix)

        if self.out_columns is not None:
            # Raise error, if "columns" not provided and "out_columns" is provided.
            _Validators._validate_dependent_argument("out_columns", self.out_columns, "columns", self.columns)

            if len(UtilFuncs._as_list(self.out_columns)) != len(
                    UtilFuncs._as_list(self.columns)):
                # Raise error, if length of the input and output columns is not same.
                err_ = Messages.get_message(MessageCodes.INVALID_LENGTH_ARGS,
                                            "columns and out_columns")
                raise TeradataMlException(err_, MessageCodes.INVALID_LENGTH_ARGS)

    def _val_transformation_fmt(self):
        """
        DESCRIPTION:
            Internal function to return a string representation of basic Transformation
            technique arguments "columns", "out_columns" and "datatype" as per SQL syntax
            of the function.
            Function will return empty string if "column" argument is None.

        PARAMETERS:
            None.

        RETURNS:
            String representing SQL syntax for arguments "columns", "out_columns"
            and "datatype".

        RAISES:
            None.

        EXAMPLE:
            self._val_transformation_fmt()
        """
        ret_value = ""
        if self.columns is not None:
            self.columns = UtilFuncs._as_list(self.columns)
            columns_fmt = "columns({})"

            columns_arg_values = self.columns
            if self.out_columns:
                self.out_columns = UtilFuncs._as_list(self.out_columns)
                columns_arg_values = []
                for col, out_col in dict(zip(self.columns, self.out_columns)).items():
                    columns_arg_values.append("{}/{}".format(col, out_col))

            ret_value = columns_fmt.format(", ".join(columns_arg_values))

            if self.datatype:
                if not isinstance(self.datatype, str):
                    self.datatype = _DtypesMappers.TDSQLALCHEMY_DATATYPE_TO_VAL_STRING_MAPPER[type(self.datatype)]\
                                    (self.datatype)
                ret_value = "{}, datatype({})".format(ret_value, self.datatype)
        return ret_value


class FillNa(_Transformations):
    """ Class to represent null replacement transformation technique. """

    def __init__(self, style="mean", value=None, columns=None, out_columns=None,
                 datatype=None):
        """
        DESCRIPTION:
            FillNa allows user to perform missing value/null replacement transformations.
            Note:
                Output of this function is passed to "fillna" argument of "Transform"
                function from Vantage Analytic Library.

        PARAMETERS:
            style:
                Optional Argument.
                Specifies the nullstyle for missing value/null value replacement.
                A literal value, the mean, median, mode, or an imputed value joined
                from another table can be used as the replacement value. The median
                value can be requested with or without averaging of two middle values
                when there is an even number of values.
                Literal value replacement is supported for numeric, character, and
                date data types.
                Mean value replacement is supported for columns of numeric type or
                date type.
                Median without averaging, mode, and imputed value replacement are
                valid for any supported type. Median with averaging is supported
                only for numeric and date type.
                Permitted Values: 'literal', 'mean', 'median', 'mode', 'median_wo_mean',
                                  'imputed'
                Default Value: 'mean'
                Types: str

            value:
                Optional Argument. Required when "style" is 'literal' or 'imputed'.
                Specifies the value to be used for null replacement transformations.
                Notes:
                    1. When "style" is 'imputed', value must be of type teradataml
                       DataFrame.
                    2. When "style" is 'literal', value can be of any type.
                    3. If date values are entered as string, the keyword 'DATE' must precede
                       the date value, and do not enclose in single quotes OR
                       pass a datetime.date object.
                       For example,
                            value='DATE 1987-06-09'
                            value=date(1987, 6, 9)
                Types: teradataml DataFrame, bool, int, str, float, datetime.date

            columns:
                Optional Argument.
                Specifies the names of the columns.
                Types: str or list of str

            out_columns:
                Optional Argument.
                Specifies the names of the output columns.
                Notes:
                    Number of elements in "columns" and "out_columns" must be same.
                Types: str or list of str

            datatype:
                Optional Argument.
                Specifies the name of the intended datatype of the output column.
                Intended data types for the output column can be specified using either the
                teradatasqlalchemy types or the permitted strings mentioned below:
                 -------------------------------------------------------------------
                | If intended SQL Data Type is  | Permitted Value to be passed is   |
                |-------------------------------------------------------------------|
                | bigint                        | bigint                            |
                | byteint                       | byteint                           |
                | char(n)                       | char,n                            |
                | date                          | date                              |
                | decimal(m,n)                  | decimal,m,n                       |
                | float                         | float                             |
                | integer                       | integer                           |
                | number(*)                     | number                            |
                | number(n)                     | number,n                          |
                | number(*,n)                   | number,*,n                        |
                | number(n,n)                   | number,n,n                        |
                | smallint                      | smallint                          |
                | time(p)                       | time,p                            |
                | timestamp(p)                  | timestamp,p                       |
                | varchar(n)                    | varchar,n                         |
                --------------------------------------------------------------------
                Notes:
                    1. char without a size is not supported.
                    2. number(*) does not include the * in its datatype format.
                Examples:
                    1. If intended datatype for the output column is "bigint", then
                       pass string "bigint" to the argument as shown below:
                       datatype="bigint"
                    2. If intended datatype for the output column is "decimal(3,5)", then
                       pass string "decimal,3,5" to the argument as shown below:
                       datatype="decimal,3,5"
                Types: str, BIGINT, BYTEINT, CHAR, DATE, DECIMAL, FLOAT, INTEGER, NUMBER, SMALLINT, TIME,
                       TIMESTAMP, VARCHAR.

        RETURNS:
            An instance of FillNa class.

        RAISES:
            TeradataMlException, TypeError, ValueError

        EXAMPLE:
            # Note:
            #   To run any transformation, user needs to use Transform() function from
            #   Vantage Analytic Library.
            #   To do so import valib first and set the "val_install_location".
            >>> from teradataml import configure, DataFrame, FillNa, load_example_data, valib
            >>> configure.val_install_location = "SYSLIB"
            >>>

            # Load example data.
            >>> load_example_data("dataframe", ["sales", "employee_info"])
            >>>

            # Create the required DataFrames.
            >>> sales = DataFrame("sales")
            >>> sales
                          Feb    Jan    Mar    Apr    datetime
            accounts
            Alpha Co    210.0  200.0  215.0  250.0  04/01/2017
            Blue Inc     90.0   50.0   95.0  101.0  04/01/2017
            Yellow Inc   90.0    NaN    NaN    NaN  04/01/2017
            Jones LLC   200.0  150.0  140.0  180.0  04/01/2017
            Red Inc     200.0  150.0  140.0    NaN  04/01/2017
            Orange Inc  210.0    NaN    NaN  250.0  04/01/2017
            >>>

            # Example 1: Replace missing values in columns 'Jan' and 'Mar', with
            #            a literal value 0. Output columns are named as 'january' and
            #            'march' respectively.
            >>> fillna_literal = FillNa(style="literal", value=0, columns=["Jan", "Mar"],
            ...                         out_columns=["january", "march"])
            >>> obj = valib.Transform(data=sales, fillna=fillna_literal, key_columns="accounts")
            >>> obj.result
                 accounts  january  march
            0    Blue Inc       50     95
            1  Orange Inc        0      0
            2     Red Inc      150    140
            3  Yellow Inc        0      0
            4   Jones LLC      150    140
            5    Alpha Co      200    215
            >>>


            # Example 2: Replace missing values in column 'Jan' with 'median' value from
            #            that column. Output column produced in the output is named as
            #            'Jan2'.
            >>> fillna_median = FillNa(style="median", columns="Jan", out_columns="Jan2")
            >>> obj = valib.Transform(data=sales, fillna=fillna_median, key_columns="accounts")
            >>> obj.result
                 accounts     Jan2
            0    Alpha Co  200.000
            1     Red Inc  150.000
            2  Orange Inc  150.000
            3   Jones LLC  150.000
            4  Yellow Inc  150.000
            5    Blue Inc   50.000
            >>>


            # Example 3: Replace missing values in column 'Apr' with a median value
            #            without mean from that column.
            >>> fillna_mwm = FillNa(style="median_wo_mean", columns="Apr")
            >>> obj = valib.Transform(data=sales, fillna=fillna_mwm, key_columns="accounts")
            >>> obj.result
                 accounts  Apr
            0    Alpha Co  250
            1    Blue Inc  101
            2  Yellow Inc  180
            3   Jones LLC  180
            4     Red Inc  180
            5  Orange Inc  250
            >>>


            # Example 4: Replace missing values in column 'Apr' with 'mode' value from
            #            that column. Output column produced in the output is named as
            #            'Apr2000'.
            >>> fillna_mode = FillNa(style="mode", columns="Apr", out_columns="Apr2000")
            >>> obj = valib.Transform(data=sales, fillna=fillna_mode, key_columns="accounts")
            >>> obj.result
                 accounts  Apr2000
            0    Blue Inc      101
            1  Orange Inc      250
            2     Red Inc      250
            3  Yellow Inc      250
            4   Jones LLC      180
            5    Alpha Co      250
            >>>


            # Example 5: Replace missing values in columns 'masters' and 'programming' using
            #            'imputed' style.
            >>> load_example_data("dataframe", ["admissions_train_nulls", "admissions_train"])

            # Dataframe to be used for 'imputed' style replacement.
            >>> admissions_train = DataFrame("admissions_train")
            >>> admissions_train
               masters   gpa     stats programming  admitted
            id
            22     yes  3.46    Novice    Beginner         0
            26     yes  3.57  Advanced    Advanced         1
            5       no  3.44    Novice      Novice         0
            17      no  3.83  Advanced    Advanced         1
            13      no  4.00  Advanced      Novice         1
            19     yes  1.98  Advanced    Advanced         0
            36      no  3.00  Advanced      Novice         0
            15     yes  4.00  Advanced    Advanced         1
            34     yes  3.85  Advanced    Beginner         0
            38     yes  2.65  Advanced    Beginner         1
            >>>

            # DataFrame containing NULL values in columns "programming" and "masters".
            >>> admissions_train_nulls = DataFrame("admissions_train_nulls")
            >>> admissions_train_nulls
               masters   gpa     stats programming  admitted
            id
            5       no  3.44    Novice      Novice         0
            7      yes  2.33    Novice      Novice         1
            22    None  3.46    Novice        None         0
            19     yes  1.98  Advanced    Advanced         0
            15    None  4.00  Advanced    Advanced         1
            17    None  3.83  Advanced    Advanced         1
            34    None  3.85  Advanced    Beginner         0
            13      no  4.00  Advanced      Novice         1
            36      no  3.00  Advanced      Novice         0
            40     yes  3.95    Novice    Beginner         0
            >>>

            # Replace NULL values in the columns "masters" and "programming"
            # in admissions_train_nulls dataframe with the values in the corresponding
            # columns' values in admissions_train dataframe.
            >>> fillna_imputed = FillNa(style="imputed",
            ...                         columns=["masters", "programming"],
            ...                         value=admissions_train)
            >>> obj = valib.Transform(data=admissions_train_nulls,
            ...                       fillna=fillna_imputed,
            ...                       key_columns="id")
            >>> obj.result
               id masters programming
            0  22     yes    Beginner
            1  36      no      Novice
            2  15     yes    Advanced
            3  38     yes    Beginner
            4   5      no      Novice
            5  17      no    Advanced
            6  34     yes    Beginner
            7  13      no      Novice
            8  26     yes    Advanced
            9  19     yes    Advanced
            >>>


            # Example 6: This example shows how one can operate on date and character
            #            columns. Example also showcases using multiple missing value
            #            treatment techniques in one single call for variable
            #            transformation.
            # Create the required DataFrames.
            >>> einfo = DataFrame("employee_info")
            >>> einfo
                        first_name marks   dob joined_date
            employee_no
            100               abcd  None  None        None
            112               None  None  None    18/12/05
            101              abcde  None  None    02/12/05
            >>>

            # Using literal style for missing value treatment on a date type
            # column "joined_date".
            >>> fillna_1 = FillNa(style="literal", value="DATE 1995-12-23",
            ...                   columns="joined_date", out_columns="date1")

            # Using literal style for missing value treatment on a character type
            # column "first_name". Repalce missing values with 'FNU', i.e.,
            # First Name Unknown.
            >>> fillna_2 = FillNa(style="literal", value="FNU", columns="first_name",
            ...                   out_columns="char1")

            # Using mean value for missing value treatment on a date type
            # column "joined_date".
            >>> fillna_3 = FillNa(style="mean", columns="joined_date",
            ...                   out_columns="date2")

            # Using median value for missing value treatment on a date type
            # column "joined_date".
            >>> fillna_4 = FillNa(style="median", columns="joined_date",
            ...                   out_columns="date2A")

            # Using median value without mean for missing value treatment on
            # a date type column "joined_date".
            >>> fillna_5 = FillNa(style="median_wo_mean", columns="joined_date",
            ...                   out_columns="date3")

            # Using mode value for missing value treatment on a date type
            # column "joined_date".
            >>> fillna_6 = FillNa(style="mode", columns="joined_date",
            ...                   out_columns="date4")

            # Using median value without mean for missing value treatment on
            # a character type column "first_name".
            >>> fillna_7 = FillNa(style="median_wo_mean", columns="first_name",
            ...                   out_columns="char2")

            # Using mode value for missing value treatment on a character type
            # column "first_name".
            >>> fillna_8 = FillNa(style="mode", columns="first_name",
            ...                   out_columns="char3")

            # Perform the missing value transformations using Transform() function
            # from Vantage Analytic Library.
            >>> obj = valib.Transform(data=einfo,
            ...                       fillna=[fillna_1, fillna_2, fillna_3, fillna_4,
            ...                       fillna_5, fillna_6, fillna_7, fillna_8],
            ...                       key_columns="employee_no")
            >>> obj.result
               employee_no     date1  char1     date2    date2A     date3     date4  char2  char3
            0          112  18/12/05    FNU  18/12/05  18/12/05  18/12/05  18/12/05   abcd   abcd
            1          101  02/12/05  abcde  02/12/05  02/12/05  02/12/05  02/12/05  abcde  abcde
            2          100  95/12/23   abcd  60/12/04  60/12/04  02/12/05  02/12/05   abcd   abcd
            >>>
        """
        # Call super()
        super().__init__(columns=columns, out_columns=out_columns, datatype=datatype, columns_optional=True)
        # Initialize style and value as data members.
        self.style = style
        self.value = value

        # Validations
        arg_info_matrix = []
        permitted_styles = ["LITERAL", "MEAN", "MEDIAN", "MEDIAN_WO_MEAN", "MODE",
                            "IMPUTED"]
        arg_info_matrix.append(["style", self.style, True, str, True, permitted_styles])
        arg_info_matrix.append(["value", self.value, True, (DataFrame, bool, int, float, str, date)])

        # Note:
        #   Validations for "columns", "out_columns" and "datatype" is done by super().
        # Other argument validations.
        _Validators._validate_function_arguments(arg_info_matrix)

        # If date object is passed to "value" argument
        # then convert date object to string format 'DATE 1978-06-09'
        if isinstance(self.value, date):
            self.value = UtilFuncs._convert_date_to_string(self.value)

        # If style is 'MEDIAN_WO_MEAN', in SQL we will use 'medianwithoutaveraging'.
        if self.style.upper() == "MEDIAN_WO_MEAN":
            self.style = "medianwithoutaveraging"

        # "value" should be provided when "style" is 'literal' or 'imputed'.
        # "value" is ignored when style is other than 'literal' or 'imputed'.
        if self.style.upper() in ["LITERAL", "IMPUTED"] and value is None:
            err_ = Messages.get_message(MessageCodes.DEPENDENT_ARG_MISSING, "value",
                                        "style={}".format(self.style))
            raise TeradataMlException(err_, MessageCodes.DEPENDENT_ARG_MISSING)

        if self.style.upper() == "IMPUTED":
            if not isinstance(value, DataFrame):
                err_ = Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE, "value",
                                            "teradataml DataFrame")
                raise TypeError(err_)
            else:
                if value._table_name is None:
                    value._table_name = df_utils._execute_node_return_db_object_name(
                        value._nodeid, value._metaexpr)
                self.value = UtilFuncs._extract_table_name(value._table_name).replace(
                    "\"", "")

        # Add double single quotes when "value" contains any of the special val symbols.
        # Note:
        #   Following are special val symbols {'{', '}', '(', ')', ',', '/'}.
        if isinstance(self.value, str) and len(re.findall(r'[\{\}\(\),/]', self.value)) > 0:
            self.value = """''{}''""".format(self.value)

    def _val_nullstyle_fmt(self):
        """
        DESCRIPTION:
            Internal function to return a string representation of nullstyle
            Transformation technique.

        PARAMETERS:
            None.

        RETURNS:
            String representing nullstyle SQL syntax.

        RAISES:
            None.

        EXAMPLE:
            self._val_nullstyle_fmt()
        """
        nullstyle_fmt = "nullstyle({})"

        nullstyle_args = self.style.lower()
        if self.style.upper() in ["LITERAL", "IMPUTED"]:
            nullstyle_args = "{}, {}".format(self.style.lower(), '\'\'\'\'' if isinstance(self.value, str) and len(
                self.value) == 0 else self.value)
        return nullstyle_fmt.format(nullstyle_args)

    def _val_sql_syntax(self):
        """
        DESCRIPTION:
            Internal function to return a string representation of null replacement
            Transformation as required by SQL.

        PARAMETERS:
            None.

        RETURNS:
            String representing SQL syntax for 'nullreplacement' SQL argument.

        RAISES:
            None.

        EXAMPLE:
            self._val_sql_syntax()
        """
        ret_value = self._val_nullstyle_fmt()
        columns_fmt = self._val_transformation_fmt()
        if columns_fmt:
            ret_value = "{}, {}".format(ret_value, columns_fmt)

        return "{" + ret_value + "}"

class Binning(_Transformations):
    """ Class to represent binning transformation technique. """

    def __init__(self, columns, style="bins", value=10, lbound=None, ubound=None,
                 out_columns=None, datatype=None, fillna=None, **kwargs):
        """
        DESCRIPTION:
            Binning allows user to perform bin coding to replace continuous numeric
            column with a categorical one to produce ordinal values (for example,
            numeric categorical values where order is meaningful). Binning uses the
            same techniques used in Histogram analysis, allowing you to choose between:
                1. equal-width bins,
                2. equal-width bins with a user-specified minimum and maximum range,
                3. bins with a user-specified width,
                4. evenly distributed bins, or
                5. bins with user-specified boundaries.

            If the minimum and maximum are specified, all values less than the minimum
            are put into bin 0, while all values greater than the maximum are put into
            bin N+1. The same is true when the boundary option is specified.

            Bin Coding supports numeric and date type columns. If date values are entered,
            the keyword DATE must precede the date value, and do not enclose in single
            quotes.

            Note:
                Output of this function is passed to "bins" argument of "Transform"
                function from Vantage Analytic Library.

        PARAMETERS:
            columns:
                Required Argument.
                Specifies the names of the columns to perform transformation on.
                Types: str or list of str

            style:
                Optional Argument.
                Specifies the bin style to use.
                Permitted Values:
                    * "bins":
                        This style allows user to specify equal-width bins without any
                        boundaries. Argument "values" must be used when this style of
                        binning is used.
                    * "binswithboundaries":
                        This style allows user to specify equal-width bins with minimum
                        and maximum range. Arguments "values", "lbound" and "ubound" must
                        be used when this style of binning is used.
                        All values less than the minimum are put into bin 0, while all
                        values greater than the maximum are put into bin N+1.
                    * "boundaries":
                        This style allows user to specify bins with boundaries.
                        To specify boundaries one should use keyword arguments as:
                            b1 --> To specify first boundary.
                            b2 --> To specify second boundary.
                            b3 --> To specify third boundary.
                            ...
                            bN --> To specify Nth boundary.
                        All values less than the first boundary value are put into bin 0,
                        while all values greater than the last boundary value are put into
                        bin N+1.
                        See "kwargs" description below for more details on how these
                        arguments must be used.
                    * "quantiles":
                        This style allows user to specify evenly-distributed bins.
                        Argument "values" must be used when this style of binning is used.
                    * "width":
                        This style allows user to specify bins with widths. Argument
                        "values" must be used when this style of binning is used.
                Default Value: 'bins'
                Types: str

            value:
                Optional Argument.
                Specifies the value to be used for bin code transformations.
                When bin style is:
                    * 'bins' or 'binswithboundaries' argument specifies the number of bins.
                    * 'quantiles' argument specifies the number of quantiles.
                    * 'width' argument specifies the bin width.
                Note:
                    Ignored when style is 'boundaries'.
                Default Value: 10
                Types: int

            lbound:
                Optional Argument.
                Specifies the minimum boundary value for 'binswithboundaries' style.
                Notes:
                    1. Ignored when style is not 'binswithboundaries'.
                    2. If date values are entered as string, the keyword 'DATE' must precede
                       the date value, and do not enclose in single quotes OR
                       pass a datetime.date object.
                       For example,
                            value='DATE 1987-06-09'
                            value=date(1987, 6, 9)
                Types: int, float, str, datetime.date

            ubound:
                Optional Argument.
                Specifies the maximum boundary value for 'binswithboundaries' style.
                Notes:
                    1. Ignored when style is not 'binswithboundaries'.
                    2. If date values are entered as string, the keyword 'DATE' must precede
                       the date value, and do not enclose in single quotes OR
                       pass a datetime.date object.
                       For example,
                            value='DATE 1987-06-09'
                            value=date(1987, 6, 9)
                Types: int, float, str, datetime.date

            out_columns:
                Optional Argument.
                Specifies the names of the output columns.
                Note:
                    Number of elements in "columns" and "out_columns" must be same.
                Types: str or list of str

            datatype:
                Optional Argument.
                Specifies the name of the intended datatype of the output column.
                Intended data types for the output column can be specified using either the
                teradatasqlalchemy types or the permitted strings mentioned below:
                 -------------------------------------------------------------------
                | If intended SQL Data Type is  | Permitted Value to be passed is   |
                |-------------------------------------------------------------------|
                | bigint                        | bigint                            |
                | byteint                       | byteint                           |
                | char(n)                       | char,n                            |
                | date                          | date                              |
                | decimal(m,n)                  | decimal,m,n                       |
                | float                         | float                             |
                | integer                       | integer                           |
                | number(*)                     | number                            |
                | number(n)                     | number,n                          |
                | number(*,n)                   | number,*,n                        |
                | number(n,n)                   | number,n,n                        |
                | smallint                      | smallint                          |
                | time(p)                       | time,p                            |
                | timestamp(p)                  | timestamp,p                       |
                | varchar(n)                    | varchar,n                         |
                --------------------------------------------------------------------
                Notes:
                    1. Argument is ignored if "columns" argument is not used.
                    2. char without a size is not supported.
                    3. number(*) does not include the * in its datatype format.
                Examples:
                    1. If intended datatype for the output column is "bigint", then
                       pass string "bigint" to the argument as shown below:
                       datatype="bigint"
                    2. If intended datatype for the output column is "decimal(3,5)", then
                       pass string "decimal,3,5" to the argument as shown below:
                       datatype="decimal,3,5"
                Types: str, BIGINT, BYTEINT, CHAR, DATE, DECIMAL, FLOAT, INTEGER, NUMBER, SMALLINT, TIME,
                       TIMESTAMP, VARCHAR.

            fillna:
                Optional Argument.
                Specifies whether the null replacement/missing value treatment should
                be performed with binning or not. Output of FillNa() can be passed to
                this argument.
                Note:
                    If the FillNa object is created with its arguments "columns",
                    "out_columns" and "datatype", then values passed in FillNa() arguments
                    are ignored. Only nullstyle information is captured from the same.
                Types: FillNa

            kwargs:
                Specifies the keyword arguments to provide the boundaries required
                for binning with bin style 'boundaries'.
                To specify boundaries one should use keyword arguments as:
                    b1 --> To specify first boundary.
                    b2 --> To specify second boundary.
                    b3 --> To specify third boundary.
                    ...
                    bN --> To specify Nth boundary.
                Notes:
                    1. When keyword arguments are used, make sure to specify boundaries
                       in sequence, i.e., b1, b2, b3, ...
                       In case a sequential keyword argument is missing an error is
                       raised.
                    2. Keyword arguments specified for the boundaries must start with 'b'.
                    3. First boundary must always be specified with "b1" argument.
                Types: int, float, str, datetime.date

        RETURNS:
            An instance of Binning class.

        RAISES:
            TeradataMlException, TypeError, ValueError

        EXAMPLE:
            # Note:
            #   To run any transformation, user needs to use Transform() function from
            #   Vantage Analytic Library.
            #   To do so import valib first and set the "val_install_location".
            >>> from teradataml import configure, DataFrame, Binning, FillNa, load_example_data, valib
            >>> configure.val_install_location = "SYSLIB"
            >>>

            # Load example data.
            >>> load_example_data("movavg", "ibm_stock")
            >>>

            # Create the required teradataml DataFrame.
            >>> ibm_stock = DataFrame.from_table("ibm_stock")
            >>> ibm_stock
                name    period  stockprice
            id
            183  ibm  62/02/07       552.0
            202  ibm  62/03/07       548.0
            181  ibm  62/02/05       551.0
            242  ibm  62/05/02       482.0
            364  ibm  62/10/25       331.0
            221  ibm  62/04/03       513.0
            38   ibm  61/07/11       473.0
            366  ibm  62/10/29       352.0
            326  ibm  62/08/30       387.0
            61   ibm  61/08/11       497.0
            >>>

            # Example 1: Binning is carried out with "bins" style, i.e. equal-width
            #            binning, with 5 number of bins. Null replacement is also combined
            #            with binning.
            #            "key_columns" argument must be used with Transform() function,
            #            when null replacement is being done.
            >>> fn = FillNa(style="literal", value=0)
            >>> bins = Binning(style="bins", value=5, columns="stockprice", fillna=fn)

            # Execute Transform() function.
            >>> obj = valib.Transform(data=ibm_stock,
            ...                       bins=bins,
            ...                       key_columns="id")
            >>> obj.result
                id  stockprice
            0  263           1
            1  324           2
            2  303           2
            3   99           5
            4   36           3
            5   97           5
            6  160           5
            7   59           4
            8   19           4
            9  122           5
            >>>


            # Example 2: Binning is carried out with multiple styles.

            # 'binswithboundaries' style:
            #   Equal-width bins with a user-specified minimum and maximum range on 'period'
            #   column. Resultant output return the value with the same column name. Number
            #   of bins created are 5.
            >>> bins_1 = Binning(style="binswithboundaries",
            ...                  value=5,
            ...                  lbound="DATE 1962-01-01",
            ...                  ubound="DATE 1962-06-01",
            ...                  columns="period")
            >>>

            # 'boundaries' style:
            #   Bins created with user specified boundaries on 'period' column. Resultant
            #   column is names as 'period2'. Three boundaries are specified with arguments
            #   "b1", "b2" and "b3". When using this style, keyword argument names must
            #   start with 'b' and they should be in sequence b1, b2, ..., bN.
            >>> bins_2 = Binning(style="boundaries",
            ...                  b1="DATE 1962-01-01",
            ...                  b2="DATE 1962-06-01",
            ...                  b3="DATE 1962-12-31",
            ...                  columns="period",
            ...                  out_columns="period2")
            >>>

            # Execute Transform() function.
            >>> obj = valib.Transform(data=ibm_stock,
            ...                       bins=[bins_1, bins_2])
            >>> obj.result
                id  period  period2
            0  223       4        1
            1  345       6        2
            2  120       0        0
            3  343       6        2
            4   57       0        0
            5  118       0        0
            6  200       3        1
            7   80       0        0
            8  162       1        1
            9   40       0        0
            >>>


            # Example 3: Binning is carried out with multiple styles 'quantiles' and
            #            'width'.

            # 'quantiles' style :
            #   Evenly distributed bins on 'stockprice' column. Resultant output returns
            #   the column with name 'stockprice_q'. Number of quantiles considered here
            #   are 4.
            >>> bins_1 = Binning(style="quantiles",
            ...                  value=4,
            ...                  out_columns="stockprice_q",
            ...                  columns="stockprice")
            >>>

            # 'width' style :
            #   Bins with user specified width on 'stockprice' column. Resultant output
            #   returns the column with name 'stockprice_w'. Width considered for binning
            #   is 5.
            >>> bins_2 = Binning(style="width",
            ...                  value=5,
            ...                  out_columns="stockprice_w",
            ...                  columns="stockprice")
            >>>

            # Execute Transform() function.
            >>> obj = valib.Transform(data=ibm_stock,
            ...                       bins=[bins_1, bins_2])
            >>> obj.result
                id  stockprice_q  stockprice_w
            0  183             4            50
            1  202             3            49
            2  181             4            50
            3  242             2            36
            4  364             1             6
            5  221             3            42
            6   38             2            34
            7  366             1            10
            8  326             1            17
            9   61             3            39
            >>>
        """
        # Call super()
        super().__init__(columns=columns, out_columns=out_columns, datatype=datatype,
                         columns_optional=False)

        # Initialize style and value as data members.
        self.style = style
        self.value = value
        self.lbound = lbound
        self.ubound = ubound
        self.fillna = fillna
        self.kwargs = kwargs

        # Validations
        arg_info_matrix = []
        permitted_styles = ["BINS", "BINSWITHBOUNDARIES", "BOUNDARIES", "QUANTILES",
                            "WIDTH"]
        arg_info_matrix.append(["style", self.style, True, str, True, permitted_styles])
        arg_info_matrix.append(["value", self.value, True, int])
        arg_info_matrix.append(["lbound", self.lbound, True, (bool, int, float, str, date)])
        arg_info_matrix.append(["ubound", self.ubound, True, (bool, int, float, str, date)])
        arg_info_matrix.append(["fillna", self.fillna, True, FillNa])
        # Note:
        #   Validations for "columns", "out_columns" and "datatype" is done by super().
        # Other argument validations.
        _Validators._validate_function_arguments(arg_info_matrix)

        # "value" should be provided when "style" is 'bins'.
        if self.style.upper() in ["BINS", "QUANTILES", "WIDTH"] and self.value is None:
            err_ = Messages.get_message(MessageCodes.DEPENDENT_ARG_MISSING, "value",
                                        "style={}".format(self.style))
            raise TeradataMlException(err_, MessageCodes.DEPENDENT_ARG_MISSING)

        # "value", "lbound", "ubound" should be provided when "style" is 'binswithboundaries'.
        if self.style.upper() == "BINSWITHBOUNDARIES":
            if self.value is None:
                err_ = Messages.get_message(MessageCodes.DEPENDENT_ARG_MISSING, "value",
                                            "style={}".format(self.style))
                raise TeradataMlException(err_, MessageCodes.DEPENDENT_ARG_MISSING)

            if self.lbound is None:
                err_ = Messages.get_message(MessageCodes.DEPENDENT_ARG_MISSING, "lbound",
                                            "style={}".format(self.style))
                raise TeradataMlException(err_, MessageCodes.DEPENDENT_ARG_MISSING)

            if self.ubound is None:
                err_ = Messages.get_message(MessageCodes.DEPENDENT_ARG_MISSING, "ubound",
                                            "style={}".format(self.style))
                raise TeradataMlException(err_, MessageCodes.DEPENDENT_ARG_MISSING)

        if self.style.upper() == "BOUNDARIES":
            # Parse kwargs now for "boundaries" style argument.
            # Expected arguments are b1, b2, ..., bN.
            # We start extracting each boundary argument one by one and store
            # it's corresponding value that can be used later to generate
            # the correct binstyle syntax.
            parse_kwargs = True
            key_num = 1
            self.__boundaries = []
            while parse_kwargs:
                value = self.kwargs.pop("b{}".format(str(key_num)), None)
                kwarg_info_matrix=[["b{}".format(str(key_num)), value,
                                    True, (int, float, str, date)]]

                _Validators._validate_function_arguments(kwarg_info_matrix)

                key_num = key_num + 1
                if value is None:
                    parse_kwargs = False
                else:
                    if isinstance(value, date):
                        value = UtilFuncs._convert_date_to_string(value)
                    self.__boundaries.append(value)

            # If kwargs still has some extra arguments that means user has
            # passed incorrect argument.
            if len(kwargs) != 0:
                err_ = "Boundary keyword arguments for \"boundaries\" binning style " \
                       "must be in sequence as b1, b2, ..., bN. Found: " \
                       "{}".format(list(kwargs.keys()))
                raise TypeError(err_)

            # After parsing kwargs, if length of self.__boundaries is 0
            # then we should raise error as boundary values are missing for
            # this binning style.
            if len(self.__boundaries) == 0:
                err_ = Messages.get_message(MessageCodes.DEPENDENT_ARG_MISSING,
                                            "b1, b2, ..., bN",
                                            "style={}".format(self.style))
                raise TeradataMlException(err_, MessageCodes.DEPENDENT_ARG_MISSING)

    def _val_sql_syntax(self):
        """
        DESCRIPTION:
            Internal function to return a string representation of binning
            Transformation as required by SQL.

        PARAMETERS:
            None.

        RETURNS:
            String representing SQL syntax for 'bincode' SQL argument.

        RAISES:
            None.

        EXAMPLE:
            self._val_sql_syntax()
        """
        # Generate and add syntax for "binstyle" SQL argument.
        if self.style.upper() in ["BINS", "QUANTILES", "WIDTH"]:
            binstyle_arg2 = self.value
        elif self.style.upper() == "BINSWITHBOUNDARIES":
            # 'lbound' is provided as date object, convert it to str format
            if isinstance(self.lbound, date):
                self.lbound = UtilFuncs._convert_date_to_string(self.lbound)

            # 'ubound' is provided as date object, convert it to str format
            if isinstance(self.ubound, date):
                self.ubound = UtilFuncs._convert_date_to_string(self.ubound)

            binstyle_arg2 = "{}, {}, {}".format(self.value, self.lbound, self.ubound)
        else:
            binstyle_arg2 = ", ".join([str(v) for v in self.__boundaries])

        ret_value = "binstyle({}, {})".format(self.style.lower(), binstyle_arg2)

        # Generate and add syntax for "columns" and "datatype" SQL arguments.
        columns_fmt = self._val_transformation_fmt()
        ret_value = "{}, {}".format(ret_value, columns_fmt)

        if self.fillna:
            ret_value = "{}, {}".format(ret_value, self.fillna._val_nullstyle_fmt())

        return "{" + ret_value + "}"


class Derive(object):
    """ Class to represent derive transformation technique. """

    def __init__(self, formula, columns, out_column, datatype=None, fillna=None):
        """
        DESCRIPTION:
            The Derive transformation requires the free-form transformation be specified
            as a formula using the following operators, arguments, and functions:
                +, -, **, *, /, %, (, ), x, y, z, abs, exp, ln, log, sqrt
            The arguments x, y, and z can only assume the value of an input column.
            An implied multiply operator is automatically inserted when a number, argument
            (x, y, z), or parenthesis is immediately followed by an argument or parenthesis.
            For example,
                4x means 4*x, xy means x*y, and x(x+1) is equivalent to x*(x+1).

            An example formula for the quadratic equation is below.
                formula="(-y+sqrt(y**2-4xz))/(2x)"

            Note:
                Output of this function is passed to "derive" argument of "Transform"
                function from Vantage Analytic Library.

        PARAMETERS:
            formula:
                Required Argument.
                Specifies the free-form transformation required for Derive.
                Arithmetic formula can be specified as string using following operators,
                arguments, and functions:
                    +, -, **, *, /, %, (, ), x, y, z, abs, exp, ln, log, sqrt
                Types: str

            columns:
                Required Argument.
                Specifies the names of the columns to use for formula.
                Types: str or list of str

            out_column:
                Required Argument.
                Specifies the name of the output column.
                Types: str

            datatype:
                Optional Argument.
                Specifies the name of the intended datatype of the output column.
                Intended data types for the output column can be specified using either the
                teradatasqlalchemy types or the permitted strings mentioned below:
                 -------------------------------------------------------------------
                | If intended SQL Data Type is  | Permitted Value to be passed is   |
                |-------------------------------------------------------------------|
                | bigint                        | bigint                            |
                | byteint                       | byteint                           |
                | char(n)                       | char,n                            |
                | date                          | date                              |
                | decimal(m,n)                  | decimal,m,n                       |
                | float                         | float                             |
                | integer                       | integer                           |
                | number(*)                     | number                            |
                | number(n)                     | number,n                          |
                | number(*,n)                   | number,*,n                        |
                | number(n,n)                   | number,n,n                        |
                | smallint                      | smallint                          |
                | time(p)                       | time,p                            |
                | timestamp(p)                  | timestamp,p                       |
                | varchar(n)                    | varchar,n                         |
                --------------------------------------------------------------------
                Notes:
                    1. Argument is ignored if "columns" argument is not used.
                    2. char without a size is not supported.
                    3. number(*) does not include the * in its datatype format.
                Examples:
                    1. If intended datatype for the output column is "bigint", then
                       pass string "bigint" to the argument as shown below:
                       datatype="bigint"
                    2. If intended datatype for the output column is "decimal(3,5)", then
                       pass string "decimal,3,5" to the argument as shown below:
                       datatype="decimal,3,5"
                Types: str, BIGINT, BYTEINT, CHAR, DATE, DECIMAL, FLOAT, INTEGER, NUMBER, SMALLINT, TIME,
                       TIMESTAMP, VARCHAR.

            fillna:
                Optional Argument.
                Specifies whether the null replacement/missing value treatment should
                be performed with derive or not. Output of FillNa() can be passed to
                this argument.
                Note:
                    If the FillNa object is created with its arguments "columns",
                    "out_columns" and "datatype", then values passed in FillNa() arguments
                    are ignored. Only nullstyle information is captured from the same.
                Types: FillNa

        RETURNS:
            An instance of Derive class.

        RAISES:
            TeradataMlException, TypeError, ValueError

        EXAMPLE:
            # Note:
            #   To run any transformation, user needs to use Transform() function from
            #   Vantage Analytic Library.
            #   To do so import valib first and set the "val_install_location".
            >>> from teradataml import configure, DataFrame, Derive, FillNa, load_example_data, valib
            >>> configure.val_install_location = "SYSLIB"
            >>>

            # Load example data.
            >>> load_example_data("dataframe", "sales")
            >>>

            # Create the required DataFrame.
            >>> sales = DataFrame("sales")
            >>> sales
                          Feb    Jan    Mar    Apr    datetime
            accounts
            Blue Inc     90.0   50.0   95.0  101.0  04/01/2017
            Alpha Co    210.0  200.0  215.0  250.0  04/01/2017
            Jones LLC   200.0  150.0  140.0  180.0  04/01/2017
            Yellow Inc   90.0    NaN    NaN    NaN  04/01/2017
            Orange Inc  210.0    NaN    NaN  250.0  04/01/2017
            Red Inc     200.0  150.0  140.0    NaN  04/01/2017
            >>>

            # Example: Includes multiple derive transformations.
            # Derive transformation 1 is done with 3 variables, x, y, z, to calculate
            # the total sales for the first quarter for each account.
            >>> fn_1 = FillNa(style='literal', value=0)
            >>> dr_1 = Derive(formula="x+y+z", columns=["Jan", "Feb", "Mar"],
            ...               out_column="q1_sales", fillna=fn_1)
            >>>

            # Derive transformation 2 is done with 2 variables, x, y, to calculate
            # the sale growth from the month of Jan to Feb.
            >>> fn_2 = FillNa(style='median')
            >>> dr_2 = Derive(formula="((y-x)/x)*100", columns=["Jan", "Feb"],
            ...               out_column="feb_growth", fillna=fn_2, datatype='bigint')
            >>>

            # Execute Transform() function.
            >>> obj = valib.Transform(data=sales, derive=[dr_1, dr_2], key_columns="accounts")
            >>> obj.result
                 accounts  q1_sales  feb_growth
            0    Alpha Co     625.0           4
            1     Red Inc     490.0          33
            2  Orange Inc       NaN          40
            3   Jones LLC     490.0          33
            4  Yellow Inc       NaN         -40
            5    Blue Inc     235.0          79
            >>>
        """
        # Initialize style and value as data members.
        self.formula = formula
        self.columns = columns
        self.out_column = out_column
        self.datatype = datatype
        self.fillna = fillna

        # Validations
        arg_info_matrix = []
        arg_info_matrix.append(["formula", self.formula, False, str, True])
        arg_info_matrix.append(["columns", self.columns, False, (str, list), True])
        arg_info_matrix.append(["out_column", self.out_column, False, str, True])
        arg_info_matrix.append(["datatype", self.datatype, True, _SuppArgTypes.VAL_ARG_DATATYPE, True])
        arg_info_matrix.append(["fillna", self.fillna, True, FillNa])

        _Validators._validate_function_arguments(arg_info_matrix)

    def _val_sql_syntax(self):
        """
        DESCRIPTION:
            Internal function to return a string representation of derive
            Transformation as required by SQL.

        PARAMETERS:
            None.

        RETURNS:
            String representing SQL syntax for 'derive' SQL argument.

        RAISES:
            None.

        EXAMPLE:
            self._val_sql_syntax()
        """
        derive_fmt = "formula(''{}''), arguments({}), outputname({})"
        arguments = ", ".join(UtilFuncs._as_list(self.columns))
        ret_value = derive_fmt.format(self.formula, arguments, self.out_column)

        # Generate and add syntax for "datatype" SQL argument.
        if self.datatype is not None:
            self.datatype = self.datatype if isinstance(self.datatype, str) else \
                            _DtypesMappers.TDSQLALCHEMY_DATATYPE_TO_VAL_STRING_MAPPER\
                            [type(self.datatype)](self.datatype)
            ret_value = "{}, datatype({})".format(ret_value, self.datatype)

        # Generate and add syntax for "nullstyle", a SQL arguments.
        if self.fillna:
            ret_value = "{}, {}".format(ret_value, self.fillna._val_nullstyle_fmt())

        # Return the SQL syntax for "derive", a SQL argument.
        return "{" + ret_value + "}"


class OneHotEncoder(_Transformations):
    """ Class to represent one hot encoding transformation technique. """

    def __init__(self, values, columns, style="dummy", reference_value=None,
                 out_columns=None, datatype=None, fillna=None):
        """
        DESCRIPTION:
            One hot encoding is useful when a categorical data element must be re-expressed
            as one or more numeric data elements, creating a binary numeric field for
            each categorical data value. One hot encoding supports character, numeric,
            and date type columns.
            One hot encoding is offered in two forms: dummy-coding and contrast-coding.
                * In dummy-coding, a new column is produced for each listed value, with
                  a value of 0 or 1 depending on whether that value is assumed by the
                  original column. If a column assumes n values, new columns can be
                  created for all n values, (or for only n-1 values, because the nth
                  column is perfectly correlated with the first n-1 columns).
                * Alternately, given a list of values to contrast-code along with a
                  reference value, a new column is produced for each listed value, with
                  a value of 0 or 1 depending on whether that value is assumed by the
                  original column, or a value of -1 if that original value is equal to
                  the reference value.

            Note:
                Output of this function is passed to "one_hot_encode" argument of
                "Transform" function from Vantage Analytic Library.

        PARAMETERS:
            values:
                Required Argument.
                Specifies the values to code and optionally the name of the
                resulting output column.
                Note:
                    1. If date values are entered as string, the keyword 'DATE' must precede
                       the date value, and do not enclose in single quotes OR
                       pass a datetime.date object.
                       For example,
                            value='DATE 1987-06-09'
                            value=date(1987, 6, 9)
                    2. Use a dict to pass value when result output column is to be named.
                       key of the dictionary must be the value to code and value must be
                       either None, in case result output column is not to be named or a
                       string if it is to be named.
                       For example,
                          values = {"Male": M, "Female": None}
                          In the example above,
                            - we would like to name the output column as 'M' for one hot
                              encoded values for "Male" and
                            - for the one hot encoding values of "Female" we would like to
                              have the output name contain/same as that of "Female", thus
                              None is passed as a value.
                Types: bool, float, int, str, dict, datetime.date or list of booleans, floats, integers,
                       strings, datetime.date

            columns:
                Required Argument.
                Specifies the name of the column. Value passed to this argument
                also plays a crucial role in determining the output column name.
                Types: str

            style:
                Optional Argument.
                Specifies the one hot encoding style to use.
                Permitted Values: 'dummy', 'contrast'
                Default Value: 'dummy'
                Types: str

            reference_value:
                Required Argument when "style" is 'contrast', ignored otherwise.
                Specifies the reference value to use for 'contrast' style. If original
                value in the column is equal to the reference value then -1 is returned
                for the same.
                Types: bool, int, float, str, datetme.date

            out_columns:
                Optional Argument.
                Specifies the name of the output column. Value passed to this argument
                also plays a crucial role in determining the output column name.
                Types: str

            datatype:
                Optional Argument.
                Specifies the name of the intended datatype of the output column.
                Intended data types for the output column can be specified using either the
                teradatasqlalchemy types or the permitted strings mentioned below:
                 -------------------------------------------------------------------
                | If intended SQL Data Type is  | Permitted Value to be passed is   |
                |-------------------------------------------------------------------|
                | bigint                        | bigint                            |
                | byteint                       | byteint                           |
                | char(n)                       | char,n                            |
                | date                          | date                              |
                | decimal(m,n)                  | decimal,m,n                       |
                | float                         | float                             |
                | integer                       | integer                           |
                | number(*)                     | number                            |
                | number(n)                     | number,n                          |
                | number(*,n)                   | number,*,n                        |
                | number(n,n)                   | number,n,n                        |
                | smallint                      | smallint                          |
                | time(p)                       | time,p                            |
                | timestamp(p)                  | timestamp,p                       |
                | varchar(n)                    | varchar,n                         |
                --------------------------------------------------------------------
                Notes:
                    1. Argument is ignored if "columns" argument is not used.
                    2. char without a size is not supported.
                    3. number(*) does not include the * in its datatype format.
                Examples:
                    1. If intended datatype for the output column is "bigint", then
                       pass string "bigint" to the argument as shown below:
                       datatype="bigint"
                    2. If intended datatype for the output column is "decimal(3,5)", then
                       pass string "decimal,3,5" to the argument as shown below:
                       datatype="decimal,3,5"
                Types: str, BIGINT, BYTEINT, CHAR, DATE, DECIMAL, FLOAT, INTEGER, NUMBER, SMALLINT, TIME,
                       TIMESTAMP, VARCHAR.

            fillna:
                Optional Argument.
                Specifies whether the null replacement/missing value treatment should
                be performed with one hot encoding or not. Output of FillNa() can be
                passed to this argument.
                Note:
                    If the FillNa object is created with its arguments "columns",
                    "out_columns" and "datatype", then values passed in FillNa() arguments
                    are ignored. Only nullstyle information is captured from the same.
                Types: FillNa

        NOTES:
            Output column names for the transformation using Transform() function depends
            on "values", "columns" and "out_columns" arguments. Here is how output column
            names are determined:
                1. If "values" is not dictionary:
                    a. If "out_columns" is not passed, then output column is formed
                       using the value in "values" and column name passed to "columns".
                       For example,
                            If values=["val1", "val2"] and columns="col"
                            then, output column names are:
                                'val1_col' and 'val2_col'
                    b. If "out_columns" is passed, then output column is formed
                       using the value in "values" and column name passed to "out_columns".
                       For example,
                            If values=["val1", "val2"], columns="col", and
                            out_columns="ocol" then, output column names are:
                                'val1_ocol' and 'val2_ocol'
                2. If "values" is a dictionary:
                    a. If value in a dictionary is not None, then that value is used
                       as output column name.
                       For example:
                            If values = {"val1": "v1"} then output column name is "v1".
                    b. If value in a dictionary is None, then rules specified in point 1
                       are applied to determine the output column name.

        RETURNS:
            An instance of OneHotEncoder class.

        RAISES:
            TeradataMlException, TypeError, ValueError

        EXAMPLE:
            # Note:
            #   To run any transformation, user needs to use Transform() function from
            #   Vantage Analytic Library.
            #   To do so import valib first and set the "val_install_location".
            >>> from teradataml import configure, DataFrame, OneHotEncoder, FillNa, load_example_data, valib
            >>> configure.val_install_location = "SYSLIB"
            >>>

            # Load example data.
            >>> load_example_data("dataframe", "admissions_train")
            >>>

            # Create the required DataFrame.
            >>> df = DataFrame("admissions_train")
            >>> df
               masters   gpa     stats programming  admitted
            id
            13      no  4.00  Advanced      Novice         1
            26     yes  3.57  Advanced    Advanced         1
            5       no  3.44    Novice      Novice         0
            19     yes  1.98  Advanced    Advanced         0
            15     yes  4.00  Advanced    Advanced         1
            40     yes  3.95    Novice    Beginner         0
            7      yes  2.33    Novice      Novice         1
            22     yes  3.46    Novice    Beginner         0
            36      no  3.00  Advanced      Novice         0
            38     yes  2.65  Advanced    Beginner         1
            >>>

            # Example 1: Encode all values 'Novice', 'Advanced', and 'Beginner'
            #            in "programming" column using "dummy" style.
            >>> dc = OneHotEncoder(values=["Novice", "Advanced", "Beginner"], columns="programming")

            # Execute Transform() function.
            >>> obj = valib.Transform(data=df, one_hot_encode=dc, key_columns="id")
            >>> obj.result
               id  Novice_programming  Advanced_programming  Beginner_programming
            0   5                   1                     0                     0
            1  34                   0                     0                     1
            2  13                   1                     0                     0
            3  40                   0                     0                     1
            4  22                   0                     0                     1
            5  19                   0                     1                     0
            6  36                   1                     0                     0
            7  15                   0                     1                     0
            8   7                   1                     0                     0
            9  17                   0                     1                     0
            >>>


            # Example 2: Encode all values 'Novice', 'Advanced', and 'Beginner'
            #            in "programming" column using "dummy" style. Also, pass
            #            "out_columns" argument, to control the name of the output column.
            >>> dc = OneHotEncoder(style="dummy", values=["Novice", "Advanced", "Beginner"],
            ...                    columns="programming", out_columns="prog")

            # Execute Transform() function.
            >>> obj = valib.Transform(data=df, one_hot_encode=dc, key_columns="id")
            >>> obj.result
               id  Novice_prog  Advanced_prog  Beginner_prog
            0  15            0              1              0
            1   7            1              0              0
            2  22            0              0              1
            3  17            0              1              0
            4  13            1              0              0
            5  38            0              0              1
            6  26            0              1              0
            7   5            1              0              0
            8  34            0              0              1
            9  40            0              0              1
            >>>


            # Example 3: Encode all values 'Novice', 'Advanced', and 'Beginner'
            #            in "programming" column using "dummy" style. Example shows
            #            why and how to pass values using dictionary. By passing dictionary,
            #            we should be able to control the name of the output columns.
            #            In this example, we would like to name the output column for
            #            value 'Advanced' as 'Adv', 'Beginner' as 'Beg' and for 'Novice'
            #            we would like to use default mechanism.
            >>> values = {"Novice": None, "Advanced": "Adv", "Beginner": "Beg"}
            >>> dc = OneHotEncoder(style="dummy", values=values, columns="programming")

            # Execute Transform() function.
            >>> obj = valib.Transform(data=df, one_hot_encode=dc, key_columns="id")
            >>> obj.result
               id  Novice_programming  Adv  Beg
            0  13                   1    0    0
            1  26                   0    1    0
            2   5                   1    0    0
            3  19                   0    1    0
            4  15                   0    1    0
            5  40                   0    0    1
            6   7                   1    0    0
            7  22                   0    0    1
            8  36                   1    0    0
            9  38                   0    0    1
            >>>


            # Example 4: Encode all values 'Novice', 'Advanced', and 'Beginner'
            #            in "programming" column using "dummy" style.
            #            Example shows controling of the output column name with dictionary
            #            and "out_columns" argument.
            #            In this example, we would like to name the output column for
            #            value 'Advanced' as 'Adv', 'Beginner' as 'Beg', 'Novice' as 'Nov_prog'.
            >>> values = {"Novice": None, "Advanced": "Adv", "Beginner": "Beg"}
            >>> dc = OneHotEncoder(style="dummy", values=values, columns="programming",
            ...                    out_columns="prog")

            # Execute Transform() function.
            >>> obj = valib.Transform(data=df, one_hot_encode=dc, key_columns="id")
            >>> obj.result
               id  Novice_prog  Adv  Beg
            0  15            0    1    0
            1   7            1    0    0
            2  22            0    0    1
            3  17            0    1    0
            4  13            1    0    0
            5  38            0    0    1
            6  26            0    1    0
            7   5            1    0    0
            8  34            0    0    1
            9  40            0    0    1
            >>>


            # Example 5: Encode 'yes' value in "masters" column using "contrast" style
            #            with reference value as 0.
            >>> dc = OneHotEncoder(style="contrast", values="yes", reference_value=0,
            ...                    columns="masters")

            # Execute Transform() function.
            >>> obj = valib.Transform(data=df, one_hot_encode=dc, key_columns="id")
            >>> obj.result
               id  yes_masters
            0  15            1
            1   7            1
            2  22            1
            3  17            0
            4  13            0
            5  38            1
            6  26            1
            7   5            0
            8  34            1
            9  40            1
            >>>


            # Example 6: Encode all values in "programming" column using "contrast" style
            #            with reference_value as 'Advanced'.
            >>> values = {"Advanced": "Adv", "Beginner": "Beg", "Novice": "Nov"}
            >>> dc = OneHotEncoder(style="contrast", values=values, reference_value="Advanced",
            ...                    columns="programming")

            # Execute Transform() function.
            >>> obj = valib.Transform(data=df, one_hot_encode=dc, key_columns="id")
            >>> obj.result
               id  Adv  Beg  Nov
            0  15    1   -1   -1
            1   7    0    0    1
            2  22    0    1    0
            3  17    1   -1   -1
            4  13    0    0    1
            5  38    0    1    0
            6  26    1   -1   -1
            7   5    0    0    1
            8  34    0    1    0
            9  40    0    1    0
            >>>


            # Example 7: Example shows combining multiple one hot encoding styles on
            #            different columns.

            # Encode all values in 'programming' column using 'dummy' encoding style.
            >>> dc_prog_dummy = OneHotEncoder(values=["Novice", "Advanced", "Beginner"],
            ...                               columns="programming", out_columns="prog")
            >>>

            # Encode all values in 'stats' column using 'dummy' encoding style.
            # Also, combine it with null replacement.
            >>> values = {"Advanced": "Adv", "Beginner": "Beg"}
            >>> fillna = FillNa("literal", "Advanced")
            >>> dc_stats_dummy = OneHotEncoder(values=values, columns="stats", fillna=fillna)
            >>>

            # Encode 'yes' in 'masters' column using 'contrast' encoding style.
            # Reference value used is 'no'.
            >>> dc_mast_contrast = OneHotEncoder(style="contrast", values="yes", reference_value="no",
            ...                                  columns="masters")
            >>>

            # Encode all values in 'programming' column using 'contrast' encoding style.
            # Reference value used is 'Advanced'.
            >>> dc_prog_contrast = OneHotEncoder(style="contrast",
            ...                                  values=["Novice", "Advanced", "Beginner"],
            ...                                  reference_value="Advanced",
            ...                                  columns="programming")
            >>>

            # Execute Transform() function.
            >>> obj = valib.Transform(data=df,
            ...                       one_hot_encode=[dc_prog_dummy, dc_stats_dummy,
            ...                                   dc_mast_contrast, dc_prog_contrast],
            ...                       key_columns="id")
            >>> obj.result
               id  Novice_prog  Advanced_prog  Beginner_prog  Adv  Beg  yes_masters  Novice_programming  Advanced_programming  Beginner_programming
            0  13            1              0              0    1    0           -1                   1                     0                     0
            1  26            0              1              0    1    0            1                  -1                     1                    -1
            2   5            1              0              0    0    0           -1                   1                     0                     0
            3  19            0              1              0    1    0            1                  -1                     1                    -1
            4  15            0              1              0    1    0            1                  -1                     1                    -1
            5  40            0              0              1    0    0            1                   0                     0                     1
            6   7            1              0              0    0    0            1                   1                     0                     0
            7  22            0              0              1    0    0            1                   0                     0                     1
            8  36            1              0              0    1    0           -1                   1                     0                     0
            9  38            0              0              1    1    0            1                   0                     0                     1
            >>>
        """
        # Initialize style and value as data members.
        self.style = style
        self.values = values
        self.reference_value = reference_value
        self.fillna = fillna
        self.columns = columns
        self.out_columns = out_columns

        # Validations
        arg_info_matrix = []
        permitted_styles = ["DUMMY", "CONTRAST"]
        arg_info_matrix.append(["style", self.style, True, str, True, permitted_styles])
        arg_info_matrix.append(["values", self.values, False,
                                (bool, float, int, str, list, dict, date)])
        arg_info_matrix.append(["reference_value", self.reference_value, True,
                                (bool, int, float, str, date)])
        arg_info_matrix.append(["fillna", self.fillna, True, FillNa])
        # "columns" and "out_columns" they can only accept a string, hence are being validated
        # here.
        arg_info_matrix.append(["columns", self.columns, False, str])
        arg_info_matrix.append(["out_columns", self.out_columns, True, str])
        # Other argument validations.
        _Validators._validate_function_arguments(arg_info_matrix)

        # Call super()
        super().__init__(columns=columns, out_columns=out_columns, datatype=datatype)
        # Note:
        #   Validations for "datatype" is done by super().

        # "reference_value" should be provided when "style" is 'contrast'.
        if self.style.upper() == "CONTRAST" and self.reference_value is None:
            err_ = Messages.get_message(MessageCodes.DEPENDENT_ARG_MISSING,
                                        "reference_value",
                                        "style={}".format(self.style))
            raise TeradataMlException(err_, MessageCodes.DEPENDENT_ARG_MISSING)

        if isinstance(self.reference_value, date):
            self.reference_value = UtilFuncs._convert_date_to_string(self.reference_value)

    def _val_sql_syntax(self):
        """
        DESCRIPTION:
            Internal function to return a string representation of design code
            Transformation as required by SQL.

        PARAMETERS:
            None.

        RETURNS:
            String representing SQL syntax for 'designcode' SQL argument.

        RAISES:
            None.

        EXAMPLE:
            self._val_sql_syntax()
        """
        # Generate syntax for "designstyle" and "designvalues" SQL arguments.
        design_style = "dummycode"
        if self.style.upper() == "CONTRAST":
            design_style = "contrastcode, {}".format(self.reference_value)

        if isinstance(self.values, list):
            self.values = [
                UtilFuncs._convert_date_to_string(val) if isinstance(val, date) else val \
                                for val in self.values]
            design_values = [str(val) if not isinstance(val, str) else val for val in self.values]
            design_values = ", ".join(design_values)
        elif isinstance(self.values, dict):
            values = []
            for val in self.values:
                if self.values[val] is not None:
                    if isinstance(self.values[val], date):
                        self.values[val] = UtilFuncs._convert_date_to_string(self.values[val])
                    values.append("{}/{}".format(val, self.values[val]))
                else:
                    values.append(str(val))
            design_values = ", ".join(values)
        elif isinstance(self.values, date):
            design_values = UtilFuncs._convert_date_to_string(self.values)
        else:
            design_values = self.values

        ret_value = "designstyle({}), designvalues({})".format(design_style,
                                                               design_values)

        # Generate and add syntax for "columns" and "datatype" SQL arguments.
        columns_fmt = self._val_transformation_fmt()
        ret_value = "{}, {}".format(ret_value, columns_fmt)

        # Generate and add syntax for "nullstyle", a SQL arguments.
        if self.fillna:
            ret_value = "{}, {}".format(ret_value, self.fillna._val_nullstyle_fmt())

        # Return the SQL syntax for "designcode", a SQL argument.
        return "{" + ret_value + "}"


class LabelEncoder(_Transformations):
    """
    Class to represent label encoding, i.e., variable recoding transformation technique.
    """

    def __init__(self, values, columns, default=None, out_columns=None, datatype=None,
                 fillna=None):
        """
        DESCRIPTION:
            Label encoding a categorical data column is done to re-express existing values
            of a column (variable) into a new coding scheme or to correct data quality
            problems and focus an analysis of a particular value. It allows for mapping
            individual values, NULL values, or any number of remaining values (ELSE
            option) to a new value, a NULL value or the same value.
            Label encoding supports character, numeric, and date type columns.

            Note:
                Output of this function is passed to "label_encode" argument of "Transform"
                function from Vantage Analytic Library.

        PARAMETERS:
            values:
                Required Argument.
                Specifies the values to be label encoded. Values can be specified in
                two formats:
                    1. A list of two-tuples, where first value in the tuple is a
                       old value and second value is a new value.
                       For example,
                            values = [(old_val1, new_val2), (old_val2, new_val2)]
                    2. A dictionary with key as old value and value as new value.
                       For example,
                            values = {old_val1: new_val2, old_val2: new_val2}
                Note:
                    1. If date values are entered as string, the keyword 'DATE' must precede
                       the date value, and do not enclose in single quotes OR
                       pass a datetime.date object.
                       For example,
                           value='DATE 1987-06-09'
                           value=date(1987, 6, 9)
                    2. To keep the old value as is, one can pass 'same' as it's new value.
                    3. To use NULL values for old or new value, one can either use string
                       'null' or None.
                Types: two-tuple, list of two-tuples, dict

            columns:
                Required Argument.
                Specifies the names of the columns containing values to be label encoded.
                Types: str or list of str

            default:
                Optional Argument.
                Specifies the value assumed for all other cases.
                Permitted Values: None, 'SAME', 'NULL', a literal
                Default Value: None
                Types: bool, float, int, str

            out_columns:
                Optional Argument.
                Specifies the names of the output columns. Value passed to this argument
                also plays a crucial role in determining the output column name.
                Note:
                    Number of elements in "columns" and "out_columns" must be same.
                Types: str or list of str

            datatype:
                Optional Argument.
                Specifies the name of the intended datatype of the output column.
                Intended data types for the output column can be specified using either the
                teradatasqlalchemy types or the permitted strings mentioned below:
                 -------------------------------------------------------------------
                | If intended SQL Data Type is  | Permitted Value to be passed is   |
                |-------------------------------------------------------------------|
                | bigint                        | bigint                            |
                | byteint                       | byteint                           |
                | char(n)                       | char,n                            |
                | date                          | date                              |
                | decimal(m,n)                  | decimal,m,n                       |
                | float                         | float                             |
                | integer                       | integer                           |
                | number(*)                     | number                            |
                | number(n)                     | number,n                          |
                | number(*,n)                   | number,*,n                        |
                | number(n,n)                   | number,n,n                        |
                | smallint                      | smallint                          |
                | time(p)                       | time,p                            |
                | timestamp(p)                  | timestamp,p                       |
                | varchar(n)                    | varchar,n                         |
                --------------------------------------------------------------------
                Notes:
                    1. Argument is ignored if "columns" argument is not used.
                    2. char without a size is not supported.
                    3. number(*) does not include the * in its datatype format.
                Examples:
                    1. If intended datatype for the output column is "bigint", then
                       pass string "bigint" to the argument as shown below:
                       datatype="bigint"
                    2. If intended datatype for the output column is "decimal(3,5)", then
                       pass string "decimal,3,5" to the argument as shown below:
                       datatype="decimal,3,5"
                Types: str, BIGINT, BYTEINT, CHAR, DATE, DECIMAL, FLOAT, INTEGER, NUMBER, SMALLINT, TIME,
                       TIMESTAMP, VARCHAR.

            fillna:
                Optional Argument.
                Specifies whether the null replacement/missing value treatment should
                be performed with recoding or not. Output of FillNa() can be passed to
                this argument.
                Note:
                    If the FillNa object is created with its arguments "columns",
                    "out_columns" and "datatype", then values passed in FillNa() arguments
                    are ignored. Only nullstyle information is captured from the same.
                Types: FillNa

        RETURNS:
            An instance of LabelEncoder class.

        RAISES:
            TeradataMlException, TypeError, ValueError

        EXAMPLE:
            # Note:
            #   To run any transformation, user needs to use Transform() function from
            #   Vantage Analytic Library.
            #   To do so import valib first and set the "val_install_location".
            >>> from teradataml import configure, DataFrame, LabelEncoder, FillNa, load_example_data, valib
            >>> configure.val_install_location = "SYSLIB"
            >>>

            # Load example data.
            >>> load_example_data("dataframe", "admissions_train")
            >>>

            # Create the required DataFrame.
            >>> admissions_train = DataFrame("admissions_train")
            >>> admissions_train
               masters   gpa     stats programming  admitted
            id
            13      no  4.00  Advanced      Novice         1
            26     yes  3.57  Advanced    Advanced         1
            5       no  3.44    Novice      Novice         0
            19     yes  1.98  Advanced    Advanced         0
            15     yes  4.00  Advanced    Advanced         1
            40     yes  3.95    Novice    Beginner         0
            7      yes  2.33    Novice      Novice         1
            22     yes  3.46    Novice    Beginner         0
            36      no  3.00  Advanced      Novice         0
            38     yes  2.65  Advanced    Beginner         1
            >>>

            # Example 1: Recode all values 'Novice', 'Advanced', and 'Beginner'
            #            in "programming" and "stats" columns.
            #            We will pass values to "label_encode" as dictionary.
            >>> rc = LabelEncoder(values={"Novice": 1, "Advanced": 2, "Beginner": 3}, columns=["stats", "programming"])

            # Execute Transform() function.
            >>> obj = valib.Transform(data=admissions_train, label_encode=rc)
            >>> obj.result
               id stats programming
            0  22     1           3
            1  36     2           1
            2  15     2           2
            3  38     2           3
            4   5     1           1
            5  17     2           2
            6  34     2           3
            7  13     2           1
            8  26     2           2
            9  19     2           2
            >>>

            # Example 2: Recode value 'Novice' as 1 which is passed as tuple to "values"
            #            argument and "label_encode" other values as 0 by passing it to "default"
            #            argument in "programming" and "stats" columns.
            >>> rc = LabelEncoder(values=("Novice", 1), columns=["stats", "programming"], default=0)

            # Execute Transform() function.
            >>> obj = valib.Transform(data=admissions_train, label_encode=rc)
            >>> obj.result
               id stats programming
            0  15     0           0
            1   7     1           1
            2  22     1           0
            3  17     0           0
            4  13     0           1
            5  38     0           0
            6  26     0           0
            7   5     1           1
            8  34     0           0
            9  40     1           0
            >>>

            # Example 3: In this example we encode values differently for multiple columns.

            # For values in "programming" column, recoding will be done as follows:
            #   Novice --> 0
            #   Advanced --> 1 and
            #   Rest of the values as --> NULL
            >>> rc_prog = LabelEncoder(values=[("Novice", 0), ("Advanced", 1)], columns="programming",
            ...                  default=None)
            >>>

            # For values in "stats" column, recoding will be done as follows:
            #   Novice --> N
            #   Advanced --> keep it as is and
            #   Beginner --> NULL
            >>> rc_stats = LabelEncoder(values={"Novice": 0, "Advanced": "same", "Beginner": None},
            ...                   columns="stats")
            >>>

            # For values in "masters" column, recoding will be done as follows:
            #   yes --> 1 and other as 0
            >>> rc_yes = LabelEncoder(values=("yes", 1), columns="masters", default=0,
            ...                 out_columns="masters_yes")
            >>>

            # For values in "masters" column, label encoding will be done as follows:
            #   no --> 1 and other as 0
            >>> rc_no = LabelEncoder(values=("no", 1), columns="masters", default=0,
            ...                out_columns="masters_no")
            >>>

            # Execute Transform() function.
            >>> obj = valib.Transform(data=admissions_train, label_encode=[rc_prog, rc_stats, rc_yes,
            ...                                                      rc_no])
            >>> obj.result
               id programming     stats masters_yes masters_no
            0  13           0  Advanced           0          1
            1  26           1  Advanced           1          0
            2   5           0         0           0          1
            3  19           1  Advanced           1          0
            4  15           1  Advanced           1          0
            5  40        None         0           1          0
            6   7           0         0           1          0
            7  22        None         0           1          0
            8  36           0  Advanced           0          1
            9  38        None  Advanced           1          0
            >>>
        """
        # Call super()
        super().__init__(columns=columns, out_columns=out_columns, datatype=datatype,
                         columns_optional=False)

        # Initialize style and value as data members.
        self.values = values
        self.default = default
        self.fillna = fillna

        # Validations
        if isinstance(self.values, tuple):
            if len(self.values) != 2:
                raise ValueError("Number of values in a tuple can only be 2.")
        elif isinstance(self.values, list):
            for tup in self.values:
                if not isinstance(tup, tuple):
                    err_ = Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE)
                    raise TypeError(err_.format("values", ['tuple or dict or list of tuples']))

                if len(tup) != 2:
                    raise ValueError("Number of values in a tuple can only be 2.")

        elif not isinstance(self.values, dict):
            err_ = Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE)
            raise TypeError(err_.format("values", ['tuple or dict or list of tuples']))

        arg_info_matrix = []
        arg_info_matrix.append(["values", self.values, False, (tuple, list, dict)])
        arg_info_matrix.append(["default", self.default, True, (bool, int, float, str)])
        arg_info_matrix.append(["fillna", self.fillna, True, FillNa])

        # Other argument validations.
        _Validators._validate_function_arguments(arg_info_matrix)
        # Note:
        #   Validations for "columns", "out_column" and "datatype" is done by super().

    def _val_sql_syntax(self):
        """
        DESCRIPTION:
            Internal function to return a string representation of LabelEncoder
            Transformation as required by SQL.

        PARAMETERS:
            None.

        RETURNS:
            String representing SQL syntax for 'recode' SQL argument.

        RAISES:
            None.

        EXAMPLE:
            self._val_sql_syntax()
        """
        # Generate syntax for "recodevalues".
        if isinstance(self.values, tuple):
            old_val = self._get_value_string_repr(self.values[0])
            new_val = self._get_value_string_repr(self.values[1])
            recode_values = "{}/{}".format(old_val, new_val)
        elif isinstance(self.values, list):
            recode_values = []
            for val in self.values:
                old_val = self._get_value_string_repr(val[0])
                new_val = self._get_value_string_repr(val[1])
                recode_values.append("{}/{}".format(old_val, new_val))
            recode_values = ", ".join(recode_values)
        else:
            recode_values = []
            for key in self.values:
                old_val = self._get_value_string_repr(key)
                new_val = self._get_value_string_repr(self.values[key])
                recode_values.append("{}/{}".format(old_val, new_val))
            recode_values = ", ".join(recode_values)

        recode_other = "NULL" if self.default is None else self.default

        ret_value = "recodevalues({}), recodeother({})".format(recode_values,
                                                               recode_other)

        # Generate and add syntax for "columns" and "datatype" SQL arguments.
        columns_fmt = self._val_transformation_fmt()
        ret_value = "{}, {}".format(ret_value, columns_fmt)

        # Generate and add syntax for "nullstyle", a SQL arguments.
        if self.fillna:
            ret_value = "{}, {}".format(ret_value, self.fillna._val_nullstyle_fmt())
        # Return the SQL syntax for "recode", a SQL argument.
        return "{" + ret_value + "}"

    def _get_value_string_repr(self, value):
        """
        DESCRIPTION:
            Internal function to return a string representation of given value if required.

        PARAMETERS:
            value:
                Required Argument.
                Specifies the value to perform conversion on.
                Types: str, bool, float, None, datetime.date

        RETURNS:
            String representation of passed argument.

        RAISES:
            None.

        Examples:
            self._get_value_string_repr(key)

        """
        if value is not None and isinstance(value, date):
            updated_val = UtilFuncs._convert_date_to_string(value)
        elif value is None:
            updated_val = "NULL"
        elif value == "":
            updated_val = "\"\""
        else:
            updated_val = value
        return updated_val


class MinMaxScalar(_Transformations):
    """ Class to represent rescale transformation technique. """

    def __init__(self, columns, lbound=0, ubound=1, out_columns=None, datatype=None,
                 fillna=None):
        """
        DESCRIPTION:
            MinMaxScalar allows rescaling that limits the upper and lower boundaries of the
            data in a continuous numeric column using a linear rescaling function based on
            maximum and minimum data values. MinMaxScalar is useful with algorithms that require
            or work better with data within a certain range. MinMaxScalar is only valid on numeric
            columns, and not columns of type date.

            The rescale transformation formulas are shown in the following examples.
            The l denotes the left bound and r denotes the right bound.
                * When both the lower and upper bounds are specified:
                    f(x,l,r) = (l+(x-min(x))(r-l))/(max(x)-min(x))
                * When only the lower bound is specified:
                    f(x,l) = x-min(x)+l
                * When only the upper bound is specified:
                    f(x,r) = x-max(x)+r
            Rescaling supports only numeric type columns.

            Note:
                Output of this function is passed to "rescale" argument of "Transform"
                function from Vantage Analytic Library.

        PARAMETERS:
            columns:
                Required Argument.
                Specifies the names of the columns to perform transformation on.
                Types: str or list of str

            lbound:
                Optional Argument.
                Specifies the lowerbound value required for rescaling the numeric data.
                If only the lower boundary is supplied, the variable is aligned to this
                value. This can be achieved by passing None to "ubound" argument.
                Default Value: 0
                Types: float, int

            ubound:
                Optional Argument.
                Specifies the upperbound value required for rescaling the numeric data.
                If only an upper boundary value is specified, the variable is aligned to
                this value. This can be achieved by passing None to "lbound" argument.
                Default Value: 1
                Types: float, int

            out_columns:
                Optional Argument.
                Specifies the names of the output columns.
                Note:
                    Number of elements in "columns" and "out_columns" must be same.
                Types: str or list of str

            datatype:
                Optional Argument.
                Specifies the name of the intended datatype of the output column.
                Intended data types for the output column can be specified using either the
                teradatasqlalchemy types or the permitted strings mentioned below:
                 -------------------------------------------------------------------
                | If intended SQL Data Type is  | Permitted Value to be passed is   |
                |-------------------------------------------------------------------|
                | bigint                        | bigint                            |
                | byteint                       | byteint                           |
                | char(n)                       | char,n                            |
                | date                          | date                              |
                | decimal(m,n)                  | decimal,m,n                       |
                | float                         | float                             |
                | integer                       | integer                           |
                | number(*)                     | number                            |
                | number(n)                     | number,n                          |
                | number(*,n)                   | number,*,n                        |
                | number(n,n)                   | number,n,n                        |
                | smallint                      | smallint                          |
                | time(p)                       | time,p                            |
                | timestamp(p)                  | timestamp,p                       |
                | varchar(n)                    | varchar,n                         |
                --------------------------------------------------------------------
                Notes:
                    1. Argument is ignored if "columns" argument is not used.
                    2. char without a size is not supported.
                    3. number(*) does not include the * in its datatype format.
                Examples:
                    1. If intended datatype for the output column is "bigint", then
                       pass string "bigint" to the argument as shown below:
                       datatype="bigint"
                    2. If intended datatype for the output column is "decimal(3,5)", then
                       pass string "decimal,3,5" to the argument as shown below:
                       datatype="decimal,3,5"
                Types: str, BIGINT, BYTEINT, CHAR, DATE, DECIMAL, FLOAT, INTEGER, NUMBER, SMALLINT, TIME,
                       TIMESTAMP, VARCHAR.

            fillna:
                Optional Argument.
                Specifies whether the null replacement/missing value treatment should
                be performed with rescaling or not. Output of 'FillNa()' can be passed to
                this argument.
                Note:
                    If the FillNa object is created with its arguments "columns",
                    "out_columns" and "datatype", then values passed in FillNa() arguments
                    are ignored. Only nullstyle information is captured from the same.
                Types: FillNa

        RETURNS:
            An instance of MinMaxScalar class.

        RAISES:
            TeradataMlException, TypeError, ValueError

        EXAMPLE:
            # Note:
            #   To run any transformation, user needs to use Transform() function from
            #   Vantage Analytic Library.
            #   To do so import valib first and set the "val_install_location".
            >>> from teradataml import configure, DataFrame, MinMaxScalar, FillNa, load_example_data, valib
            >>> configure.val_install_location = "SYSLIB"
            >>>

            # Load example data.
            >>> load_example_data("dataframe", "sales")
            >>>

            # Create the required DataFrames.
            >>> df = DataFrame("sales")
            >>> df
                          Feb    Jan    Mar    Apr    datetime
            accounts
            Alpha Co    210.0  200.0  215.0  250.0  04/01/2017
            Blue Inc     90.0   50.0   95.0  101.0  04/01/2017
            Yellow Inc   90.0    NaN    NaN    NaN  04/01/2017
            Jones LLC   200.0  150.0  140.0  180.0  04/01/2017
            Red Inc     200.0  150.0  140.0    NaN  04/01/2017
            Orange Inc  210.0    NaN    NaN  250.0  04/01/2017
            >>>

            # Example 1: Rescale values in column "Feb", using the default bounds, which is
            #            with lowerbound as 0 and upperbound as 1.
            >>> rs = MinMaxScalar(columns="Feb")

            # Execute Transform() function.
            >>> obj = valib.Transform(data=df, rescale=rs)
            >>> obj.result
                 accounts       Feb
            0    Blue Inc  0.000000
            1    Alpha Co  1.000000
            2   Jones LLC  0.916667
            3  Yellow Inc  0.000000
            4  Orange Inc  1.000000
            5     Red Inc  0.916667
            >>>

            # Example 2: Rescale values in column "Feb", using only lowerbound as -1.
            #            To use only lowerbound, one must pass None to "ubound".
            >>> rs = MinMaxScalar(columns="Feb", lbound=-1, ubound=None)

            # Execute Transform() function.
            >>> obj = valib.Transform(data=df, rescale=rs)
            >>> obj.result
                 accounts    Feb
            0   Jones LLC  109.0
            1  Yellow Inc   -1.0
            2     Red Inc  109.0
            3    Blue Inc   -1.0
            4    Alpha Co  119.0
            5  Orange Inc  119.0
            >>>

            # Example 3: Rescale values in columns "Jan" and "Apr", using only upperbound as 10.
            #            To use only upperbound, one must pass None to "lbound".
            #            We shall also combine this with missing value treatment. We shall replace
            #            missing values with "mode" null style replacement.
            >>> fn = FillNa(style="mode")
            >>> rs = MinMaxScalar(columns=["Jan", "Apr"], lbound=None, ubound=10, fillna=fn)

            # Execute Transform() function.
            >>> obj = valib.Transform(data=df, rescale=rs, key_columns="accounts")
            >>> obj.result
                 accounts    Jan    Apr
            0    Alpha Co   10.0   10.0
            1    Blue Inc -140.0 -139.0
            2  Yellow Inc  -40.0   10.0
            3   Jones LLC  -40.0  -60.0
            4     Red Inc  -40.0   10.0
            5  Orange Inc  -40.0   10.0
            >>>

            # Example 4: This example shows combining multiple ways of rescaling in one
            #            Transform() call.

            # Rescale values in column "Feb" using lowerbound as -1 and upperbound as 1.
            # Name the output column as "Feb1".
            >>> rs_1 = MinMaxScalar(columns="Feb", lbound=-1, ubound=1, out_columns="Feb1")
            >>>

            # Rescale values in column "Feb" using only upperbound as 1.
            # Name the output column as "FebU".
            >>> rs_2 = MinMaxScalar(columns="Feb", lbound=None, ubound=1, out_columns="FebU")
            >>>

            # Rescale values in column "Feb" using only lowerbound as 0 (default value).
            # Name the output column as "FebL".
            >>> rs_3 = MinMaxScalar(columns="Feb", ubound=None, out_columns="FebL")
            >>>

            # Rescale values in columns "Jan" and "Apr" using default bounds.
            # Name the output columns as "Jan1" and "Apr1".
            # Combine with Missing value treatment, with literal null replacement.
            >>> fn_1 = FillNa(style="literal", value=0)
            >>> rs_4 = MinMaxScalar(columns=["Jan", "Apr"], out_columns=["Jan1", "Apr1"], fillna=fn_1)
            >>>

            # Rescale values in columns "Jan" and "Apr" using default bounds.
            # Name the output columns as "Jan2" and "Apr2".
            # Combine with Missing value treatment, with median null replacement.
            >>> fn_2 = FillNa(style="median")
            >>> rs_5 = MinMaxScalar(columns=["Jan", "Apr"], out_columns=["Jan2", "Apr2"], fillna=fn_2)
            >>>

            # Execute Transform() function.
            >>> obj = valib.Transform(data=df, rescale=[rs_1, rs_2, rs_3, rs_4, rs_5],
            ...                       key_columns="accounts")
            >>> obj.result
                 accounts      Feb1   FebU   FebL  Jan1   Apr1      Jan2      Apr2
            0    Blue Inc -1.000000 -119.0    0.0  0.25  0.404  0.000000  0.000000
            1    Alpha Co  1.000000    1.0  120.0  1.00  1.000  1.000000  1.000000
            2   Jones LLC  0.833333   -9.0  110.0  0.75  0.720  0.666667  0.530201
            3  Yellow Inc -1.000000 -119.0    0.0  0.00  0.000  0.666667  0.765101
            4  Orange Inc  1.000000    1.0  120.0  0.00  1.000  0.666667  1.000000
            5     Red Inc  0.833333   -9.0  110.0  0.75  0.000  0.666667  0.765101
            >>>
        """
        # Call super()
        super().__init__(columns=columns, out_columns=out_columns, datatype=datatype,
                         columns_optional=False)

        # Initialize style and value as data members.
        self.lbound = lbound
        self.ubound = ubound
        self.fillna = fillna

        # Validations
        arg_info_matrix = []
        arg_info_matrix.append(["lbound", self.lbound, True, (float, int)])
        arg_info_matrix.append(["ubound", self.ubound, True, (float, int)])
        arg_info_matrix.append(["fillna", self.fillna, True, FillNa])
        # Note:
        #   Validations for "columns", "out_columns" and "datatype" is done by super().
        # Other argument validations.
        _Validators._validate_function_arguments(arg_info_matrix)

        if self.lbound is None and self.ubound is None:
            raise TeradataMlException(
                Messages.get_message(MessageCodes.SPECIFY_AT_LEAST_ONE_ARG,
                                     "lbound", "ubound"),
                MessageCodes.SPECIFY_AT_LEAST_ONE_ARG)

    def _val_sql_syntax(self):
        """
        DESCRIPTION:
            Internal function to return a string representation of rescale
            Transformation as required by SQL.

        PARAMETERS:
            None.

        RETURNS:
            String representing SQL syntax for 'rescale' SQL argument.

        RAISES:
            None.

        EXAMPLE:
            self._val_sql_syntax()
        """
        # Generate syntax for "rescale" SQL argument.
        rescale_values = []
        if self.lbound is not None:
            rescale_values.append("lowerbound/{}".format(self.lbound))

        if self.ubound is not None:
            rescale_values.append("upperbound/{}".format(self.ubound))

        ret_value = "rescalebounds({})".format(", ".join(rescale_values))

        # Generate and add syntax for "columns" and "datatype" SQL arguments.
        columns_fmt = self._val_transformation_fmt()
        ret_value = "{}, {}".format(ret_value, columns_fmt)

        # Generate and add syntax for "nullstyle", a SQL arguments.
        if self.fillna:
            ret_value = "{}, {}".format(ret_value, self.fillna._val_nullstyle_fmt())

        return "{" + ret_value + "}"


class Retain(_Transformations):
    """
    Class to represent Retain transformation technique to retain or copy columns
    from input to output.
    """

    def __init__(self, columns, out_columns=None, datatype=None):
        """
        DESCRIPTION:
            Retain option allows you to copy one or more columns into the final
            analytic data set. By default, the result column name is the same as
            the input column name, but this can be changed. If a specific type is
            specified, it results in casting the retained column.
            The Retain transformation is supported for all valid data types.

            Note:
                Output of this function is passed to "retain" argument of "Transform"
                function from Vantage Analytic Library.

        PARAMETERS:
            columns:
                Required Argument.
                Specifies the names of the columns to retain.
                Types: str or list of str

            out_columns:
                Optional Argument.
                Specifies the names of the output columns.
                Note:
                    Number of elements in "columns" and "out_columns" must be same.
                Types: str or list of str

            datatype:
                Optional Argument.
                Specifies the name of the intended datatype of the output column.
                Intended data types for the output column can be specified using either the
                teradatasqlalchemy types or the permitted strings mentioned below:
                 -------------------------------------------------------------------
                | If intended SQL Data Type is  | Permitted Value to be passed is   |
                |-------------------------------------------------------------------|
                | bigint                        | bigint                            |
                | byteint                       | byteint                           |
                | char(n)                       | char,n                            |
                | date                          | date                              |
                | decimal(m,n)                  | decimal,m,n                       |
                | float                         | float                             |
                | integer                       | integer                           |
                | number(*)                     | number                            |
                | number(n)                     | number,n                          |
                | number(*,n)                   | number,*,n                        |
                | number(n,n)                   | number,n,n                        |
                | smallint                      | smallint                          |
                | time(p)                       | time,p                            |
                | timestamp(p)                  | timestamp,p                       |
                | varchar(n)                    | varchar,n                         |
                --------------------------------------------------------------------
                Notes:
                    1. Argument is ignored if "columns" argument is not used.
                    2. char without a size is not supported.
                    3. number(*) does not include the * in its datatype format.
                Examples:
                    1. If intended datatype for the output column is "bigint", then
                       pass string "bigint" to the argument as shown below:
                       datatype="bigint"
                    2. If intended datatype for the output column is "decimal(3,5)", then
                       pass string "decimal,3,5" to the argument as shown below:
                       datatype="decimal,3,5"
                Types: str, BIGINT, BYTEINT, CHAR, DATE, DECIMAL, FLOAT, INTEGER, NUMBER, SMALLINT, TIME,
                       TIMESTAMP, VARCHAR.

        RETURNS:
            An instance of Retain class.

        RAISES:
            TeradataMlException, TypeError, ValueError

        EXAMPLE:
            # Note:
            #   To run any transformation, user needs to use Transform() function from
            #   Vantage Analytic Library.
            #   To do so import valib first and set the "val_install_location".
            >>> from teradataml import configure, DataFrame, load_example_data, valib, Retain
            >>> configure.val_install_location = "SYSLIB"
            >>>

            # Load example data.
            >>> load_example_data("dataframe", "sales")
            >>>

            # Create the required DataFrames.
            >>> sales = DataFrame("sales")
            >>> sales
                          Feb    Jan    Mar    Apr    datetime
            accounts
            Alpha Co    210.0  200.0  215.0  250.0  04/01/2017
            Blue Inc     90.0   50.0   95.0  101.0  04/01/2017
            Yellow Inc   90.0    NaN    NaN    NaN  04/01/2017
            Jones LLC   200.0  150.0  140.0  180.0  04/01/2017
            Red Inc     200.0  150.0  140.0    NaN  04/01/2017
            Orange Inc  210.0    NaN    NaN  250.0  04/01/2017
            >>>

            # Example: Shows retaining some column unchanged and some with name or datatype
            #          change.

            # Retain columns "accounts" and "Feb" as is.
            >>> rt_1 = Retain(columns=["accounts", "Feb"])
            >>>

            # Retain column "Jan" with name as "january".
            >>> rt_2 = Retain(columns="Jan", out_columns="january")
            >>>

            # Retain column "Mar" and "Apr" with name as "march" and "april" with
            # datatype changed to 'bigint'.
            >>> rt_3 = Retain(columns=["Mar", "Apr"], out_columns=["march", "april"],
            ...               datatype="bigint")
            >>>


            # Execute Transform() function.
            >>> obj = valib.Transform(data=sales, retain=[rt_1, rt_2, rt_3])
            >>> obj.result
                 accounts   accounts1    Feb  january  march  april
            0    Alpha Co    Alpha Co  210.0    200.0  215.0  250.0
            1    Blue Inc    Blue Inc   90.0     50.0   95.0  101.0
            2  Yellow Inc  Yellow Inc   90.0      NaN    NaN    NaN
            3   Jones LLC   Jones LLC  200.0    150.0  140.0  180.0
            4     Red Inc     Red Inc  200.0    150.0  140.0    NaN
            5  Orange Inc  Orange Inc  210.0      NaN    NaN  250.0
            >>>
        """
        # Call super()
        super().__init__(columns=columns, out_columns=out_columns, datatype=datatype,
                         columns_optional=False)

    def _val_sql_syntax(self):
        """
        DESCRIPTION:
            Internal function to return a string representation of retain
            Transformation as required by SQL.

        PARAMETERS:
            None.

        RETURNS:
            String representing SQL syntax for 'retain' SQL argument.

        RAISES:
            None.

        EXAMPLE:
            self._val_sql_syntax()
        """
        # Generate and return syntax for "columns" and "datatype" SQL arguments.
        return "{" + self._val_transformation_fmt() + "}"


class Sigmoid(_Transformations):
    """
    Class to represent sigmoid transformation technique for rescaling of continuous
    numeric data.
    """

    def __init__(self, columns, style="logit", out_columns=None, datatype=None,
                 fillna=None):
        """
        DESCRIPTION:
            Sigmoid transformation allows rescaling of continuous numeric data in a more
            sophisticated way than the Rescaling transformation function. In a Sigmoid
            transformation, a numeric column is transformed using a type of sigmoid or
            s-shaped function.

            These non-linear transformations are more useful in data mining than a linear
            Rescaling transformation. The Sigmoid transformation is supported for numeric
            columns only.

            For absolute values of x greater than or equal to  36, the value of the
            sigmoid function is effectively 1 for positive arguments or 0 for negative
            arguments, within about 15 digits of significance.

            Note:
                Output of this function is passed to "sigmoid" argument of "Transform"
                function from Vantage Analytic Library.

        PARAMETERS:
            columns:
                Required Argument.
                Specifies the names of the columns to scale.
                Types: str or list of str

            style:
                Optional Argument.
                Specifies the style of sigmoid function to use.
                Permitted Values:
                    * "logit":
                        The logit function produces a continuously increasing value
                        between 0 and 1.
                    * "modifiedlogit":
                        The modified logit function is twice the logit minus 1 and
                        produces a value between -1 and 1.
                    * "tanh":
                        The hyperbolic tangent function also produces a value between
                        -1 and 1.
                Default Value: 'logit'
                Types: str

            out_columns:
                Optional Argument.
                Specifies the names of the output columns.
                Note:
                    Number of elements in "columns" and "out_columns" must be same.
                Types: str or list of str

            datatype:
                Optional Argument.
                Specifies the name of the intended datatype of the output column.
                Intended data types for the output column can be specified using either the
                teradatasqlalchemy types or the permitted strings mentioned below:
                 -------------------------------------------------------------------
                | If intended SQL Data Type is  | Permitted Value to be passed is   |
                |-------------------------------------------------------------------|
                | bigint                        | bigint                            |
                | byteint                       | byteint                           |
                | char(n)                       | char,n                            |
                | date                          | date                              |
                | decimal(m,n)                  | decimal,m,n                       |
                | float                         | float                             |
                | integer                       | integer                           |
                | number(*)                     | number                            |
                | number(n)                     | number,n                          |
                | number(*,n)                   | number,*,n                        |
                | number(n,n)                   | number,n,n                        |
                | smallint                      | smallint                          |
                | time(p)                       | time,p                            |
                | timestamp(p)                  | timestamp,p                       |
                | varchar(n)                    | varchar,n                         |
                --------------------------------------------------------------------
                Notes:
                    1. Argument is ignored if "columns" argument is not used.
                    2. char without a size is not supported.
                    3. number(*) does not include the * in its datatype format.
                Examples:
                    1. If intended datatype for the output column is "bigint", then
                       pass string "bigint" to the argument as shown below:
                       datatype="bigint"
                    2. If intended datatype for the output column is "decimal(3,5)", then
                       pass string "decimal,3,5" to the argument as shown below:
                       datatype="decimal,3,5"
                Types: str, BIGINT, BYTEINT, CHAR, DATE, DECIMAL, FLOAT, INTEGER, NUMBER, SMALLINT, TIME,
                       TIMESTAMP, VARCHAR.

            fillna:
                Optional Argument.
                Specifies whether the null replacement/missing value treatment should
                be performed with sigmoid transformation or not. Output of FillNa() can be
                passed to this argument.
                Note:
                    If the FillNa object is created with its arguments "columns",
                    "out_columns" and "datatype", then values passed in FillNa() arguments
                    are ignored. Only nullstyle information is captured from the same.
                Types: FillNa

        RETURNS:
            An instance of Sigmoid class.

        RAISES:
            TeradataMlException, TypeError, ValueError

        EXAMPLE:
            # Note:
            #   To run any transformation, user needs to use Transform() function from
            #   Vantage Analytic Library.
            #   To do so import valib first and set the "val_install_location".
            >>> from teradataml import configure, DataFrame, FillNa, Sigmoid, load_example_data, valib
            >>> configure.val_install_location = "SYSLIB"
            >>>

            # Load example data.
            >>> load_example_data("dataframe", "sales")
            >>>

            # Create the required teradataml DataFrame.
            >>> sales = DataFrame("sales")
            >>> sales
                          Feb    Jan    Mar    Apr    datetime
            accounts
            Blue Inc     90.0   50.0   95.0  101.0  04/01/2017
            Orange Inc  210.0    NaN    NaN  250.0  04/01/2017
            Red Inc     200.0  150.0  140.0    NaN  04/01/2017
            Yellow Inc   90.0    NaN    NaN    NaN  04/01/2017
            Jones LLC   200.0  150.0  140.0  180.0  04/01/2017
            Alpha Co    210.0  200.0  215.0  250.0  04/01/2017
            >>>

            # Example 1: Scale values in columns "Jan" and "Mar" using sigmoid function "tanh".
            #            Combine the scaling with null replacement.
            >>> fn = FillNa(style="literal", value=0)
            >>> sig = Sigmoid(style="tanh", columns=["Jan", "Mar"], fillna=fn)

            # Execute Transform() function.
            >>> obj = valib.Transform(data=sales, sigmoid=sig, key_columns="accounts")
            >>> obj.result
                 accounts  Jan  Mar
            0    Alpha Co  1.0  1.0
            1     Red Inc  1.0  1.0
            2  Orange Inc  0.0  0.0
            3   Jones LLC  1.0  1.0
            4  Yellow Inc  0.0  0.0
            5    Blue Inc  1.0  1.0
            >>>


            # Example 2: Rescaling with Sigmoid is carried out with multiple styles.
            >>> load_example_data("dataframe", "iris_test")
            >>> df = DataFrame("iris_test")
            >>> df
                 sepal_length  sepal_width  petal_length  petal_width  species
            id
            5             5.0          3.6           1.4          0.2        1
            60            5.2          2.7           3.9          1.4        2
            15            5.8          4.0           1.2          0.2        1
            30            4.7          3.2           1.6          0.2        1
            40            5.1          3.4           1.5          0.2        1
            80            5.7          2.6           3.5          1.0        2
            120           6.0          2.2           5.0          1.5        3
            70            5.6          2.5           3.9          1.1        2
            20            5.1          3.8           1.5          0.3        1
            65            5.6          2.9           3.6          1.3        2
            >>>

            # Rescale values in columns "sepal_length", "sepal_width", "petal_length"
            # and "petal_width" with 'logit' (default) sigmoid function.
            >>> sig_1 = Sigmoid(columns=["sepal_length", "sepal_width", "petal_length",
            ...                          "petal_width"],
            ...                 out_columns=["sl", "sw", "pl", "pw"])
            >>>

            # Rescale values in columns "sepal_length", "sepal_width", "petal_length"
            # and "petal_width" with 'tanh' sigmoid function.
            >>> sig_2 = Sigmoid(style="tanh",
            ...                 columns=["sepal_length", "sepal_width", "petal_length",
            ...                          "petal_width"],
            ...                 out_columns=["sl_t", "sw_t", "pl_t", "pw_t"])
            >>>

            # Rescale values in columns "sepal_length" and "sepal_width" with 'modifiedlogit'
            # sigmoid function.
            # Combine it with null replacement using 'median' style.
            >>> fn = FillNa(style="median")
            >>> sig_3 = Sigmoid(style="modifiedlogit", columns=["sepal_length", "sepal_width"],
            ...                 out_columns=["sl_ml", "sw_ml"], fillna=fn)
            >>>

            # Execute Transform() function.
            >>> obj = valib.Transform(data=df, sigmoid=[sig_1, sig_2, sig_3],
            ...                       key_columns="id")
            >>> obj.result
                id        sl        sw        pl        pw      sl_t      sw_t      pl_t      pw_t     sl_ml     sw_ml
            0    5  0.993307  0.973403  0.802184  0.549834  0.999909  0.998508  0.885352  0.197375  0.986614  0.946806
            1   60  0.994514  0.937027  0.980160  0.802184  0.999939  0.991007  0.999181  0.885352  0.989027  0.874053
            2   15  0.996982  0.982014  0.768525  0.549834  0.999982  0.999329  0.833655  0.197375  0.993963  0.964028
            3   30  0.990987  0.960834  0.832018  0.549834  0.999835  0.996682  0.921669  0.197375  0.981973  0.921669
            4   40  0.993940  0.967705  0.817574  0.549834  0.999926  0.997775  0.905148  0.197375  0.987880  0.935409
            5   80  0.996665  0.930862  0.970688  0.731059  0.999978  0.989027  0.998178  0.761594  0.993330  0.861723
            6  120  0.997527  0.900250  0.993307  0.817574  0.999988  0.975743  0.999909  0.905148  0.995055  0.800499
            7   70  0.996316  0.924142  0.980160  0.750260  0.999973  0.986614  0.999181  0.800499  0.992632  0.848284
            8   20  0.993940  0.978119  0.817574  0.574443  0.999926  0.999000  0.905148  0.291313  0.987880  0.956237
            9   65  0.996316  0.947846  0.973403  0.785835  0.999973  0.993963  0.998508  0.861723  0.992632  0.895693
            >>>
        """
        # Call super()
        super().__init__(columns=columns, out_columns=out_columns, datatype=datatype,
                         columns_optional=False)
        # Initialize style and value as data members.
        self.style = style
        self.fillna = fillna

        # Validations
        arg_info_matrix = []
        permitted_styles = ["LOGIT", "MODIFIEDLOGIT", "TANH"]
        arg_info_matrix.append(["style", self.style, True, str, True, permitted_styles])
        arg_info_matrix.append(["fillna", self.fillna, True, FillNa])
        # Note:
        #   Validations for "columns", "out_columns" and "datatype" is done by super().
        # Other argument validations.
        _Validators._validate_function_arguments(arg_info_matrix)

    def _val_sql_syntax(self):
        """
        DESCRIPTION:
            Internal function to return a string representation of sigmoid
            Transformation as required by SQL.

        PARAMETERS:
            None.

        RETURNS:
            String representing SQL syntax for 'sigmoidstyle' SQL argument.

        RAISES:
            None.

        EXAMPLE:
            self._val_sql_syntax()
        """
        # Generate and add syntax for "sigmoidstyle" SQL argument.
        ret_value = "sigmoidstyle({})".format(self.style.lower())

        # Generate and add syntax for "columns" and "datatype" SQL arguments.
        columns_fmt = self._val_transformation_fmt()
        ret_value = "{}, {}".format(ret_value, columns_fmt)

        if self.fillna:
            ret_value = "{}, {}".format(ret_value, self.fillna._val_nullstyle_fmt())

        return "{" + ret_value + "}"


class ZScore(_Transformations):
    """ Class to represent Z-Score transformation technique for rescaling. """

    def __init__(self, columns, out_columns=None, datatype=None, fillna=None):
        """
        DESCRIPTION:
            ZScore will allows rescaling of continuous numeric data in a more
            sophisticated way than a Rescaling transformation. In a Z-Score
            transformation, a numeric column is transformed into its Z-score based
            on the mean value and standard deviation of the data in the column.
            Z-Score transforms each column value into the number of standard
            deviations from the mean value of the column. This non-linear transformation
            is useful in data mining rather than in a linear Rescaling transformation.
            The Z-Score transformation supports both numeric and date type input data.

            Note:
                Output of this function is passed to "zscore" argument of "Transform"
                function from Vantage Analytic Library.

        PARAMETERS:
            columns:
                Required Argument.
                Specifies the name(s) of the column(s) to perform transformation on.
                Types: str or list of str

            out_columns:
                Optional Argument.
                Specifies the names of the output columns.
                Note:
                    Number of elements in "columns" and "out_columns" must be same.
                Types: str or list of str

            datatype:
                Optional Argument.
                Specifies the name of the intended datatype of the output column.
                Intended data types for the output column can be specified using either the
                teradatasqlalchemy types or the permitted strings mentioned below:
                 -------------------------------------------------------------------
                | If intended SQL Data Type is  | Permitted Value to be passed is   |
                |-------------------------------------------------------------------|
                | bigint                        | bigint                            |
                | byteint                       | byteint                           |
                | char(n)                       | char,n                            |
                | date                          | date                              |
                | decimal(m,n)                  | decimal,m,n                       |
                | float                         | float                             |
                | integer                       | integer                           |
                | number(*)                     | number                            |
                | number(n)                     | number,n                          |
                | number(*,n)                   | number,*,n                        |
                | number(n,n)                   | number,n,n                        |
                | smallint                      | smallint                          |
                | time(p)                       | time,p                            |
                | timestamp(p)                  | timestamp,p                       |
                | varchar(n)                    | varchar,n                         |
                --------------------------------------------------------------------
                Notes:
                    1. Argument is ignored if "columns" argument is not used.
                    2. char without a size is not supported.
                    3. number(*) does not include the * in its datatype format.
                Examples:
                    1. If intended datatype for the output column is "bigint", then
                       pass string "bigint" to the argument as shown below:
                       datatype="bigint"
                    2. If intended datatype for the output column is "decimal(3,5)", then
                       pass string "decimal,3,5" to the argument as shown below:
                       datatype="decimal,3,5"
                Types: str, BIGINT, BYTEINT, CHAR, DATE, DECIMAL, FLOAT, INTEGER, NUMBER, SMALLINT, TIME,
                       TIMESTAMP, VARCHAR.

            fillna:
                Optional Argument.
                Specifies whether the null replacement/missing value treatment should
                be performed with Z-Score transformation or not. Output of 'FillNa()'
                can be passed to this argument.
                Note:
                    If the FillNa object is created with its arguments "columns",
                    "out_columns" and "datatype", then values passed in FillNa() arguments
                    are ignored. Only nullstyle information is captured from the same.
                Types: FillNa

        RETURNS:
            An instance of ZScore class.

        RAISES:
            TeradataMlException, TypeError, ValueError

        EXAMPLE:
            # Note:
            #   To run any transformation, user needs to use Transform() function from
            #   Vantage Analytic Library.
            #   To do so import valib first and set the "val_install_location".
            >>> from teradataml import configure, DataFrame, FillNa, load_example_data, valib, ZScore
            >>> configure.val_install_location = "SYSLIB"
            >>>

            # Load example data.
            >>> load_example_data("dataframe", "sales")
            >>>

            # Create the required DataFrames.
            >>> sales = DataFrame("sales")
            >>> sales
                          Feb    Jan    Mar    Apr    datetime
            accounts
            Alpha Co    210.0  200.0  215.0  250.0  04/01/2017
            Blue Inc     90.0   50.0   95.0  101.0  04/01/2017
            Yellow Inc   90.0    NaN    NaN    NaN  04/01/2017
            Jones LLC   200.0  150.0  140.0  180.0  04/01/2017
            Red Inc     200.0  150.0  140.0    NaN  04/01/2017
            Orange Inc  210.0    NaN    NaN  250.0  04/01/2017
            >>>

            # Example 1: Rescaling with ZScore is carried out on "Feb" column.
            >>> zs = ZScore(columns="Feb")

            # Execute Transform() function.
            >>> obj = valib.Transform(data=sales, zscore=zs)
            >>> obj.result
                 accounts       Feb
            0    Blue Inc -1.410220
            1    Alpha Co  0.797081
            2   Jones LLC  0.613139
            3  Yellow Inc -1.410220
            4  Orange Inc  0.797081
            5     Red Inc  0.613139
            >>>


            # Example 2: Rescaling with ZScore is carried out with multiple columns "Jan"
            #            and "Apr" with null replacement using "mode" style.
            >>> fn = FillNa(style="mode")
            >>> zs = ZScore(columns=["Jan", "Apr"], out_columns=["january", "april"], fillna=fn)

            # Execute Transform() function.
            >>> obj = valib.Transform(data=sales, zscore=zs, key_columns="accounts")
            >>> obj.result
                 accounts   january     april
            0    Blue Inc -2.042649 -1.993546
            1    Alpha Co  1.299867  0.646795
            2   Jones LLC  0.185695 -0.593634
            3  Yellow Inc  0.185695  0.646795
            4  Orange Inc  0.185695  0.646795
            5     Red Inc  0.185695  0.646795
            >>>
        """
        # Call super()
        super().__init__(columns=columns, out_columns=out_columns, datatype=datatype,
                         columns_optional=False)
        self.fillna = fillna

        # Validations
        arg_info_matrix = []
        arg_info_matrix.append(["fillna", self.fillna, True, FillNa])
        # Note:
        #   Validations for "columns", "out_columns" and "datatype" is done by super().
        # Other argument validations.
        _Validators._validate_function_arguments(arg_info_matrix)

    def _val_sql_syntax(self):
        """
        DESCRIPTION:
            Internal function to return a string representation of zscore
            Transformation as required by SQL.

        PARAMETERS:
            None.

        RETURNS:
            String representing SQL syntax for 'zscore' SQL argument.

        RAISES:
            None.

        EXAMPLE:
            self._val_sql_syntax()
        """
        # Generate and add syntax for "columns" and "datatype" SQL arguments.
        ret_value = self._val_transformation_fmt()

        # Generate and add syntax for "nullstyle", a SQL arguments.
        if self.fillna:
            ret_value = "{}, {}".format(ret_value, self.fillna._val_nullstyle_fmt())

        return "{" + ret_value + "}"