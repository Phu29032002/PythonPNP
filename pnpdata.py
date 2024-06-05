import csv
import time
import serial

# Replace 'your_file.csv' with the path to your CSV file
csv_file_path = 'last.csv'

# Initialize an empty dictionary to store data by Part ID
part_data = {}

# Read the CSV file
with open(csv_file_path, mode='r') as file:
    # Create a CSV reader object
    csv_reader = csv.DictReader(file)

    # Iterate over each row in the CSV file
    for row in csv_reader:
        # Extract Part ID, Rotation, X, and Y from the row
        part_id = row['Part ID']
        rotation = float(row['Rotation'])
        x = float(row['X'])
        y = float(row['Y'])

        # Store the data in the dictionary
        part_data[part_id] = {
            'Rotation': rotation,
            'X': x,
            'Y': y
        }

# Function to send data to STM32
def send_data_to_stm32(ser, message):
    ser.write(message.encode())
    print(f"Sent: {message}")

# Function to receive data from STM32
# Function to receive data from STM32
def receive_data_from_stm32(ser):
    while True:
        if ser.in_waiting > 0:
            try:
                response = ser.readline().decode('utf-8', errors='ignore').strip()
                print(f"Received: {response}")
                return response
            except UnicodeDecodeError as e:
                #print(f"Decode error: {e}")
                continue

ser = serial.Serial(
    port='COM75',  # Replace with your COM port
    baudrate=9600,
    timeout=1
)
data1='bottom'
send_data_to_stm32(ser, data1)
time.sleep(2)
# Iterate over the part_data dictionary and send data
part_ids = list(part_data.keys())
for idx, part_id in enumerate(part_ids):
    values = part_data[part_id]
    data_string = f"{part_id},{values['Rotation']},{values['X']},{values['Y']}\n"
    send_data_to_stm32(ser, data_string)  # Pass the ser object and message

    # Wait for the correct response
    while True:
        response = receive_data_from_stm32(ser)
        if response == data_string.strip():
            break
        else:
            print("Mismatch, waiting for the correct response...")

    time.sleep(2)

    # If this is the last part, send the "end" message
    if idx == len(part_ids) - 1:
        send_data_to_stm32(ser, "end")  # Pass the ser object and message

while True:
    response = receive_data_from_stm32(ser)
    if response:
        print(f"Received: {response}")
    time.sleep(1)
