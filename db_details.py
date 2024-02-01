import mysql.connector
global conn

# Database connection parameters
MYSQL_USER = "root"
MYSQL_PASSWORD = ""
MYSQL_HOST = "localhost"
MYSQL_DATABASE = "pizzabot"
MYSQL_PORT = 3306 

def create_conn():
    # Establish database connection
    conn = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
        # port=MYSQL_PORT
    )
    return conn
