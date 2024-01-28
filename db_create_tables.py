from db_details import *

delete_locations_table = """
drop table if exists locations;
"""

delete_orders_table = """
drop table if exists orders;
"""

delete_pizzas_table = """
drop table if exists pizzas;
"""

create_pizzas_table = """
CREATE TABLE IF NOT EXISTS pizzas (
    pizza_id INT NOT NULL AUTO_INCREMENT,
    pizza_type VARCHAR(50),
    price DECIMAL(10, 2),
    preparation_time INT, 
    PRIMARY KEY (pizza_id)
);
"""

create_orders_table = """
CREATE TABLE IF NOT EXISTS orders (
    order_id INT NOT NULL,
    pizza_id INT,
    quantity INT,
    size VARCHAR(30),
    total_price DECIMAL(10, 2),
    order_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    preparation_time INT, 
    transit_time INT,
    status ENUM('Being Prepared', 'In Transit', 'Delivered') DEFAULT 'Being Prepared',
    PRIMARY KEY (order_id, pizza_id, size),
    FOREIGN KEY (pizza_id) REFERENCES pizzas(pizza_id)
);
"""
create_locations_table = """
CREATE TABLE IF NOT EXISTS locations (
    location_id INT NOT NULL AUTO_INCREMENT,
    location_name VARCHAR(40),
    time_taken INT,
    PRIMARY KEY (location_id)
);
"""

# Create a cursor
conn = create_conn()
cursor = conn.cursor()

# Execute SQL statements to create tables
cursor.execute(delete_locations_table)
cursor.execute(delete_orders_table)
cursor.execute(delete_pizzas_table)
cursor.execute(create_pizzas_table)
cursor.execute(create_orders_table)
cursor.execute(create_locations_table)

# Commit the changes and close the cursor and connection
conn.commit()
cursor.close()
conn.close()

print("Tables created successfully!")