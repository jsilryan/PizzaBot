import mysql.connector

# Database connection parameters
MYSQL_USER = "root"
MYSQL_PASSWORD = ""
MYSQL_HOST = "localhost"

# Database name to be created
NEW_DATABASE = "pizzabot"

# Establish connection to MySQL server
connection = mysql.connector.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD
)

# Create a cursor to execute SQL statements
cursor = connection.cursor()

# SQL statement to check if the database exists
check_database_query = f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{NEW_DATABASE}'"

# Execute the SQL statement
cursor.execute(check_database_query)

# Fetch the result
result = cursor.fetchone()

# Check if the database exists
if result:
    print(f"The database '{NEW_DATABASE}' exists.")
else:
    # SQL statement to create a new database
    create_database_query = f"CREATE DATABASE IF NOT EXISTS {NEW_DATABASE}"
    print(f"The database '{NEW_DATABASE}' does not exist. Creating one...")

    # Execute the SQL statement
    cursor.execute(create_database_query)

# Commit the changes and close the cursor and connection
connection.commit()
cursor.close()
connection.close()

