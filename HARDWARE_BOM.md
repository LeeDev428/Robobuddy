# 🤖 RoboBuddy Hardware Bill of Materials (BOM)

> **Architecture Note:** The robot is tethered to your PC (GTX 1650) for GPU-accelerated YOLO vision. The Pi handles only servo control. All ML inference, vision processing, and data storage happen on your laptop.

---

## 📋 Quick Summary

| Category | Est. Cost | Purpose |
|----------|-----------|---------|
| **Core Brain (Raspberry Pi)** | ₱3,500–4,500 | Motor control, servo driver, network bridge |
| **Motion (Servos + Bracket)** | ₱2,000–3,500 | Head tilt/pan, arm wave |
| **Power Supply** | ₱1,500–2,500 | Stable 5V/2A for Pi, 6V/2A for servos |
| **Storage (SSD)** | ₱1,200–3,000 | Fast detection logs, YOLO weights, conversation history |
| **Connectivity** | ₱500–1,500 | WiFi/USB, microphone, speaker |
| **3D Printed Chassis** | ₱1,000–2,000 (printing cost) | Head, arm holders, cable management |
| **Miscellaneous** | ₱800–1,500 | Breadboard, jumpers, connectors, headers |
| **TOTAL** | **₱10,500–18,500** | — |

---

## 🧠 1. Core Controller (Raspberry Pi)

### Primary Choice: Raspberry Pi 4 Model B (4GB recommended for your use case)

| Component | Spec | Why | Cost |
|-----------|------|-----|------|
| **Raspberry Pi 4 Model B** | 4GB RAM (or 8GB if budget) | Enough to run socket server + servo control + WiFi. Not running YOLO here—your PC does that. | ₱2,500–3,500 |
| **MicroSD Card** | 32GB UHS-I | Boot OS, Pi-side scripts. Speed matters for logging commands. | ₱400–600 |
| **Power Supply** | 5V/3A USB-C | Stable supply prevents servo lag/glitches. Official is best. | ₱600–800 |

### Why Raspberry Pi 4?
- Stable GPIO for servo control via PCA9685
- Dual WiFi (2.4/5GHz) for reliable laptop→Pi communication
- Affordable entry point; no need for Jetson (since ML runs on your GTX 1650)
- Plenty of community examples for servo control

---

## 🎮 2. Motion Control (Servos + Driver)

### Servo Driver: PCA9685 16-Channel PWM Module

| Component | Spec | Why | Cost |
|-----------|------|-----|------|
| **PCA9685 Breakout** | 16-channel, I2C | Daisy-chain up to 62 modules; clean control of multiple servos. Standard for hobby robotics. | ₱150–250 |
| **Micro Servo Motors** | SG90 or MG90S (metal gear) | SG90: cheap, plastic gears (OK for demo). MG90S: metal gears, smoother (recommended). | ₱300–500/each |
| **Number of Servos** | Suggested: 4–6 | 2 for head (pan/tilt), 1–2 for arm, 1–2 for backup/future. Start with 2. | — |
| **Servo Power Supply** | 6V/2A regulated | Do NOT power servos from Pi GPIO. Use separate 6V supply. | ₱800–1,200 |

### Servo Configuration for Beginner Build:
1. **Servo 0 (Head Pan):** Left/Right turning
2. **Servo 1 (Head Tilt):** Up/Down nod
3. **Servo 2 (Arm):** Waving motion
4. **Servo 3 (Optional):** Backup or small mouth movement

### Wiring Strategy:
```
Pi GPIO pins (I2C):
  Pin 3 (SDA) → PCA9685 SDA
  Pin 5 (SCL) → PCA9685 SCL
  GND → PCA9685 GND

PCA9685 Servo Ports:
  Port 0 → Head Pan (SG90)
  Port 1 → Head Tilt (SG90)
  Port 2 → Arm Wave (MG90S)
  Port 3 → Reserved

Power:
  6V supply GND → PCA9685 GND
  6V supply + → PCA9685 V+ (through LDO if needed)
  Servos connect directly to PCA9685 slots (power rails already on breakout)
```

---

## 🔋 3. Power Management

### Recommended Setup (Beginner-Safe):

| Component | Spec | Why | Cost |
|-----------|------|-----|------|
| **USB-C Power for Pi** | 5V/3A, certified | Stable power = no random reboots during socket transmission | ₱600–800 |
| **Servo Power Supply** | 6V/2A, regulated | Separate from Pi PSU avoids voltage drops. Use quality supply to prevent servo jitter. | ₱800–1,200 |
| **Power Distribution Module** | Optional: XT60 connectors + fused panel | Clean wire management. Not essential for first prototype but saves debugging time. | ₱300–500 |

