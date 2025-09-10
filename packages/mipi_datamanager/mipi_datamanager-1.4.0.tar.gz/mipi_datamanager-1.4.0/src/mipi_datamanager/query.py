from mipi_datamanager import connection
from mipi_datamanager.errors import FormatParameterError
import pandas as pd
import re

def truncate_sql_inserts(sql: str, max_inserts: int) -> str:
    """
    Collapses INSERT INTO @…; or INSERT INTO #…; values for SQL readability.

    Args:
        sql (str): full SQL text
        max_inserts (int): number of insert rows to keep

    Returns:
        The SQL string where all insert lines beyond the first `max_inserts`
        have been replaced by a comment stating how many were truncated.
    """
    lines = sql.splitlines(keepends=True)
    result = []
    insert_seen = 0
    truncated = 0
    i = 0

    # regex now matches either '@' or '#' after INSERT INTO
    insert_re = re.compile(r"\s*INSERT INTO [@#]", re.IGNORECASE)

    while i < len(lines):
        line = lines[i]
        if insert_re.match(line):
            insert_seen += 1
            if insert_seen <= max_inserts:
                result.append(line)
            else:
                # count and skip all further insert lines
                j = i
                while j < len(lines) and insert_re.match(lines[j]):
                    truncated += 1
                    j += 1
                result.append(f"-- truncated {truncated} insert values\n")
                i = j - 1
        else:
            result.append(line)
        i += 1

    return ''.join(result)

def execute_sql_file(file_path: str, connection: connection.Odbc, format_parameters_list: list = None) -> pd.DataFrame:
    """

    Executes a sql query from a sql file. Optionally renders string formatting into '{}' brackets.

    Args:
        file_path: file path to the sql
        connection: MiPi connection object
        format_parameters_list: arguments to be passed into sql placeholders

    Returns: dataframe

    """

    sql = read_sql_file(file_path, format_parameters_list)
    df = execute_sql_string(sql, connection)
    print(f"Successfully Read:      File: {file_path}")

    return df


def execute_sql_string(sql: str, connection: connection.Odbc, format_parameters_list: list = None, collapse_inserts_on_error: int = 10) -> pd.DataFrame:
    """
    Executes a sql query from a sql string. Optionally renders string formatting into '{}' brackets.

    Args:
        sql: SQL text string
        connection: MiPi connection object
        format_parameters_list: arguments to be passed into sql placeholders

    Returns:

    """
    if format_parameters_list:
        param_count = sql.count("{}")

        if param_count != len(format_parameters_list):
            raise FormatParameterError(
                f"Number of arguments: {len(format_parameters_list)} does not match the number of place holders")

        _sql = sql.format(*format_parameters_list)

    else:
        _sql = sql

    try:
        with connection as con:
            return pd.read_sql(_sql, con)

    except Exception as e:
            cleaned = truncate_sql_inserts(str(e), collapse_inserts_on_error)
            raise type(e)(f"SQL execution failed:\n{cleaned}").with_traceback(e.__traceback__)

def read_sql_file(file_path: str, format_parameters_list: list = None) -> str:
    """

    Reads a SQL file and optionally renders string formatting into '{}' brackets

    Args:
        file_path: filepath to the sql
        format_parameters_list: arguments to be passed into sql placeholders

    Returns: resolved sql string

    """

    assert isinstance(format_parameters_list,
                      list) or format_parameters_list is None, "Format Parameters list must be type list"

    if not format_parameters_list:
        format_parameters_list = []

    with open(file_path, 'r') as f:
        sql = f.read()
        param_count = sql.count("{}")
        if param_count != len(format_parameters_list):
            raise FormatParameterError(
                f"Number of arguments: {len(format_parameters_list)} does not match the number of place holders")
        _sql = sql.format(*format_parameters_list)

    return _sql
