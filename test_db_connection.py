# test_db_connection.py

import pyodbc

def get_db_connection():
    conn = pyodbc.connect(
        "Driver={ODBC Driver 17 for SQL Server};"
        r"Server=DESKTOP-OLUTMPH\SQLSERVER2024;"
        "Database=PatientDB;"
        "Trusted_Connection=yes;"
    )
    return conn

# Test the connection and insert
try:
    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert dummy test
    cursor.execute("INSERT INTO Patients (Name, Age) VALUES (?, ?)", ("TestUser", 99))
    conn.commit()

    # Fetch data
    cursor.execute("SELECT * FROM Patients")
    rows = cursor.fetchall()
    for row in rows:
        print(row)

    cursor.close()
    conn.close()

except Exception as e:
    print("❌ Error connecting to DB or inserting data:", e)
