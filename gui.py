import tkinter as tk
from tkinter import ttk
import paho.mqtt.client as mqtt
from pyowm.owm import OWM
from pyowm.utils.config import get_default_config_for_subscription_type
import json

class MyGUI:

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
        #Deteccion de diferencia de temperaturas para publicar encendido o apagado de ventilacion
        if len(self.sensorData1) > 0 and len(self.sensorData2) > 0:
            if abs(float(self.sensorData1[0].split(',')[0].split(':')[-1][1:]) - float(self.sensorData2[0].split(',')[0].split(':')[-1][1:])) > 5 or abs(float(self.sensorData1[0].split(',')[1].split(':')[-1][:-1]) - float(self.sensorData2[0].split(',')[1].split(':')[-1][:-1])) > 15:
                self.mqttClient.publish('Bug_00/Execute', "ON")
                self.mqttClient.publish('Bug_01/Execute', "ON")
        else:
            self.mqttClient.publish('Bug_00/Execute', "OFF")
            self.mqttClient.publish('Bug_01/Execute', "OFF")

                    


    def updateData(self, listbox1, listbox2, dataList):
        # Clear the Listbox
        listbox1.delete(0, tk.END)
        listbox2.delete(0, tk.END)

        # Add the latest messages to the Listbox
        for message in dataList:
            listbox1.insert(tk.END, message.split(',')[0][1:])
            listbox2.insert(tk.END, message.split(',')[1][:-1])
        
        if len(self.sensorData1) > 0 and len(self.sensorData2) > 0:
            self.currentAvg = [(float(self.sensorData1[0].split(',')[0].split(':')[-1][1:]) + float(self.sensorData2[0].split(',')[0].split(':')[-1][1:]))/2, (float(self.sensorData1[0].split(',')[1].split(':')[-1][:-1]) + float(self.sensorData2[0].split(',')[1].split(':')[-1][:-1]))/2]
        else :
            self.currentAvg = [message.split(',')[0].split(':')[-1][1:], message.split(',')[1].split(':')[-1][:-1]]
        self.currentParam['text'] = f"Current parameters \n Temperature {self.currentAvg[1]} | Humidity {self.currentAvg[0]}\nDew point: {float(self.currentAvg[1])-((100-float(self.currentAvg[0]))/5)}"


    def onSelect(self):
        location = str(self.cityMenu.get())+","+str(self.countryMenu.get())
        observation = mgr.weather_at_place(location)
        n = observation.weather
        paramet = f"Target parameters \n Temperature {n.temperature('celsius')['temp']} | Humidity {n.humidity}"
        self.targetParam['text'] = paramet
        self.pb.start()
        self.statusLabel['text'] = 'Copying climate'
        

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

        

    def __init__(self, root):
        self.root = root
        self.root.title("MicroClimate Digital Twin")

        self.mqttClient = mqtt.Client()
        self.mqttClient.connect("3.133.119.117", 1883, 60)
        self.mqttClient.subscribe("Bug_00/Report")
        self.mqttClient.subscribe("Bug_01/Report")
        self.mqttClient.on_message = self.on_message
        self.mqttClient.loop_start()

        self.sensorData1 = []
        self.sensorData2 = []
        self.currentAvg = []
        self.currentParamText = "Awaitng data"
            

        # Set window size and position
        screen_width = 810
        screen_height = 700


        third_width = screen_width // 3
        top_half_height = screen_height // 2

        # Right panel
        right_panel = tk.Frame(root, bg="lavender", width=third_width, height=screen_height, highlightbackground="black", highlightthickness=1)
        right_panel.pack(side=tk.LEFT, fill=tk.Y)

        
        label = tk.Label(right_panel, text="Country", bg="lavender").grid(row=0, column=0, pady=10)

        self.countryMenu = ttk.Combobox(right_panel, values=countries, width=5, justify='center', state='readonly')
        self.countryMenu.bind('<<ComboboxSelected>>', self.countryOption)
        self.countryMenu.set(country.get())
        self.countryMenu.grid(row=0, column=1, padx=10, pady=10, sticky='W')

        label = tk.Label(right_panel, text="City", bg="lavender").grid(row=1, column=0, pady=10)

        self.cityMenu = ttk.Combobox(right_panel, values=cities, width=15, justify='center', state='readonly')
        self.cityMenu.set(city.get())
        self.cityMenu.grid(row=1, column=1, padx=10, pady=10, sticky='W')

        loadButton = tk.Button(right_panel, text="Copy Climate", command=self.onSelect)
        loadButton.grid(row=2, column=0, columnspan=2, padx=10, pady=20)

        self.targetParam = tk.Label(right_panel, text=paramet, bg="lavender")
        self.targetParam.grid(row=3, column=0, columnspan=2, pady=30)

        self.statusLabel = tk.Label(right_panel, text='', bg="lavender")
        self.statusLabel.grid(row=4, column=0, columnspan=2)

        self.pb = ttk.Progressbar(right_panel, orient= 'horizontal', length=150, mode='indeterminate')
        self.pb.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

        self.currentParam = tk.Label(right_panel, text=self.currentParamText, bg="lavender")
        self.currentParam.grid(row=6, column=0, columnspan=2, pady=30)


        # Top left panel (Module 1)
        module1_panel = tk.Frame(root, bg="lightgray", width=third_width * 2, height=screen_height / 4)
        module1_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        

        # Add a title to the lateral panel
        title_label = tk.Label(module1_panel, text="Module 1", bg="lightgray")
        title_label.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='ns')

        # Create a Listbox to display the latest messages
        self.tempListbox_1 = tk.Listbox(module1_panel, selectbackground="lightblue", justify='center', selectmode=tk.SINGLE)
        self.tempListbox_1.grid(row=1, column=0, padx=5, pady=5)

        self.humListbox_1 = tk.Listbox(module1_panel, selectbackground="lightblue", justify='center', selectmode=tk.SINGLE)
        self.humListbox_1.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(module1_panel, text="Fan: ", bg="lightgray").grid(row=2, column=0, sticky='E', pady=(65, 30))

        fanIndicator = tk.Canvas(module1_panel, width=25, height=25, bg="lightgray", highlightthickness=0)
        fanIndicator.grid(row=2, column=1, padx=5, pady=(65, 30), sticky='W')
        self.fanStatus = fanIndicator.create_oval(3, 3, 25, 25, fill="gray35")

        tk.Label(module1_panel, text="Humidifier: ", bg="lightgray").grid(row=3, column=0, sticky='E')

        humIndicator = tk.Canvas(module1_panel, width=25, height=25, bg="lightgray", highlightthickness=0)
        humIndicator.grid(row=3, column=1, padx=5, pady=5, sticky='W')
        self.humStatus = humIndicator.create_oval(3, 3, 25, 25, fill="gray35")


        
        # Top right panel (Module 2)
        module2_panel = tk.Frame(root, bg="lightgray", width=third_width * 2, height=top_half_height // 2)
        module2_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Add a title to the lateral panel
        title_label = tk.Label(module2_panel, text="Module 2", bg="lightgray")
        title_label.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='ns')

        # Create a Listbox to display the latest messages
        self.tempListbox_2 = tk.Listbox(module2_panel, selectbackground="lightblue", justify='center', selectmode=tk.SINGLE)
        self.tempListbox_2.grid(row=1, column=0, padx=5, pady=5)

        self.humListbox_2 = tk.Listbox(module2_panel, selectbackground="lightblue", justify='center', selectmode=tk.SINGLE)
        self.humListbox_2.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(module2_panel, text="Lighting: ", bg="lightgray").grid(row=2, column=0, sticky='E', pady=(65, 30))

        ledIndicator = tk.Canvas(module2_panel, width=25, height=25, bg="lightgray", highlightthickness=0)
        ledIndicator.grid(row=2, column=1, padx=5, pady=(65, 30), sticky='W')
        self.ledStatus = ledIndicator.create_oval(0, 0, 25, 25, fill="gray35")

        tk.Label(module2_panel, text="Air Conditioner: ", bg="lightgray").grid(row=3, column=0, sticky='E')

        peltIndicator = tk.Canvas(module2_panel, width=25, height=25, bg="lightgray", highlightthickness=0)
        peltIndicator.grid(row=3, column=1, padx=5, pady=5, sticky='W')
        self.peltStatus = peltIndicator.create_oval(0, 0, 25, 25, fill="gray35")

if __name__ == "__main__":

    root = tk.Tk()

    config_dict = get_default_config_for_subscription_type('free')
    #Objeto del gestor del API
    owm = OWM('96ffa7534e55465cc7b0f714d3a9ba01', config_dict)
    mgr = owm.weather_manager()
    
    with open('city.list.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    countries = []
    cities = []
               
    for i in data:
        if i['country'] not in countries:
            countries.append(i['country'])

    countries.sort()

    country = tk.StringVar(root)
    country.set('MX')
    city = tk.StringVar(root)
    
    for i in data:
        if i['country'] == country.get() and i['name'] not in cities:
            cities.append(i['name'])
    cities.sort()
    city.set('Hermosillo')
    location = str(city.get())+","+str(country.get())
    observation = mgr.weather_at_place(location)
    w = observation.weather
    paramet = f"Target parameters \n Temperature {w.temperature('celsius')['temp']} | Humidity {w.humidity}"

    
    gui = MyGUI(root)
    root.mainloop()
    
