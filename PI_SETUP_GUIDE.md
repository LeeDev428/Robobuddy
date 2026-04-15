# 🤖 Raspberry Pi Setup Guide for RoboBuddy

> This guide covers setting up your Raspberry Pi 4 as the servo control server for RoboBuddy.

---

## 📋 Prerequisites

- Raspberry Pi 4 (4GB recommended)
- MicroSD card (32GB+, class 10)
- Power supply (5V/3A USB-C)
- Ethernet cable OR WiFi setup
- PCA9685 servo driver (I2C)
- Servo motors connected to PCA9685
- Laptop with RoboBuddy code (already configured in main branch)

---

## 🔧 Step 1: Flash Raspberry Pi OS

### On your laptop:

1. **Download Raspberry Pi Imager**
   - Visit: https://www.raspberrypi.com/software/
   - Download and install for your OS

2. **Flash MicroSD Card**
   ```
   - Insert MicroSD card into laptop card reader
   - Open Raspberry Pi Imager
   - Choose Device: Raspberry Pi 4
   - Choose OS: Raspberry Pi OS (64-bit Lite) [no GUI to save resources]
   - Choose Storage: Your MicroSD card
   - Click NEXT → EDIT SETTINGS:
     - Set hostname: robobuddy (or similar)
     - Enable SSH (password auth)
     - Set username: pi, password: raspberry
     - Configure WiFi (if not using Ethernet)
   - Click SAVE → YES
   - Wait ~5 minutes for flashing to complete
   ```

3. **Eject card and insert into Raspberry Pi**

---

## 🌐 Step 2: Connect to Raspberry Pi

### Option A: Ethernet (Fastest, Most Reliable)
```bash
# Connect Pi to router via Ethernet cable
# On your laptop, find the Pi's IP:
ping robobuddy.local

# Or check your router's connected devices list
```

### Option B: WiFi (Convenient for Demos)
```bash
# Pi should auto-connect to WiFi (configured during flashing)
# On your laptop:
ssh pi@robobuddy.local
# Password: raspberry
```

### Option C: USB Serial Console (If network fails)
```bash
# Connect Pi to laptop via USB-C cable
# Use PuTTY or similar serial terminal
# Serial settings: 115200 baud, 8 data bits, 1 stop bit
```

---

## 📦 Step 3: Update System & Install Dependencies

```bash
# SSH into Pi (replace robobuddy.local with IP if needed)
ssh pi@robobuddy.local
password: raspberry

# Update package lists
sudo apt update
sudo apt upgrade -y

# Install required system packages
sudo apt install -y python3-pip python3-dev python3-venv git i2c-tools

# Enable I2C (for PCA9685 communication)
sudo raspi-config
# Navigate to: Interfacing Options → I2C → Enable
# Exit and reboot: sudo reboot

# After reboot, verify I2C is working:
i2cdetect -y 1
# You should see "40" in the grid (PCA9685 I2C address)
```

---

## 🐍 Step 4: Clone RoboBuddy Repo & Install Python Dependencies

```bash
# Still SSH'd into Pi:

# Clone your repo
cd ~
git clone https://github.com/LeeDev428/Robobuddy.git
cd Robobuddy

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Pi-specific dependencies
pip install --upgrade pip

# Install servo control libraries
pip install adafruit-circuitpython-pca9685 adafruit-circuitpython-busdevice board

# Install other RoboBuddy requirements (optional on Pi, mainly for testing)
pip install pyttsx3 pyaudio requests groq
```

---

## 🔌 Step 5: Hardware Wiring Setup

### PCA9685 I2C Connection to Raspberry Pi

```
PCA9685 Breakout → Raspberry Pi GPIO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SDA (Pin 3)    → GPIO 2 (Pin 3)    [I2C Data]
SCL (Pin 5)    → GPIO 3 (Pin 5)    [I2C Clock]
GND            → GND (Pin 6, 9, etc)
V+ (5V)        → 5V (Pin 2, 4)

Servo Motors → PCA9685 Slots
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Channel 0 → Head Pan (SG90)
Channel 1 → Head Tilt (SG90)
Channel 2 → Arm Wave (MG90S)

Servo Power Supply → PCA9685
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
6V PSU +  → PCA9685 V+
6V PSU -  → PCA9685 GND (shared with Pi GND)
```

### Wiring Photo Checklist:
- [ ] PCA9685 SDA connected to Pi GPIO 2
- [ ] PCA9685 SCL connected to Pi GPIO 3
- [ ] PCA9685 GND connected to Pi GND
- [ ] Servo motors plugged into PCA9685 slots
- [ ] 6V servo power supply connected to PCA9685 V+ and GND
- [ ] All connections soldered or secure jumpers (no loose wires)

### Test I2C Connection:
```bash
# Still SSH'd into Pi:
i2cdetect -y 1

# Expected output (PCA9685 at address 0x40):
#      0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
# 00:                         -- -- -- -- -- -- -- --
# 10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
# 20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
# 30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
# 40: 40 -- -- -- -- -- -- -- -- -- -- -- -- -- -- --  ← Here!
# ...
```

---

## 🚀 Step 6: Test Servo Server Manually

