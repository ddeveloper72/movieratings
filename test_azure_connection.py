import pyodbc
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

server = os.getenv('AZURE_SQL_HOST')
database = os.getenv('AZURE_SQL_NAME')
username = os.getenv('AZURE_SQL_USER')
password = os.getenv('AZURE_SQL_PASSWORD')

print(f'Server: {server}')
print(f'Database: {database}')
print(f'Username: {username}')
print(f'Password: {"***" if password else "Not set"}')
print()

# Try multiple connection string formats
formats = [
    # Format 1: Simple format
    f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}',
    # Format 2: With port
    f'DRIVER={{SQL Server}};SERVER={server},1433;DATABASE={database};UID={username};PWD={password}',
    # Format 3: With tcp: prefix
    f'DRIVER={{SQL Server}};SERVER=tcp:{server},1433;DATABASE={database};UID={username};PWD={password}',
]

connection_successful = False
for i, conn_str in enumerate(formats, 1):
    print(f'\n--- Attempt {i} ---')
    print(f'Format: {conn_str.replace(password, "***")}')
    try:
        conn = pyodbc.connect(conn_str, timeout=10)
        print('✅ Connection successful!')
    
        # Test query
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION")
        row = cursor.fetchone()
        print(f'SQL Server version: {row[0][:50]}...')
        
        cursor.close()
        conn.close()
        print('\n✅ Azure SQL Database connection is working correctly!')
        connection_successful = True
        break
        
    except Exception as e:
        print(f'❌ Connection failed: {e}')
        continue

if not connection_successful:
    print('\n❌ All connection attempts failed.')
    print('\nTroubleshooting:')
    print('1. Check that your Azure SQL firewall allows your IP address')
    print('2. Verify your credentials in the .env file')
    print('3. Ensure the database exists and is running')
    print('4. Try resetting the password in Azure Portal')
