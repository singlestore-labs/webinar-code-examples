import uvicorn
from fastapi import FastAPI, Depends, Request
import logging
import sys
from sqlalchemy import *
from dotenv import load_dotenv
import os
from pydantic import BaseModel
from datetime import datetime
import openai

class Action(BaseModel):
    anonymousId: str = None
    channel: str
    context: dict
    event: str
    integrations: dict
    messageId: str
    originalTimestamp: str
    projectId: str
    properties: dict
    receivedAt: str
    sentAt: str
    timestamp: str
    type: str
    userId: str
    version: str
    writeKey: str

class Customer(BaseModel):
    anonymousId: str = None
    channel: str
    context: dict
    integrations: dict
    messageId: str
    originalTimestamp: str
    projectId: str
    receivedAt: str
    sentAt: str
    timestamp: str
    traits: dict
    type: str
    userId: str
    version: str
    writeKey: str

logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

load_dotenv()
s2_user = os.getenv('S2_USER')
s2_pass = os.getenv('S2_PASS')
s2_host = os.getenv('S2_HOST')
print(s2_host)
model_id = 'text-embedding-ada-002'
openai.api_key = os.getenv('OPENAI_API_KEY')

connection_url = "mysql://{}:{}@{}:3306/plg_data".format(s2_user,s2_pass,s2_host)
conn = create_engine(connection_url)

app = FastAPI()

def create_embeddings(content,model_id):
    try:
        response = openai.Embedding.create(input=str(content),model=model_id)

        embedding = response['data'][0]['embedding']
        tokens = response['usage']['total_tokens']
        status = 'success'
        return embedding,tokens,status
    except Exception as e:
        print(e)
        embedding = ''
        tokens = 0
        status = 'failed'
        return embedding,tokens,status

def format_timestamp(date_time_string):
    try:
        # Attempt to parse with 'Z' format
        parsed_datetime = datetime.strptime(date_time_string, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        try:
            # If parsing with 'Z' format fails, attempt to parse with timezone offset
            parsed_datetime = datetime.fromisoformat(date_time_string)
        except ValueError:
            raise ValueError("Invalid date-time format")

    # Format the parsed datetime as a string in the required format for SQL
    formatted_datetime = parsed_datetime.strftime("%Y-%m-%d %H:%M:%S.%f")
    return formatted_datetime

def write_action_to_db(payload):
    event = payload['event']
    seg_message_id = payload['messageId']
    seg_original_timestamp = format_timestamp(payload['originalTimestamp'])
    seg_received_at = format_timestamp(payload['receivedAt'])
    seg_sent_at = format_timestamp(payload['sentAt'])
    seg_timestamp = format_timestamp(payload['timestamp'])
    user_id = payload['userId']

    new_payload = {}
    new_payload['event'] = event
    new_payload['seg_message_id'] = seg_message_id
    new_payload['seg_original_timestamp'] = seg_original_timestamp
    new_payload['seg_received_at'] = seg_received_at
    new_payload['seg_sent_at'] = seg_sent_at
    new_payload['seg_timestamp'] = seg_timestamp
    new_payload['user_id'] = user_id

    logger.info("Creating Embedding for {}".format(new_payload))
    embedding,tokens,status = create_embeddings(new_payload,model_id)
    logger.info("Writing to DB")
    try:
        with conn.connect() as connection:
            connection.execute(text("INSERT INTO \
                        actions (event, seg_message_id, seg_original_timestamp, \
                        seg_received_at, seg_sent_at, seg_timestamp, user_id, embedding) \
                        VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', JSON_ARRAY_PACK('{}'))".format(event, seg_message_id, seg_original_timestamp, seg_received_at, seg_sent_at, seg_timestamp, user_id, str(embedding))))
            connection.commit()
            return {"status": "successfully wrote action to db"}
    except Exception as e:
        logger.error(e)

def write_customer_to_db(payload):

    cust_created_timestamp = format_timestamp(payload['traits']['created_at'])
    cust_email = payload['traits']['email']
    cust_first_name = payload['traits']['firstName']
    cust_last_name = payload['traits']['lastName']
    cust_phone = payload['traits']['phone']
    cust_user_id = payload['userId']
    seg_message_id = payload['messageId']
    seg_received_at = format_timestamp(payload['receivedAt'])
    seg_sent_at = format_timestamp(payload['sentAt'])
    seg_timestamp = format_timestamp(payload['timestamp'])

    new_payload = {}
    new_payload['cust_created_timestamp'] = cust_created_timestamp
    new_payload['cust_email'] = cust_email
    new_payload['cust_first_name'] = cust_first_name
    new_payload['cust_last_name'] = cust_last_name
    new_payload['cust_phone'] = cust_phone
    new_payload['cust_user_id'] = cust_user_id
    new_payload['seg_message_id'] = seg_message_id
    new_payload['seg_received_at'] = seg_received_at
    new_payload['seg_sent_at'] = seg_sent_at
    new_payload['seg_timestamp'] = seg_timestamp

    logger.info("Creating Embedding for {}".format(new_payload))
    embedding,tokens,status = create_embeddings(new_payload,model_id)
    logger.info("Writing customer to DB")
    try:
        with conn.connect() as connection:
            connection.execute(text("INSERT INTO \
                        customers (created_at, email, first_name, \
                        last_name, phone, user_id, seg_message_id, \
                        seg_received_at, seg_sent_at, seg_timestamp, embedding) \
                        VALUES ('{}', '{}', '{}', '{}', '{}', '{}', \
                    '{}', '{}', '{}', '{}', JSON_ARRAY_PACK('{}'))".format(cust_created_timestamp, cust_email, cust_first_name, cust_last_name, cust_phone, cust_user_id, seg_message_id, seg_received_at, seg_sent_at, seg_timestamp, str(embedding))))
            connection.commit()
            return {"status": "successfully wrote customer to db"}
    except Exception as e:
        logger.error(e)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/action")
async def webhook(action: Action):
    payload = action.dict()
    logger.info("Writing to DB")
    write_action_to_db(payload)
    logger.info("Received action: {}/{}".format(action.event,action.userId))
    return {"status": "ok"}

@app.post("/identify")
async def identify(customer: Customer):
    payload = customer.dict()
    logger.info("Writing to DB")
    write_customer_to_db(payload)
    logger.info("Identified customer {} in database".format(customer.userId))
    return {"status": "okay"}

@app.post("/test")
async def get_body(request: Request):
    logger.info(await request.body())
    return {"status": "ok"}

if __name__ == "__main__":
    logger.info('Starting Server')
    uvicorn.run(app, host="0.0.0.0", port=5000)