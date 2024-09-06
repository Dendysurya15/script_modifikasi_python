import pymssql

# Connection details
server = '10.9.115.115\\PKSNBMSTAGING2'
database = 'PKSNBMSTAGING2'
username = 'userstaging'
password = 'Qwerty@123'

# Attempt to connect to the database
try:
    connection = pymssql.connect(server=server, user=username, password=password, database=database)
    cursor = connection.cursor()
    cursor.execute('SELECT 1')  # Simple query to test the connection
    row = cursor.fetchone()
    if row:
        print("Connection successful!")
    connection.close()
except pymssql.InterfaceError as e:
    print(f"Interface error: {e}")
except pymssql.DatabaseError as e:
    print(f"Database error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
