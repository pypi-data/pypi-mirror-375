# ##################################################################
#
# Copyright 2024 Teradata. All rights reserved.
# TERADATA CONFIDENTIAL AND TRADE SECRET
#
# Primary Owner: mounika.kotha@teradata.com
# Secondary Owner: Aanchal Kavedia (aanchal.kavedia@teradata.com)
#
# Notes:
#   * This code is only for internal use.
#   * The code may perform modify, create, or delete operations
#     in database based on given query. Hence, limit the permissions
#     granted to the credentials.
#   * This file implements the functionality of loading data to a table.
#
# ##################################################################

import csv
import json
import os
import datetime
from teradataml.common.exceptions import TeradataMlException
from teradataml.common.messages import Messages
from teradataml.common.messagecodes import MessageCodes
from teradataml.context.context import *
from teradataml.dataframe.copy_to import copy_to_sql
import pandas as pd
import numpy as np
from teradataml import *
from teradataml.options import display
from teradataml.common.utils import UtilFuncs
from teradataml.common.sqlbundle import SQLBundle
import teradataml.context.context as tdmlctx
from teradataml.context.context import _get_context_temp_databasename
from collections import OrderedDict, defaultdict
from teradataml.telemetry_utils.queryband import collect_queryband

json_data = {}
col_types_dict = {}
curr_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "example-data")


@collect_queryband(queryband='LoadData')
def load_data(function_name, table_name):
    """
    This function loads the data to the specified table. This is only used for
    trying examples for the analytic functions, to load the required data.

    Note:
        Database used for loading table depends on the following conditions:
        1. If the configuration option "temp_table_database" is set, then the
           tables are loaded in the database specified in this option.
        2. If the configuration option "temp_table_database" is not set and
           "temp_database_name" parameter is used while creating context, then
           the tables are loaded in the database specified in
           "temp_database_name" parameter.
        3. If none of them are specified then the tables are created in the
           connecting users' default database or the connecting database.

    PARAMETERS:
        function_name:
            Required Argument.
            The argument contains the prefix name of the example json file to be used to load data.
            Note: One must use the function_name values only as specified in the load_data()
                  function calls specified in the example sections of teradataml API's. If any other
                  string is passed as prefix input an error will be raised as 'prefix_str_example.json'
                  file not found.
            This *_example.json file contains the schema information for the tables that can be loaded
            using this JSON file. Sample json containing table schema is as follows. Here we can
            load three tables 'sentiment_extract_input', 'sentiment_word' and 'restaurant_reviews', with
            <function_name>_exmaple.json, assuming file name is <function_name>_exmaple.json
                {
                    "sentiment_extract_input": {
                        "id" : "integer",
                        "product" : "varchar(30)",
                        "category" : "varchar(10)",
                        "review" : "varchar(1500)"
                    },
                    "sentiment_word": {
                        "word" : "varchar(10)",
                        "opinion" : "integer"
                    },
                    "restaurant_reviews": {
                        "id" : "integer",
                        "review_text" : "varchar(500)"
                    }
                }

            Type : str

        table_name
            Required Argument.
            Specifies the name of the table to be created in the database.
            Note: Table names provided here must have an equivalent datatfile (CSV) present at
                  teradataml/data. Schema information for the same must also be present in
                  <function_name>_example.json as shown in 'function_name' argument description.
            Type : string or list of str

    EXAMPLES:
        >>> from teradataml import *
        >>> from teradatagenai import load_data

        # Example 1: When connection is created without "temp_database_name",
        # table is loaded in users' default database.
        >>> con = create_context(host = 'tdhost', username='tduser', password = 'tdpassword')
        >>> load_data('employee', 'employee_data')
        # Create a teradataml DataFrame.
        >>> df = DataFrame("employee_data")

        # Example 3: When connection is created with "temp_database_name"
        # parameter and configuration option "temp_table_database" is also
        # specified, then the table is created in the database specified in the
        # configuration option.
        >>> con = create_context(host = 'tdhost', username='tduser', password = 'tdpassword',
                                temp_database_name = "temp_db")
        >>> configure.temp_table_database = "temp_db1"
        >>> load_data('employee', 'employee_data')
        # Create a teradataml DataFrame.
        >>> df = DataFrame(in_schema("temp_db1", "employee_data"))

    RETURNS:
        None.

    RAISES:
        TeradataMlException - If table load fails.
        FileNotFoundError - If invalid function_name is provided.

    """
    # Check if context is created or not.
    if get_connection() is None:
        raise TeradataMlException(Messages.get_message(MessageCodes.INVALID_CONTEXT_CONNECTION),
                                  MessageCodes.INVALID_CONTEXT_CONNECTION)

    example_filename = os.path.join(curr_dir, "{}_example.json".format(function_name.lower()))
    global json_data

    # Read json file to get table columns and datatypes
    with open(format(example_filename)) as json_input:
        json_data = json.load(json_input, object_pairs_hook=OrderedDict)

    if isinstance(table_name, list):
        for table in table_name:
            try:
                __create_table_insert_data(table)
            except TeradataMlException as err:
                if err.code == MessageCodes.TABLE_ALREADY_EXISTS:
                    # TODO - Use the improved way of logging messages when the right tools for it are built in
                    print("WARNING: Skipped loading table {} since it already exists in the database.".format(table))
                else:
                    raise
    else:
        try:
            __create_table_insert_data(table_name)
        except TeradataMlException as err:
            if err.code == MessageCodes.TABLE_ALREADY_EXISTS:
                # TODO - Use the improved way of logging messages when the right tools for it are built in
                print("WARNING: Skipped loading table {} since it already exists in the database.".format(table_name))
            else:
                raise

    json_input.close()

