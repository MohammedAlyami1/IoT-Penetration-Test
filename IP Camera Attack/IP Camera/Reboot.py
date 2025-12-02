import time
import sys
from onvif import ONVIFCamera

# --- CONFIGURATION ---
YOUR_IP = '192.168.0.100' # Your camera's IP address
YOUR_PORT = 2020         # Tapo's ONVIF port is 2020
YOUR_USERNAME = 'admin1'   # The Camera Account username you created
YOUR_PASSWORD = 'password123' # The Camera Account password you created
# ---------------------

def main():
    print("--- Starting continuous reboot loop ---")
    print("Press Ctrl+C in this terminal to stop the script.")
    
    # This creates an infinite loop
    while True:
        try:
            # 1. Try to connect to the camera
            print(f"Attempting to connect to {YOUR_IP}...")
            mycam = ONVIFCamera(YOUR_IP, YOUR_PORT, YOUR_USERNAME, YOUR_PASSWORD)
            print("Connection successful.")

            # 2. If connection works, create service and send reboot
            device_service = mycam.create_devicemgmt_service()
            print("--- Sending REBOOT command NOW ---")
            device_service.SystemReboot()
            
            # 3. Wait for the camera to start rebooting
            print("Reboot command sent. Waiting 25 seconds for camera to cycle...")
            time.sleep(25) # Wait for the camera to go down and start coming back up

        except KeyboardInterrupt:
            # This allows you to stop the script with Ctrl+C
            print("\nStopping loop. Camera will now reboot normally.")
            sys.exit(0)
            
        except Exception as e:
            # This will happen MOST of the time, because the camera is offline
            print(f"Connection failed (camera is likely rebooting): {e}")
            # Wait a few seconds before trying to connect again
            time.sleep(10)

if __name__ == '__main__':
    main()
