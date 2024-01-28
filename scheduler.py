from db_details import create_conn
from datetime import datetime, timedelta
import schedule
import time

# Change to minutes later
def update_order_status():
    print("Updating order status...")
    conn = create_conn()
    cursor = conn.cursor(buffered=True)

    # Get orders that are still in progress
    cursor.execute("SELECT order_id, order_time, preparation_time, transit_time FROM orders WHERE status = 'Being Prepared' OR status = 'In Transit'")
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
            print("In Transit")
        elif current_time >= time_fully_delivered:
            # Update the status to 'Delivered'
            cursor.execute("UPDATE orders SET status = 'Delivered' WHERE order_id = %s", (order_id,))
            conn.commit()
            print("Delivered")

    cursor.close()
    conn.close()

# Schedule the update_order_status function to run every 30 seconds
schedule.every(30).seconds.do(update_order_status)

# Run the scheduler indefinitely
while True:
    schedule.run_pending()
    time.sleep(1)