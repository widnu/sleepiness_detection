# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 13:15:25 2020

@author: widnu
"""
from datetime import datetime
import time
import cv2
import matplotlib
import numpy
from matplotlib import pyplot as plt
import urllib3
import threading
import sys
import paho.mqtt.publish as publish
import pandas as pd
import os
import csv
import json

# ThingSpeak variables
channelId = '987232'
apiKey = 'MRZ2J95WLJB2SW4R'
baseURL = 'http://api.thingspeak.com/update?api_key=' + apiKey
bulkUpdateURL = 'http://api.thingspeak.com/channels/'+channelId+'/bulk_update.json'
http = urllib3.PoolManager()

# Eyes detection variables
eyesList = []
detectedSleepTime = 5
eyesListMaxLen = 12     # publish MQTT everytime we reach this max length
EYES_DATASET_CSV = "eyes_dataset.csv"

# MQTT message publisher variables
#MQTT_SERVER = "192.168.137.2"
MQTT_SERVER = "192.168.1.2"
MQTT_PATH = "wakeup_channel"

# http://api.thingspeak.com/update?api_key=MRZ2J95WLJB2SW4R?field1=100&field2=48&field3=29&field4=29
# send data to ThingSpeak
#def sendThingSpeakData(params):
#    requestUrl = baseURL + params
#    print("requestUrl = ", requestUrl)
#    resp = http.request('GET', requestUrl)
    
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

def publishMQTTWakeUpMsg():
    print("Send MQTT Message...")
    publish.single(MQTT_PATH, "Send MQTT wake-up message", hostname=MQTT_SERVER)

def writeDataToCsv(dataframe):
    if not os.path.isfile(EYES_DATASET_CSV):
        dataframe.to_csv(EYES_DATASET_CSV, index=False)
    else:
        dataframe.to_csv(EYES_DATASET_CSV, mode='a', header=False, index=False)
   
# multiple cascades: https://github.com/Itseez/opencv/tree/master/data/haarcascades

#https://github.com/Itseez/opencv/blob/master/data/haarcascades/haarcascade_frontalface_default.xml
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
#https://github.com/Itseez/opencv/blob/master/data/haarcascades/haarcascade_eye.xml
eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')

cap = cv2.VideoCapture(0)

while 1:
    ret, img = cap.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x,y,w,h) in faces:
        # detect face
        if(w > 0):
            cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = img[y:y+h, x:x+w]
        
        eyes = eye_cascade.detectMultiScale(roi_gray)
        for (ex,ey,ew,eh) in eyes:
            # detect eyes
            if(ew > 0):
                cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
                dateTimeObj = datetime.now()
                eyesList.append([4, ex, ey, ew, eh, str(dateTimeObj.date()), str(dateTimeObj.time())])
                    
        # cannot detect the eyes, set zero to the list
        if(len(eyes) == 0):
            dateTimeObj = datetime.now()
            eyesList.append([4, 0, 0, 0, 0, str(dateTimeObj.date()), str(dateTimeObj.time())])
            
#        print("face = ", faces, "eyes = ", eyes)
#        print("eyesList = ", eyesList)
        
        if(len(eyesList) >= eyesListMaxLen):
            df = pd.DataFrame(eyesList, columns=list('cxywhdt'))
            print(df)
            eyesList = []
            
            # publish mqtt message to wake the user up
            closedEyesCnt = df[df.x == 0].shape[0]
#            publishMQTTWakeUpMsg()
            if(closedEyesCnt >= 8):
                publishMQTTWakeUpMsg()
            
            writeDataToCsv(df)
            
        time.sleep(detectedSleepTime)

    cv2.imshow('img',img)
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break

cap.release()
cv2.destroyAllWindows()

sendThingSpeakBulk()