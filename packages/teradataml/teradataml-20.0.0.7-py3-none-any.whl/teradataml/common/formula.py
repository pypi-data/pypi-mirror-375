"""
Unpublished work.
Copyright (c) 2018 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner: mounika.kotha@teradata.com
Secondary Owner:
    
This file implements processing of formula variables that will be used 
in Teradata Vantage Analytical function wrappers.
"""

import inspect
import re
from teradataml.common.exceptions import TeradataMlException
from teradataml.common.messagecodes import MessageCodes
from teradataml.common.messages import Messages
from teradataml.utils.validators import _Validators

def as_categorical(columns):
    """
    Function to explicitly specify columns to be treated as categorical type. Sometimes, user may need to
    treat column(s) as categorical column, when used in analytic function. User will be able to do so via
    formula and this function. User can classify Numeric columns as categorical columns.

    PARAMETERS:
        columns:
            Required Argument.
            Specifies the name or names of column to be treated as categorical in formula for analytic function.

    RAISES:
        TypeError - If incorrect type of value is passed.
        ValueError - If empty string is passed.

    RETURNS:
        A string

    EXAMPLES:
        # Let's say a DataFrame has numeric columns 'stories' and 'garagepl'. To treat these columns as categorical
        # in analytic function execution, one can use 'as_categorical()' function and combine the output of the same
        # with formula string to be passed to formula argument of analytic function.
        formula = "homestyle ~ lotsize + price + fullbase + driveway + prefarea \
                    + {}".format(as_categorical(["stories", "garagepl"]))


    """
    # Validate argument types
    _Validators._validate_function_arguments([["columns", columns, False, (str, list), True]])

    if isinstance(columns, str):
        columns = [columns]

    return " + ".join(["CATEGORICAL({})".format(col) for col in columns])

def __as_numerical(columns):
    """
    Function to explicitly specify columns to be treated as numeric type in a formula.
    Currently, this is internal function, and is not exposed. It'll be exposed as and when required.
    As of now, just passing varchar column directly to Numerical Columns argument fails with error.

    Provisions for Numeric columns processing are already made as part of this Formula class.
    :param columns:
    :return:
    """
    # Validate argument types
    _Validators._validate_function_arguments([["columns", columns, False, (str, list), True]])

    if isinstance(columns, str):
        columns = [columns]

    return " + ".join(["NUMERICAL({})".format(col) for col in columns])

