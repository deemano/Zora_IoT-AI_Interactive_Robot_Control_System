import subprocess
import speech_recognition as sr
import openai
import os
from gtts import gTTS
import time
import signal
import sys
from xarm.wrapper import XArmAPI
from pydub import AudioSegment
import re

# Ensure the API key is set correctly
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("API key not found. Set the OPENAI_API_KEY environment variable.")

# Initialize the OpenAI client
client = openai.OpenAI(api_key=api_key)

# Modes
XARM_MODE = "xarm"
DIALOGUE_MODE = "dialogue"
DRONE_MODE = "drone"
ACTIVE_MODE = None

arm = None  # xArm object will be initialized when needed

# Intro Zora
def adjust_speed(file_path, speed_factor):
    sound = AudioSegment.from_file(file_path)
    # Speed up the sound
    faster_sound = sound.speedup(playback_speed=speed_factor)
    faster_sound.export(file_path, format="mp3")

def greet_user():
    intro_text = ("Hi there! I'm Zora "#, the AI assistant from FML401 Robotics & AI Labs at Liverpool Hope University. "
                  #"I am also the first non-human Liverpool football fan; self-proclaimed, obviously. "
                  #"I'm here to help you navigate the exciting world of robotics and artificial intelligence.")
                  )
    tts = gTTS(text=intro_text, lang='en', slow=False)
    tts.save("intro.mp3")
    adjust_speed("intro.mp3", speed_factor=1.2)  # Increase speed by 50%
    os.system("mpg321 intro.mp3")


def initialize_arm():
    global arm
    if arm is None:
        try:
            arm = XArmAPI('192.168.1.242')  # Replace with the actual IP address of your xArm-7
            arm.connect()
            arm.motion_enable(enable=True)
            arm.set_mode(0)
            arm.set_state(0)
            print("Connected to xArm successfully")
        except Exception as e:
            print(f"Failed to connect to xArm: {e}")
            arm = None

def disconnect_arm():
    global arm
    if arm is not None:
        try:
            arm.disconnect()
            print("Disconnected from xArm successfully")
        except Exception as e:
            print(f"Failed to disconnect from xArm: {e}")
        arm = None

