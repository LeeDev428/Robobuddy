# AI Interactive Companion Robot Project

# Create a modular Python system for an AI robot with the following features:

# 1. Person detection using YOLOv8 with webcam input
# 2. When a person is detected, trigger a greeting event
# 3. Capture microphone input and convert speech to text using Whisper
# 4. Send text to Groq API using Llama 3 model for conversational response
# 5. Convert AI response to speech using pyttsx3 or Piper TTS
# 6. Send commands to Raspberry Pi via socket connection to control servo motors
# 7. Implement simple movements like head turning or arm waving

# Structure the project into modules:
# - vision.py: handles YOLO detection
# - speech_recognition.py: handles microphone input
# - conversation_ai.py: handles Groq API requests
# - tts.py: handles text-to-speech
# - robot_controller.py: sends commands to Raspberry Pi
# - main.py: orchestrates all components

# The system should:
# - Continuously monitor camera feed
# - Detect a person and greet them
# - Listen for user input
# - Generate AI response
# - Speak response
# - Trigger movement when speaking

# Write clean, modular, well-commented Python code

Create this folder structure:
ai-robot/
│
├── main.py
├── vision.py
├── speech_recognition.py
├── conversation_ai.py
├── tts.py
├── robot_controller.py
├── config.py
├── requirements.txt
└── README.md
Or if you have better and neat stucture, pls do it

- Start SIMPLE:

Step 1 → Talking AI (no movement)
Step 2 → Add person detection
Step 3 → Add servo movement
Step 4 → Improve design


- Check my entirecodebase comprehensively and review and understand it all systemmatically from migration/database, backend and frontend. Please follow the existing convention and dont over engineer and simplify it as long it will work and follows my requirements/concern issues. DId you get me? here's my codebase.  Understand, Breakdown and Execute and also Read and understand the 'D:\Programming\Personal-Projects\Robobuddy\README.md'. Did you get me all?