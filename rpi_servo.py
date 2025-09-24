import RPi.GPIO as GPIO
import time

# Global variable to track if GPIO has been initialized
_gpio_initialized = False
_servo_controller_instance = None

def force_cleanup_gpio():
    """Force cleanup of all GPIO resources"""
    global _gpio_initialized, _servo_controller_instance
    try:
        # Stop any existing PWM objects
        for pin in [29, 31]:  # tray1_pin, tray2_pin
            try:
                pwm = GPIO.PWM(pin, 50)
                pwm.stop()
            except:
                pass
        
        # Cleanup GPIO
        GPIO.cleanup()
        time.sleep(0.2)  # Give time for cleanup
        _gpio_initialized = False
        _servo_controller_instance = None
        print("Forced GPIO cleanup completed")
    except Exception as e:
        print(f"Force cleanup error: {e}")

class ServoController:
    def __init__(self):
        global _gpio_initialized
        
        self.tray1_pin = 29  # GPIO 32 for Tray 1 (SG90)
        self.tray2_pin = 31  # GPIO 33 for Tray 2
        self.frequency = 50  # 50Hz for standard servos
        self.servo1 = None
        self.servo2 = None
        
        # Disable GPIO warnings
        GPIO.setwarnings(False)
        
        # Force cleanup before initialization
        force_cleanup_gpio()
        
        # Initialize GPIO
        try:
            # Set GPIO mode and setup pins
            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(self.tray1_pin, GPIO.OUT)
            GPIO.setup(self.tray2_pin, GPIO.OUT)
            _gpio_initialized = True
            print("GPIO initialized for servos")
        except Exception as e:
            print(f"GPIO setup error: {e}")
            _gpio_initialized = False
        
        # Create PWM objects
        try:
            # Stop any existing PWM on these pins first
            try:
                GPIO.PWM(self.tray1_pin, self.frequency).stop()
            except:
                pass
            try:
                GPIO.PWM(self.tray2_pin, self.frequency).stop()
            except:
                pass
            
            self.servo1 = GPIO.PWM(self.tray1_pin, self.frequency)
            self.servo2 = GPIO.PWM(self.tray2_pin, self.frequency)
            self.servo1.start(0)
            self.servo2.start(0)
            print("ServoController initialized (real hardware)")
        except Exception as e:
            print(f"Error initializing servos: {e}")
            # Don't raise exception, just log and continue without servos
            self.servo1 = None
            self.servo2 = None

    def _move_servo(self, servo, angle):
        if not servo:
            print("Warning: Servo not initialized")
            return
        # Convert angle (0-180) to duty cycle
        duty = 2 + (angle / 18)
        servo.ChangeDutyCycle(duty)
        time.sleep(0.5)
        servo.ChangeDutyCycle(0)

    def dispense_from_tray_1(self, medicine_name):
        print(f"Dispensing from Tray 1: {medicine_name}")
        start_time = time.perf_counter()
        self._move_servo(self.servo1, 90)  # Move to 90 degrees
        time.sleep(1)
        self._move_servo(self.servo1, 0)   # Return to 0 degrees
        elapsed = time.perf_counter() - start_time
        print(f"Dispense complete (Tray 1). [BENCHMARK] Took {elapsed:.2f} seconds.")

    def dispense_from_tray_2(self, medicine_name):
        print(f"Dispensing from Tray 2: {medicine_name}")
        start_time = time.perf_counter()
        self._move_servo(self.servo2, 90)  # Move to 90 degrees
        time.sleep(1)
        self._move_servo(self.servo2, 0)   # Return to 0 degrees
        elapsed = time.perf_counter() - start_time
        print(f"Dispense complete (Tray 2). [BENCHMARK] Took {elapsed:.2f} seconds.")

    def cleanup(self):
        try:
            if self.servo1:
                self.servo1.stop()
            if self.servo2:
                self.servo2.stop()
        except:
            pass
        
        try:
            GPIO.cleanup()
        except:
            pass
        
        print("ServoController cleaned up.")

def get_servo_controller():
    global _servo_controller_instance
    if _servo_controller_instance is None:
        _servo_controller_instance = ServoController()
    return _servo_controller_instance

def cleanup_servo_controller(controller=None):
    global _servo_controller_instance, _gpio_initialized
    if controller:
        controller.cleanup()
    _servo_controller_instance = None
    _gpio_initialized = False 