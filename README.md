# Zora IoT-AI Interactive Robot Control System

Welcome to the Zora IoT-AI Interactive Robot Control System! This project showcases an innovative framework for human-robot interaction, leveraging advanced IoT and AI technologies to control a robotic arm and other devices through natural language commands.

Project Overview
The Zora system integrates a variety of cutting-edge technologies to create an interactive and responsive control system for robotic devices. At its core, it utilizes a Raspberry Pi 5 as the main processing unit, facilitating seamless communication between hardware peripherals and cloud-based AI services.

Key Features
Voice Command Input: Users can control the robotic arm using natural language commands captured through a USB-3 360-degree microphone.
Speech Recognition: The system employs Google's Voice Recognition Engine, accessed via the SpeechRecognition library, to accurately transcribe user commands.
AI Processing: Commands are processed using OpenAI's GPT-3.5-Turbo model, which generates appropriate responses and robotic control instructions.
Text-to-Speech Output: Google's Text-to-Speech API, integrated through the gTTS library, converts AI-generated text responses into audio played through stereo speakers.
Robust Control Mechanism: The UFactory xArm-7 robotic arm executes commands with high precision, thanks to a dedicated control box and the xArm-Python-SDK.
Latency Optimization: The system is designed to minimize latency, ensuring responsive and safe human-robot interaction even during peak server times.
System Architecture
The architecture comprises three main components:

Core Processing Unit: Raspberry Pi 5 handles real-time data processing, API communications, and hardware interfacing.
Admin System: Securely connected via SSH, this unit allows for development, supervision, and troubleshooting.
Robotic and IoT Devices: The xArm-7 robotic arm and other IoT devices are integrated for precise and complex task execution.
Future Enhancements
Enhanced User Interaction: Implement verbal start and end cues for recording to streamline voice command input.
Advanced Motion Control: Enable the system to record and replicate complex motion patterns, including reversing sequences.
3D Vision Integration: Explore the integration of a 3D vision system to improve situational awareness and interaction.
Expansion to Additional Devices: Extend the control capabilities to include other robotic devices, broadening the system's application scope.
