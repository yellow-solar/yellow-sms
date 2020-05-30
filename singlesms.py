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

# USERNAME = "atyellowuganda"
# API_KEY = "ac2d7a5054b5f4e3e25fda1f2634ce80fb9bb81386ac06fe9c9c3743e2517f80"
# SENDER = None

USERNAME = "newshirt"
API_KEY = "9b0e40cf471546d8b3564cd685ad74f1a3490c9702947c5633dd84d774b37868"
SENDER = "YELLOW"

africastalking.initialize(USERNAME, API_KEY)

sms = africastalking.SMS
response = sms.send(
        message = "Hi Cy, Please confirm this message with Ben", 
        recipients = ['+265999576414'],
        sender_id = SENDER,
        )

print(response)

