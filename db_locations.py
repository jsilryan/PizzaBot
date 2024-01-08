from db_details import *

locations = [
    {"location_name": "CBD", "time_taken": 0},
    {"location_name": "Westlands", "time_taken": 15},  
    {"location_name": "Langata", "time_taken": 20},  
    {"location_name": "Kasarani", "time_taken": 25},  
    {"location_name": "South B", "time_taken": 10},  
    {"location_name": "South C", "time_taken": 12},  
    {"location_name": "Karen", "time_taken": 30},  
]

# Create a cursor
conn = create_conn()
cursor = conn.cursor()

for location in locations:
    cursor.execute("SELECT COUNT(*) FROM locations WHERE location_name = %s", (location["location_name"],))
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.execute(
            "INSERT INTO locations (location_name, time_taken) VALUES (%s, %s)",
            (location["location_name"], location["time_taken"])
        )
        print(f"Inserted: {location["location_name"]} - {location["time_taken"]} minutes")
    else:
        print(f"Skipped: {location["location_name"]} - Already exists in the database")

# Commit the changes and close the cursor and connection
conn.commit()
cursor.close()
conn.close()

print("Locations' insertion process completed!")