### Do NOT Do:
- ❌ Power servos from Pi GPIO (max 50mA per pin → servos stall/brown-out the Pi)
- ❌ Use cheap wall adapters (noisy power → servo vibration and detection lag)

---

## 💾 4. Storage (Critical for Your ML Workflow)

### Strategy:
1. **Laptop SSD (Primary):** Where you run YOLO, store raw detection logs, conversation history
2. **Raspberry Pi (Boot):** MicroSD card for OS + Pi scripts only
3. **Optional External SSD:** Portable backup of detection database

### Recommended Laptop Storage Setup:

| Device | Capacity | Speed | Purpose | Cost |
|--------|----------|-------|---------|------|
| **NVMe SSD** | 512GB–1TB | PCIe 4.0 (7GB/s) | Laptop internal. YOLO inference cache + detection frames + chat logs. | ₱2,500–4,000 |
| **External SSD (optional)** | 256GB–512GB | USB 3.1 Gen2 (500MB/s) | Nightly backup of detection DB + conversation history. Portable for demos. | ₱1,500–2,500 |

### Data Storage Breakdown (Estimation):
```
Per Detection Frame (YOLO output):
  - Timestamp: 30 bytes
  - Confidence score: 20 bytes
  - Bounding box coords: 50 bytes
  - Person ID (future): 20 bytes
  Total per detection: ~120 bytes

Expected Usage (8 hrs/day continuous):
  - 30 detections/min × 60 min × 8 hrs = 14,400 detections/day
  - 14,400 × 120 bytes = ~1.7 MB/day
  - Per year: ~620 MB (easily fits in 1TB SSD)

Per Conversation:
  - User text: 200–500 bytes
  - AI response: 500–2000 bytes
  - Timestamp, metadata: 100 bytes
  Total per exchange: ~1–3 KB
  
Expected Usage (20 conversations/day):
  - 20 × 2 KB = ~40 KB/day
  - Per year: ~14 MB (negligible)
```

### Storage File Structure (Recommended):
```
C:\RoboBuddy_Data\
├── detections\
│   └── 2026-04-15_detections.jsonl
├── conversations\
│   └── 2026-04-15_chat_log.jsonl
├── models\
│   ├── yolov8n.pt
│   └── yolov8n_face.pt (future)
└── backups\
    └── weekly_snapshot_2026-04-13.tar.gz
```

---

## 📷 5. Vision & Audio Input

| Component | Spec | Why | Cost |
|-----------|------|-----|------|
| **USB Webcam** | 1080p/30fps, wide-angle (90°+) | Good for YOLO person detection. USB = laptop direct connection. | ₱600–1,200 |
| **USB Microphone** | Cardioid, noise-canceling (optional) | Better than laptop mic. Connects directly to your PC. | ₱300–800 |
| **USB Speaker** | 2W–5W, small | For TTS output. Can mount on robot chassis. | ₱200–600 |

### Recommendation:
- **Logitech C920** (1080p, well-tested with OpenCV): ₱1,000–1,500
- **Blue Yeti USB** (professional mic, overkill but future-proof): ₱1,500–2,000
- **Budget combo:** Cheap USB speaker + phone microphone via USB adapter: ₱500–800

---

## 📡 6. Connectivity & Communication

### Pi ↔ Laptop Connection Options:

| Method | Latency | Reliability | Setup Difficulty | Cost |
|--------|---------|-------------|------------------|------|
| **WiFi (Recommended)** | 10–50ms | 95%+ if good router | Easy (auto-discovery possible) | ₱0 (your home WiFi) |
| **USB Tether** | <1ms | 99.9% | Medium (Pi can be powered via USB) | ₱100–200 (USB-A to USB-C cable) |
| **Ethernet + PoE Hat** | <1ms | 99.9% | Medium | ₱1,500–2,000 |

### Beginner Recommendation:
**WiFi is best for demos** (no cables to your PC). Just ensure:
- Your Pi is on the same network as your laptop
- Firewall allows port 5000 (or whatever you choose) traffic

---

## 🖨️ 7. 3D Printed Chassis & Molds

### Why 3D Print?
- **Lightweight** (PLA/PETG): ~50–100g for small robot
- **Quick iteration** (re-print in hours if design changes)
- **Low cost** (printing service ₱50–100/hr, or DIY printer ₱8k–15k one-time)
- **Professional look** for your technopreneurship demo

### Recommended Design (Beginner Kit):

