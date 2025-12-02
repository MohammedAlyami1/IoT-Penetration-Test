# IoT Security Research Tools

**⚠️ EDUCATIONAL AND AUTHORIZED TESTING ONLY ⚠️**

This repository contains security research tools for testing IoT devices. These scripts are intended **ONLY** for:
- Educational purposes
- Security research on your own devices
- Authorized penetration testing with explicit written permission
- Demonstrating vulnerabilities to improve security

**Using these tools without authorization is illegal and unethical.**

---

## 📋 Table of Contents

1. [Drone Control Scripts](#drone-control-scripts)
2. [ESP32 IoT Testing](#esp32-iot-testing)
3. [IP Camera Security Tools](#ip-camera-security-tools)
4. [Requirements](#requirements)
5. [Legal Disclaimer](#legal-disclaimer)

---

## 🚁 Drone Control Scripts

### Drone.py - E88 Drone Keyboard Control

Live keyboard control for E88 drones via UDP socket communication.

**Features:**
- Real-time keyboard control with visual HUD
- Arrow keys for pitch/roll control
- Space/Shift for throttle (up/down)
- Q/E for yaw (rotation)
- Arm/disarm sequence
- Emergency stop (ESC key)
- 50Hz packet rate for smooth control

**Usage:**
```bash
# Install dependencies
pip install pynput

# Connect to drone WiFi first, then run:
python3 Drone.py
```

**Controls:**
- `↑/↓` - Pitch forward/backward
- `←/→` - Roll left/right
- `SPACE` - Throttle up
- `SHIFT` - Throttle down
- `Q/E` - Yaw left/right
- `A` - Arm/disarm motors
- `T` - Takeoff
- `L` - Land
- `ESC` - Emergency stop

---

### Drone_injection.py - Raw 802.11 Packet Injection

Advanced drone control using Scapy for raw 802.11 frame injection.

**Features:**
- Raw packet injection at Layer 2
- MAC address spoofing capability
- Can hijack drone from another controller
- No WiFi association required
- Monitor mode interface support

**Requirements:**
- Root privileges
- Wireless adapter in monitor mode
- Scapy library

**Setup:**
```bash
# Install dependencies
pip install scapy pynput

# Enable monitor mode
sudo airmon-ng start wlan0

# Edit configuration in script:
DRONE_MAC = "08:17:91:4B:8C:64"  # Your drone's MAC
INTERFACE = "wlan0mon"            # Monitor interface
SPOOFED_CLIENT_MAC = "XX:XX:XX:XX:XX:XX"

# Run with root
sudo python3 Drone_injection.py
```

**Advantages:**
- Works without connecting to drone WiFi
- Can override existing connections
- More stealthy operation
- Greater control flexibility

---

## 🔔 ESP32 IoT Testing

### Reply.py - ESP32 Device Command Injection

TCP socket tool for testing ESP32-based IoT devices.

**Features:**
- Send commands to ESP32 devices
- Test alarm systems
- Temperature sensor manipulation
- Command response monitoring

**Configuration:**
```python
TARGET_IP = "192.168.0.103"  # ESP32 IP address
TARGET_PORT = 80              # Device port
```

**Available Commands:**
1. `ALARM` - Trigger alarm
2. `CLEAR` - Silence alarm
3. `TEMP:60` - Send fake temperature reading

**Usage:**
```bash
python3 Reply.py
```

**Use Cases:**
- Testing IoT device security
- Validating input sanitization
- Checking authentication mechanisms
- Demonstrating command injection vulnerabilities

---

## 📷 IP Camera Security Tools

### Control.py - ONVIF Camera PTZ Control

Control Pan-Tilt-Zoom (PTZ) cameras via ONVIF protocol.

**Features:**
- Camera movement control (pan/tilt)
- Continuous movement with duration
- Profile token management
- Service discovery

**Configuration:**
```python
YOUR_IP = '192.168.0.100'      # Camera IP
YOUR_PORT = 2020               # ONVIF port (Tapo: 2020)
YOUR_USERNAME = 'admin1'       # Camera account
YOUR_PASSWORD = 'password123'  # Camera password
```

**Movement Commands:**
```python
# Pan: x-axis (-1.0 to 1.0)
# Tilt: y-axis (-1.0 to 1.0)
move_request.Velocity = {'PanTilt': {'x': 0.5, 'y': 0}}  # Right
move_request.Velocity = {'PanTilt': {'x': -0.5, 'y': 0}} # Left
move_request.Velocity = {'PanTilt': {'x': 0, 'y': 0.5}}  # Up
move_request.Velocity = {'PanTilt': {'x': 0, 'y': -0.5}} # Down
```

---

### BrutforcePort2020.py - ONVIF Credential Testing

Brute force tool for testing weak ONVIF camera credentials.

**Features:**
- Dictionary-based credential testing
- Automatic reboot on success
- User/password file support
- Progress monitoring

**Setup:**
1. Create `user.txt` with usernames (one per line):
```
admin
admin1
root
user
```

2. Create `pass.txt` with passwords (one per line):
```
admin
password
12345
password123
```

3. Configure script:
```python
YOUR_IP = '192.168.0.100'
YOUR_PORT = 2020
USER_FILE = 'user.txt'
PASS_FILE = 'pass.txt'
```

**Usage:**
```bash
python3 BrutforcePort2020.py
```

**Output:**
- Shows each attempt
- Reports valid credentials when found
- Sends reboot command on success

---

### Reboot.py - Continuous Camera Reboot Loop

Denial of Service testing tool for IP cameras.

**Features:**
- Continuous reboot loop
- Connection retry logic
- Graceful shutdown (Ctrl+C)
- Timing management

**Configuration:**
```python
YOUR_IP = '192.168.0.100'
YOUR_PORT = 2020
YOUR_USERNAME = 'admin1'
YOUR_PASSWORD = 'password123'
```

**Usage:**
```bash
python3 Reboot.py
# Press Ctrl+C to stop
```

**Behavior:**
1. Connects to camera
2. Sends reboot command
3. Waits 25 seconds
4. Reconnects and repeats
5. Keeps camera in perpetual reboot state

**Use Case:**
- Testing device resilience
- Demonstrating DoS vulnerabilities
- Validating reboot throttling mechanisms

---

## 📦 Requirements

### Python Packages

```bash
# Drone control
pip install pynput

# Packet injection
pip install scapy

# IP Camera control
pip install onvif-zeep

# All dependencies
pip install pynput scapy onvif-zeep
```

### System Requirements

**For Drone Injection:**
- Linux OS (Kali Linux recommended)
- Wireless adapter supporting monitor mode
- Root/sudo access
- `airmon-ng` tool

**For Camera Tools:**
- Python 3.6+
- Network access to target camera
- ONVIF protocol support on camera

**For ESP32 Testing:**
- Network connectivity to ESP32 device
- TCP socket support

---

## ⚖️ Legal Disclaimer

### READ THIS CAREFULLY

These tools are provided for **EDUCATIONAL AND AUTHORIZED TESTING ONLY**.

**You MAY use these tools:**
- ✅ On devices you own
- ✅ In authorized penetration tests with written permission
- ✅ In controlled lab environments
- ✅ For security research and education

**You MAY NOT use these tools:**
- ❌ On devices you don't own without explicit permission
- ❌ To disrupt services or cause harm
- ❌ To gain unauthorized access to systems
- ❌ For any illegal or malicious purposes

**Legal Consequences:**
Unauthorized access to computer systems is illegal under:
- Computer Fraud and Abuse Act (CFAA) in the USA
- Computer Misuse Act in the UK
- Similar laws in virtually all countries

Violations can result in:
- Criminal prosecution
- Heavy fines
- Imprisonment
- Civil liability

---

## 🛡️ Responsible Disclosure

If you discover vulnerabilities using these tools:

1. **Do not** exploit them maliciously
2. **Do not** publicly disclose without vendor coordination
3. **Do** report to the vendor through proper channels
4. **Do** allow reasonable time for fixes (typically 90 days)
5. **Do** follow coordinated disclosure guidelines

---

## 🔒 Security Best Practices

### For Device Owners

**Drones:**
- Use latest firmware
- Change default WiFi passwords
- Enable encryption if available
- Monitor for unauthorized connections

**IP Cameras:**
- Change default credentials immediately
- Use strong, unique passwords
- Disable unused protocols (ONVIF if not needed)
- Keep firmware updated
- Use VLANs to isolate cameras
- Enable rate limiting for authentication
- Monitor access logs

**IoT Devices:**
- Change default credentials
- Disable unnecessary services
- Use network segmentation
- Implement authentication
- Validate all inputs
- Enable logging

---

## 📚 Educational Resources

### Understanding the Attacks

**Drone Control:**
- Demonstrates unencrypted UDP control protocols
- Shows MAC address spoofing techniques
- Illustrates 802.11 frame injection
- Highlights lack of authentication

**ONVIF Vulnerabilities:**
- Weak default credentials
- Lack of rate limiting
- Unlimited reboot commands
- Protocol design flaws

**IoT Command Injection:**
- Insufficient input validation
- Lack of authentication
- Plain text protocols
- Command parsing vulnerabilities

---

## 🤝 Contributing

If you discover improvements or additional security issues:

1. Test responsibly on your own devices
2. Document your findings clearly
3. Submit pull requests with detailed descriptions
4. Include responsible disclosure information

---

## 📝 Version History

- **v1.0** - Initial release
  - Basic drone control scripts
  - IP camera ONVIF tools
  - ESP32 testing utilities

---

## 👤 Author

Security Research Tools Collection

**Contact:** For responsible disclosure or security questions only

---

## 📄 License

These tools are provided "AS IS" for educational purposes only. The author assumes no liability for misuse. Users are responsible for complying with all applicable laws and regulations.

---

## ⚠️ Final Warning

**THINK BEFORE YOU ACT**

Before running any of these scripts:
1. Do you own this device?
2. Do you have written authorization?
3. Are you in a controlled environment?
4. Do you understand the consequences?

If you answered "NO" to any of these questions, **DO NOT PROCEED**.

Security research is about making systems safer, not causing harm.

---

**Stay Curious. Stay Ethical. Stay Legal.** 🔐
