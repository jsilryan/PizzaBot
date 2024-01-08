import re

def get_session_id(session_str: str):
    id = re.search(r"/sessions/(.*?)/contexts/", session_str)
    if id:
        extracted_string = id.group(1) # Group(0) -> whole match || Group(1) -> Only what is inside the brackets
        return extracted_string
    
    return ""

def get_pizza_dict_string(pizza_dict: dict):
    if len(pizza_dict) == 1:
        key, value = next(iter(pizza_dict.items()))
        return f"{int(value)} {key}"

    pizza_strings = [f"{int(value)} {key}" for key, value in pizza_dict.items()]
    return ", and ".join([", ".join(pizza_strings[:-1]), pizza_strings[-1]])

if __name__ == "__main__":
    food = {"bhajia" : 3, "burger" : 1}
    print(get_pizza_dict_string(food))
    # print(get_session_id("projects/pizza-chatbot-stwi/agent/sessions/b88aa043-a14a-d648-efb7-da33cf4e6c88/contexts/ongoing-order"))