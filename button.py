from gpiozero import Button, Device
from gpiozero.pins.mock import MockFactory
import alexa_api

# Your refresh token (should be kept secure, consider using environment variables)
refresh_token = "Atnr|EwICIGUPzdrtbJcLvf__PudRQ8iEJCadd4nc4tmJP8w1FxpKs9REGnQiwWaUWaWQ0T7shEVsEQdxEkoV94jpSkOXmsb4WuDb1XrM5tzGMoM2LbYEM5BGT8HkrM2EjxAzHPHaM7Kw7wAEEh4IvL3v2yj4xw8L0rSw79YCfqA_fPXEZ0yfiPHvn5XhDTCJof8y-hRVqm2UuahjRLrkI4H5qOp5V7t0zGd2-2LMmMUXxzYGfzYAvK0Muzk4TyYGd09uoMdvHhX6SrXj65w0XSIJIhMMb0Ii8A4ttbiMDAnmWmCJP7w7i63CCBfzlhSC9iZIldcY478"

# The name of your Alexa device
device_name = "Adam's Echo Dot"  # Replace with your device name

# MyCare skill invocation name - matches what's defined in skill model
skill_invocation_name = "my care assistant"

# Set the mock pin factory for testing
Device.pin_factory = MockFactory()

# Create a simulated button on pin 17
button = Button(17)

# Note: The skill should be created separately through the Alexa Developer Console
# or using the deployment script in skills/mycare_skill/deploy.sh
print(f"Button configured to trigger the '{skill_invocation_name}' skill")

# Define what happens when the button is pressed
def button_pressed():
    print(f"Button pressed! Opening {skill_invocation_name}...")
    
    # Using alexa_api to invoke our skill via the Alexa device
    command = f"Alexa, open {skill_invocation_name}"
    result = alexa_api.execute_command("textcommand", command, refresh_token, device_name)
    
    if result:
        print("Command sent successfully!")
    else:
        print("Failed to send command. Check your connection and Alexa device settings.")

# Assign the function to the button press event
button.when_pressed = button_pressed

# For demo purposes - simulate a button press
print("Simulating button press...")
button.pin.drive_low()  # Simulate closing the circuit
button.pin.drive_high() # Simulate releasing the button

print("Done! In a real setup, the button would trigger the skill on your Echo device.")
