import tkinter as tk
import paho.mqtt.client as mqtt

# Global variable to store the latest 10 messages
latest_messages = []

def publish_to_mqtt(value):
    # Define your MQTT broker information
    broker_address = "3.138.178.240"
    port = 1883
    topic = "Bug_00/Execute"

    # Create an MQTT client
    client = mqtt.Client()

    # Connect to the broker
    client.connect(broker_address, port, 60)

    # Publish the value to the specified topic
    client.publish(topic, value)

    # Disconnect from the broker
    client.disconnect()

def on_publish_button_click():
    value = entry.get()
    publish_to_mqtt(value)

def on_message(client, userdata, msg):
    # Update the latest messages list with the received message
    latest_messages.append(msg.payload.decode("utf-8"))

    # Keep only the latest 10 messages
    if len(latest_messages) > 10:
        latest_messages.pop(0)

    # Update the Listbox with the latest messages
    update_latest_messages_listbox()

def update_latest_messages_listbox():
    # Clear the Listbox
    latest_messages_listbox.delete(0, tk.END)

    # Add the latest messages to the Listbox
    for message in latest_messages:
        latest_messages_listbox.insert(tk.END, message)

# Create the main window
window = tk.Tk()
window.title("MQTT Publisher")

# Create and place the label
label = tk.Label(window, text="Fan")
label.grid(row=0, column=0, pady=10)

# Create and place the entry box
entry = tk.Entry(window)
entry.grid(row=1, column=0, pady=10)

# Create and place the publish button
publish_button = tk.Button(window, text="Publish", command=on_publish_button_click)
publish_button.grid(row=2, column=0, pady=10)

# Create a lateral panel
side_panel = tk.Frame(window, bg="lightgray", width=200, height=300)
side_panel.grid(row=0, column=1, rowspan=3, sticky="ns")

# Add a title to the lateral panel
title_label = tk.Label(side_panel, text="Latest published on Report", bg="lightgray")
title_label.pack(pady=5)

# Create a Listbox to display the latest messages
latest_messages_listbox = tk.Listbox(side_panel, selectbackground="lightblue", selectmode=tk.SINGLE)
latest_messages_listbox.pack(expand=True, fill=tk.BOTH)

# Connect to the MQTT broker and subscribe to the "Report" topic
mqtt_client = mqtt.Client()
mqtt_client.connect("3.138.178.240", 1883, 60)
mqtt_client.subscribe("Bug_00/Report")
mqtt_client.on_message = on_message
mqtt_client.loop_start()

# Run the Tkinter event loop
window.mainloop()
