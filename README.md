# PizzaBot
- Make sure mysql, python and pip is installed
  
## Steps to ensure PizzaBot works
1. Open terminal and go to the folder you downloaded it in.
2. pip install -r requirements.txt
3. Run:
    a. python create_db.py
    b. python create_tables.py
    c. python db_pizzas.py
    d. python db_locations.py
    e. uvicorn main:app --reload
4. In a different terminal, run:
    - python scheduler.py
5. In a different terminal run -> Do this if there is an error in the chatbot after entering the location:
    - .\ngrok http 8000
    - get the forwarding link and put it in the fulfillment url part in Dialogflow
6. In a different terminal, run:
    - cd frontend
    - npm start

## Extras
- In case ngrok doesn't work, install it by going to ngrok.com, follow the steps and replace the ngrok.exe with the new one you have downloaded. 
