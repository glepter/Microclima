import tkinter as tk
from tkinter import ttk
import paho.mqtt.client as mqtt
from pyowm.owm import OWM
from pyowm.utils.config import get_default_config_for_subscription_type
import json

#Se declara la clase
class MyGUI:
    def light(self, event):
        if self.actuatorState[0] == 'OFF':
            self.mqttClient.publish('Host/Execute', "light: ON")
        elif self.actuatorState[0] == 'ON':
            self.mqttClient.publish('Host/Execute', "light: OFF")

    def temp(self, event):
        if self.actuatorState[1] == 'OFF':
            self.mqttClient.publish('Host/Execute', "temp: ON")
        elif self.actuatorState[1] == 'ON':
            self.mqttClient.publish('Host/Execute', "temp: OFF")

    def hmdr(self, event):
        if self.actuatorState[2] == 'OFF':
            self.mqttClient.publish('Host/Execute', "hmdr: ON")
        elif self.actuatorState[2] == 'ON':
            self.mqttClient.publish('Host/Execute', "hmdr: OFF")

    #Funcion vinculada al evento de nuevo mensaje en topico suscrito
    def on_message(self, mqttClient, userdata, msg):        
        #Discriminacion por topico
        print(msg.payload)
        if msg.topic == 'Bug_00/Report':
            self.sensorData1.insert(0, msg.payload.decode("utf-8"))
            if len(self.sensorData1) > 10:
                self.sensorData1.pop(-1)
            self.updateData(self.humListbox_1, self.tempListbox_1, self.sensorData1)
        elif msg.topic == 'Bug_01/Report':
            self.sensorData2.insert(0, msg.payload.decode("utf-8"))
            if len(self.sensorData2) > 10:
                self.sensorData2.pop(-1)
            self.updateData(self.humListbox_2, self.tempListbox_2, self.sensorData2)
        elif msg.topic == 'Host/Report':

            dat = json.dumps(msg).replace('{', '').replace('}', '').replace('"', '').replace(' ', '').replace('\\', '').split(",")
            for i in range(len(dat)):
                if dat[i].split(":")[1] == "light":
                    if str(dat[i].split(":")[-1]) == "OFF":
                        self.ledStatus['fill'] = 'gray35'
                    elif str(dat[i].split(":")[-1]) == "ON":
                         self.ledStatus['fill'] = 'green'

                elif dat[i].split(":")[1] == "temp":
                    if str(dat[i].split(":")[-1]) == "OFF":
                        self.tempStatus['fill'] = 'gray35'
                    elif str(dat[i].split(":")[-1]) == "ON":
                         self.tempStatus['fill'] = 'green'

                elif dat[i].split(":")[1] == "hmdr":
                    if str(dat[i].split(":")[-1]) == "OFF":
                        self.humStatus['fill'] = 'gray35'
                    elif str(dat[i].split(":")[-1]) == "ON":
                         self.humStatus['fill'] = 'green'

                    


            self.sensorData2.insert(0, msg.payload.decode("utf-8"))
            if len(self.sensorData2) > 10:
                self.sensorData2.pop(-1)
            self.updateData(self.humListbox_2, self.tempListbox_2, self.sensorData2)
        #Deteccion de diferencia de temperaturas para publicar encendido o apagado de ventilacion
        if len(self.sensorData1) > 0 and len(self.sensorData2) > 0:
            if abs(float(self.sensorData1[0].split(',')[0].split(':')[-1][1:]) - float(self.sensorData2[0].split(',')[0].split(':')[-1][1:])) > 5 or abs(float(self.sensorData1[0].split(',')[1].split(':')[-1][:-1]) - float(self.sensorData2[0].split(',')[1].split(':')[-1][:-1])) > 15:
                self.mqttClient.publish('Bug_00/Execute', "ON")
                self.mqttClient.publish('Bug_01/Execute', "ON")
        else:
            self.mqttClient.publish('Bug_00/Execute', "OFF")
            self.mqttClient.publish('Bug_01/Execute', "OFF")

                    

    #Funcion para limpiar y actualizar datos de los listboxes
    def updateData(self, listbox1, listbox2, dataList):
        #Limpia el listbox actual
        listbox1.delete(0, tk.END)
        listbox2.delete(0, tk.END)

        #Itera sobre los mensajes guardados y los desplega en su listbox
        for message in dataList:
            listbox1.insert(tk.END, message.split(',')[0][1:])
            listbox2.insert(tk.END, message.split(',')[1][:-1])
        
        #Condicion para confirmar que tengo dato de los dos modulos antes de calcular el promedio para actualizar el label de las condiciones actuales, en caso de no tenerlos actualiza utilizando la informacion del mensaje recien llegado
        if len(self.sensorData1) > 0 and len(self.sensorData2) > 0:
            self.currentAvg = [(float(self.sensorData1[0].split(',')[0].split(':')[-1][1:]) + float(self.sensorData2[0].split(',')[0].split(':')[-1][1:]))/2, (float(self.sensorData1[0].split(',')[1].split(':')[-1][:-1]) + float(self.sensorData2[0].split(',')[1].split(':')[-1][:-1]))/2]
        else :
            self.currentAvg = [message.split(',')[0].split(':')[-1][1:], message.split(',')[1].split(':')[-1][:-1]]
        self.currentParam['text'] = f"Current parameters \n Temperature {self.currentAvg[1]} | Humidity {self.currentAvg[0]}\nDew point: {float(self.currentAvg[1])-((100-float(self.currentAvg[0]))/5)}"

    #Funcion vinculada al boton para copiar el clima, obtiene los datos de ciudad y pais, hace la solicitud a OWM actualiza los parametros en la GUI y comienza la barra de carga
    def onSelect(self):
        location = str(self.cityMenu.get())+","+str(self.countryMenu.get())
        observation = mgr.weather_at_place(location)
        n = observation.weather
        paramet = f"Target parameters \n Temperature {n.temperature('celsius')['temp']} | Humidity {n.humidity}"
        self.targetParam['text'] = paramet
        self.pb.start()
        self.statusLabel['text'] = 'Copying climate'
        
    #Funcion vinculada a la seleccion del pais, abre el archivo json de las ciudad de OWM, actualiza la lista de ciudades del menu
    def countryOption(self, value):
        with open('city.list.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        cities = []
        self.cityMenu['values'] = []
        
        for i in data:
            if i['country'] == self.countryMenu.get():
                cities.append(i['name'])
        cities.sort()
        self.cityMenu.set(cities[1])
        self.cityMenu['values'] = cities

        
    #Inicializacion del objeto
    def __init__(self, root):
        self.root = root
        self.root.title("MicroClimate Digital Twin")

        #Creacion del objeto del cliente MQTT
        self.mqttClient = mqtt.Client()
        self.mqttClient.connect("192.168.10.102", 1883, 60)
        self.mqttClient.subscribe("Bug_00/Report")
        self.mqttClient.subscribe("Bug_01/Report")
        self.mqttClient.on_message = self.on_message
        self.mqttClient.loop_start()

        #Listas para contener datos temporales/actualizables
        self.sensorData1 = []
        self.sensorData2 = []
        self.currentAvg = []
        self.currentParamText = "Awaitng data"
        self.actuatorState = ["OFF", "OFF", "OFF"]
            

        #Valores del tamaño de pantalla y divisiones para las secciones internas
        screenWidth = 810
        screenHeight = 700

        #Definicion del panel Izquierdo
        leftPanel = tk.Frame(root, bg="lavender", width=screenWidth // 3, height=screenHeight, highlightbackground="black", highlightthickness=1)
        leftPanel.pack(side=tk.LEFT, fill=tk.Y)

        #Label y Combobox para Pais
        label = tk.Label(leftPanel, text="Country", bg="lavender").grid(row=0, column=0, pady=10)

        self.countryMenu = ttk.Combobox(leftPanel, values=countries, width=5, justify='center', state='readonly')
        self.countryMenu.bind('<<ComboboxSelected>>', self.countryOption)
        self.countryMenu.set(country.get())
        self.countryMenu.grid(row=0, column=1, padx=10, pady=10, sticky='W')

        #Label y Combobox para ciudad
        label = tk.Label(leftPanel, text="City", bg="lavender").grid(row=1, column=0, pady=10)

        self.cityMenu = ttk.Combobox(leftPanel, values=cities, width=15, justify='center', state='readonly')
        self.cityMenu.set(city.get())
        self.cityMenu.grid(row=1, column=1, padx=10, pady=10, sticky='W')

        #Boton para copiar clima
        loadButton = tk.Button(leftPanel, text="Copy Climate", command=self.onSelect)
        loadButton.grid(row=2, column=0, columnspan=2, padx=10, pady=20)

        #Label para parametros objetivo
        self.targetParam = tk.Label(leftPanel, text=paramet, bg="lavender")
        self.targetParam.grid(row=3, column=0, columnspan=2, pady=30)

        #Label para estado del programa
        self.statusLabel = tk.Label(leftPanel, text='', bg="lavender")
        self.statusLabel.grid(row=4, column=0, columnspan=2)

        #Barra de progreso
        self.pb = ttk.Progressbar(leftPanel, orient= 'horizontal', length=150, mode='indeterminate')
        self.pb.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

        #Label para parametro actuales
        self.currentParam = tk.Label(leftPanel, text=self.currentParamText, bg="lavender")
        self.currentParam.grid(row=6, column=0, columnspan=2, pady=30)


        #Panel para modulo 1
        module1Panel = tk.Frame(root, bg="lightgray", width=screenWidth // 3 * 2, height=screenHeight / 4)
        module1Panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        

        #Label del panel
        titleLabel = tk.Label(module1Panel, text="Module 1", bg="lightgray")
        titleLabel.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='ns')

        #Listboxes para data de modulo 1
        self.tempListbox_1 = tk.Listbox(module1Panel, selectbackground="lightblue", justify='center', selectmode=tk.SINGLE)
        self.tempListbox_1.grid(row=1, column=0, padx=5, pady=5)

        self.humListbox_1 = tk.Listbox(module1Panel, selectbackground="lightblue", justify='center', selectmode=tk.SINGLE)
        self.humListbox_1.grid(row=1, column=1, padx=5, pady=5)


        #Labels e indicador para estado actual de actuadores en panel modulo 1
        tk.Label(module1Panel, text="Fan: ", bg="lightgray").grid(row=2, column=0, sticky='E', pady=(65, 30))

        fanIndicator = tk.Canvas(module1Panel, width=25, height=25, bg="lightgray", highlightthickness=0)
        fanIndicator.grid(row=2, column=1, padx=5, pady=(65, 30), sticky='W')
        self.fanStatus = fanIndicator.create_oval(3, 3, 25, 25, fill="gray35")

        tk.Label(module1Panel, text="Humidifier: ", bg="lightgray").grid(row=3, column=0, sticky='E')

        humIndicator = tk.Canvas(module1Panel, width=25, height=25, bg="lightgray", highlightthickness=0)
        humIndicator.grid(row=3, column=1, padx=5, pady=5, sticky='W')
        self.humStatus = humIndicator.create_oval(3, 3, 25, 25, fill="gray35")
        humIndicator.tag_bind(self.humStatus, '<Button-1>', self.hmdr)


        
        #Panel para modulo 2
        module2Panel = tk.Frame(root, bg="lightgray", width=screenWidth // 3 * 2, height=screenHeight // 2 // 2)
        module2Panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        #Label del panel
        titleLabel = tk.Label(module2Panel, text="Module 2", bg="lightgray")
        titleLabel.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='ns')

        #Listboxes para data de modulo 2
        self.tempListbox_2 = tk.Listbox(module2Panel, selectbackground="lightblue", justify='center', selectmode=tk.SINGLE)
        self.tempListbox_2.grid(row=1, column=0, padx=5, pady=5)

        self.humListbox_2 = tk.Listbox(module2Panel, selectbackground="lightblue", justify='center', selectmode=tk.SINGLE)
        self.humListbox_2.grid(row=1, column=1, padx=5, pady=5)

        #Labels e indicador para estado actual de actuadores en panel modulo 2
        tk.Label(module2Panel, text="Lighting: ", bg="lightgray").grid(row=2, column=0, sticky='E', pady=(65, 30))

        ledIndicator = tk.Canvas(module2Panel, width=25, height=25, bg="lightgray", highlightthickness=0)
        ledIndicator.grid(row=2, column=1, padx=5, pady=(65, 30), sticky='W')
        self.ledStatus = ledIndicator.create_oval(0, 0, 25, 25, fill="gray35")
        ledIndicator.tag_bind(self.ledStatus, '<Button-1>', self.light)

        tk.Label(module2Panel, text="Air Conditioner: ", bg="lightgray").grid(row=3, column=0, sticky='E')

        tempIndicator = tk.Canvas(module2Panel, width=25, height=25, bg="lightgray", highlightthickness=0)
        tempIndicator.grid(row=3, column=1, padx=5, pady=5, sticky='W')
        self.tempStatus = tempIndicator.create_oval(0, 0, 25, 25, fill="gray35")
        tempIndicator.tag_bind(self.tempStatus, '<Button-1>', self.temp)

if __name__ == "__main__":

    root = tk.Tk()

    #Configuracion del OWM
    config_dict = get_default_config_for_subscription_type('free')
    #Objeto del gestor del API
    owm = OWM('96ffa7534e55465cc7b0f714d3a9ba01', config_dict)
    mgr = owm.weather_manager()
    
    with open('city.list.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    countries = []
    cities = []
    
    #Llenado de lista de paises desde el archivo json, ordenado, valor por defecto "MX"
    for i in data:
        if i['country'] not in countries:
            countries.append(i['country'])
    countries.sort()
    country = tk.StringVar(root)
    country.set('MX')
    city = tk.StringVar(root)
    
    #Llenado de lista de ciudades del pais seleccionado actualmente, ordenado, valor por defecto "Hermosillo"
    for i in data:
        if i['country'] == country.get() and i['name'] not in cities:
            cities.append(i['name'])
    cities.sort()
    city.set('Hermosillo')

    #Solicitud de datos de OWM y actualizado de etiquetas
    location = str(city.get())+","+str(country.get())
    observation = mgr.weather_at_place(location)
    w = observation.weather
    paramet = f"Target parameters \n Temperature {w.temperature('celsius')['temp']} | Humidity {w.humidity}"

    #Crea instancia de la clase y asigna el objeto a la variable gui
    gui = MyGUI(root)
    root.mainloop()