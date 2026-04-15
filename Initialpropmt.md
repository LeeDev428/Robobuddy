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