# RoboBuddy Hardware Shopping List (Philippines)

This is a buyer-friendly list with specific variants, estimated prices, and where you can buy each item.

Project setup assumed:
- AI and vision on your laptop with GTX 1650
- Raspberry Pi controls servos only
- Detection and conversation logs stored on fast SSD

## Buying Strategy
- Buy core parts first: Raspberry Pi, PCA9685, 2 to 4 servos, power supplies, webcam, mic.
- Add optional upgrades only after Stage 3 works.
- Prefer shops with high ratings, many sold units, and real photo reviews.

## A. Core Compute and Control

| Component | Recommended Variant | Good Alternatives | Estimated Price (PHP) | Where to Buy | Search Keywords |
|---|---|---|---:|---|---|
| Raspberry Pi | Raspberry Pi 4 Model B 4GB | Pi 4 8GB, Pi 5 4GB | 3,000 to 5,800 | Shopee Mall, Lazada Mall, official Pi resellers in PH | Raspberry Pi 4 4GB board only |
| MicroSD (OS only) | SanDisk Ultra 32GB A1 U1 | Samsung EVO Plus 32GB | 250 to 500 | Shopee Mall, Lazada Mall, Octagon, PC Express | microSD 32GB A1 U1 |
| Pi power adapter | Official 5V 3A USB-C | UGREEN or Anker 5V 3A certified | 450 to 900 | Shopee Mall, Lazada Mall, DataBlitz, PC Express | raspberry pi 5v 3a usb c power supply |

Notes:
- Pi 4 4GB is enough since your laptop handles ML.
- Avoid unknown no-brand adapters for Pi stability.

## B. Servo Motion System

| Component | Recommended Variant | Good Alternatives | Estimated Price (PHP) | Where to Buy | Search Keywords |
|---|---|---|---:|---|---|
| Servo driver | PCA9685 16-channel I2C board | Adafruit PCA9685 (higher quality) | 120 to 900 | Shopee, Lazada, Makerlab Electronics | pca9685 servo driver i2c |
| Head/arm servos | MG90S metal gear (x3 or x4) | SG90 plastic gear (budget) | MG90S: 140 to 260 each, SG90: 70 to 150 each | Shopee, Lazada, Alexan Electronics, e-Gizmo | mg90s metal gear servo 9g |
| Stronger arm option | MG996R high torque (x1) | DS3218 digital servo | 220 to 650 each | Shopee, Lazada | mg996r servo metal gear |

Variant guide:
- SG90: cheapest, fine for light demos, wears out faster.
- MG90S: best beginner balance for reliability and cost.
- MG996R: stronger, bigger, needs better mounting and more current.

## C. Power and Electrical Safety

| Component | Recommended Variant | Good Alternatives | Estimated Price (PHP) | Where to Buy | Search Keywords |
|---|---|---|---:|---|---|
| Servo PSU | 5V to 6V 3A regulated DC supply | 5V 5A if multiple servos | 300 to 1,000 | Shopee, Lazada, electronics stores | 6v 3a regulated power supply |
| Buck converter | LM2596 step-down module | MP1584 module | 40 to 120 | Shopee, Lazada | lm2596 buck converter |
| Fuse and holder | Inline blade fuse 3A to 5A | Mini fuse holder kits | 60 to 250 | Shopee, Lazada, auto supply | inline fuse holder 5a |
| Wire set | Silicone wire 22AWG + 20AWG | JST kit + dupont kit | 120 to 350 | Shopee, Lazada | silicone wire 22awg |

Important:
- Do not power servos from Pi GPIO pins.
- Share common ground between Pi and servo PSU.

## D. Vision and Audio Peripherals

| Component | Recommended Variant | Good Alternatives | Estimated Price (PHP) | Where to Buy | Search Keywords |
|---|---|---|---:|---|---|
| Webcam | Logitech C920/C922 1080p | Rapoo C260, A4Tech PK series | 900 to 4,500 | Shopee Mall, Lazada Mall, DataBlitz | logitech c920 webcam |
| USB microphone | Fifine K669B or K690 | BM800 with USB interface, Maono AU-A04 | 700 to 3,500 | Shopee Mall, Lazada Mall, JB Music | fifine k669b usb mic |
| Speaker | Creative Pebble 2.0 | Any USB powered 3W to 10W speaker | 700 to 1,800 | Shopee Mall, Lazada Mall, Octagon | creative pebble speaker |

Beginner pick:
- C920 + Fifine K669B + Creative Pebble is a stable combo.

## E. Data Storage for Logs and Future Face Recognition

| Component | Recommended Variant | Good Alternatives | Estimated Price (PHP) | Where to Buy | Search Keywords |
|---|---|---|---:|---|---|
| External SSD | Samsung T7 500GB USB 3.2 | Crucial X6/X8, Kingston XS1000 | 2,800 to 5,500 | Shopee Mall, Lazada Mall, DataBlitz | samsung t7 500gb |
| Internal NVMe SSD (if laptop upgrade) | WD SN770 1TB | Kingston NV2 1TB, Crucial P3 Plus 1TB | 2,700 to 4,800 | EasyPC, DynaQuest, PCHub, Lazada Mall | wd sn770 1tb nvme |
| Backup flash drive | SanDisk Extreme Pro 256GB | Kingston DataTraveler Max | 1,600 to 3,200 | Shopee Mall, Lazada Mall | sandisk extreme pro usb 3.2 |

