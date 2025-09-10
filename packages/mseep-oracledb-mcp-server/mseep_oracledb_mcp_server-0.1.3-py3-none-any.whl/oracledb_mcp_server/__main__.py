import os
import sys
import argparse
import json

from oracledb_mcp_server.utils import setup_logging, create_db_connection
from dotenv import load_dotenv
from sqlalchemy import text
import pandas as pd
from mcp.server.fastmcp import FastMCP

# Global variables
DEBUG = True
COMMENT_DB_CONNECTION_STRING = None
DB_CONNECTION_STRING = None
TABLE_WHITE_LIST = None
TABLE_BLACK_LIST = None
COLUMN_WHITE_LIST = None
COLUMN_BLACK_LIST = None
QUERY_LIMIT_SIZE = 10
TAB_WHITE_LIST= None

logger = setup_logging(debug=DEBUG)
dev_db_connection = None
comment_db_connection = None
table_df = None
table_column_df = None

# FastMCP server
mcp = FastMCP("oracledb_mcp_server")

def load_environment_variables(env_path: str = None):
    """
    Load environment variables

    Args:
        env_path (str): Path to the .env file
    
    Returns:
        None
    """
    global DEBUG, COMMENT_DB_CONNECTION_STRING, DB_CONNECTION_STRING, TABLE_WHITE_LIST, TABLE_BLACK_LIST, COLUMN_WHITE_LIST, COLUMN_BLACK_LIST, QUERY_LIMIT_SIZE, logger
    
    logger.debug("Loading environment variables...")

    # Processing CLI input arguments
    parser = argparse.ArgumentParser(
        description="OracleDB MCP Server CLI v0.1.0",
        prog="oracledb_mcp_server"
    )
    parser.add_argument(
        "--env",
        help="Path to .env file to load environment variables from",
        default=None
    )
    args = parser.parse_args()
    
    # Load environment variables
    env_path = args.env if args.env else os.path.join(os.getcwd(), ".env")
    
    # Processing .env file
    try:
        if env_path and os.path.exists(env_path):
            load_dotenv(env_path)
            logger.debug(f"Environment variables loaded from: {env_path}")
        else:
            logger.debug("No .env file specified or file does not exist")

        # Updating logging level from environment variable
        DEBUG = os.getenv("DEBUG", "FALSE").lower() in ("true", "1", "yes")
        logger = setup_logging(debug=DEBUG)
        logger.debug("DEBUG: %s", DEBUG)

        # Updating OracleDB connection string from environment variable
        if not os.getenv("COMMENT_DB_CONNECTION_STRING"):
            logger.debug("COMMENT_DB_CONNECTION_STRING environment variable is not set")
        else:
            COMMENT_DB_CONNECTION_STRING = os.getenv("COMMENT_DB_CONNECTION_STRING")
            logger.debug("COMMENT_DB_CONNECTION_STRING: %s", COMMENT_DB_CONNECTION_STRING)

        # Updating OracleDB connection string from environment variable
        if not os.getenv("DB_CONNECTION_STRING"):
            logger.debug("DB_CONNECTION_STRING environment variable is not set")
        else:
            DB_CONNECTION_STRING = os.getenv("DB_CONNECTION_STRING")
            logger.debug("DB_CONNECTION_STRING: %s", DB_CONNECTION_STRING)

        # Updating white listed table names from environment variable
        if os.getenv("TABLE_WHITE_LIST"):
            TABLE_WHITE_LIST = os.getenv("TABLE_WHITE_LIST").split(",")
            logger.debug("TABLE_WHITE_LIST: %s", TABLE_WHITE_LIST)
        else:
            logger.debug("TABLE_WHITE_LIST not set, will not filter tables")

        # Updating white listed column names from environment variable
        if os.getenv("COLUMN_WHITE_LIST"):
            COLUMN_WHITE_LIST = os.getenv("COLUMN_WHITE_LIST").split(",")
            logger.debug("COLUMN_WHITE_LIST: %s", COLUMN_WHITE_LIST)
        else:
            logger.debug("COLUMN_WHITE_LIST not set, will not filter columns")
        
        # Updating query limit size from environment variable
        if os.getenv("QUERY_LIMIT_SIZE"):
            QUERY_LIMIT_SIZE = int(os.getenv("QUERY_LIMIT_SIZE"))
            logger.debug("QUERY_LIMIT_SIZE: %s", QUERY_LIMIT_SIZE)

    except Exception as e:
        logger.error(f"Error loading environment variables: {str(e)}")
        sys.exit(1)

