from functools import wraps

from teradataml.common.utils import UtilFuncs

from teradataml.common.exceptions import TeradataMlException
from teradataml.common.messages import Messages
from teradataml.common.messagecodes import MessageCodes
from sqlalchemy import func, literal
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import expression
from sqlalchemy.sql.elements import BinaryExpression, ColumnClause
from sqlalchemy.sql.expression import case as case_when

from .sql import _SQLColumnExpression, _resolve_value_to_type
from .sql_interfaces import ColumnExpression

from teradatasqlalchemy.dialect import preparer, dialect as td_dialect
from teradatasqlalchemy import (BYTEINT, SMALLINT, INTEGER, BIGINT, DECIMAL, FLOAT)
from teradatasqlalchemy import (CHAR, VARCHAR, CLOB, NUMBER)
from teradatasqlalchemy import (TIMESTAMP, DATE, TIME)

__all__ = ['translate', 'to_numeric']

def _as_varchar_literal(arg):
    """
    return a sqlalchemy literal

    Parameters
    ---------
    arg: string literal

    """
    return literal(arg, type_ = VARCHAR(len(arg)))

# TODO: refactor this once more functions are created
#def _implementation(fn):
#
#  """
#    This decorator wraps sql functions that generate expressions
#    that can be used in DataFrame and Series methods such as assign.
#
#    The wrapper performs error checks as well as implements
#    the kind of ColumnExpression instance to return
#
#    Parameters
#    ----------
#      A function or method that generates sql.
#      The function is from the sql_functions module.
#
#    Examples
#    --------
#      @implementation
#      def unicode_to_latin(x)
#
#  """
#  @wraps
#  def inner(*args, **kw):
#
#      res = fn(*args, **kw)
#      return _SQLColumnExpression(res)
#
#
#@_implementation

def translate(x, source = 'UNICODE', target = 'LATIN'):
    """
    Returns a TRANSLATE(x USING source_TO_target) expression

    PARAMETERS:
      x: A ColumnExpression instance coming from the DataFrame
         or output of other functions in sql_functions. A python
         string literal may also be used.

      source, target: str with values:
        - 'UNICODE'
        - 'LATIN'

    REFERENCES:
      Chapter 28: String Operators and Functions
      Teradata® Database SQL Functions, Operators, Expressions, and
      Predicates, Release 16.20

    EXAMPLES:
      >>> from teradataml.dataframe.sql_functions import translate

      >>> df = DataFrame('df')
      >>> tvshow = df['tvshow']

      >>> res = df.assign(tvshow = translate(tvshow))
    """

    # error checking
    if not isinstance(x, str) and not isinstance(x, ColumnExpression):
      msg = Messages.get_message(MessageCodes.TDMLDF_UNKNOWN_TYPE).format('x', "a DataFrame column or string")
      raise TeradataMlException(msg, MessageCodes.TDMLDF_UNKNOWN_TYPE)

    if not isinstance(source, str):
      msg = Messages.get_message(MessageCodes.TDMLDF_UNKNOWN_TYPE).format('source', "a string")
      raise TeradataMlException(msg, MessageCodes.TDMLDF_UNKNOWN_TYPE)

    if not isinstance(target, str):
      msg = Messages.get_message(MessageCodes.TDMLDF_UNKNOWN_TYPE).format('target', "a string")
      raise TeradataMlException(msg, MessageCodes.TDMLDF_UNKNOWN_TYPE)

    supported = ('UNICODE', 'LATIN')
    if (source.upper() not in supported):
      msg = Messages.get_message(MessageCodes.INVALID_ARG_VALUE).format(source.upper(), 'source', "in {}".format(supported))
      raise TeradataMlException(msg, MessageCodes.INVALID_ARG_VALUE)

    if (target.upper() not in supported):
      msg = Messages.get_message(MessageCodes.INVALID_ARG_VALUE).format(target.upper(), 'target', "in {}".format(supported))
      raise TeradataMlException(msg, MessageCodes.INVALID_ARG_VALUE)

    # get the sqlalchemy expression
    expr = None
    if isinstance(x, ColumnExpression):
      expr = x.expression

    else:
      expr = literal(x, type_ = VARCHAR(length = len(x), charset = 'UNICODE'))

    if not isinstance(expr.type, (CHAR, VARCHAR, CLOB)):
      msg = Messages.get_message(MessageCodes.TDMLDF_UNKNOWN_TYPE).format('x', "a DataFrame column of type CHAR, VARCHAR, or CLOB")
      raise TeradataMlException(msg, MessageCodes.TDMLDF_UNKNOWN_TYPE)

    # get the result type
    length, charset = expr.type.length, target
    typ_ = CLOB(length, charset) if isinstance(expr.type, CLOB) else VARCHAR(length, charset)

    # define an inner class to generate the sql expression
    class _translate(expression.FunctionElement):
        name = '_translate'
        type = typ_

    custom = source + '_TO_' + target
    @compiles(_translate)
    def default__translate(element, compiler, **kw):
        column_expression = compiler.process(element.clauses, **kw)
        return ('TRANSLATE({x} USING ' + custom + ')').format(x = column_expression)

    return _SQLColumnExpression(_translate(expr.expression))