def __create_table_insert_data(tablename):
    """
    Function creates table and inserts data from csv into the table.

    PARAMETERS:
        tablename:
            Required Argument.
            Specifies the name of the table to be created in the database.
            Type : str

    EXAMPLES:
         __create_table_insert_data("ville_temperature")

    RETURNS:
         None.

    RAISES:
         TeradataMlException - If table already exists in database.
     """
    csv_file = os.path.join(curr_dir, "{}.csv".format(tablename))
    col_types_dict = json_data[tablename]
    column_dtypes = ''
    date_time_varbyte = {}
    pti_table = False
    pti_clause = ""

    '''
    Create column datatype string required to create a table.
    EXAMPLE:
        id integer,model varchar(30)
    '''
    column_count = 0
    for column in col_types_dict.keys():
        if column in ["TD_TIMECODE", "TD_SEQNO"]:
            column_count = column_count + 1
            continue

        if column == "<PTI_CLAUSE>":
            pti_table = True
            pti_clause = col_types_dict[column]
            continue

        # Create a dictionary with column names as list of values which has 
        # datatype as date, timestamp and varbyte.
        # EXAMPLE : date_time_varbyte_columns = {'date':['orderdate']}
        for column_type in ["date", "timestamp", "varbyte"]:
            if column_type in col_types_dict[column]:
                date_time_varbyte.setdefault(column_type, []).append(column)

        column_dtypes = "{0}{1} {2},\n".format(column_dtypes, column, col_types_dict[column])
        column_count = column_count + 1

    td_number_of_columns = '?,' * column_count
    # Deriving global connection using context.get_context()
    con = get_connection()
    # Get temporary database.
    temp_db = _get_context_temp_databasename(table_type=
                                             TeradataConstants.TERADATA_TABLE)
    table_exists = con.dialect.has_table(con, tablename, schema=temp_db,
                                         table_only=True)
    if table_exists:
        raise TeradataMlException(Messages.get_message(MessageCodes.TABLE_ALREADY_EXISTS, tablename),
                                  MessageCodes.TABLE_ALREADY_EXISTS)
    else:
        tablename = "{}.{}".format(UtilFuncs._teradata_quote_arg(_get_context_temp_databasename
                                                                 (table_type=TeradataConstants.TERADATA_TABLE), "\"",
                                                                 False),
                                   UtilFuncs._teradata_quote_arg(tablename, "\"", False))
        if pti_table:
            UtilFuncs._create_table_using_columns(tablename, column_dtypes[:-2], pti_clause)
        else:
            UtilFuncs._create_table_using_columns(tablename, column_dtypes[:-2])

        try:
            __insert_into_table_from_csv(tablename, td_number_of_columns[:-1], csv_file, date_time_varbyte)
        except:
            # Drop the table, as we have created the same.
            UtilFuncs._drop_table(tablename)
            raise

def __insert_into_table_from_csv(tablename, column_markers, file, date_time_varbyte_columns):
    """
    Builds and executes a prepared statement with parameter markers for a table. 

    PARAMETERS:
        tablename:
            Required Argument.
            Table name to insert data into.
            Types: str

        column_markers
            Required Argument.
            The parameter markers for the insert prepared statement.
            Types: str

        file
            Required Argument.
            csv file which contains data to be loaded into table.
            Types: str

        date_time_varbyte_columns
            Required Argument.
            Dictionary containing date, time and varbyte columns.
            Types: Dictionary

    EXAMPLES:
        date_time_varbyte_columns = {'date':['orderdate']}
        preparedstmt = __insert_into_table_from_csv(
                        'mytab', '?, ?','file.csv', date_time_varbyte_columns )

    RETURNS:
         None

    RAISES:
        Database error if an error occurred while executing the DDL statement.

    """
    insert_stmt = SQLBundle._build_insert_into_table_records(tablename, column_markers)

    # Defining the formatter.
    formatter = {
        "date": lambda op: datetime.datetime.strptime(op, '%Y-%m-%d'),
        "timestamp": lambda op: datetime.datetime.strptime(op, '%Y-%m-%d %H:%M:%S'),
        "timestamp(6)": lambda op: datetime.datetime.strptime(op, '%Y-%m-%d %H:%M:%S.%f'),
        "varbyte": lambda op: bytes.fromhex(op)
    }

    if tdmlctx.td_connection is not None:
        try:
            with open(file, 'r') as f:
                reader = csv.reader(f)
                # Read headers of csv file
                headers = next(reader)

                insert_list = []
                for row in reader:
                    # For NULL values, entries in csv are ""
                    # Handling table with NULL values
                    new_row = []  # Row with None when element is empty
                    for element in row:
                        if element == "":
                            new_row.append(None)
                        else:
                            new_row.append(element)
                    '''
                    The data in the row is converted from string to date or 
                    timestamp format, which is required to insert data into
                    table for date or timestamp columns.
                    '''
                    for key, value in date_time_varbyte_columns.items():
                        for val in value:
                            if val in headers and new_row[headers.index(val)] is not None:
                                try:
                                    new_row[headers.index(val)] = formatter[key](new_row[headers.index(val)])
                                except ValueError:
                                    pass

                    insert_list.append(tuple(new_row))

                # Batch Insertion (using DBAPI's executeMany) used here to insert list of dictionaries
                execute_sql(insert_stmt, insert_list)

        except:
            raise
    else:
        raise TeradataMlException(Messages.get_message(MessageCodes.CONNECTION_FAILURE),
                                  MessageCodes.CONNECTION_FAILURE)