Storage recommendation for your use case:
- Minimum: 500GB external SSD.
- Better: 1TB NVMe internal plus 500GB external backup.

## F. Chassis and 3D Print Materials

| Component | Recommended Variant | Good Alternatives | Estimated Price (PHP) | Where to Buy | Search Keywords |
|---|---|---|---:|---|---|
| Filament (prototype) | PLA+ 1.75mm 1kg | Standard PLA 1kg | 550 to 1,200 | Shopee, Lazada, 3D Manila | pla plus filament 1.75 |
| Filament (durable parts) | PETG 1.75mm 1kg | ABS (harder to print) | 700 to 1,500 | Shopee, Lazada | petg filament 1.75 |
| 3D printing service | Local print service per gram/hour | Maker spaces in your city | 300 to 2,000 total per robot shell | Facebook local 3D groups, Print service shops | 3d printing service philippines |
| Fasteners | M2/M3 screws and heat-set inserts | Self tapping screws | 120 to 450 | Shopee, Lazada, Handyman | m3 screw assortment |

Mold/chassis advice:
- For beginners, do 3D print parts first before investing in full mold tooling.
- Start with modular design: head module, arm module, base module.

## G. Wiring and Prototyping Essentials

| Component | Recommended Variant | Good Alternatives | Estimated Price (PHP) | Where to Buy | Search Keywords |
|---|---|---|---:|---|---|
| Breadboard | 830 tie-point full-size | Half-size boards | 90 to 250 | Shopee, Lazada | breadboard 830 |
| Jumper wires | Dupont M-M, M-F, F-F set | Premium silicone jumpers | 80 to 250 | Shopee, Lazada | dupont jumper wire set |
| Soldering kit | 60W temp-controlled iron | Pinecil V2 | 600 to 2,500 | Shopee, Lazada, Deeco | soldering station 60w |
| Multimeter | Uni-T UT33D+ | ANENG budget models | 300 to 1,200 | Shopee Mall, Lazada Mall, hardware stores | uni-t multimeter |

## H. Optional Upgrades (Future)

| Upgrade | Variant | Estimated Price (PHP) | Why |
|---|---|---:|---|
| UPS for Pi | UPS HAT or mini UPS | 1,200 to 3,500 | Safe shutdown and no brownouts |
| Better camera | Intel RealSense or depth cam | 8,000 to 20,000 | Better perception and future navigation |
| Face recognition camera path | Global shutter USB cam | 2,500 to 8,000 | Better face capture consistency |
| On-robot AI later | Jetson Orin Nano | 20,000 to 35,000 | Full standalone robot without laptop |

## Practical Store Recommendations (PH)
- Marketplace: Shopee Mall and Lazada Mall for best return policies and buyer protection.
- PC parts: EasyPC, DynaQuest, PCHub, DataBlitz for SSD and peripherals.
- Electronics: Makerlab Electronics, Alexan, e-Gizmo style stores for robotics components.
- 3D printing: local FB groups and city maker communities for faster turnaround.

## Suggested Purchase Packs

### Pack 1: Minimum Demo Build (Stage 1 to 3)
- Pi 4 4GB
- PCA9685
- 3x MG90S
- Pi adapter 5V 3A
- Servo PSU 6V 3A
- Webcam 1080p
- USB mic and speaker
- Breadboard and jumper kit
- Estimated total: 8,500 to 13,000

### Pack 2: Better Reliability Build
- Everything in Pack 1
- Extra 2x MG90S spare
- Samsung T7 500GB external SSD
- Better webcam (C920 or C922)
- Better mic (Fifine K669B)
- Estimated total: 13,000 to 19,000

### Pack 3: Presentation Ready Build
- Everything in Pack 2
- Full printed chassis set in PLA+/PETG
- Cable management and fastener kit
- Estimated total: 16,000 to 24,000

## What to Avoid
- Very cheap unbranded power adapters for Pi or servos.
- Fake high-capacity microSD cards from unknown sellers.
- Buying all parts from one seller without checking ratings and reviews.

## Fast Buying Checklist
- [ ] Pi 4 4GB
- [ ] microSD 32GB A1
- [ ] Pi 5V 3A adapter
- [ ] PCA9685 board
- [ ] MG90S x4
- [ ] Servo PSU 6V 3A
- [ ] Webcam 1080p
- [ ] USB mic
- [ ] USB speaker
- [ ] External SSD 500GB
- [ ] Breadboard and jumper kit
- [ ] PLA+ filament or print service budget

If you want, I can also create a second file with direct buy links and a final cart-style budget based on your preferred store, city, and maximum budget.