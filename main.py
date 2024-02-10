from fastapi import FastAPI, BackgroundTasks
from fastapi import Request
from fastapi.responses import JSONResponse
from db_helper import * 
from helper_func import *
from asyncio import sleep

app = FastAPI()

inprogress_orders = {}
name_number = {}
locations_list = ["CBD", "Westlands", "Langata", "Kasarani", "South B", "South C", "Karen"]

@app.get("/")
async def root():
    return {"message" : "Hello World"}

@app.post("/")
async def handle_request(request: Request, tasks: BackgroundTasks):
    # tasks.add_task(schedule_task)
    
    # Get JSON data from the request
    payload = await request.json()

    # Get necessary info from the payload -> WebhookRequest from DialogFlow
    intent = payload['queryResult']['intent']['displayName']
    parameters = payload['queryResult']['parameters']
    output_contexts = payload['queryResult']['outputContexts']

    session_id = get_session_id(output_contexts[0]['name'])

    intent_handler_dict = {
        "TrackOrder - OngoingTracking" : track_order,
        "OrderAdd - OngoingOrder" : add_to_order,
        "OrderRemove - OngoingOrder": remove_from_order,
        "OrderComplete - OngoingOrder" : complete_order,
        "GetLocation - OngoingOrder" : add_name_and_number
    }

    text = intent_handler_dict[intent](parameters, session_id)
    return text

def add_to_order(parameters: dict, session_id: str):
    pizza_type = parameters['pizza-type']
    quantities = parameters['number']
    sizes = parameters['size']
    
    if len(pizza_type) != len(quantities):
        fulfillment_text = "I didn't get that correctly. Please specify the food items and their exact corresponding quantites eg 4 medium Pepperoni pizzas."

    elif len(pizza_type) != len(sizes):
        fulfillment_text = "I didn't get that correctly. Please specify each food item with its size eg 3 medium Margherita pizzas and 2 small Hawaiian pizzas."

    else:
        new_pizza_dict = dict(zip(zip(pizza_type, sizes), quantities))

        if session_id in inprogress_orders:
            current = inprogress_orders[session_id]
            for key, value in new_pizza_dict.items():
                if key in current:
                    # Key (pizza_type, size) already exists in current, update the quantity
                    current[key] = current[key] + value
                else:
                    # Key does not exist, add the key-value pair
                    current[key] = value
            # else:
            #     current.update(new_pizza_dict)
            inprogress_orders[session_id] = current
        else:
            inprogress_orders[session_id] = new_pizza_dict
        
        order_string = get_pizza_dict_string(inprogress_orders[session_id])
        fulfillment_text = f"Your order comprises: {order_string} pizzas. Would you need anything else added, removed or is the order perfect?"
       
    return JSONResponse(content={
        "fulfillmentText" : fulfillment_text
    })

def complete_order(parameters: dict, session_id: str):
    if session_id not in inprogress_orders:
        fulfillment_text = f"Sorry, I have trouble finding your order. Please place a new order."
    else:
        location = parameters['locations'][0]
        if location not in locations_list:
            fulfillment_text = f"{location} is not among the areas we deliver to. Choose one of these instead: {', '.join(locations_list[:-1])}, and {locations_list[-1]}"
        else:
            transit_time = get_transit_time(location)
            pizza_order = inprogress_orders[session_id] 
            order_string = get_pizza_dict_string(pizza_order)
            name = name_number['name']
            phone = name_number['phone']
            order_id = db_save(pizza_order, transit_time, name, phone, location)

            if order_id == -1:
                fulfillment_text = "Sorry, I couldn't place your order due to a backend error.\nPlease place a new order again."
            else:
                order_total = get_order_total_price(order_id)
                total_time = get_total_time(order_id)
                fulfillment_text = f"Splendid. {name_number['name']} your order has been placed and will be delivered to {location}.\nYour Order ID is # {order_id}.\n" \
                                    f"Your order comprises: {order_string} pizzas. " \
                                    f"Your Order Total = {order_total}. The delivery will take an estimate of {total_time} minutes. You can pay at the time of delivery!"
    
            # Remove the session_id from the inprogress_orders once completed
            del inprogress_orders[session_id]

    return JSONResponse(content={
        "fulfillmentText" : fulfillment_text
    })

