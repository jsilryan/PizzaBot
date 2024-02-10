from db_details import create_conn
from decimal import Decimal # Use it when calculating total_price to avoid errors
from datetime import datetime, timedelta
import mysql.connector
from helper_func import get_order_dict_string

def get_order_status(order_id: int):
    conn = create_conn()
    cursor = conn.cursor(buffered=True)

    pizzas = {}
    try:
        query = "SELECT pizza_id, size, quantity, total_price, status, full_order_id FROM orders WHERE order_id = %s"
        cursor.execute(query, (order_id,))
        result = cursor.fetchall()
        print(f"FOIQ: {result}")
        if result:
            full_order_id = result[0][5]
            print(f"Full Order ID: {full_order_id}")
            query_2 = "SELECT name, phone FROM full_orders WHERE full_order_id = %s"
            cursor.execute(query_2, (full_order_id,))
            result_2 = cursor.fetchone()
            name = result_2[0]
            phone = result_2[1]
            for row in result:
                pizza_id, size, quantity, total_price, status, full_order_id = row
                query_1 = "SELECT pizza_type FROM pizzas where pizza_id = %s"
                cursor.execute(query_1, (pizza_id,)) # Make sure when querying I put a ',' after if it is only 1 values eg (pizza_id,)
                result_1 = cursor.fetchone()
                pizza_type = result_1[0]
                pizzas[(pizza_type, size, quantity)] = status

            full_order = get_order_dict_string(pizzas, order_id, name, phone)

        if full_order is not None:
            print(f"Result: {full_order}")
            return full_order
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
    elif table == "pizzas":
        query = "SELECT MAX(pizza_id) FROM pizzas"
    elif table == "full_orders":
        query = "SELECT MAX(full_order_id) FROM full_orders"

    cursor.execute(query)

    # Get result
    result = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    if result is None:
        return 1
    else:
        return result + 1

def insert_order_item(pizza_type, quantity, size, order_id, transit_time, name, phone, location, full_order_id):
    conn = create_conn()
    cursor = conn.cursor(buffered=True)
    query = ("SELECT pizza_id, price, preparation_time FROM pizzas WHERE pizza_type = %s")
    cursor.execute(query, (pizza_type,))
    result = cursor.fetchone()

    query_1 = ("SELECT * from full_orders where full_order_id = %s")
    cursor.execute(query_1, (full_order_id,))
    result_1 = cursor.fetchone()

    if result_1 is None:
        insert_full_order_query = ("INSERT INTO full_orders (full_order_id, name, phone, location, total_amount) VALUES (%s, %s, %s, %s, %s)")
        try:
            cursor.execute(insert_full_order_query, (full_order_id, name, phone, location, 0))
            conn.commit()
            print("Insert Full Order successful!")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            conn.rollback() 
            return -1

    if result:
        pizza_id = result[0]
        price = result[1]

        if size == "small":
            price -= 300
        elif size == "medium":
            price -= 150
        
        preparation_time = result[2] * quantity # Multiply to get total time it will take to make 1 pizza type of the quantity provided
        total_price = Decimal(quantity) * price

        insert_order_query = ("INSERT INTO orders (order_id, pizza_id, quantity, size, total_price, preparation_time, transit_time, full_order_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)") 
        try:
            cursor.execute(insert_order_query, (order_id, pizza_id, quantity, size, total_price, preparation_time, transit_time, full_order_id))
            conn.commit()
            print("Insert Order successful!")
            return total_price
        
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


def insert_total_amount(total_amount:int, order_id: int):
    conn = create_conn()
    cursor = conn.cursor(buffered=True)

    try:
        query = "SELECT pizza_id, size, quantity, total_price, status, full_order_id FROM orders WHERE order_id = %s"
        cursor.execute(query, (order_id,))
        result = cursor.fetchall()

        if result:
            full_order_id = result[0][5]
            print(f"Full Order ID - Insert Totals: {full_order_id}")
            update_query = "UPDATE full_orders SET total_amount = %s WHERE full_order_id = %s"
            cursor.execute(update_query, (total_amount, full_order_id))
            conn.commit()
            print("Insert Total Price successful!")
        
    finally:
        # Close the cursor and connection in the 'finally' block
        cursor.close()
        conn.close()