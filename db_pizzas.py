from db_details import create_conn

# Pizza data
pizza_types = [
    {"type": "Hawaiian", "size": "large", "estimated_price": 1000.00, "estimated_preparation_time": 5},
    {"type": "Chicken Mushroom", "size": "large", "estimated_price": 1200.00, "estimated_preparation_time": 6},
    {"type": "Chicken Periperi", "size": "large", "estimated_price": 1100.00, "estimated_preparation_time": 6},
    {"type": "Vegetarian", "size": "large", "estimated_price": 900.00, "estimated_preparation_time": 4},
    {"type": "Boerewors", "size": "large", "estimated_price": 1300.00, "estimated_preparation_time": 7},
]

# Create a cursor
conn = create_conn()
cursor = conn.cursor()
print("Connected")

# Insert pizza data into the database with a check
for pizza in pizza_types:
    # Check if the pizza type already exists
    cursor.execute("SELECT COUNT(*) FROM pizzas WHERE pizza_type = %s", (pizza["type"],))
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.execute(
            "INSERT INTO pizzas (pizza_type, price, preparation_time) VALUES (%s, %s, %s)",
            (pizza["type"], pizza["estimated_price"], pizza["estimated_preparation_time"])
        )
        print(f"Inserted: {pizza['type']} - {pizza['estimated_price']} Kshs - {pizza["estimated_preparation_time"]} minutes")
    else:
        print(f"Skipped: {pizza['type']} - Already exists in the database")

# Commit the changes and close the cursor and connection
conn.commit()
cursor.close()
conn.close()

print("Pizza types insertion process completed!")
