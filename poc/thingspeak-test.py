from datetime import datetime
from matplotlib import pyplot as plt
import urllib3
import paho.mqtt.publish as publish
import pandas as pd

# ThingSpeak variables
channelId = '987232'
apiKey = 'MRZ2J95WLJB2SW4R'
baseURL = 'http://api.thingspeak.com/update?api_key=' + apiKey
bulkUpdateURL = 'http://api.thingspeak.com/channels/'+channelId+'/bulk_update.json'
http = urllib3.PoolManager()

EYES_DATASET_CSV = "eyes_dataset.csv"

def sendThingSpeakBulk():
    print("Send ThingSpeak bulk updates...")
    colnames=[
            'delta_t',
            'field1',
            'field2',
            'field3',
            'field4',
            'field5',
            'field6'
          ] 
    dfForJson = pd.read_csv(EYES_DATASET_CSV, names=colnames, header=None, skiprows=1)
    encodedBody = dfForJson.to_json(orient ='records')
    encodedBody = '{"write_api_key": "'+apiKey+'","updates": '+encodedBody+'}'
    
    print("bulkUpdateURL = ", bulkUpdateURL)
    print("encodedBody = ", encodedBody)
    http.urlopen('POST', bulkUpdateURL, headers={'Content-Type':'application/json'}, body=encodedBody).data
    print("Complete ThingSpeak bulk updates...")

sendThingSpeakBulk()

