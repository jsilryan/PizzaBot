# PizzaBot
- A chatbot for ordering pizzas made using Google Dialogflow, FastAPI and MySQL
- Make sure mysql, python and pip is installed

## Fork then Clone it
- Fork the repo
- From the forked repo, clone the repo -> git clone -- forked_repo.git --
- You can make changes
  - touch new_file.txt
  - git add .
  - git push origin
  
## Steps to ensure PizzaBot works
1. Open terminal and go to the folder you cloned it in.
2. pip install -r requirements.txt
3. Run:
    - python create_db.py
    - python create_tables.py
    - python db_pizzas.py
    - python db_locations.py
    - uvicorn main:app --reload
4. In a different terminal, run:
    - python scheduler.py
5. In a different terminal run -> Do this if there is an error in the chatbot after entering the location:
    - .\ngrok http 8000
    - get the forwarding link and put it in the fulfillment url part in Dialogflow
6. In a different terminal, run:
    - cd frontend
    - npm i lite-server
    - npm start

## Extras
- In case ngrok doesn't work, install it by going to ngrok.com, follow the steps and replace the ngrok.exe with the new one you have downloaded. 
