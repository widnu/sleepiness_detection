# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 11:12:43 2020

@author: widnu
"""
import pyttsx3
import paho.mqtt.client as mqtt

#MQTT_SERVER = "192.168.1.5"
MQTT_SERVER = "192.168.137.2"
MQTT_PATH = "wakeup_channel"

def on_textToSpeech() :
    engine = pyttsx3.init()
    print("hellooooo")
    engine.say('Good morning Allen. Have you brushed your teeth?')
    engine.runAndWait()
    
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(MQTT_PATH)
    
# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    on_textToSpeech()
    # more callbacks, etc
    
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_SERVER, 1883, 60)
 
# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()

# ----------



        
