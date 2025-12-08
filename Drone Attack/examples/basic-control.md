# Basic Drone Control - Getting Started

## 🎯 Objective

Learn to control the E88 drone using keyboard input through the standard UDP-based control method. This is the simplest attack vector that works when you can connect to the drone before the legitimate user.

---

## 📋 Prerequisites

**Hardware:**
- E88/Z708 Wi-Fi controlled drone
- Laptop/computer with Wi-Fi capability
- Charged drone battery

**Software:**
- Python 3.6 or higher
- `pynput` library installed
- `Drone.py` script

**Network:**
- Ability to connect to drone's Wi-Fi network
- Drone SSID: `WIFI-UFO-648c4b` (or similar)
- No password required (open network)

---

## 🔧 Phase 1: Installation & Setup

### Step 1: Install Dependencies

```bash
# Install pynput library
pip install pynput

# Verify installation
python3 -c "from pynput import keyboard; print('✓ pynput installed successfully')"
```

**Expected Output:**
```
✓ pynput installed successfully
```

---

### Step 2: Verify Drone.py Script

```bash
# Check if script exists
ls -lh Drone.py

# View script header
head -n 20 Drone.py
```

**Expected:**
```
-rw-r--r-- 1 user user 12K Dec 07 15:30 Drone.py
#!/usr/bin/env python3
"""
E88 Drone - Live Keyboard Control
...
```

---

### Step 3: Power On Drone

**Physical Setup:**
1. Place drone on flat, stable surface
2. Ensure 2+ meters clearance in all directions
3. Remove any obstacles (people, furniture, pets)
4. Install charged battery
5. Power on drone (switch on bottom)

**Indicators:**
- ✅ LEDs start blinking
- ✅ Propellers do NOT spin (unarmed state)
- ✅ Wi-Fi network broadcasts after ~10 seconds

---

## 📡 Phase 2: Network Connection

### Step 4: Scan for Drone Network

**Linux (nmcli):**
```bash
# Scan for networks
nmcli device wifi list

# Look for drone SSID
nmcli device wifi list | grep -i "UFO\|WIFI"
```

**Expected Output:**
```
WIFI-UFO-648c4b  Infra  11    54 Mbit/s  85      ▂▄▆█  --
```

---

### Step 5: Connect to Drone

**Method 1: Command Line (Linux)**
```bash
# Connect to open network
nmcli device wifi connect "WIFI-UFO-648c4b"
```

**Method 2: GUI (Any OS)**
1. Click Wi-Fi icon in system tray
2. Look for network: `WIFI-UFO-648c4b`
3. Click to connect (no password needed)
4. Wait for "Connected" status

---

### Step 6: Verify Connection

```bash
# Check connection status
nmcli connection show --active

# Should show drone network
# Check IP address assigned
ifconfig wlan0  # or ip addr show wlan0
```

**Expected IP Range:**
```
inet 192.168.1.XXX  netmask 255.255.255.0
```

**Typical IP assignments:**
- Drone (AP): `192.168.1.1`
- Your device: `192.168.1.XXX` (e.g., 192.168.1.100)

---

### Step 7: Test Connectivity

```bash
# Ping the drone
ping -c 3 192.168.1.1
```

**Expected Output:**
```
PING 192.168.1.1 (192.168.1.1) 56(84) bytes of data.
64 bytes from 192.168.1.1: icmp_seq=1 ttl=64 time=2.34 ms
64 bytes from 192.168.1.1: icmp_seq=2 ttl=64 time=1.89 ms
64 bytes from 192.168.1.1: icmp_seq=3 ttl=64 time=2.12 ms

--- 192.168.1.1 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss
```

✅ Drone is reachable!

---

## 🎮 Phase 3: First Flight

### Step 8: Launch Control Script

```bash
# Navigate to script directory
cd /path/to/drone-attack/

# Run the script
python3 Drone.py
```

---

### Step 9: Safety Checklist Display

