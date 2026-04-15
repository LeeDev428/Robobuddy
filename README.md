# 🤖 AI Interactive Companion Robot

## 📌 Project Overview

The AI Interactive Companion Robot is a hardware-integrated system that combines artificial intelligence, computer vision, and voice interaction to create a more natural and engaging way for humans to interact with technology.

The system is capable of detecting people in real time, initiating conversations, responding using AI-generated voice, and performing simple physical movements.

---

## 🎯 Goal

To develop an AI-powered robot that can detect users, engage in natural conversation, and respond through voice and movement, demonstrating the integration of multiple AI technologies into a single interactive system.

---

## ❗ Problem Statement

Traditional systems such as websites and mobile applications lack physical interaction and engagement. Users experience limited interaction that feels impersonal.

This project addresses the need for a more human-like, interactive, and accessible AI system that enhances user engagement in public and educational environments.

---

## ⚙️ System Architecture

### 🧠 Laptop (AI Processing)

* Runs YOLOv8 for person detection
* Handles speech recognition (Whisper)
* Sends requests to Groq API (Llama 3)
* Coordinates system logic

### 🤖 Raspberry Pi (Robot Controller)

* Controls servo motors (movement)
* Handles audio output (speaker)
* Executes physical actions

### ☁️ AI Services

* Groq API for conversational AI (Llama 3)

---

## 🧱 Software Structure

```text
Robobuddy/
├── ai_robot/
│   ├── __init__.py
│   ├── main.py
│   ├── vision.py
│   ├── speech_recognition.py
│   ├── conversation_ai.py
│   ├── tts.py
│   ├── robot_controller.py
│   └── config.py
├── main.py
├── requirements.txt
└── README.md
```

---

## 🚀 Stage-by-Stage Development

1. Stage 1: Talking AI only (Whisper -> Groq -> TTS)
2. Stage 2: Add YOLO person detection + greeting trigger
3. Stage 3: Add Raspberry Pi servo movement commands via socket
4. Stage 4: Full cycle improvements (re-greeting per detection cycle)

---

## 🧪 Setup (Windows)

1. Create and activate a virtual environment
2. Install dependencies
3. Set environment variables
4. Run the desired stage

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Environment variables (PowerShell example):

```powershell
$env:GROQ_API_KEY="your_key_here"
$env:GROQ_MODEL="llama-3.1-8b-instant"
$env:WHISPER_MODEL="base"
$env:ROBOT_HOST="192.168.1.50"
$env:ROBOT_PORT="5000"
```

Run commands:

```powershell
# Stage 1: talking AI only
python main.py --stage 1

# Stage 2: add person detection
python main.py --stage 2

# Stage 3: add movement socket commands
python main.py --stage 3

# Stage 4: full loop with repeated detection cycle
python main.py --stage 4
```

Optional flag:

```powershell
python main.py --stage 2 --no-preview
```

---

## 🔌 Raspberry Pi Socket Command Contract

Your Raspberry Pi server should listen for newline-separated commands:

* `HEAD_LEFT`
* `HEAD_RIGHT`
* `WAVE_ARM`
* `SPEAK_START`
* `SPEAK_END`

These are sent by `robot_controller.py`.

---

## 🧰 Suggested Hardware (For Your Technopreneurship Demo)

Essential:

* Raspberry Pi 4 (4GB or 8GB)
* PCA9685 servo driver
* 2 to 4 micro servo motors (SG90/MG90S)
* 5V external power supply for servos
* USB webcam (720p is enough for demo)
* USB microphone
* USB or 3.5mm speaker
* Breadboard + jumper wires

Recommended build extras:

* Pan-tilt bracket for head movement
* Lightweight acrylic/chassis frame
* Power bank or UPS hat for portability

---

## ⚠️ Notes

* `openai-whisper` may require FFmpeg installed in your system path.
* First YOLO run downloads model weights (`yolov8n.pt`) automatically.
* First Whisper run downloads the selected model (`base`, `small`, etc.).

---

## 🔄 System Flow

1. Camera detects a person using YOLOv8
2. System triggers greeting
3. User speaks through microphone
4. Speech is converted to text (Whisper)
5. Text is sent to Groq API
6. AI generates response
7. Response is converted to speech
8. Robot speaks and performs movement

---

## 🧩 Core Features

* Person Detection (Computer Vision)
* Voice Interaction (Speech-to-Text & Text-to-Speech)
* AI Conversation (Groq API)
* Minimal Robot Movement (Servo Motors)
* Real-time Interaction

---

## 🛠️ Technologies Used

### AI & Software

* Python
* YOLOv8 (Ultralytics)
* Whisper (Speech Recognition)
* Groq API (Llama 3)
* pyttsx3 / Piper TTS

### Hardware

* Raspberry Pi 4
* USB Camera
* Microphone
* Speaker
* Servo Motors

---

## 💰 Estimated Cost

Total Cost: ₱12,000 (approx.)

---

## 💼 Market Potential

This system can be used in:

* Schools and exhibitions
* Museums and public spaces
* Reception and customer service
* Interactive kiosks

---

## 🚀 Future Improvements

* Face Recognition
* Emotion Detection
* Full autonomous navigation
* Local AI model (offline mode)

---

## 👨‍💻 Developer

Lee Torres