def case(whens, value=None, else_=None):
    """
    Returns a ColumnExpression based on the CASE expression.

    PARAMETERS:
        whens:
            Required Argument.
            Specifies the criteria to be compared against. It accepts two different forms,
            based on whether or not the value argument is used.

            In the first form, it accepts a list of 2-tuples; each 2-tuple consists of (<sql expression>, <value>),
            where the <sql expression> is a boolean expression and “value” is a resulting value.
            For example:

                case([
                        (df.first_name == 'wendy', 'W'),
                        (df.first_name == 'jack', 'J')
                    ])

            In the second form, it accepts a Python dictionary of comparison values mapped to a resulting value;
            this form requires 'value' argument to be present, and values will be compared using the '==' operator.
            For example:

                case(
                    {"wendy": "W", "jack": "J"},
                      value=df.first_name
                    )

            Types: List of 2-tuples or Dictionary of comparison value mapped to a resulting value.

        value:
            Optional Argument. Required when 'whens' is of dictionary type.
            Specifies a SQL expression (ColumnExpression or literal) which will be used as a fixed “comparison point”
            for candidate values within a dictionary passed to the 'whens' argument.
            Types: ColumnExpression or SQL Expression (Python literal)

        else_:
            Optional Argument.
            Specifies a SQL expression (ColumnExpression or literal) which will be the evaluated result of
            the CASE construct if all expressions within 'whens' evaluate to False.
            When omitted, will produce a result of NULL if none of the 'when' expressions evaluate to True.
            Types: ColumnExpression or SQL Expression (Python literal)


    RETURNS:
        ColumnExpression


    EXAMPLES:
        >>> from teradataml.dataframe.sql_functions import case
        >>> load_example_data("GLM", ["admissions_train"])
        >>> df = DataFrame("admissions_train")
        >>> print(df)
           masters   gpa     stats programming  admitted
        id
        5       no  3.44    Novice      Novice         0
        3       no  3.70    Novice    Beginner         1
        1      yes  3.95  Beginner    Beginner         0
        20     yes  3.90  Advanced    Advanced         1
        8       no  3.60  Beginner    Advanced         1
        25      no  3.96  Advanced    Advanced         1
        18     yes  3.81  Advanced    Advanced         1
        24      no  1.87  Advanced      Novice         1
        26     yes  3.57  Advanced    Advanced         1
        38     yes  2.65  Advanced    Beginner         1
        >>> print(df.shape)
        (40, 6)

        >>> # Example showing 'whens' passed a 2-tuple - assign rating based on GPA
        >>> # gpa > 3.0        = 'good'
        >>> # 2.0 < gpa <= 3.0 = 'average'
        >>> # gpa <= 2.0       = 'bad'
        >>> # Filtering all the 'good' scores only.
        >>> good_df = df[case([(df.gpa > 3.0, 'good'),
                               (df.gpa > 2.0, 'average')],
                               else_='bad') == 'good']
        >>> print(good_df)
           masters   gpa     stats programming  admitted
        id
        13      no  4.00  Advanced      Novice         1
        11      no  3.13  Advanced    Advanced         1
        9       no  3.82  Advanced    Advanced         1
        26     yes  3.57  Advanced    Advanced         1
        3       no  3.70    Novice    Beginner         1
        1      yes  3.95  Beginner    Beginner         0
        20     yes  3.90  Advanced    Advanced         1
        18     yes  3.81  Advanced    Advanced         1
        5       no  3.44    Novice      Novice         0
        32     yes  3.46  Advanced    Beginner         0
        >>> print(good_df.shape)
        (35, 6)

        >>> # Use DataFrame.assign() to create a new column with the rating
        >>> whens_df = df.assign(rating = case([(df.gpa > 3.0, 'good'),
                                                (df.gpa > 2.0, 'average')],
                                                else_='bad'))
        >>> print(whens_df)
           masters   gpa     stats programming  admitted   rating
        id
        5       no  3.44    Novice      Novice         0     good
        3       no  3.70    Novice    Beginner         1     good
        1      yes  3.95  Beginner    Beginner         0     good
        20     yes  3.90  Advanced    Advanced         1     good
        8       no  3.60  Beginner    Advanced         1     good
        25      no  3.96  Advanced    Advanced         1     good
        18     yes  3.81  Advanced    Advanced         1     good
        24      no  1.87  Advanced      Novice         1      bad
        26     yes  3.57  Advanced    Advanced         1     good
        38     yes  2.65  Advanced    Beginner         1  average
        >>> print(whens_df.shape)
        (40, 7)

        >>> # Example not specifying 'else_'
        >>> no_else =  df.assign(rating = case([(df.gpa > 3.0, 'good')]))
        >>> print(no_else)
           masters   gpa     stats programming  admitted  rating
        id
        5       no  3.44    Novice      Novice         0    good
        3       no  3.70    Novice    Beginner         1    good
        1      yes  3.95  Beginner    Beginner         0    good
        20     yes  3.90  Advanced    Advanced         1    good
        8       no  3.60  Beginner    Advanced         1    good
        25      no  3.96  Advanced    Advanced         1    good
        18     yes  3.81  Advanced    Advanced         1    good
        24      no  1.87  Advanced      Novice         1    None
        26     yes  3.57  Advanced    Advanced         1    good
        38     yes  2.65  Advanced    Beginner         1    None
        >>> print(no_else.shape)
        (40, 7)

        >>> # Example showing 'whens' passed a dictionary along with 'value'
        >>> whens_value_df = df.assign(admitted_text = case({ 1 : "admitted", 0 : "not admitted"},
                                                            value=df.admitted,
                                                            else_="don't know"))

        >>> print(whens_value_df)
           masters   gpa     stats programming  admitted  admitted_text
        id
        13      no  4.00  Advanced      Novice         1       admitted
        11      no  3.13  Advanced    Advanced         1       admitted
        9       no  3.82  Advanced    Advanced         1       admitted
        28      no  3.93  Advanced    Advanced         1       admitted
        33      no  3.55    Novice      Novice         1       admitted
        10      no  3.71  Advanced    Advanced         1       admitted
        16      no  3.70  Advanced    Advanced         1       admitted
        32     yes  3.46  Advanced    Beginner         0   not admitted
        34     yes  3.85  Advanced    Beginner         0   not admitted
        17      no  3.83  Advanced    Advanced         1       admitted
        >>> print(whens_value_df.shape)
        (40, 7)

        >>> # Example showing how you can decide on projecting a column based on the value of expression.
        >>> # In this example, you end up projecting values from column 'average_rating' if 2.0 < gpa <= 3.0,
        >>> # and the values from column 'good_rating' when gpa > 3.0, naming the column 'ga_rating'.

        >>> from sqlalchemy.sql import literal_column
        >>> whens_new_df = df.assign(good_rating = case([(df.gpa > 3.0, 'good')]))
        >>> whens_new_df = whens_new_df.assign(avg_rating = case([((whens_new_df.gpa > 2.0) & (whens_new_df.gpa <= 3.0),
                                                                  'average')]))
        >>> literal_df = whens_new_df.assign(ga_rating = case([(whens_new_df.gpa > 3.0, literal_column('good_rating')),
                                                               (whens_new_df.gpa > 2.0, literal_column('avg_rating'))]))
        >>> print(literal_df)
           masters   gpa     stats programming  admitted good_rating   avg_rating ga_rating
        id
        5       no  3.44    Novice      Novice         0        good         None      good
        3       no  3.70    Novice    Beginner         1        good         None      good
        1      yes  3.95  Beginner    Beginner         0        good         None      good
        20     yes  3.90  Advanced    Advanced         1        good         None      good
        8       no  3.60  Beginner    Advanced         1        good         None      good
        25      no  3.96  Advanced    Advanced         1        good         None      good
        18     yes  3.81  Advanced    Advanced         1        good         None      good
        24      no  1.87  Advanced      Novice         1        None         None      None
        26     yes  3.57  Advanced    Advanced         1        good         None      good
        38     yes  2.65  Advanced    Beginner         1        None      average   average

    """

    # Variable contains_type stores the tdtypes
    contains_type = set()
    # Validations
    new_whens = whens
    # whens can be a dictionary, but requires values to be specified
    if isinstance(whens, dict):
        # Make sure values is passed and is of required type
        if not value:
            raise TeradataMlException(Messages.get_message(MessageCodes.DEPENDENT_ARG_MISSING, "value",
                                                           "whens of dictionary type"),
                                      MessageCodes.DEPENDENT_ARG_MISSING)
        # as whens can take value only as Python type, so first mapping the value of
        # Python type to tdtypes and storing the tdtypes in contains_type
        for _, values in whens.items():
            contains_type.add(type(_resolve_value_to_type(values)))
        # If it is a teradataml ColumnExpression, we need to pass the SQLAlchemy Column Expression
        if isinstance(value, ColumnExpression):
            value = value.expression

    # whens can be a list of 2-tuples
    elif isinstance(whens, list):
        new_whens = []
        # Make sure the list of tuples has _SQLColumnExpression as first element
        for when in whens:
            raise_err = True if (not isinstance(when, tuple) or len(when) != 2) else False
            if raise_err or (not isinstance(when[0], ColumnExpression) and not isinstance(when[0], BinaryExpression)):
                raise TeradataMlException(Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE, 'whens',
                                                               "a list of 2-tuples with each tuple having a"
                                                               " boolean expression as the first element"),
                                          MessageCodes.UNSUPPORTED_DATATYPE)

            # If it is a teradataml ColumnExpression, we need to use the SQLAlchemy Column Expression
            new_whens.append((when[0].expression if isinstance(when[0], ColumnExpression) else when[0],
                              when[1].expression if isinstance(when[1], ColumnExpression) else when[1]))
            # If when[1] is a teradataml ColumnExpression type or when[1] is a literal_column then store
            # the tdtypes in contains_type.
            if isinstance(when[1], (ColumnExpression, ColumnClause)):
                contains_type.add(type(when[1].type))
            # If when[1] is of Python data type, so first mapping the value of
            # Python type to tdtypes and storing the tdtypes in contains_type
            else:
                contains_type.add(type(_resolve_value_to_type(when[1])))

        # values will be ignored by SQLAlchemy when 'whens' is a 2-tuple list.
        # However, an issue was noticed with it when it was actually passed a value, which resulted in an
        # incorrectly formed CASE statement. We forcefully set it to NULL.
        if value is not None:
            value = None
    else:
        raise TeradataMlException(Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE, 'whens',
                                                               "a list of 2-tuples with each tuple having a"
                                                               " boolean expression as the first element"),
                                          MessageCodes.UNSUPPORTED_DATATYPE)

    # If it is a teradataml ColumnExpression, we need to use the SQLAlchemy Column Expression
    # and storing the tdtypes of ColumnExpression in contains_type
    if isinstance(else_, ColumnExpression):
        else_ = else_.expression
        contains_type.add(type(else_.type))
    # If else_ is literal_column then store the tdtypes of literal_column used
    elif isinstance(else_, ColumnClause):
        contains_type.add(type(else_.type))
    # if else_ is of python data type so first mapping the value of
    # Python type to tdtypes and storing the tdtypes in contains_type
    else:
        contains_type.add(type(_resolve_value_to_type(else_)))

    if isinstance(new_whens, dict):
        output_case_when = case_when(new_whens, value=value, else_=else_)
    else:
        output_case_when = case_when(*new_whens, value=value, else_=else_)

    # Here assigning the correct tdypes if there are multiple tdtypes present in case function
    # according to below conditions and if contains_type doesnot contain any below condition
    # we kept the type of output_case_when as it is(means type provided by case_when)
    # If VARCHAR tdtypes present in case function assign column type to VARCHAR tdtypes
    if VARCHAR in contains_type:
        output_case_when.type = VARCHAR()
    # If FLOAT tdypes present in case function assign column type to FLOAT tdtypes
    elif FLOAT in contains_type:
        output_case_when.type = FLOAT()
    # If NUMBER tdypes present in case function assign column type to NUMBER tdtypes
    elif NUMBER in contains_type:
        output_case_when.type = NUMBER()
    # If DECIMAL tdypes present in case function assign column type to DECIMAL tdtypes
    elif DECIMAL in contains_type:
        output_case_when.type = DECIMAL()
    # If BIGINT tdypes present in case function assign column type to BIGINT tdtypes
    elif BIGINT in contains_type:
        output_case_when.type = BIGINT()
    # If INTEGER tdypes present in case function assign column type to INTEGER tdtypes
    elif INTEGER in contains_type:
        output_case_when.type = INTEGER()
    # If SMALLINT tdypes present in case function assign column type to SMALLINT tdtypes
    elif SMALLINT in contains_type:
        output_case_when.type = SMALLINT()
    # If BYTEINT tdypes present in case function assign column type to BYTINT tdtypes
    elif BYTEINT in contains_type:
        output_case_when.type = BYTEINT()

    return _SQLColumnExpression(output_case_when)

