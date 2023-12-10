import machine
import network
import time
import json
import dht
import umqtt.simple as mqtt

#Funcion vinculada al evento de nuevo mensaje en topico suscrito
def callBack(topic, msg):
    #Se descarga el json en un string, se limpia de todos los marcadores y se separa por cada elemento y se ejecuta la instruccion
    dat = json.dumps(msg).replace('{', '').replace('}', '').replace('"', '').replace(' ', '').replace('\\', '').split(",")
    for i in range(len(actuators)):
        if dat[i].split(":")[1] == "light":
            if str(dat[i].split(":")[-1]) == "OFF":
                actuators[i].value(1)
                currentState[dat[i].split(":")[-1]] =  "OFF"
            elif str(dat[i].split(":")[-1]) == "ON":
                actuators[i].value(0)
                currentState[dat[i].split(":")[-1]] =  "ON"
        if dat[i].split(":")[1] == "temp":
            if str(dat[i].split(":")[-1]) == "OFF":
                actuators[i].value(1)
                currentState[dat[i].split(":")[-1]] =  "OFF"
            elif str(dat[i].split(":")[-1]) == "ON":
                actuators[i].value(0)
                currentState[dat[i].split(":")[-1]] =  "ON"
        if dat[i].split(":")[1] == "hmdr":
            if str(dat[i].split(":")[-1]) == currentState['hmdr']:
                pass
            else:
                if str(dat[i].split(":")[-1]) == "OFF":
                    actuators[i].value(0)
                    time.sleep(0.03)
                    actuators[i].value(1)
                    time.sleep(0.03)
                    actuators[i].value(0)
                    time.sleep(0.03)
                    actuators[i].value(1)
                    time.sleep(0.03)
                    actuators[i].value(0)
                    time.sleep(0.03)
                    actuators[i].value(1)
                    time.sleep(0.03)                    
                    currentState[dat[i].split(":")[-1]] =  "OFF"
                elif str(dat[i].split(":")[-1]) == "ON":
                    actuators[i].value(0)
                    time.sleep(0.03)
                    actuators[i].value(1)
                    currentState[dat[i].split(":")[-1]] =  "ON"
    #Publica estado actual de los actuadores
    mqtt_client.publish(pubTopic, json.dumps(str(currentState)))
            


#Parametros y etiquetas
SSID = 'SSID'
password = 'PASSWORD'
serverAddr = "192.168.10.102"
serverPort = 1883
clientName = 'Host'
pubTopic = clientName + '/Report'
subTopic = clientName + '/Execute'
lastPub = time.ticks_ms() 
pubInterval = 4000
actuators = [machine.Pin(16, machine.Pin.OUT), machine.Pin(5, machine.Pin.OUT), machine.Pin(4, machine.Pin.OUT)]
currentState = {"light":"OFF", "temp":"OFF", "hmdr":"OFF"}


#Inicializacion de WiFi
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect(SSID, password)
while not sta_if.isconnected():
    pass

#Inicializacion del cliente MQTT
mqtt_client = mqtt.MQTTClient(clientName, serverAddr, serverPort)
mqtt_client.connect()

mqtt_client.set_callback(callBack)
mqtt_client.subscribe(subTopic)



#Programa principal
while True:
    mqtt_client.wait_msg()
