import tkinter as tk
import json

class MyGUI:
    def countryOption(self, value):
        with open('city.list.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        cities = []
        
        for i in data:
            if i['country'] == country.get():
                cities.append(i['name'])
        city.set(cities[0])
        self.cityMenu['menu'].delete(0, 'end')

        # Insert list of new options (tk._setit hooks them up to var)
        for c in cities:
            self.cityMenu['menu'].add_command(label=c, command=tk._setit(city, c))

    def __init__(self, root):
        self.root = root
        self.root.title("Tkinter GUI Example")

        # Set window size and position
        screen_width = 810
        screen_height = 700


        third_width = screen_width // 3
        top_half_height = screen_height // 2

        # Right panel
        right_panel = tk.Frame(root, bg="blue", width=third_width, height=screen_height)
        right_panel.pack(side=tk.LEFT, fill=tk.Y)

        
        label = tk.Label(right_panel, text="Country").grid(row=0, column=0, pady=10)

        countryMenu = tk.OptionMenu(right_panel, country, *countries, command=self.countryOption)
        countryMenu.grid(row=0, column=1, padx=10, pady=10)

        label = tk.Label(right_panel, text="City").grid(row=1, column=0, pady=10)

        self.cityMenu = tk.OptionMenu(right_panel, city, *cities, command=cityOption)
        self.cityMenu.grid(row=1, column=1, padx=10, pady=10)







        # Top left panel (Module 1)
        module1_panel = tk.Frame(root, bg="green", width=third_width * 2, height=screen_height / 4)
        module1_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)


        # Add a title to the lateral panel
        title_label = tk.Label(module1_panel, text="Module 1", bg="lightgray")
        title_label.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='ns')

        # Create a Listbox to display the latest messages
        tempListbox_1 = tk.Listbox(module1_panel, selectbackground="lightblue", selectmode=tk.SINGLE)
        tempListbox_1.grid(row=1, column=0, padx=5, pady=5)

        humListbox_1 = tk.Listbox(module1_panel, selectbackground="lightblue", selectmode=tk.SINGLE)
        humListbox_1.grid(row=1, column=1, padx=5, pady=5)



        # Top right panel (Module 2)
        module2_panel = tk.Frame(root, bg="red", width=third_width * 2, height=top_half_height // 2)
        module2_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Add a title to the lateral panel
        title_label = tk.Label(module2_panel, text="Module 2", bg="lightgray")
        title_label.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='ns')

        # Create a Listbox to display the latest messages
        tempListbox_2 = tk.Listbox(module2_panel, selectbackground="lightblue", selectmode=tk.SINGLE)
        tempListbox_2.grid(row=1, column=0, padx=5, pady=5)

        humListbox_2 = tk.Listbox(module2_panel, selectbackground="lightblue", selectmode=tk.SINGLE)
        humListbox_2.grid(row=1, column=1, padx=5, pady=5)

if __name__ == "__main__":
    def cityOption(value):
        print(cities)

    
        

    root = tk.Tk()
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
        if i['country'] == country.get():
            cities.append(i['name'])
    city.set(cities[0])
        

    
    
    gui = MyGUI(root)
    root.mainloop()
    