@mcp.tool(name="get_table_details", description="Get table names and description of Oracle Database Tables")
def get_table_details():
    """
    Return table name and description of tables in the Oracle database.

    Args:
        None

    Returns:
        pd.DataFrame: DataFrame containing table names and their comments
    """ 

    global table_df,TAB_WHITE_LIST

    SQL_QUERY = "select TABLE_NAME,COMMENTS from USER_TAB_COMMENTS where TABLE_TYPE='TABLE'"

    if TABLE_WHITE_LIST is not None:
        TAB_WHITE_LIST="("
        for i, table in enumerate(TABLE_WHITE_LIST):
            TAB_WHITE_LIST += "'" + table + "'"
            if i < len(TABLE_WHITE_LIST) - 1:
                TAB_WHITE_LIST += ","
        TAB_WHITE_LIST=TAB_WHITE_LIST+")"
        SQL_QUERY = SQL_QUERY + "AND TABLE_NAME in "+TAB_WHITE_LIST

    # if TABLE_BLACK_LIST is not None:
    #     BLACK_LIST="("
    #     for i, table in enumerate(TABLE_BLACK_LIST):
    #         BLACK_LIST += "'" + table + "'"
    #         if i < len(TABLE_BLACK_LIST) - 1:
    #             BLACK_LIST += ","
    #     BLACK_LIST=BLACK_LIST+")"
    #     SQL_QUERY = SQL_QUERY + "AND TABLE_NAME not in "+BLACK_LIST

    logger.debug(f"Table SQL Query: {SQL_QUERY}")
    try:
        result = comment_db_connection.execute(text(SQL_QUERY))
        table_df = pd.DataFrame(result.fetchall(), columns=result.keys())
        # logger.debug(table_df)
        return table_df.to_json(orient='records', indent=2)
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        if comment_db_connection:
            comment_db_connection.close()
        sys.exit(1)

@mcp.tool(name="get_column_details", description="Returns table names, column name and column description of Oracle Database Table Columns")
def get_column_details():
    """
    Return table names, column names and descriptions of columns in the Oracle database.
    
    This function queries the database for column information from tables that have been
    previously retrieved by get_table_details(). It applies filtering based on
    COLUMN_WHITE_LIST and TABLE_WHITE_LIST global variables.
    
    Args:
        None
        
    Returns:
        pd.DataFrame: DataFrame containing table names, column names and their comments
    """
    global table_column_df

    # Ensure we have table information available before proceeding
    if table_df is None or table_df.empty:
        logger.error("Error loading table details")
        sys.exit(1)
    
    # Base SQL query to get column information from user_col_comments joined with user_tab_comments
    SQL_QUERY = """select col.table_name,
                        col.column_name,
                        col.comments
                    from user_col_comments col,
                        user_tab_comments tab
                    where tab.table_name = col.table_name
                    and tab.table_type = 'TABLE'"""
    WHITE_LIST = "("
    
    # Process column white list if provided
    if COLUMN_WHITE_LIST is not None:
        for i, column in enumerate(COLUMN_WHITE_LIST):
            logger.debug(f"Column - {column}")
            # Check if column is specified in table.column format
            if "." in column:
                # Split into table and column parts
                table_name, column_name = column.split(".", 1)
                logger.debug(f"table_name - {table_name}")
                # Verify this table is in our table list
                for table in table_df['table_name'].values:
                    logger.debug(f"table - {table}")
                    if table_name == table:
                        WHITE_LIST += "'" + column_name + "'"
                        # Add comma if not the last item
                        if i < len(COLUMN_WHITE_LIST) - 1:
                            WHITE_LIST += ","

    # Complete the white list parenthesis
    WHITE_LIST = WHITE_LIST + ")"
    
    # Append filtering conditions to the SQL query
    SQL_QUERY = SQL_QUERY + "AND col.COLUMN_NAME in " + WHITE_LIST + "AND col.TABLE_NAME in " + TAB_WHITE_LIST

    # Execute the query
    logger.debug(f"Columns SQL Query: {SQL_QUERY}")
    try:
        result = comment_db_connection.execute(text(SQL_QUERY))
        # Convert results to DataFrame
        table_column_df = pd.DataFrame(result.fetchall(), columns=result.keys())
        # logger.debug(table_column_df)
        return table_column_df.to_json(orient='records', indent=2)
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        if comment_db_connection:
            comment_db_connection.close()
        sys.exit(1)

