# dg_connection.py

# Importing the pyodbc library to connect Python with a SQL Server database using ODBC
import pyodbc

# Function to establish and return a database connection
def get_db_connection():
    # Connecting to the SQL Server using ODBC Driver 17
    # Replace the Server, Database, or Driver as needed for your setup
    conn = pyodbc.connect(
        "Driver={ODBC Driver 17 for SQL Server};"         # Specifies the ODBC driver for SQL Server
        r"Server=DESKTOP-OLUTMPH\SQLSERVER2024;"          # Server name and SQL Server instance (raw string to handle backslash)
        "Database=PatientDB;"                             # Name of the target database
        "Trusted_Connection=yes;"                         # Uses Windows authentication for the connection
    )
    return conn  # Return the connection object to be used elsewhere in the app
