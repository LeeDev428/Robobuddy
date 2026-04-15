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