**The script will display:**
```
======================================================================
  E88 DRONE - LIVE KEYBOARD CONTROL
======================================================================

[!] SAFETY CHECKLIST:
  ☑ Connected to drone WiFi
  ☑ Drone on flat surface
  ☑ Clear space (2+ meters all directions)
  ☑ Ready to hit ESC for emergency stop
  ☑ Official app closed

[!] IMPORTANT:
  • This requires 'pynput' library
  • Install with: pip install pynput
  • Press ESC at ANY time for emergency stop
  • Keep hands away from propellers

Press ENTER to start, or Ctrl+C to abort...
```

**Review checklist carefully!**

---

### Step 10: Start Control System

Press **ENTER** to continue.

**Initialization Output:**
```
[*] Starting control system...
[*] Establishing connection with drone...
[✓] Connected to drone at 192.168.1.1:7099
[*] Sending neutral packets to establish connection...
[✓] Drone connected! Telemetry: 5301000000
[*] Keyboard control active!
[*] Press 'A' to arm motors, then 'T' to takeoff
```

---

### Step 11: Visual HUD Interface

**The screen will display:**
```
======================================================================
  E88 DRONE - LIVE KEYBOARD CONTROL
======================================================================

Status: STANDBY
Packets Sent: 0
Last Telemetry: 5301000000

----------------------------------------------------------------------
CONTROLS:
  Roll (←/→):     0x80  [██████████░░░░░░░░░░] CENTER
  Pitch (↑/↓):    0x80  [██████████░░░░░░░░░░] CENTER
  Throttle (Space/Shift): 0x80  [██████████░░░░░░░░░░] CENTER
  Yaw (Q/E):      0x80  [██████████░░░░░░░░░░] CENTER

----------------------------------------------------------------------
ACTIVE KEYS: None

----------------------------------------------------------------------
KEYBOARD CONTROLS:
  ↑/↓ Arrows    - Pitch Forward/Backward
  ←/→ Arrows    - Roll Left/Right
  SPACE         - Throttle Up (Ascend)
  SHIFT         - Throttle Down (Descend)
  Q/E           - Yaw Left/Right (Rotate)
  T             - Takeoff (Auto)
  L             - Land
  A             - Arm/Disarm Motors
  ESC           - Emergency Stop & Exit
======================================================================
```

---

## 🚁 Phase 4: Flight Operations

### Step 12: Arm Motors

**Press: `A`**

**What Happens:**
1. Script displays: `[*] Arming motors...`
2. Throttle cycles: UP → DOWN → UP → CENTER
3. Takes ~2 seconds
4. Display shows: `[✓] Motors armed!`
5. Status changes to: `ARMED & FLYING`

**Physical Indicators:**
- Propellers may twitch slightly
- LEDs change pattern (solid or different blink)
- Drone is now ready to fly

⚠️ **IMPORTANT:** After arming, drone is ready to take off!

---

### Step 13: Takeoff

**Press: `T`**

**Auto-Takeoff Sequence:**
1. Throttle automatically increases
2. Drone lifts off to ~1 meter height
3. Hovers automatically
4. Control returns to manual

**Expected:**
- Smooth vertical ascent
- Stabilizes at hover height
- Minor corrections to maintain position

---

### Step 14: Basic Maneuvering

**Forward Movement:**
- **Press and Hold: `↑`**
- Drone pitches forward and moves
- Release key → drone stops and hovers

**Backward Movement:**
- **Press and Hold: `↓`**
- Drone pitches backward
- Release → hover

**Left Movement:**
- **Press and Hold: `←`**
- Drone rolls left
- Release → hover

**Right Movement:**
- **Press and Hold: `→`**
- Drone rolls right
- Release → hover

**Visual Feedback:**
```
ACTIVE KEYS: ↑

CONTROLS:
  Pitch (↑/↓):    0xA0  [████████████████░░░░] ►
                        ↑ Shows forward movement
```

---