```bash
# Still SSH'd into Pi:
cd ~/Robobuddy

# Run the servo server in test mode
python3 pi_servo_server.py

# Expected output:
# ==================================================
# RoboBuddy Raspberry Pi Servo Control Server
# ==================================================
# [SERVO] PCA9685 initialized successfully
# [SERVO] All servos initialized to safe positions
# [SERVER] Listening on 0.0.0.0:5000
```

### On a separate terminal (your laptop):
```bash
# Test sending commands to Pi
# Replace 192.168.1.50 with your Pi's actual IP

import socket

sock = socket.create_connection(("192.168.1.50", 5000), timeout=2.0)
sock.sendall(b"HEAD_LEFT\n")
sock.close()

# Servo should turn left!
```

---

## 📝 Step 7: Set Up Pi Servo Server to Auto-Start

### Option A: systemd Service (Recommended)

```bash
# Create service file
sudo nano /etc/systemd/system/robobuddy-servo.service
```

Paste this content:
```ini
[Unit]
Description=RoboBuddy Servo Control Server
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/Robobuddy
Environment="PATH=/home/pi/Robobuddy/venv/bin"
ExecStart=/home/pi/Robobuddy/venv/bin/python3 pi_servo_server.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable robobuddy-servo
sudo systemctl start robobuddy-servo

# Check status:
sudo systemctl status robobuddy-servo

# View logs:
sudo journalctl -u robobuddy-servo -f
```

### Option B: cron + screen (Simple Alternative)

```bash
# Edit crontab:
crontab -e

# Add this line (runs at Pi startup):
@reboot cd /home/pi/Robobuddy && source venv/bin/activate && python3 pi_servo_server.py > /tmp/robobuddy.log 2>&1
```

---

## ✅ Step 8: Verify Full System

### On your laptop:
```bash
# Ensure your Pi is reachable
ping robobuddy.local

# Test Stage 1 (Talking AI - no hardware needed yet)
python main.py --stage 1

# Test Stage 3 (with servo commands)
# Set environment:
$env:ROBOT_HOST="192.168.1.50"  # Or your Pi's IP
$env:GROQ_API_KEY="your_key"

python main.py --stage 3

# Try saying: "wave your arm"
# The servo should move!
```

---

## 🐛 Troubleshooting

### Problem: `i2cdetect` shows nothing
**Solution:**
- Check SSH connection works: `ssh pi@robobuddy.local`
- Verify I2C is enabled: `sudo raspi-config` → Interfacing → I2C
- Check wiring: SDA on GPIO 2, SCL on GPIO 3, GND connected
- Reboot Pi: `sudo reboot`

### Problem: "ModuleNotFoundError: No module named 'adafruit_pca9685'"
**Solution:**
```bash
source ~/Robobuddy/venv/bin/activate
pip install adafruit-circuitpython-pca9685
```

### Problem: Servo not moving / twitching randomly
**Solution:**
- Check 6V power supply voltage (multimeter test)
- Verify servo power connector is firmly seated in PCA9685
- Test single servo manually:
  ```bash
  python3
  from pi_servo_server import ServoController
  servo = ServoController()
  servo.set_servo_position(0, 90)  # Should center
  ```

### Problem: Pi loses WiFi connection
**Solution:**
- Use Ethernet if possible (more stable for demos)
- If WiFi, reconfigure:
  ```bash
  sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
  ```
  Add your network details, then reboot

### Problem: Socket connection timeout from laptop
**Solution:**
- Verify Pi's IP: `hostname -I` (on Pi terminal)
- Verify firewall: `sudo ufw status` (likely disabled by default, that's OK)
- Test connectivity: `ping <pi_ip>` from laptop
- Check servo server is running: `sudo systemctl status robobuddy-servo`

---

## 📊 Monitoring & Logs

### Check if servo server is running:
```bash
# SSH into Pi:
sudo systemctl status robobuddy-servo

# View recent logs:
sudo journalctl -u robobuddy-servo -n 50
```

### Manual log file:
```bash
tail -f /tmp/robobuddy.log
```

---

## 🔄 Updating Code on Pi

```bash
# SSH into Pi:
cd ~/Robobuddy
git pull origin master

# Restart servo server if changes to pi_servo_server.py:
sudo systemctl restart robobuddy-servo
```

---

## 💡 Next Steps

1. **Deploy to Pi:** Follow steps 1–7 above
2. **Test locally:** Run Stage 3 with laptop + Pi connection
3. **Add 3D chassis:** Mount servos inside printed head
4. **Integrate webcam:** USB webcam plugged into laptop (YOLO runs there)
5. **Full Stage 4:** Person detection → greeting → conversation loop

---

## 📞 Quick Command Reference

```bash
# SSH into Pi
ssh pi@robobuddy.local

# Restart servo server
sudo systemctl restart robobuddy-servo

# Check I2C
i2cdetect -y 1

# View servo server logs
sudo journalctl -u robobuddy-servo -f

# Manual servo test
python3 pi_servo_server.py

# Check Pi IP address
hostname -I

# Reboot Pi
sudo reboot

# Shutdown Pi (safe)
sudo shutdown -h now
```

---

## 🎓 For Your Technopreneurship Presentation

**Talking Points:**
- "The Pi is only ₱3,500, acts as a remote servo puppet"
- "All ML inference (YOLO) runs on my laptop's GTX 1650"
- "Data is logged for future face recognition training"
- "Future scalability: Replace Pi with Jetson Nano for full autonomy"

---

**Stuck?** Check the main README.md or ask for help!