@mcp.tool(name="execute_sql", description="Executes an SQL query on the Oracle Database")
def execute_sql(sqlString: str) -> str:
    """
    Execute a SQL query against the Oracle database.
    
    This function executes the provided SQL query using the established database 
    connection and returns the result as a JSON string. If an error occurs during
    execution, the function will log the error and return a JSON error message.
    
    Args:
        sqlString (str): The SQL query to execute
    
    Returns:
        str: JSON string containing either query results or error message
    """
    logger.debug(f"Execution SQL Query: {sqlString}")
    try:
        result = dev_db_connection.execute(text(sqlString))
        rows = result.fetchmany(QUERY_LIMIT_SIZE)
        df = pd.DataFrame(rows, columns=result.keys())
        return df.to_json(orient='records', indent=2)
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        error_msg = {"error": str(e), "status": "failed"}
        return pd.Series(error_msg).to_json(indent=2)

@mcp.tool(name="create_comment_db_connection", description="Connect to comments Oracle Database to get Oracle Schema Table and Columns Comments")
def create_comment_db_connection(commentDBConnectionString: str) -> str:
    """
    Connect to the Oracle database that contains table and column comments.

    This function establishes a connection to the database containing metadata
    information like table and column descriptions. It uses the provided connection
    string to create a connection to the comments database.
    
    Args:
        commentDBConnectionString (str): The database connection string for the comments database
        
    Returns:
        str: JSON string containing status message and result
    """

    global comment_db_connection, COMMENT_DB_CONNECTION_STRING
    COMMENT_DB_CONNECTION_STRING = commentDBConnectionString

    try:
        comment_db_connection = create_db_connection(COMMENT_DB_CONNECTION_STRING)
        result = {"status": "success", "message": "Connection to comments database established successfully"}
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Failed to connect to comments database: {str(e)}")
        error_result = {"status": "error", "message": str(e)}
        return json.dumps(error_result, indent=2)

@mcp.tool(name="connect_to_database", description="Connect to Oracle Database to run SQL Queries")
def connect_to_database(devDBConnectionString: str) -> str:
    """
    Connect to the Oracle database for executing SQL queries.

    This function establishes a connection to the database for running
    queries. It uses the provided connection string to create a database connection.
    
    Args:
        devDBConnectionString (str): The database connection string for the target database
        
    Returns:
        str: Success message if the connection was established
    """
    
    global dev_db_connection, DB_CONNECTION_STRING
    DB_CONNECTION_STRING = devDBConnectionString

    try:
        dev_db_connection = create_db_connection(DB_CONNECTION_STRING)
        return "Connection to database established successfully"
    except Exception as e:
        logger.error(f"Failed to connect to database: {str(e)}")
        return f"Error: {str(e)}"


def main():
    """
    Entry point for the oracledb_mcp_server.
    The server supports dynamic parsing of the OracleDB document and executes SQL calls with the appropriate request parameters.

    Configuration is controlled via environment variables:
    - DEBUG: Enable debug logging (optional default is False)
    - COMMENT_DB_CONNECTION_STRING: Oracle DB connection String for comments. (required)
    - DB_CONNECTION_STRING: Oracle DB connection String for execution of queries. (required)
    - TABLE_WHITE_LIST: White Listed table names in list format ["table1", "table2"] (optional)
    - COLUMN_WHITE_LIST: White Listed table-column names in list format ["table.column1", "table.column2"] (optional)
    - QUERY_LIMIT_SIZE: Default value is 10 records if not provided(optional default is 10)
    """
    try:
        global logger,comment_db_connection,dev_db_connection

        print("""
              #############################################
              #       OracleDB MCP SERVER CLI STARTING    #
              #############################################
              """)

        logger.info("Started OracleDB MCP Server")

        # Load environment variables
        load_environment_variables()

        # Connect to the OracleDB
        if COMMENT_DB_CONNECTION_STRING is not None:
            comment_db_connection = create_db_connection(COMMENT_DB_CONNECTION_STRING)
        
        if DB_CONNECTION_STRING is not None:
            dev_db_connection = create_db_connection(DB_CONNECTION_STRING)

        # Start the FastMCP server
        mcp.run()

    except KeyboardInterrupt:
        logger.info("Server shutting down gracefully...")
    except Exception as e:
        logger.error(f"Error starting the openapi_mcp_server: {str(e)}")
        sys.exit(1)
    finally:
        logger.info("Server stopped")

if __name__ == '__main__':
    main()
