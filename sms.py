""" Send SMSs using AfricasTalking API and project key

    Functions to accept a csv upload or an already existing dataset
        Database tasks
        - store sms header
        - store sms lines
        
""" 

# Standard library
import json
import os

# Third party libraries
from flask import Flask, request, render_template
from flask_restful import Resource, Api
import pandas as pd
import numpy as np
# africas talking API client
import africastalking

### Functions

def commListImport(batchname, personalised=False):
    """ Import a csv to be used to send sms list """

    # Import data
    df = pd.read_csv(batchname+'.csv')
    #lower case column names
    df.columns = [col.lower() for col in df.columns.values]
    
    # Check for necessary columns of batch list
    # Basic set - angaza_id, first name, number
    if all([(x in df.columns) for x in ['id','name','number']]):
        # if personalised have to check more:
        pass
    else:
        raise KeyError("Missing columns  id, name or number in csv")

    # only sms with first name
    df['provided_name'] = df['name']
    df['name'] = df['name'].apply(lambda x: str(x).split(' ')[0]) 

    return(df)

def bulkSMSfromDF(df, msg_str, batchname, delete = False):
    """ Send a bulk sms from a dataframe input, same msg to all recipients """

    # Check the length and confirm with user
    if len(msg_str) > 160:
        confirmation = input("Msg is more than 1 sms, please confirm send: ")
        if confirmation[0].lower()!='y':
            return(print('stopping.'))

    # Make sure the phone number is just numbers and correct length - if not force fail
    df['number'] = df['number'].replace('[^0-9]','',regex=True)
    df['valid_number'] = df['number'].apply(lambda x: len(str(x)) == 12)
    
    # Turn to string and add the plus
    df['number'] = df['number'].apply(lambda x: "+" + str(x)) 

    # Send messages via AfricasTalking - only ones ith valid number
    response = sms.send(
        message = msg_str, 
        recipients = df.loc[df['valid_number'],'number'].values.tolist(),
        sender_id = SENDER_ID)['SMSMessageData']
    print("Messages sent")

    # Store the json result 
    file_method = 'w'
    if f'{batchname}.json' in os.listdir(RESPONSES_PATH):
        file_method = 'a'
        print("WARNING: batch already ran, appending results, will corrupt json")
    with open(f'{RESPONSES_PATH}/{batchname}.json', file_method) as outfile:
        json.dump(response, outfile)

    # Process the results - save message code,status and ID
    # Create recipient columns is df
    df['summary'] = response['Message']
    df['message_parts'] = np.NaN
    df['status_code'] = np.NaN
    df['cost'] = np.NaN
    df['status'] = np.NaN
    df['message_id'] = np.NaN
    df['message'] = msg_str
    # for each recipient, add relevant field to relevant list
    try:
        for recipient in response['Recipients']:
            row = df[df['number'] == recipient['number']].index
            df.loc[row, 'message_parts'] = recipient['messageParts']
            df.loc[row, 'status_code'] = recipient['statusCode']
            df.loc[row, 'cost'] = recipient['cost']
            df.loc[row, 'status'] = recipient['status']
            df.loc[row, 'message_id'] = recipient['messageId']
    except:
        print('Header not found')

    # Store processed df with response fields output
    df.to_csv(f"{PROCESSED_PATH}/{batchname}.csv", index=False)

    # Remove the input file if requested
    if delete:
        os.remove(batchname+'.csv')

    # Store in SQL - when using WebApp


# Need to figure out which part is personalised
# Client name, Agent name, Agent number etc.
# then run the asynchronous API in order to call each individual 
# # or synchronous but it'll take long neh? 
#      response = sms.send(
#         message = #personalised message, 
#         recipients = df_send['phone'].values.tolist(), 
#         sender_id = SENDER_ID)

# else:
#     raise Exception
# ----


if __name__ == '__main__':
    # Depending on environment - send to sandbox or live account, API key
    ### User input for file name
    env = input("Input 'd' for test or 'p' for live: ")
    batchname = input("Input batch name (reference to csv name): ") 

    if env == 'p':
        config = 'africastalking'
        PROCESSED_PATH = 'results'
        RESPONSES_PATH = 'raw-responses/prod'
    else:
        config = 'africastalkingsandbox'
        PROCESSED_PATH='tested'
        RESPONSES_PATH = 'raw-responses/test'
        # File paths
    
    # Import config for 
    with open('config.json', 'r') as f:
        cfg = json.load(f)[config] 

    # Initialize SDK with Yellow config.json
    USERNAME = cfg['user']
    API_KEY = cfg['authtoken']    
    SENDER_ID = cfg['senderID']
    africastalking.initialize(USERNAME, API_KEY)

    # File import
    df = commListImport(batchname=batchname)
    # df.to_csv('test_output.csv')

    # SMS send
    # Initialize a service e.g. SMS
    sms = africastalking.SMS
    bulkSMSfromDF(df,
        msg_str = input("Enter bulk message: "),
        batchname=batchname,
        delete=False
    )
    # print(df.head())