
#!/usr/bin/env python

from onvif import ONVIFCamera
import time

# --- CONFIGURATION ---
# !! Replace with your camera's details
# !! Use the "Camera Account" username/password, NOT your Tapo app login
YOUR_IP = '192.168.0.100' # Your camera's IP address
YOUR_PORT = 2020         # Tapo's ONVIF port is 2020
YOUR_USERNAME = 'admin1'  # The Camera Account username you created
YOUR_PASSWORD = 'password123' # The Camera Account password you created
# ---------------------

def move_camera(ptz, move_request, duration_sec):
    """Helper function to start a move, wait, and then stop."""
    print(f"Moving for {duration_sec} second(s)...")
    ptz.ContinuousMove(move_request)
    time.sleep(duration_sec)
    ptz.Stop({'ProfileToken': move_request.ProfileToken})
    print("Move complete.")

def main():
    try:
        # 1. Connect to the camera
        mycam = ONVIFCamera(YOUR_IP, YOUR_PORT, YOUR_USERNAME, YOUR_PASSWORD)
        print("Connected to camera.")

        # 2. Create the media service
        media_service = mycam.create_media_service()
        
        # 3. Get the first profile (usually the high-res one)
        profiles = media_service.GetProfiles()
        profile_token = profiles[0].token

        # 4. Create the PTZ service
        ptz_service = mycam.create_ptz_service()

        # 5. Create a "move request" object
        move_request = ptz_service.create_type('ContinuousMove')
        move_request.ProfileToken = profile_token

        # --- Example Commands ---
        
         Move RIGHT for 1 second
        print("Moving RIGHT...")
        move_request.Velocity = {'PanTilt': {'x': 0.5, 'y': 0}}
        move_camera(ptz_service, move_request, 0)

        time.sleep(1) # Pause

        # Move LEFT for 1 second
        print("Moving LEFT...")
        move_request.Velocity = {'PanTilt': {'x': -0.5, 'y': 0}}
        move_camera(ptz_service, move_request, 1)

        time.sleep(1) # Pause

        # Move UP for 0.5 seconds
        print("Moving UP...")
        move_request.Velocity = {'PanTilt': {'x': 0, 'y': 0.5}}
        move_camera(ptz_service, move_request, 5)

        time.sleep(1) # Pause

        # Move DOWN for 0.5 seconds
        print("Moving DOWN...")
        move_request.Velocity = {'PanTilt': {'x': 0, 'y': -0.5}}
        move_camera(ptz_service, move_request, 5)

        print("All moves finished.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
