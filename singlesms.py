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

