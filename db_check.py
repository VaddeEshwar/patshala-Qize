import pyodbc

conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=educational.database.windows.net,1433;"
    "DATABASE=twamdb;"
    "UID=potshala@educational;"
    "PWD=2he&tAmoKLTlwr7G+T*8;"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
)
print("✅ Connection successful!")