### Step 15: Altitude Control

**Ascend:**
- **Press and Hold: `SPACE`**
- Drone climbs
- Release → maintains altitude

**Descend:**
- **Press and Hold: `SHIFT`**
- Drone descends
- Release → maintains altitude

**Visual Feedback:**
```
ACTIVE KEYS: SPACE

CONTROLS:
  Throttle (Space/Shift): 0xC0  [███████████████████░] ►
```

---

### Step 16: Rotation (Yaw)

**Rotate Left (Counter-Clockwise):**
- **Press and Hold: `Q`**
- Drone spins left
- Release → stops rotation

**Rotate Right (Clockwise):**
- **Press and Hold: `E`**
- Drone spins right
- Release → stops rotation

---

### Step 17: Combined Movements

**Example: Forward + Right**
- Hold `↑` + `→` simultaneously
- Drone moves diagonally forward-right

**Example: Ascend + Rotate**
- Hold `SPACE` + `Q`
- Drone climbs while rotating

**Visual Feedback:**
```
ACTIVE KEYS: ↑, →, SPACE

CONTROLS:
  Roll (←/→):     0xA0  [████████████████░░░░] ►
  Pitch (↑/↓):    0xA0  [████████████████░░░░] ►
  Throttle:       0xC0  [███████████████████░] ►
```

---

### Step 18: Landing

**Press: `L`**

**Auto-Landing Sequence:**
1. All controls reset to center
2. Throttle gradually decreases
3. Drone descends smoothly
4. Motors stop when on ground
5. Status returns to: `STANDBY`

---

### Step 19: Emergency Stop

**Press: `ESC` at ANY time**

**What Happens:**
1. Display shows: `[!] ESC pressed - Emergency landing!`
2. Land command sent immediately
3. All controls reset
4. Drone descends rapidly
5. Script exits

**Use When:**
- Drone out of control
- Obstacle detected
- Any unsafe situation
- Ready to end session

---

## 📊 Understanding the HUD

### Control Values Explained

```
0x00 = Minimum (0)
0x80 = Center/Neutral (128)
0xFF = Maximum (255)
```

**Roll Example:**
```
0x00  [░░░░░░░░░░░░░░░░░░░░] ◄  Full Left
0x40  [█████░░░░░░░░░░░░░░░] ◄  Half Left
0x80  [██████████░░░░░░░░░░] CENTER
0xC0  [███████████████░░░░░] ►  Half Right
0xFF  [████████████████████] ►  Full Right
```

---

### Packet Statistics

**Packets Sent:**
- Updates at 50Hz (50 packets per second)
- Shows connection is active
- Typical: 1000+ packets in 20 seconds

**Telemetry:**
- `5301000000` = Drone acknowledgment
- Confirms bi-directional communication
- Changes indicate drone responses

---

## 🎯 Flight Patterns Practice

### Pattern 1: Square

```
1. Takeoff (T)
2. Forward 2 seconds (↑)
3. Hover 1 second (release)
4. Right 2 seconds (→)
5. Hover 1 second
6. Backward 2 seconds (↓)
7. Hover 1 second
8. Left 2 seconds (←)
9. Land (L)
```

---

### Pattern 2: Circle

```
1. Takeoff (T)
2. Hold ↑ + Q (forward + rotate left)
3. Maintain for 8-10 seconds
4. Release both keys
5. Land (L)
```

---

### Pattern 3: Hover Practice

```
1. Takeoff (T)
2. Ascend to 2m (SPACE for 3 seconds)
3. Hover for 10 seconds (no input)
4. Observe drift and make corrections
5. Descend (SHIFT)
6. Land (L)
```

---

## ⚠️ Troubleshooting

### Problem: "Cannot bind to port 7099"

**Cause:** Port already in use

**Solution:**
```bash
# Find process using port
sudo lsof -i :7099

# Kill the process
sudo kill -9 [PID]

# Restart script
python3 Drone.py
```