class Formula(object):
    """
    This class contains all the variables and datatypes of the formula input provided
    by the user.
    """
    def __init__(self, metaexpr, formula, arg_name, response_column=None,
                 all_columns=None, categorical_columns=None, numerical_columns=None):
        """
        Constructor for the Formula class.

        PARAMETERS:
            metaexpr - Parent meta data (_MetaExpression object).
            formula - Specifies formula string passed by the user.
            arg_name - Specifies the argument name of the argument used to specify for formula.

        RAISES:
            TypeError - In case of incorrect type of value passed to any argument.
            ValueError - Invalid value passed to arguments.
            TeradataMlException - If formula is in incorrect format.

        EXAMPLE:
            formula = "admitted ~ masters + gpa + stats + programming"
            formula_object = Formula(data._metaexpr, formula, "formula")

        RETURNS:
            A formula object.
        """
        if inspect.stack()[1][3] == '_from_formula_attr':
            self.__formula = formula
            self._all_columns = all_columns
            self._response_column = response_column
            self._numeric_columns = numerical_columns
            self._categorical_columns = categorical_columns
        else:
            awu_matrix = []
            awu_matrix.append([arg_name, formula, False, (str), True])
            awu_matrix.append(["arg_name", arg_name, False, (str), True])

            # Validate argument types
            _Validators._validate_function_arguments(awu_matrix)

            # Validations for formula.
            formula_expression = r"^(\s*\w*\s*[~]\s*)((([(\w+)|(\w+\(\w+\))|(\w+\(\.\))]\s*[+]?\s*)*\s*[(\w+)|(\w+\(\w+\))|(\w+\(\.\))]\s*)|(\.))$"
            if bool(re.match(formula_expression,formula)) is False:
                raise TeradataMlException(Messages.get_message(MessageCodes.FORMULA_INVALID_FORMAT, arg_name),
                                MessageCodes.FORMULA_INVALID_FORMAT)

            # Validate that dependent variables are present.
            dependent_var, independent_vars = re.split('~', formula)
            if ((len(dependent_var.strip()) == 0) or (len(re.sub(' ', '', dependent_var)) == 0)):
                raise TeradataMlException(Messages.get_message(MessageCodes.FORMULA_MISSING_DEPENDENT_VARIABLE, arg_name),
                                          MessageCodes.FORMULA_MISSING_DEPENDENT_VARIABLE)

            # Variables holding formula information.
            self.__dependent_vars = dependent_var.strip()
            self.__independent_var_str = independent_vars
            self.__independent_vars = []
            self.__metaexpr = metaexpr
            self.__all_col_notation_used = False
            self._formula_column_type_map = {}
            self._all_columns = None
            self._categorical_columns = None
            self._numeric_columns = None
            self._response_column = self.__dependent_vars
            self.__formula = formula

            # Variables used for processing explicit variables.
            # Variables that will be classified based on their types.
            self._default_independent_variables = []
            # Variables that will be classified as 'Categorical' regardless of their types.
            self._explicit_independent_categorical = []
            # Variables that will be classified as 'Numerical' regardless of their types.
            self._explicit_independent_numerical = []

            # Patterns to identify the explicit classificatioon for some columns.
            self.__EXPLICIT_CATEGORICAL_PATTERN = r"CATEGORICAL\((.+)\)"
            self.__EXPLICIT_NUMERICAL_PATTERN = r"NUMERICAL\((.+)\)"
            self.__EXPLICIT_CATEGORICAL_PATTERN_ALL_COL = r"CATEGORICAL\(\.\)"
            self.__EXPLICIT_NUMERICAL_PATTERN_ALL_COL = r"NUMERICAL\(\.\)"

            # Process independent variables.
            self.__process_independent_vars()

            # Validate columns used as independent and dependent variables exist in dataframe.
            _Validators._validate_column_exists_in_dataframe(self.__independent_vars, self.__metaexpr)
            _Validators._validate_column_exists_in_dataframe(self.__dependent_vars, self.__metaexpr)

            # Set the column type for all variables in formula.
            for column in self._get_independent_vars():
                self.__set_column_type(column)
            self.__set_column_type(self.__dependent_vars)

    @classmethod
    def _from_formula_attr(cls, formula, response_column=None, all_columns=None,
                           categorical_columns=None, numerical_columns=None):

        """
        Classmethod which will be used by Model Cataloging, to instantiate this Formula class.
        """
        return cls(metaexpr=None, formula=formula, arg_name="formula", response_column=response_column,
                   all_columns=all_columns, categorical_columns=categorical_columns,
                   numerical_columns=numerical_columns)

    def __set_column_type(self, column):
        """
        Internal function, to map column name to column type.

        PARAMETER:
            column:
                Required Argument.
                Name of the column to be added to the mapper.

        RAISES:
            None.

        RETURNS:
            None.

        EXAMPLES:
             self.__set_column_type(self.__dependent_vars)
        """
        for c in self.__metaexpr.c:
            if column == c.name:
                self._formula_column_type_map[column] = type(c.type)

    def __classify_as_categorical(self, col, all=False):
        """
        Method to check whether the column provided in the string must be classified as categorical or not.

        PARAMETERS:
            col:
                Required Argument.
                Specifies column string from the formula.
                Types: str

            all:
                Optional Argument.
                Specifies boolean flag asking to validate for all columns to be classified as categorical or not.
                Types: bool

        RETURNS:
             True, if columns is to be classified as Categorical

        RAISES:
            TeradataMlExacpetion - If multiple '.' are used in formula.

        EXAMPLES:
            self.__classify_as_categorical(col)
        """
        if all:
            pattern_cat = re.compile(self.__EXPLICIT_CATEGORICAL_PATTERN_ALL_COL)
            match_cat = pattern_cat.match(col)
            if match_cat is not None:
                self._explicit_independent_categorical = list(set([c.name for c in self.__metaexpr.c]) -
                                                             {self._get_dependent_vars()})
                return True

        else:
            pattern_cat = re.compile(self.__EXPLICIT_CATEGORICAL_PATTERN)
            match_cat = pattern_cat.match(col)
            if match_cat is not None:
                if match_cat.group(1).strip() == ".":
                    if self.__all_col_notation_used:
                        raise TeradataMlException(Messages.get_message(MessageCodes.FORMULA_INVALID_FORMAT,
                                                                       "mulitple time all column dot (.) notation is used"),
                                                  MessageCodes.FORMULA_INVALID_FORMAT)
                    else:
                        self.__all_col_notation_used = True
                self._explicit_independent_categorical.append(match_cat.group(1).strip())
                return True

        return False

    def __classify_as_numerical(self, col, all=False):
        """
        Method to check whether the column provided in the string must be classified as numerical or not.

        PARAMETERS:
            col:
                Required Argument.
                Specifies column string from the formula.
                Types: str

            all:
                Optional Argument.
                Specifies boolean flag asking to validate for all columns to be classified as numerical or not.
                Types: bool

        RETURNS:
             True, if columns is to be classified as Categorical

        RAISES:
            TeradataMlExacpetion - If multiple '.' are used in formula.

        EXAMPLES:
            self.__classify_as_numerical(col)
        """
        if all:
            pattern_cat = re.compile(self.__EXPLICIT_NUMERICAL_PATTERN_ALL_COL)
            match_cat = pattern_cat.match(col)
            if match_cat is not None:
                self._explicit_independent_numerical = list(set([c.name for c in self.__metaexpr.c]) -
                                                           {self._get_dependent_vars()})
                return True

        else:
            pattern_cat = re.compile(self.__EXPLICIT_NUMERICAL_PATTERN)
            match_cat = pattern_cat.match(col)
            if match_cat is not None:
                if match_cat.group(1).strip() == ".":
                    if self.__all_col_notation_used:
                        raise TeradataMlException(Messages.get_message(MessageCodes.FORMULA_INVALID_FORMAT,
                                                                       "mulitple time all column dot (.) notation is used"),
                                                  MessageCodes.FORMULA_INVALID_FORMAT)
                    else:
                        self.__all_col_notation_used = True
                self._explicit_independent_numerical.append(match_cat.group(1).strip())
                return True

        return False

    def __process_independent_vars(self):
        """
        Internal method to process variables on the RHS of the formula.

        PARAMETERS:
            None.

        RAISES:
            None.

        RETURNS:
            True on success of processing independent varaibles.

        EXAMPLES:
            self.__process_independent_vars()
        """
        # If independent variable is ".", then use the same.
        if self.__independent_var_str.strip() == ".":
            self.__independent_vars = list(set([c.name for c in self.__metaexpr.c]) - {self.__dependent_vars})
            self._default_independent_variables = self.__independent_vars
            return True

        # If all independent variables are needed to be classified as categorical or numerical,
        # then update the lists accordingly.
        if self.__classify_as_categorical(self.__independent_var_str.strip(), True):
            # If dot '.' notation is used in as_categorical, that means,
            # user wants to classify all columns as categorical.
            self.__independent_vars = list(set([c.name for c in self.__metaexpr.c]) - {self.__dependent_vars})
            self._explicit_independent_categorical = self._get_independent_vars()
            return True

        if self.__classify_as_numerical(self.__independent_var_str.strip(), True):
            # If dot '.' notation is used in as_numerical, that means,
            # user wants to classify all columns as numerical.
            self.__independent_vars = list(set([c.name for c in self.__metaexpr.c]) - {self.__dependent_vars})
            self._explicit_independent_numerical = self._get_independent_vars()
            return True

        # Check whether formula contains any column that must classified as categorical/numerical column.
        for col in self._var_split(self.__independent_var_str):
            # First let's check if any column, must be categorized as categorical/numerical column or not.
            # If not add it directly to independent_vars list.
            if not self.__classify_as_categorical(col) and not self.__classify_as_numerical(col):
                self._default_independent_variables.append(col)

        if len(self._explicit_independent_categorical) > 0:
            # Process columns from 'explicit_independent_categorical' for explicit classification as Categorical
            self.__process_explicit_independent_variables()

        if len(self._explicit_independent_numerical) > 0:
            # Process columns from 'explicit_independent_numerical' for explicit classification as Numerical
            self.__process_explicit_independent_variables(True)

        self.__independent_vars = self._default_independent_variables + self._explicit_independent_categorical \
                                  + self._explicit_independent_numerical

        return True

    def __process_explicit_independent_variables(self, numerical=False):
        """
        Internal method to process independent variables, which have been asked by user to be
        explicitly classified as either categorical or numerical.

        PARAMETERS:
            numerical:
                Optional Argument.
                Specifies a flag that allows us to process for numerical variables, if set to True.
                Otherwise, processing happens for categorical variables.
                Default Value: False
                Types: bool

        RAISES:
            None.

        RETURNS:
            None.

        EXAMPLES:
            # To process categorical varaibles.
            self.__process_explicit_independent_variables()

            # To process numerical varaibles.
            self.__process_explicit_independent_variables(True)
        """
        if not numerical:
            explicit_list = self._explicit_independent_categorical
            other_explicit_list = self._explicit_independent_numerical
        else:
            explicit_list = self._explicit_independent_numerical
            other_explicit_list = self._explicit_independent_categorical

        if "." in explicit_list:
            # If all column notation '.' dot is used, then we must include all columns in
            # CATEGORICAL/NUMERICAL category, excluding following columns:
            #   1. Dependent variable column
            #   2. Default independent variables specified by user, i.e., variables specified without casting.
            #   3. NUMERICAL/CATEGORICAL independent variable explicitly specified by user using
            #      'as_numerical()/as_categorical()'.
            explicit_list = list(set([c.name for c in self.__metaexpr.c]) - {self.__dependent_vars}
                                 - set(self._default_independent_variables) - set(other_explicit_list))

        if not numerical:
            self._explicit_independent_categorical = explicit_list
        else:
            self._explicit_independent_numerical = explicit_list

    def _get_all_vars(self):
        """
        Method returns a list which contains all the variables of the formula.
        """
        all_vars = self.__independent_vars
        if self.__dependent_vars is not None:
            all_vars.insert(0,self._get_dependent_vars())
        return all_vars

    def _get_dependent_vars(self):
        """
        Method returns variable on the LHS of the formula.
        """
        return self.__dependent_vars.strip()

    def _get_independent_vars(self):
        """
        Method returns variable on the RHS of the formula.
        """
        return self.__independent_vars
    
    def _var_split(self, var):
        """
        Split string into multiple strings on + or -.

        PARAMETERS:
            string  - var to split

        RETURNS:
            A list of strings
        """
        split_expr = re.split(r"[+-]", var)
        varlist = filter(None,split_expr)
        return [col.strip() for col in list(varlist)]

    def get_categorical_columns(self, data_types):
        """
        Function that will return all columns that belong to categorical column types.
        Columns present in '_explicit_independent_categorical' list are directly added as
        categorical columns, without type checking, where as columns in _default_independent_variables
        are type checked against 'data_types'.

        PARAMETERS:
            data_types:
                Required Argument.
                Specifies the list of categorical column types.
                Types: SQLAlchemy VisitableType or List of such types.

        RETURNS:
            List of column names which are to be classified as categorical columns.

        RAISES:
            None.

        EXAMPLES:
            data_types = UtilsFunc()._get_categorical_datatypes()
            print(str(formula_object.get_categorical_columns(data_types)))
        """
        if self._categorical_columns is not None:
            return self._categorical_columns

        columns_bytype = []
        for column in self._default_independent_variables:
            if self._formula_column_type_map[column] in data_types:
                columns_bytype.append(column)

        for column in self._explicit_independent_categorical:
            columns_bytype.append(column)

        self._categorical_columns = columns_bytype
        return columns_bytype

    def get_numerical_columns(self, data_types, all=False):
        """
        Function that will return all columns that belong to numerical column types.
        Columns present in '_explicit_independent_numerical' list are directly added as
        numerical columns, without type checking, where as columns in _default_independent_variables
        are type checked against 'data_types'.

        PARAMETERS:
            data_types:
                Required Argument.
                Specifies the list of numerical column types.
                Types: SQLAlchemy VisitableType or List of such types.

            all:
                Optional Argument.
                Specifies a boolean that will decide whether to add dependent variable as well as
                part of the returned columns or not.
                If True, the dependent variable is also considered.
                Default Value: False
                Types: bool


        RETURNS:
            List of column names which are to be classified as numerical columns.

        RAISES:
            None.

        EXAMPLES:
            # Get "numerical" type columns
            data_types = UtilsFunc()._get_numeric_datatypes()
            print(str(formula_object.get_numerical_columns(data_types)))

            # Get "numerical" type columns including dependent variable, if it is of type numeric.
            data_types = UtilsFunc()._get_numeric_datatypes()
            print(str(formula_object.get_numerical_columns(data_types, all=True)))
        """
        if self._numeric_columns is not None:
            return self._numeric_columns

        columns_bytype = []
        if all:
            if self._formula_column_type_map[self.__dependent_vars] in data_types:
                columns_bytype.append(self.__dependent_vars)

        for column in self._default_independent_variables:
            if self._formula_column_type_map[column] in data_types:
                columns_bytype.append(column)

        for column in self._explicit_independent_numerical:
            columns_bytype.append(column)

        self._numeric_columns = columns_bytype
        return columns_bytype

    def get_all_columns(self, data_types):
        """
        Function that will return all columns that belong to types specified by data_types.

        PARAMETERS:
            data_types:
                Required Argument.
                Specifies the list of categorical column types.
                Types: SQLAlchemy VisitableType or List of such types.

        RETURNS:
            List of column names which belong to types specified by data_types.

        RAISES:
            None.

        EXAMPLES:
            data_types = UtilsFunc()._get_all_datatypes()
            print(str(formula_object.get_all_columns(data_types)))
        """
        if self._all_columns is not None:
            return self._all_columns

        columns_bytype = []
        for column in self._get_all_vars():
            if self._formula_column_type_map[column] in data_types:
                columns_bytype.append(column)

        self._all_columns = columns_bytype
        return columns_bytype

    @property
    def all_columns(self):
        """
        DESCRIPTION:
            Property to get the list of all columns used in formula.

        PARAMETERS:
            None.

        RETURNS:
            List of all columns used in formula.

        RAISES:
            None.

        EXAMPLES:
            # Load the data to run the example
            load_example_data("decisionforest", ["housing_train"])

            # Create teradataml DataFrame.
            housing_train = DataFrame.from_table("housing_train")

            # Example 1 -
            decision_forest_out1 = DecisionForest(formula = "homestyle ~ bedrooms + lotsize + gashw + driveway + \
                                                  stories + recroom + price + garagepl + bathrms + fullbase + airco + \
                                                  prefarea",
                                                  data = housing_train,
                                                  tree_type = "classification",
                                                  ntree = 50,
                                                  nodesize = 1,
                                                  variance = 0.0,
                                                  max_depth = 12,
                                                  mtry = 3,
                                                  mtry_seed = 100,
                                                  seed = 100)

            # Print all columns used in formula.
            decision_forest_out1.formula.all_columns
        """
        if self._all_columns is None:
            self._all_columns = [self.response_column]

            if self.categorical_columns is not None:
                for col in self.categorical_columns:
                    if col not in self._all_columns:
                        self._all_columns.append(col)

            if self.numeric_columns is not None:
                for col in self.numeric_columns:
                    if col not in self._all_columns:
                        self._all_columns.append(col)

        return self._all_columns

    @property
    def categorical_columns(self):
        """
        DESCRIPTION:
            Property to get the list of all independent categorical columns used in formula.

        PARAMETERS:
            None.

        RETURNS:
            List of categorical columns used in formula.
            If no categorical column is used in formula, property will return None.

        RAISES:
            None.

        EXAMPLES:
            # Load the data to run the example
            load_example_data("decisionforest", ["housing_train"])

            # Create teradataml DataFrame.
            housing_train = DataFrame.from_table("housing_train")

            # Example 1 -
            decision_forest_out1 = DecisionForest(formula = "homestyle ~ bedrooms + lotsize + gashw + driveway + \
                                                  stories + recroom + price + garagepl + bathrms + fullbase + airco + \
                                                  prefarea",
                                                  data = housing_train,
                                                  tree_type = "classification",
                                                  ntree = 50,
                                                  nodesize = 1,
                                                  variance = 0.0,
                                                  max_depth = 12,
                                                  mtry = 3,
                                                  mtry_seed = 100,
                                                  seed = 100)

            # Print categorical columns used in formula.
            decision_forest_out1.formula.categorical_columns
        """
        return self._categorical_columns

    @property
    def numeric_columns(self):
        """
        DESCRIPTION:
            Property to get the list of all independent numerical columns used in formula.

        PARAMETERS:
            None.

        RETURNS:
            List of numerical columns used in formula.
            If no numerical column is used in formula, property will return None.

        RAISES:
            None.

        EXAMPLES:
            # Load the data to run the example
            load_example_data("decisionforest", ["housing_train"])

            # Create teradataml DataFrame.
            housing_train = DataFrame.from_table("housing_train")

            # Example 1 -
            decision_forest_out1 = DecisionForest(formula = "homestyle ~ bedrooms + lotsize + gashw + driveway + \
                                                  stories + recroom + price + garagepl + bathrms + fullbase + airco + \
                                                  prefarea",
                                                  data = housing_train,
                                                  tree_type = "classification",
                                                  ntree = 50,
                                                  nodesize = 1,
                                                  variance = 0.0,
                                                  max_depth = 12,
                                                  mtry = 3,
                                                  mtry_seed = 100,
                                                  seed = 100)

            # Print numeric columns used in formula.
            decision_forest_out1.formula.numeric_columns
        """
        return self._numeric_columns

    @property
    def response_column(self):
        """
        DESCRIPTION:
            Property to get the response column used in formula.

        PARAMETERS:
            None.

        RETURNS:
            Returns response column.

        RAISES:
            None.

        EXAMPLES:
            # Load the data to run the example
            load_example_data("decisionforest", ["housing_train"])

            # Create teradataml DataFrame.
            housing_train = DataFrame.from_table("housing_train")

            # Example 1 -
            decision_forest_out1 = DecisionForest(formula = "homestyle ~ bedrooms + lotsize + gashw + driveway + \
                                                  stories + recroom + price + garagepl + bathrms + fullbase + airco + \
                                                  prefarea",
                                                  data = housing_train,
                                                  tree_type = "classification",
                                                  ntree = 50,
                                                  nodesize = 1,
                                                  variance = 0.0,
                                                  max_depth = 12,
                                                  mtry = 3,
                                                  mtry_seed = 100,
                                                  seed = 100)

            # Print response column used in formula.
            decision_forest_out1.formula.response_column
        """
        return self._response_column
    
    def __repr__(self):
        """Returns the string representation for a 'formula' instance."""
        return self.__formula

    def __str__(self):
        """Returns the string representation for a 'formula' instance."""
        return self.__formula