def release_audio_devices():
    processes = subprocess.run(['lsof', '/dev/snd'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    lines = processes.strip().split('\n')[1:]  # Skip the header line
    for line in lines:
        parts = line.split()
        pid = int(parts[1])
        try:
            os.kill(pid, signal.SIGKILL)
        except Exception as e:
            print(f"Failed to kill process {pid}: {e}")

def record_audio(duration=3, device="plughw:CARD=Microphone,DEV=0"):
    release_audio_devices()
    try:
        subprocess.run([
            "arecord",
            "--device=" + device,
            "--format=S16_LE",
            f"--duration={duration}",
            "--rate=16000",
            "--file-type=wav",
            "temp_audio.wav"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error recording audio: {e}")
        return False
    return True

def transcribe_audio(file_path="temp_audio.wav"):
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(file_path) as source:
            audio = recognizer.record(source)
        print("Audio captured, transcribing...")
        try:
            text = recognizer.recognize_google(audio)
            print(f"Transcription: {text}")
            return text
        except sr.UnknownValueError:
            print("I could not understand the audio")
            return None
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return None
    except Exception as e:
        print(f"Error with audio file: {e}")
        return None

def chat_with_gpt(prompt, mode):
    try:
        if mode == "xarm":
            messages = [
                {"role": "system", "content": "You are a helpful assistant for robotic arm operations. Respond with clear and direct commands for the robotic arm."},
                {"role": "user", "content": prompt}
            ]
        elif mode == "dialogue":
            messages = [
                {"role": "system", "content": "You are a conversational AI designed to engage in general discussion and provide information as requested."},
                {"role": "user", "content": prompt}
            ]
        elif mode == "drone":
            messages = [
                {"role": "system", "content": "You are assisting with drone operations. Provide guidance and support for controlling the drone."},
                {"role": "user", "content": prompt}
            ]
        else:
            # Default message if mode is not set or recognized
            messages = [
                {"role": "system", "content": "You are a helpful assistant. Provide assistance as requested."},
                {"role": "user", "content": prompt}
            ]

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error with OpenAI API: {e}")
        return None

def correct_common_mishearings(text):
    corrections = {
        "write": "right",
        "front": "forward",
        "beck": "back",
        "upward": "up",
        "downward": "down"
    }
    for wrong, right in corrections.items():
        text = re.sub(r'\b' + wrong + r'\b', right, text, flags=re.IGNORECASE)
    return text

def extract_distance(command):
    # Search for the first sequence of one or more digits
    match = re.search(r'\d+', command)
    if match:
        return int(match.group(0))  # Convert the found number to an integer
    return 0

def get_current_position():
    try:
        pos = arm.get_position()
        print(f"Received position data: {pos}, type: {type(pos)}")  # Print the position data and its type
        if pos is not None and pos[0] == 0:  # Check if the fetch was successful
            # Extract and return the Cartesian coordinates (x, y, z)
            return pos[1][0], pos[1][1], pos[1][2]  
        else:
            raise ValueError("Position data is invalid or fetch was unsuccessful")
    except Exception as e:
        print(f"Failed to get current position: {e}")
        return None, None, None

def move_xarm(axis, distance):
    print(f"Command to move on axis {axis} by {distance} units")
    current_x, current_y, current_z = get_current_position()
    if None in [current_x, current_y, current_z]:
        print("Error fetching current position. Cannot execute move command.")
        return

    if axis == 'x':
        target_x = current_x + distance
        command = lambda: arm.set_position(x=target_x, wait=True)
    elif axis == 'y':
        target_y = current_y + distance
        command = lambda: arm.set_position(y=target_y, wait=True)
    elif axis == 'z':
        target_z = current_z + distance
        command = lambda: arm.set_position(z=target_z, wait=True)
    else:
        print("Invalid axis. Cannot execute move command.")
        return

    try:
        command()
        print(f"Moving xArm along {axis} to {distance} units relative to current position")
    except Exception as e:
        print(f"Error moving xArm: {e}")


def process_command(transcribed_text):
    global ACTIVE_MODE
    corrected_text = correct_common_mishearings(transcribed_text)
    print(f"User said (corrected if needed): {corrected_text}")

    # Check for the stop command universally
    if "stop" in corrected_text.lower():
        print("Stop command received, halting current operations.")
        return "Operation halted by user."

    # Mode engagement commands
    if "engage arm" in corrected_text.lower():
        ACTIVE_MODE = XARM_MODE
        initialize_arm()
        return "Xarm mode activated."
    elif "engage dialogue" in corrected_text.lower():
        ACTIVE_MODE = DIALOGUE_MODE
        disconnect_arm()
        return "Dialogue mode activated."
    elif "engage drone" in corrected_text.lower():
        ACTIVE_MODE = DRONE_MODE
        disconnect_arm()
        return "Drone mode activated."
    elif "exit" in corrected_text.lower():
        print("Exit command received.")
        release_audio_devices()
        disconnect_arm()
        sys.exit(0)

    # Handle commands based on the active mode
    if ACTIVE_MODE == XARM_MODE:
        direction, axis_movement = None, None
        directions = {
            "right": ("y", "+"),
            "left": ("y", "-"),
            "up": ("z", "+"),
            "down": ("z", "-"),
            "forward": ("x", "+"),
            "back": ("x", "-")
        }
        for dir_keyword, (axis, move) in directions.items():
            if dir_keyword in corrected_text.lower():
                direction = dir_keyword
                axis_movement = (axis, move)
                break
        if axis_movement:
            distance = extract_distance(corrected_text)
            if axis_movement[1] == "+":
                move_xarm(axis_movement[0], distance)
            else:
                move_xarm(axis_movement[0], -distance)
            return f"Moving xArm {direction} by {distance} cm"
        else:
            return "Command not recognized or missing direction"
    elif ACTIVE_MODE == DIALOGUE_MODE or ACTIVE_MODE == DRONE_MODE:
        # Use chat_with_gpt for dialogue and drone interactions
        return chat_with_gpt(corrected_text, ACTIVE_MODE)
    else:
        return "Please activate a mode first."


def text_to_speech(text):
    tts = gTTS(text=text, lang='en', slow=False)  # Set slow to False for faster playback
    tts.save("response.mp3")
    os.system("mpg321 response.mp3")  # Plays the mp3 file containing the speech output

def signal_handler(sig, frame):
    print("Exiting gracefully...")
    release_audio_devices()
    disconnect_arm()  # Properly disconnect the arm
    sys.exit(0)

if __name__ == "__main__":
    greet_user()  # This will print the greeting message first
    signal.signal(signal.SIGINT, signal_handler)
    release_audio_devices()

    duration = 3  # Duration for audio recording
    device = "plughw:CARD=Microphone,DEV=0"  # ALSA device name

    while True:
        start_time = time.time()

        print(f"Recording for {duration} seconds using device {device}")
        if not record_audio(duration, device):
            time.sleep(1)
            continue
        record_end_time = time.time()

        transcribed_text = transcribe_audio()
        transcribe_end_time = time.time()

        gpt_end_time = None  # Ensure gpt_end_time is defined
        tts_end_time = None  # Ensure tts_end_time is defined

        if transcribed_text:
            print(f"User said: {transcribed_text}")
            if "exit" in transcribed_text.lower():
                print("Exiting the loop.")
                release_audio_devices()
                disconnect_arm()  # Properly disconnect the arm
                sys.exit(0)
            response = process_command(transcribed_text)
            gpt_end_time = time.time()

            if response:
                print(f"GPT says: {response}")
                text_to_speech(response)
                tts_end_time = time.time()

        total_time = time.time() - start_time
        print(f"Total time: {total_time:.2f} seconds")
        print(f"Recording time: {record_end_time - start_time:.2f} seconds")
        print(f"Transcription time: {transcribe_end_time - record_end_time:.2f} seconds")
        if gpt_end_time:
            print(f"GPT response time: {gpt_end_time - transcribe_end_time:.2f} seconds")
        if tts_end_time:
            print(f"TTS and playback time: {tts_end_time - gpt_end_time:.2f} seconds")

        time.sleep(1)  # Delay before the next loop iteration
