from db_details import create_conn
from decimal import Decimal # Use it when calculating total_price to avoid errors
from datetime import datetime, timedelta
import schedule
import time
import mysql.connector

def get_order_status(order_id: int):
    conn = create_conn()
    cursor = conn.cursor(buffered=True)

    try:
        query = "SELECT status FROM orders WHERE order_id = %s"
        cursor.execute(query, (order_id,))
        result = cursor.fetchone()
        print(f"Result: {result}")

        if result is not None:
            return result[0]
        else:
            return None

    finally:
        # Close the cursor and connection in the 'finally' block
        cursor.close()
        conn.close()

    
def get_next_id(table):
    conn = create_conn()
    cursor = conn.cursor(buffered=True)
    if table == "orders":
        query = "SELECT MAX(order_id) FROM orders"
    else:
        query = "SELECT MAX(pizza_id) FROM pizzas"
    cursor.execute(query)

    # Get result
    result = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    if result is None:
        return 1
    else:
        return result + 1

def insert_order_item(pizza_type, quantity, size, order_id, transit_time):
    conn = create_conn()
    cursor = conn.cursor(buffered=True)
    query = ("SELECT pizza_id, price, preparation_time FROM pizzas WHERE pizza_type = %s")
    cursor.execute(query, (pizza_type,))
    result = cursor.fetchone()

    if result:
        pizza_id = result[0]
        price = result[1]

        if size == "small":
            price -= 300
        elif size == "medium":
            price -= 150
        
        preparation_time = result[2] * quantity # Multiply to get total time it will take to make 1 pizza type of the quantity provided
        total_price = Decimal(quantity) * price

        insert_order_query = ("INSERT INTO orders (order_id, pizza_id, quantity, size, total_price, preparation_time, transit_time) VALUES (%s, %s, %s, %s, %s, %s, %s)") 
        try:
            cursor.execute(insert_order_query, (order_id, pizza_id, quantity, size, total_price, preparation_time, transit_time))
            conn.commit()
            print("Insert successful!")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            conn.rollback()
            return -1
    else:
        print(f"No pizza found of type: {pizza_type}")

    cursor.close()
    conn.close()

def get_order_total_price(order_id):
    conn = create_conn()
    cursor = conn.cursor(buffered=True)
    get_total_price_sum_query = "SELECT SUM(total_price) FROM orders WHERE order_id = %s"
    cursor.execute(get_total_price_sum_query, (order_id,))
    total_price_sum_result = cursor.fetchone()
    cursor.close()
    conn.close()

    if total_price_sum_result:
        total_price_sum = total_price_sum_result[0]
        print(f"Sum of total prices for Order ID {order_id}: {total_price_sum}")
        return total_price_sum
    else:
        return -1

def get_transit_time(location: str):
    conn = create_conn()
    cursor = conn.cursor(buffered=True)

    transit_time_query = "SELECT time_taken FROM locations WHERE location_name = %s"

    cursor.execute(transit_time_query, (location,))
    time_taken = cursor.fetchone()[0]
    cursor.close()
    conn.close()

    return time_taken

def get_total_time(order_id):
    conn = create_conn()
    cursor = conn.cursor(buffered=True)

    # Get orders that are still in progress
    cursor.execute("SELECT transit_time, preparation_time FROM orders WHERE order_id = %s", (order_id,))
    orders = cursor.fetchall()
    transit_time = orders[0][0]
    total_prep_time = 0
    for order in orders:
        # Get the total preparation time
        total_prep_time += order[1]

    fully_delivered = transit_time + total_prep_time
    print(f"Transit: {transit_time} || Prep: {total_prep_time} || Delivered: {fully_delivered}")

    cursor.close()
    conn.close()
    return fully_delivered

# Change to minutes later
def update_order_status():
    conn = create_conn()
    cursor = conn.cursor(buffered=True)

    # Get orders that are still in progress
    cursor.execute("SELECT order_id, order_time, preparation_time, transit_time FROM orders WHERE status = 'Being Prepared'")
    orders = cursor.fetchall()

    all_orders = {}

    for order_id, order_time, preparation_time, transit_time in orders:
        if order_id not in all_orders:
            all_orders[order_id] = {
                "order_time" : order_time,
                "prep_time" : preparation_time,
                "transit_time" : transit_time
            }
        else:
            old_prep_time = all_orders[order_id]["prep_time"]
            new_prep_time = old_prep_time + preparation_time
            all_orders[order_id]["prep_time"] = new_prep_time

    for order_id, order_info in all_orders.items():
        time_at_transit = order_info["order_time"] + timedelta(seconds=order_info["prep_time"])
        time_fully_delivered = time_at_transit + timedelta(seconds=order_info["transit_time"])
        current_time = datetime.now()
        print(f"Transit: {time_at_transit} || Delivered: {time_fully_delivered} || Current Time: {current_time}")

        # Check if the current time has passed the expected completion time
        if current_time >= time_at_transit and current_time < time_fully_delivered:
            # Update the status to 'In Transit'
            cursor.execute("UPDATE orders SET status = 'In Transit' WHERE order_id = %s", (order_id,))
            conn.commit()
        elif current_time > time_fully_delivered:
            # Update the status to 'Delivered'
            cursor.execute("UPDATE orders SET status = 'Delivered' WHERE order_id = %s", (order_id,))
            conn.commit()

    cursor.close()
    conn.close()
