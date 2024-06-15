from flask import Flask, render_template_string, redirect, url_for
import subprocess
import psutil
import os
import signal

app = Flask(__name__)

# Existing functions like kill_existing_processes(), release_audio_device()...

@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>LHU IoT Dashboard</title>
        <style>
            body {
                background-image: url('/static/1341345_6704.jpg');
                background-size: cover;
                font-family: Arial, sans-serif;
                color: white;
            }
            .container {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 20px;
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                width: 80%;
                padding: 20px;
                background: rgba(0, 0, 0, 0.7);
                border-radius: 10px;
            }
            h1 {
                position: absolute;
                top: 4%;
                left: 50%;
                transform: translate(-50%, -50%);
                font-size: 2em;
            }
            button {
                width: 100%;
                height: 50px;
                font-size: 16px;
                background: #333;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                transition: background 0.3s;
            }
            button:hover {
                background: #555;
            }
            .status-indicator {
                text-align: center;
                padding: 10px;
                font-size: 18px;
                border-radius: 5px;
                background: #444;
            }
        </style>
    </head>
    <body>
        <h1>LHU IoT Dashboard</h1>
        <div class="container">
            <div class="status-indicator">Mode: Idle</div>
            <div></div>
            <div></div>
            <div></div>
            <form action="/reset_audio" method="post">
                <button type="submit">Reset Audio Devices</button>
            </form>
            <form action="/activate_xarm" method="post">
                <button type="submit">Activate xArm Mode</button>
            </form>
            <form action="/activate_dialogue" method="post">
                <button type="submit">Activate Dialogue Mode</button>
            </form>
            <form action="/activate_drone" method="post">
                <button type="submit">Activate Drone Mode</button>
            </form>
            <form action="/disconnect_xarm" method="post">
                <button type="submit">Disconnect xArm</button>
            </form>
            <form action="/emergency_stop" method="post">
                <button type="submit" style="background:red;">Emergency Stop</button>
            </form>
            <form action="/shutdown_system" method="post">
                <button type="submit">Shutdown System</button>
            </form>
        </div>
    </body>
    </html>
    ''')

# Example route implementations for the new actions
@app.route('/disconnect_xarm', methods=['POST'])
def disconnect_xarm():
    # Logic to disconnect xArm goes here
    return redirect(url_for('index'))

@app.route('/emergency_stop', methods=['POST'])
def emergency_stop():
    # Logic to halt all operations immediately
    return redirect(url_for('index'))

@app.route('/shutdown_system', methods=['POST'])
def shutdown_system():
    # Logic to safely shutdown or reboot the system
    return redirect(url_for('index'))

if __name__ == '__main__':
    kill_existing_processes()
    app.run(host='0.0.0.0', port=5000)
