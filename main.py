import machine
import network
import time
import json
import dht
import umqtt.simple as mqtt

#Funcion vinculada al evento de nuevo mensaje en topico suscrito
def callBack(topic, msg):
    fan = machine.Pin(12, machine.Pin.OUT, machine.Pin.PULL_UP)
    dat = json.dumps(msg).split(':')[-1].split('"')[1]
    print(dat)
    if str(dat) == "OFF":
        fan.value(1)
    elif str(dat) == "ON":
        fan.value(0)
    else:
        fan.value(1)


#Parametros y etiquetas
SSID = 'SSID'
password = 'PASSWORD'
serverAddr = "192.168.10.102"
serverPort = 1883
clientName = 'Bug_01'
pubTopic = clientName + '/Report'
subTopic = clientName + '/Execute'
lastPub = time.ticks_ms() 
pubInterval = 4000
sensor = dht.DHT11(machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP))


#Inicializacion de WiFi
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.connect(SSID, password)
while not sta.isconnected():
    pass

#Inicializacion del cliente MQTT
mqttClient = mqtt.MQTTClient(clientName, serverAddr, serverPort)
mqttClient.connect()

mqttClient.set_callback(callBack)
mqttClient.subscribe(subTopic)


#Programa principal
while True:
    #Revisa por mensajes pendientes
    mqttClient.check_msg()

    #Evalua si ha transcurrido el sampling time, en caso de haberlo hecho, actualiza el tiempo de ultima publicacion
    if time.ticks_ms() - lastPub >= pubInterval:
        lastPub = time.ticks_ms()

        #Solicita una medicion al DHT11, estructura la informacion en formato json y la publica al topico
        try:
            sensor.measure()
            payload = {
                'temp': sensor.temperature(),
                'humd': sensor.humidity(),
            }
            mqttClient.publish(pubTopic, json.dumps(payload))
        except:
            pass