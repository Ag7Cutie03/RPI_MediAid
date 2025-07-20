# MedDispenser

A web-based smart medical dispenser for Raspberry Pi, designed to automate and track medicine dispensing, provide reminders, and offer drug information with text-to-speech support.

## Features
- **Web Interface**: User-friendly dashboard for patients and admins (Flask-based)
- **User Authentication**: Registration, login, and admin management
- **Tray Management**: Assign, reset, and monitor medicine trays
- **Automated Dispensing**: Servo-controlled trays for scheduled dispensing
- **Drug Information Lookup**: Fetches instructions from FDA API and reads them aloud
- **Text-to-Speech**: Uses Google TTS (gTTS) for spoken instructions and reminders
- **Dispense History**: Tracks and displays dispense events per user
- **Admin Tools**: Emergency password reset, user and tray statistics

## Hardware Requirements
- Raspberry Pi 4B (or compatible)
- 2x SG90 Servo Motors (connected to GPIO 32 and 33)
- Audio output (for TTS)
- (Optional) Display for web interface

## Software Requirements
- Python 3.8+
- See `requirements.txt` for Python dependencies
- System packages (install via apt):
  - `sudo apt-get install alsa-utils`
  - `sudo apt-get install chromium-browser`
  - `sudo apt-get install pulseaudio pulseaudio-utils`

## Installation
1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd MedDispenser
   ```
2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Install system dependencies** (see above)
4. **Connect servo motors** to GPIO pins 32 and 33 (BOARD mode: pins 29 and 31)
5. **(Optional) Set a Flask secret key**
   - By default, uses `fallback_secret_key`. For production, set the `SECRET_KEY` environment variable.

## Usage
1. **Start the application**
   ```bash
   python Medical_with_RPI.py
   ```
2. **Access the web interface**
   - Open a browser and go to: [http://localhost:5000](http://localhost:5000)
3. **Register or log in**
   - Default admin: `admin` / `admin123`
4. **Set up trays and schedules** via the dashboard
5. **Dispensing**
   - The system will automatically dispense at scheduled times and announce instructions

## File Structure
- `Medical_with_RPI.py` — Main application (Flask server, logic)
- `rpi_servo.py` — Servo control for dispensing
- `weblookup.py` — Drug info lookup and TTS
- `templates/` — HTML templates for web UI
- `static/css/` — CSS styles
- `medicine.csv` — Medicine database
- `users.db` — User and tray data (auto-created)

## Troubleshooting
- **No audio output?**
  - Ensure `alsa-utils` and `pulseaudio` are installed and configured
  - Check audio device is enabled on Raspberry Pi
- **Servo not moving?**
  - Double-check wiring and GPIO pin numbers
  - Run as root if required for GPIO access
- **Web interface not loading?**
  - Ensure Flask server is running and accessible on port 5000

## License
MIT License

---
For questions or contributions, open an issue or pull request on GitHub. 