---

### Problem: No telemetry received

**Symptoms:**
```
[!] Warning: No telemetry received (drone may not be responding)
```

**Solutions:**
1. **Check connection:**
   ```bash
   ping 192.168.1.1
   ```

2. **Verify drone is powered on:**
   - Check LED status
   - Ensure battery charged

3. **Close official app:**
   - Drone can only accept one connection
   - Disconnect phone app

4. **Restart drone:**
   - Power off
   - Wait 10 seconds
   - Power on
   - Reconnect

---

### Problem: Drone doesn't respond to commands

**Checklist:**
1. ✓ Motors armed? (Press `A`)
2. ✓ Status shows "ARMED & FLYING"?
3. ✓ Packets Sent counter increasing?
4. ✓ Telemetry showing data?

**If all above are YES:**
- Drone may need recalibration
- Try emergency stop (ESC) and restart
- Check propeller installation

---

### Problem: Drone drifts during hover

**This is NORMAL:**
- Consumer drones have basic stabilization
- Indoor air currents affect flight
- Manual corrections needed

**Improve hovering:**
- Fly in windless environment
- Make small, gentle corrections
- Practice smooth control inputs

---

### Problem: Controls feel inverted

**Check orientation:**
- Script assumes drone "forward" = front LEDs
- If rear is facing you, controls seem inverted
- Rotate drone or adjust mentally

---

## 🛡️ Safety Guidelines

### Pre-Flight

✓ **Environment:**
- Indoor: minimum 3m × 3m clear space
- Outdoor: 5m clearance, no wind
- Away from people and pets
- No overhead obstacles

✓ **Drone:**
- Fully charged battery
- Propellers secure
- No visible damage
- Firmware updated

✓ **Controller:**
- Laptop fully charged or plugged in
- Script tested and working
- Familiar with emergency stop

---

### During Flight

✓ **Maintain:**
- Visual line of sight
- Attention on drone
- Finger near ESC key
- Calm and deliberate movements

✓ **Avoid:**
- Flying near people
- Flying near obstacles
- Aggressive maneuvers
- Overconfidence

---

### Post-Flight

✓ **Always:**
- Land before battery critical
- Disarm motors (script does automatically)
- Disconnect from Wi-Fi
- Power off drone
- Remove battery if storing

---

## 📈 Skill Progression

### Beginner (Day 1)
- ✓ Connect to drone
- ✓ Arm motors
- ✓ Takeoff and land
- ✓ Hover practice
- ✓ Emergency stop

### Intermediate (Week 1)
- ✓ Forward/backward flight
- ✓ Left/right flight
- ✓ Altitude control
- ✓ Basic rotations
- ✓ Simple patterns

### Advanced (Month 1)
- ✓ Combined movements
- ✓ Smooth transitions
- ✓ Complex patterns
- ✓ Precision control
- ✓ Long duration flights

---

## 🎓 Key Takeaways

1. **Pre-emptive control is simple** - First to connect wins
2. **UDP protocol is unencrypted** - All commands visible
3. **No authentication required** - Drone trusts first connection
4. **Bi-directional handshake needed** - Must listen on port 7099
5. **50Hz update rate critical** - Maintains responsive control

---

## 🔗 Next Steps

Now that you've mastered basic control:

1. ✅ [Deauthentication Attack](deauth-attack.md) - Hijack from active pilot
2. ✅ [Packet Injection](packet-injection.md) - Advanced mid-flight hijacking
3. Study protocol details in main README

---

## ⚖️ Legal Reminder

**This control method demonstrates:**
- Lack of authentication (security flaw)
- Unencrypted communication (privacy issue)
- "First-connect" vulnerability (design flaw)

**Only use on:**
- ✅ Your own drone
- ✅ With permission
- ✅ In safe environment
- ❌ NEVER on others' drones

**Unauthorized drone hijacking = Federal crime**

---

**Happy (Legal) Flying!** 🚁✈️🔐