def to_numeric(arg, **kw):

    """
    Convert a string-like representation of a number to a Numeric type.

    PARAMETERS:
      arg: DataFrame column
      kw: optional keyword arguments
        format_: string. Specifies the format of a string-like number to convert to numeric
        nls: dict where 'param' and 'value' are keys:

             - param specifies one of the following string values:
                 -'CURRENCY', 'NUMERIC_CHARACTERS', 'DUAL_CURRENCY', 'ISO_CURRENCY'

             - value: specifies characters that are returned by number format elements.
                      See References for more information

    REFERENCES:
      Chapter 14: Data Type Conversion Functions
      Teradata® Database SQL Functions, Operators, Expressions, and
      Predicates, Release 16.20


    RETURNS:
      A DataFrame column of numeric type

    NOTES:
      - If the arg column input is a numeric type, it is returned as is
      - Nulls may be introduced in the result if the parsing fails
      - You may need to strip() columns that have leading or trailing spaces
        in order for to_numeric to parse correctly

    EXAMPLES:

      >>> df = DataFrame('numeric_strings')

                    hex decimal commas numbers
          0        19FF   00.77   08,8       1
          1        abcd    0.77   0,88       1
          2  ABCDEFABCD   0.7.7   ,088     999
          3        2018    .077   088,       0

      >>> df.dtypes

          hex        str
          decimal    str
          commas     str
          numbers    str

      # converting string numbers to numeric
      >>> df.assign(drop_columns = True,
                    numbers = df.numbers,
                    numeric = to_numeric(df.numbers))

            numbers numeric
          0       1       1
          1       1       1
          2     999     999
          3       0       0


      # converting decimal-like strings to numeric
      # Note that strings not following the format return None
      >>> df.assign(drop_columns = True,
                   decimal = df.decimal,
                   numeric_dec = to_numeric(df.decimal))

            decimal numeric_dec
          0   00.77         .77
          1    0.77         .77
          2   0.7.7        None
          3    .077        .077

      # converting comma (group separated) strings to numeric
      # Note that strings not following the format return None
      >>> df.assign(drop_columns = True,
                    commas = df.commas,
                    numeric_commas = to_numeric(df.commas, format_ = '9G99'))

            commas numeric_commas
          0   08,8           None
          1   0,88             88
          2   ,088           None
          3   088,           None

      # converting hex strings to numeric
      >>> df.assign(drop_columns = True,
                    hex = df.hex, 
                    numeric_hex = to_numeric(df.hex, format_ = 'XXXXXXXXXX'))

                    hex   numeric_hex
          0        19FF          6655
          1        abcd         43981
          2  ABCDEFABCD  737894443981
          3        2018          8216

      # converting literals to numeric
      >>> df.assign(drop_columns = True,
                    a = to_numeric('123,456',format_ = '999,999'),
                    b = to_numeric('1,333.555', format_ = '9,999D999'),
                    c = to_numeric('2,333,2',format_ = '9G999G9'),
                    d = to_numeric('3E20'),
                    e = to_numeric('$41.99', format_ = 'L99.99'),
                    f = to_numeric('$.12', format_ = 'L.99'),
                    g = to_numeric('dollar123,456.00',
                                   format_ = 'L999G999D99', 
                                   nls = {'param': 'currency', 'value': 'dollar'})).head(1)

              a         b      c                         d      e    f       g
          0  123456  1333.555  23332 300000000000000000000  41.99  .12  123456

      # For more information on format elements and parameters, see the Reference.
    """

    # validation
    if not isinstance(arg, str) and not isinstance(arg, ColumnExpression):
        msg = Messages.get_message(MessageCodes.TDMLDF_UNKNOWN_TYPE).format('arg', "a string or DataFrame column of type CHAR or VARCHAR")
        raise TeradataMlException(msg, MessageCodes.TDMLDF_UNKNOWN_TYPE)

    expr = None
    if isinstance(arg, ColumnExpression):
        expr = arg.expression
    else:
        expr = literal(arg, type_ = VARCHAR(length = len(arg), charset = 'UNICODE'))

    # The only reason to use to_numeric with a numerically typed column is if downcast is used, 
    # but those downcasted types are not supported (uint8, int8, float32)
    # TODO: Look into supporting downcasting if we implement the three downcasted types above
    if isinstance(expr.type, tuple(UtilFuncs()._get_numeric_datatypes())):
        return arg

    if not isinstance(expr.type, (VARCHAR, CHAR)):
        msg = Messages.get_message(MessageCodes.TDMLDF_UNKNOWN_TYPE).format('arg', "a string or DataFrame column of type CHAR or VARCHAR")
        raise TeradataMlException(msg, MessageCodes.TDMLDF_UNKNOWN_TYPE)

    fmt = kw.get('format_', None)
    nls = kw.get('nls', None)

    if fmt is not None and not isinstance(fmt, str):
        msg = Messages.get_message(MessageCodes.TDMLDF_UNKNOWN_TYPE).format('format_', "a string")
        raise TeradataMlException(msg, MessageCodes.TDMLDF_UNKNOWN_TYPE)

    if nls is not None and not isinstance(nls, dict):
        msg = Messages.get_message(MessageCodes.TDMLDF_UNKNOWN_TYPE).format('nls', "a dict")
        raise TeradataMlException(msg, MessageCodes.TDMLDF_UNKNOWN_TYPE)

    # prepare for _to_number
    if fmt is not None:
        fmt = _as_varchar_literal(fmt)

        if nls is not None:
            if not (('param' in nls) and ('value' in nls)):
                msg = Messages.get_message(MessageCodes.INVALID_ARG_VALUE).format(nls, 'nls', 'dict with "param" and "value" keys')
                raise TeradataMlException(msg, MessageCodes.INVALID_ARG_VALUE)

            if not isinstance(nls['param'], str) and not isinstance(nls['value'], str):
                msg = Messages.get_message(MessageCodes.INVALID_ARG_VALUE).format(nls, 'nls', 'dict with "param" and "value" keys mapping to string values')
                raise TeradataMlException(msg, MessageCodes.INVALID_ARG_VALUE)

            nls_params = ('NUMERIC_CHARACTERS', 'CURRENCY', 'DUAL_CURRENCY', 'ISO_CURRENCY')

            if not nls['param'].upper() in nls_params:
                msg = Messages.get_message(MessageCodes.INVALID_ARG_VALUE).format(nls['param'].upper(), "nls['param']", 'in {}'.format(nls_params))
                raise TeradataMlException(msg, MessageCodes.INVALID_ARG_VALUE)

            nls_param = nls['param'].upper()
            nls_value = _as_varchar_literal(nls['value'])
            nls = {'param': nls_param, 'value': nls_value}

    elif nls is not None:
      msg = Messages.get_message(MessageCodes.MISSING_ARGS).format('format_. format_ keyword must be specfied if the nls keyword is used')
      raise TeradataMlException(msg, MessageCodes.MISSING_ARGS)

    label = arg.name if isinstance(arg, ColumnExpression) else arg
    stmt = _to_number(expr, format_=fmt, nls=nls).label(label)

    return _SQLColumnExpression(stmt)


