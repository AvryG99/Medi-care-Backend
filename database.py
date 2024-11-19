import pyodbc

def execute_query(code, db_config):
    exec_globals = {}
    exec_locals = {}
    exec(code, exec_globals, exec_locals)
    query_function = exec_locals.get('query_database')
    if not query_function:
        raise ValueError("The generated code does not define a 'query_database' function.")
    
    connection_string = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={db_config['server']};"
        f"DATABASE={db_config['database']};"
        f"Trusted_Connection=yes;"
    )
    return query_function(connection_string)

