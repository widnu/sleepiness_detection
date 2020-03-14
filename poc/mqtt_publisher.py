import paho.mqtt.publish as publish
 
MQTT_SERVER = "192.168.1.2"
MQTT_PATH = "wakeup_channel"
 
publish.single(MQTT_PATH, "Please wake me up!", hostname=MQTT_SERVER)