class _to_number(expression.FunctionElement):
    """
    Internal class used for representing the TO_NUMBER function in the SQL Engine.

    """
    name = '_to_number'
    type = NUMBER()

    def __init__(self, arg, format_=None, nls=None, **kw):
        """
        See docstring for_to_numeric.

        Reference
        ---------
        Chapter 14: Data Type Conversion Functions
        Teradata® Database SQL Functions, Operators, Expressions, and
        Predicates, Release 16.20

        """
        args = [arg, format_]
        if nls is not None:
            args.append(nls['value'])
            self.nls_param = 'NLS_' + nls['param']

        args = (x for x in args if x is not None)
        super().__init__(*args)

@compiles(_to_number)
def _visit_to_number(element, compiler, **kw):
    """
    Compilation method for the _to_number function element class

    Parameters
    ----------
    element: A sqlalchemy ClauseElement instance
    compiler: A sqlalchemy.engine.interfaces.Compiled instance

    """
    col_exps = [compiler.process(exp, **kw) for exp in element.clauses]

    optional = ''

    # handle format
    if len(col_exps) >= 2:
        optional += ', {}'.format(col_exps[1])

        # handle nls
        if len(col_exps) >= 3:
            optional += ", '{} = '{}''".format(element.nls_param, col_exps[2])

    res = ('TO_NUMBER({x}{optional})').format(x = col_exps[0], optional = optional)
    return res
