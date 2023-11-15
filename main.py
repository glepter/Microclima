import machine
import network
import time
import json
import dht
import umqtt.simple as mqtt

def callBack(topic, msg):
    fan = machine.Pin(12, machine.Pin.OUT, machine.Pin.PULL_UP)
    dat = json.dumps(msg).split(':')[-1].split('"')[1]
    if str(dat) == "OFF":
        fan.value(1)
    elif str(dat) == "ON":
        fan.value(0)
    else:
        fan.value(1)
        print('Sintax Error_00')


# Replace these with your own Wi-Fi and MQTT broker settings
SSID = 'int-ms'
password = 'ConectatePuto-721'
serverAddr = "3.138.178.240"
serverPort = 1883
clientName = 'Bug_00'
pubTopic = clientName + '/Report'
subTopic = clientName + '/Execute'


# Initialize Wi-Fi
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect(SSID, password)
while not sta_if.isconnected():
    pass
print('Connected to ' + SSID)

# Initialize MQTT client
mqtt_client = mqtt.MQTTClient(clientName, serverAddr, serverPort)
mqtt_client.connect()
print('Connected to Broker at ' + serverAddr)

mqtt_client.set_callback(callBack)
mqtt_client.subscribe(subTopic)

sensor = dht.DHT11(machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP))

while True:
    
    
    mqtt_client.check_msg()
    try:
        sensor.measure()
    
    except:
        print('Failed attempt')
     
    # Create a JSON payload
    payload = {
        'temp': sensor.temperature(),
        'humd': sensor.humidity(),
    }
    # Publish the JSON payload to MQTT
    mqtt_client.publish(pubTopic, json.dumps(payload))
    print('\nData sent\n')

    time.sleep(4)