| Part | Dimensions | Material | Print Time | Cost (at printing service) |
|------|-----------|----------|------------|---------------------------|
| **Head Housing** | ~80mm dia. sphere (split) | PLA | 3–4 hrs | ₱100–150 |
| **Servo Mount Bracket** | 40×30mm | PLA | 30 min | ₱20–30 |
| **Arm Link** | ~60mm extruded L-shape | PETG (stronger) | 1–2 hrs | ₱30–50 |
| **Base/Chassis** | 150×100×80mm box | PLA | 5–6 hrs | ₱150–200 |
| **Camera Mount** | 30×20mm clip | PLA | 30 min | ₱20–30 |
| **TOTAL Print Cost** | — | — | ~15 hrs | **₱320–460** |

### Where to Get Files (Free/Cheap):
1. **Thingiverse** (https://www.thingiverse.com) — Search "robot head servo mount" or "pan-tilt bracket"
2. **Printables** (https://www.printables.com) — Similar, community-driven
3. **MyMiniFactory** — Higher-quality paid designs (₱50–200/file)

### DIY Chassis Recommendation for Your First Build:
**Simple "Cute Bot" Head:**
- Hollow sphere (PLA, split into 2 halves)
- Servo motor mounted inside for head tilt
- Second servo on base for pan
- Camera mounted on front
- Example design: Search "Roboflow robot head 3D print"

### Local 3D Printing Services (Philippines):
- **PrintNow.ph** — ₱50–100/hr machine time + material
- **Makinate** — Same rate, good quality
- **Local maker spaces** — Often ₱200–500/month membership (unlimited printing)

---

## 🧩 8. Miscellaneous Components & Wiring

| Component | Spec | Qty | Why | Cost |
|-----------|------|-----|-----|------|
| **Breadboard** | 830 holes, solderless | 1 | Circuit prototyping (servo testing) | ₱100–200 |
| **Jumper Wires** | M-M, M-F, 20cm | 50pcs assorted | Connecting Pi GPIO to PCA9685 | ₱100–150 |
| **Pi GPIO Headers** | 2×20 or breakout | 1–2 | If your Pi doesn't have pre-soldered headers | ₱50–100 |
| **I2C Pullup Resistors** | 4.7kΩ (optional) | 2 | Improves I2C signal; often built into PCA9685 | ₱20–50 |
| **XT60 Connectors** | Pair (male/female) | 2–3 | Clean power distribution | ₱50–100 |
| **Fuse Holder + Fuses** | 5A–10A | 1 set | Servo PSU protection | ₱100–200 |
| **Heatsinks** | Small, for Pi | 1 set | Passive cooling (Pi 4 gets warm under YOLO load over SSH) | ₱50–100 |
| **Solder + Iron** | 60/40 tin/lead + 25W iron | 1 set | If you want permanent connections (not essential for first prototype) | ₱300–600 |

---

## 🔧 9. Tools & Accessories (Nice-to-Have)

| Tool | Why | Cost |
|------|-----|------|
| **Digital Multimeter** | Debugging power issues, GPIO voltages | ₱200–500 |
| **USB Logic Analyzer** | Debugging I2C/PWM signals | ₱300–800 |
| **Servo Tester** | Test individual servo before Pi integration | ₱100–300 |
| **Cable Management Kit** | Velcro, clips, sleeves | ₱100–200 |

---

## 📊 Complete BOM Table (To-Buy Checklist)

| Item | Qty | Unit Cost | Total | Notes |
|------|-----|-----------|-------|-------|
| **Raspberry Pi 4 Model B (4GB)** | 1 | ₱3,000 | ₱3,000 | Core controller |
| **MicroSD Card 32GB** | 1 | ₱500 | ₱500 | Pi OS boot |
| **Pi Power Supply 5V/3A** | 1 | ₱700 | ₱700 | Official recommended |
| **PCA9685 Breakout** | 1 | ₱200 | ₱200 | Servo driver |
| **SG90 Servo Motor** | 4 | ₱350 | ₱1,400 | Head (2×) + Arm (1×) + Spare (1×) |
| **MG90S Servo Motor** | 2 | ₱450 | ₱900 | Backup or stronger arm drive |
| **Servo Power Supply 6V/2A** | 1 | ₱1,000 | ₱1,000 | Separate PSU for servos |
| **USB Webcam 1080p** | 1 | ₱900 | ₱900 | Vision input |
| **USB Microphone** | 1 | ₱500 | ₱500 | Audio input |
| **USB Speaker 2W** | 1 | ₱400 | ₱400 | TTS output |
| **External SSD 256GB USB3.1** | 1 | ₱2,000 | ₱2,000 | Detection logs + chat backup |
| **Breadboard + Jumper Wires** | 1 set | ₱250 | ₱250 | Prototyping |
| **GPIO Headers + Connectors** | 1 set | ₱200 | ₱200 | Header connectivity |
| **XT60 + Fuse Kit** | 1 set | ₱300 | ₱300 | Power distribution |
| **3D Printing (15 hrs @ ₱75/hr + filament)** | — | ₱75/hr | ₱1,350 | Chassis, mounts |
| **Miscellaneous (cables, solder, heatsinks)** | — | — | ₱800 | Buffer for small items |
| | | **TOTAL** | **₱13,900** | |

---

## 🎯 Beginner Assembly Roadmap

### Phase 1: Get It Talking (Week 1)
1. Laptop: Install Python env + requirements
2. Run `python main.py --stage 1` (Groq API test)
3. USB mic + speaker test (no hardware needed yet)

### Phase 2: Add Vision (Week 2–3)
1. Assemble Pi (power, MicroSD, basic SSH access)
2. Connect Pi to laptop WiFi
3. Test YOLO on laptop (GTX 1650 runs detection)
4. Verify Pi socket server receives commands

### Phase 3: Add Motion (Week 3–4)
1. Assemble PCA9685 on breadboard
2. Connect 1–2 servo motors for testing
3. Program servo test script (sweep 0–180°)
4. Run `python main.py --stage 3` (socket → servo)

### Phase 4: Full Integration + 3D Chassis (Week 5–6)
1. Print chassis parts
2. Mount all servos and electronics in chassis
3. Run `python main.py --stage 4` (full loop)
4. Demo recording for technopreneurship subject

---

## 💡 Storage + Data Strategy (Important for Your Subject)

### What Your ML System Needs to Track:

```python
# detection_log.py (Example structure)
{
    "timestamp": "2026-04-15T10:30:45.123Z",
    "person_detected": True,
    "confidence": 0.87,
    "bounding_box": {"x": 150, "y": 80, "w": 200, "h": 300},
    "person_id": None,  # NULL until face rec implemented
    "frame_hash": "abc123def456...",  # For deduplication
    "location": "demo_room"
}

# conversation_log.py
{
    "timestamp": "2026-04-15T10:31:02.456Z",
    "user_input": "Hi RoboBuddy, how are you?",
    "ai_response": "Hello! I'm doing great, thanks for asking...",
    "model_used": "llama-3.1-8b-instant",
    "tokens_used": 145,
    "person_detected_at_time": True
}
```

### Backup Strategy for Demos:
- **Weekly export** detection + conversation logs to external SSD
- **Cloud backup** option: AWS S3 / Google Drive (for future face rec model training)

---

## ⚠️ Important Beginner Notes

1. **GPU Utilization:** Your GTX 1650 can run YOLOv8n at ~50 FPS. YOLO runs on your laptop, not the Pi. The Pi only receives detection results + sends servo commands.

2. **Network Latency:** WiFi servo commands (~10–50ms latency) are acceptable for demo purposes. For smoother movement, use Ethernet or USB tether.

3. **Power Budget:**
   - Pi 4 idle: ~3W
   - Pi 4 active (socket server): ~8W
   - 4× SG90 servos (all moving): ~6W
   - **Total:** ~14W (well under typical USB PSU)

4. **Storage Pricing:** Don't buy the most expensive SSD. A mid-range NVMe (e.g., Kingston A2000 or Samsung 970 EVO Plus) is more than enough. You'll never fill 512GB with detection logs.

5. **3D Printing Material:**
   - **PLA:** Easiest to print, biodegradable, good for prototypes (demo-safe)
   - **PETG:** Stronger, more durable, slightly harder to print (for final version)
   - **Resin:** Smoother finish, more expensive, requires curing (overkill for your demo)

---

## 🎓 Technopreneurship Subject Demo Talking Points

When presenting to your subject teacher/evaluator:

✅ **Show the architecture:** "My PC's GTX 1650 handles vision ML. The Pi is just a remote puppet that moves servos based on what the camera sees."

✅ **Show the data pipeline:** "Every detection is logged here [show external SSD]. In the future, I can train face recognition on this data."

✅ **Show the cost breakdown:** "Total cost is ₱14k for a prototype that would cost 10× more if fully autonomous with embedded GPU."

✅ **Scalability angle:** "If this goes to production, I swap the Pi for a Jetson Nano (embedded GPU) and it becomes fully independent."

---

## 📝 Next Steps for You

1. **Verify inventory** against this BOM
2. **Order components** (suggest: Lazada/Shopee bulk orders to save shipping)
3. **Set up laptop:** Git clone your Robobuddy repo, install requirements, get Stage 1 running
4. **Assemble Pi:** Flash Raspberry Pi OS, set up SSH, test socket connection
5. **I can help you with:** Raspberry Pi server script, 3D model recommendations, sensor calibration, database schema for logging

---

**Questions?** Just ask. I can also provide:
- Raspberry Pi control script (servo PWM via I2C)
- Database schema for detection + conversation logging
- 3D model starter files
- Wiring diagrams (ASCII or visual)
