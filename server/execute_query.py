import mysql.connector
import pandas as pd
import os
import io
import tiktoken


# def execute_queries(queries, mydb):
#     cursor = mydb.cursor()
#     # Join the list of query parts into a single query string
#     full_query = " ".join(queries)

#     try:
#         cursor.execute(full_query)
#         result = cursor.fetchall()
#         if result:
#             column_names = [column[0] for column in cursor.description]
#             result_dict = [dict(zip(column_names, row)) for row in result]
#             # Convert to DataFrame
#             df = pd.DataFrame(result_dict)
#             # Convert DataFrame to CSV
#             csv_io = io.StringIO()
#             df.to_csv(csv_io, index=False)
#             csv_string = csv_io.getvalue()
#             print(f"csv_string: {csv_string}")
#             return csv_string
#     except Exception as e:
#         print(f"Error occurred: {e}")
#         raise e  # re-raise the exception after logging it
#     return "No data returned from query."

def query_to_df(query_result, cursor):
    """
    This helper function converts the result of an SQL query to a pandas DataFrame and then to a CSV string.
    """
    column_names = [column[0] for column in cursor.description]
    result_dict = [dict(zip(column_names, row)) for row in query_result]
    # Convert to DataFrame
    df = pd.DataFrame(result_dict)
    # Convert DataFrame to CSV
    csv_io = io.StringIO()
    df.to_csv(csv_io, index=False)
    csv_string = csv_io.getvalue()
    return csv_string

def execute_queries(query_string, mydb):
    queries = query_string.split(';')
    cursor = mydb.cursor()
    result_dfs = []  # Create an empty list to store DataFrames

    for query in queries:
        query = query.strip()  # Remove leading/trailing white space
        if query:  # Ensure query is not empty
            try:
                cursor.execute(query)
                result = cursor.fetchall()
                if result:
                    csv_string = query_to_df(result, cursor)
                    # Append this df to result_dfs
                    result_dfs.append(pd.read_csv(io.StringIO(csv_string)))
            except Exception as e:
                print(f"Error occurred: {e}")
                raise e  # re-raise the exception after logging it

    if result_dfs:
        # Combine all DataFrames in result_dfs
        result_df = pd.concat(result_dfs, ignore_index=True)
        # Convert result_df to CSV
        csv_io = io.StringIO()
        result_df.to_csv(csv_io, index=False)
        csv_string = csv_io.getvalue()
        print(f"csv_string: {csv_string}")
        return csv_string
    else:
        return "No data returned from query."




