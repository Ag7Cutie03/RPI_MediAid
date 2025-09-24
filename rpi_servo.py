import RPi.GPIO as GPIO
import time

class ServoController:
    def __init__(self):
        # Pin assignments
        self.tray1_pin = 29  # BOARD 29
        self.tray2_pin = 31  # BOARD 31
        self.frequency = 50

        GPIO.setmode(GPIO.BOARD)
        # Optionally disable warnings
        GPIO.setwarnings(False)
        GPIO.setup(self.tray1_pin, GPIO.OUT)
        GPIO.setup(self.tray2_pin, GPIO.OUT)

        # Create PWM only once per pin
        self.servo1 = GPIO.PWM(self.tray1_pin, self.frequency)
        self.servo2 = GPIO.PWM(self.tray2_pin, self.frequency)
        self.servo1.start(0)
        self.servo2.start(0)

        print("ServoController initialized (real hardware)")

    def _move_servo(self, servo, angle):
        duty = 2 + (angle / 18)
        servo.ChangeDutyCycle(duty)
        time.sleep(0.5)
        servo.ChangeDutyCycle(0)

    def dispense_from_tray_1(self, medicine_name):
        print(f"Dispensing from Tray 1: {medicine_name}")
        start_time = time.perf_counter()
        self._move_servo(self.servo1, 90)
        time.sleep(1)
        self._move_servo(self.servo1, 0)
        elapsed = time.perf_counter() - start_time
        print(f"Dispense complete (Tray 1). [BENCHMARK] Took {elapsed:.2f} seconds.")

    def dispense_from_tray_2(self, medicine_name):
        print(f"Dispensing from Tray 2: {medicine_name}")
        start_time = time.perf_counter()
        self._move_servo(self.servo2, 90)
        time.sleep(1)
        self._move_servo(self.servo2, 0)
        elapsed = time.perf_counter() - start_time
        print(f"Dispense complete (Tray 2). [BENCHMARK] Took {elapsed:.2f} seconds.")

    def cleanup(self):
        try:
            self.servo1.stop()
        except Exception:
            pass
        try:
            self.servo2.stop()
        except Exception:
            pass
        GPIO.cleanup()
        print("ServoController cleaned up.")

# Singleton holder
_servo_instance = None

def get_servo_controller():
    global _servo_instance
    if _servo_instance is None:
        _servo_instance = ServoController()
    return _servo_instance

def cleanup_servo_controller():
    global _servo_instance
    if _servo_instance is not None:
        _servo_instance.cleanup()
        _servo_instance = None