def db_save(order: dict, transit_time, name, phone, location):
    next_order_id = get_next_id("orders")
    next_full_order_id = get_next_id("full_orders")
    total_amount = 0
    for (pizza_type, size), quantity in order.items():
        return_amount = insert_order_item(
            pizza_type,
            quantity,
            size,
            next_order_id,
            transit_time,
            name, 
            phone,
            location,
            next_full_order_id
        )
        if return_amount == -1:
            return -1
        else:
            total_amount += return_amount

    insert_total_amount(total_amount, next_order_id)
        
    return next_order_id


def track_order(parameters: dict, session_id: str):
    order_id = int(parameters['order_id'])
    order_status = get_order_status(order_id)
    fulfillment_text = ""

    if order_status:
        fulfillment_text = order_status
    else:
        fulfillment_text = f"No order found with Order ID: {order_id}"

    # Now 'fulfillment_text' contains all the information
    print(fulfillment_text)

    return JSONResponse(content={
        "fulfillmentText" : fulfillment_text
    })
 
def remove_from_order(parameters: dict, session_id: str):
    if session_id not in inprogress_orders:
        fulfillment_text = f"Sorry, I have trouble finding your order. Please place a new order."
    else:
        current = inprogress_orders[session_id] 
        pizza_items = parameters["pizza-type"]
        sizes = parameters["size"]
        quantity = parameters["number"]
        print(f'Quantity: {quantity}')

        if len(pizza_items) != len(quantity):
            fulfillment_text = "I didn't get that correctly. Please specify the food items and their exact corresponding quantites to be removed eg Remove 4 medium Pepperoni pizzas."

        elif len(pizza_items) != len(sizes):
            fulfillment_text = "I didn't get that correctly. Please specify the food item to be removed with its size eg Remove 3 medium Margherita pizzas and 2 small Hawaiian pizzas."

        else:
            removed_items = {}
            non_existing = []

            pizza_dict = {(pizza_items[i], sizes[i]): quantity[i] for i in range(len(pizza_items))}
            print(f'Pizza Dict: {pizza_dict}')
            print(f'Current : {current}')
            for key in pizza_dict:
                print(f'Key: {key}')
                if key not in current:
                    non_existing.append(key)
                else:
                    removed_items[key] = quantity[0]
                    print(f'Current[key] : {current[key]}')
                    current[key] = current[key] - quantity[0]
                    if current[key] == 0:
                        del current[key]

            if len(removed_items) > 0:
                if len(current.keys()) == 0:
                    fulfillment_text = "Your order is now empty!"
                else:
                    order_string = get_pizza_dict_string(inprogress_orders[session_id])
                    if len(removed_items) == 1:
                        for (pizza_type, size), quantity in removed_items.items():
                            fulfillment_text = f"Removed {quantity} {pizza_type} {size}. Your order comprises: {order_string}."
                    else:
                        removed_items_text = ", ".join(f"{size} {pizza}: {quantity}" for (pizza, size), quantity in removed_items.items())
                        last_comma_index = removed_items_text.rfind(',')
                        removed_items_text = f"{removed_items_text[:last_comma_index]}, and {removed_items_text[last_comma_index + 1:]}"
                        fulfillment_text = f"Removed {removed_items_text}. Your order comprises: {order_string}."

            if len(non_existing) > 0:
                if len(non_existing) == 1:
                    fulfillment_text = f"{non_existing[0][1].capitalize()} {non_existing[0][0]} is not part of your order!"
                else:
                    fulfillment_text = f"{',  '.join(non_existing[:-1])}, and {non_existing[-1]} are not in your order!"            
            else:
                statement = get_pizza_dict_string(current)
                fulfillment_text = f"Your order is left with the following: {statement}. Do you want to add or remove any other pizza, or should I place the order?"

    return JSONResponse(content={
        "fulfillmentText" : fulfillment_text
    })


def add_name_and_number(parameters: dict, session_id: str):
    if session_id not in inprogress_orders:
        fulfillment_text = f"Sorry, I have trouble finding your order. Please place a new order."
    else:
        name = parameters["given-name"]
        phone = parameters["phone-number"]
        if not name:
            fulfillment_text = f"Please enter your name."
        elif not phone:
            fulfillment_text = f"Enter a valid phone numer."
        else:
            name_number["name"] = name
            name_number["phone"] = phone
            fulfillment_text = f"Name: {name_number['name']}, Phone Number: {name_number['phone']}. To which location would you like the delivery to be made?" \
                                " Please choose from the following options: CBD, Westlands, Langata, Kasarani, South B, South C, or Karen."

    return JSONResponse(content={
        "fulfillmentText" : fulfillment_text
    })
