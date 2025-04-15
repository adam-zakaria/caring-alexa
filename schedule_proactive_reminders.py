import alexa_api

"""
See docs/schedule_proactive_reminders.md for more details
"""

# Your refresh token (should be kept secure, consider using environment variables)
refresh_token = "Atnr|EwICIGUPzdrtbJcLvf__PudRQ8iEJCadd4nc4tmJP8w1FxpKs9REGnQiwWaUWaWQ0T7shEVsEQdxEkoV94jpSkOXmsb4WuDb1XrM5tzGMoM2LbYEM5BGT8HkrM2EjxAzHPHaM7Kw7wAEEh4IvL3v2yj4xw8L0rSw79YCfqA_fPXEZ0yfiPHvn5XhDTCJof8y-hRVqm2UuahjRLrkI4H5qOp5V7t0zGd2-2LMmMUXxzYGfzYAvK0Muzk4TyYGd09uoMdvHhX6SrXj65w0XSIJIhMMb0Ii8A4ttbiMDAnmWmCJP7w7i63CCBfzlhSC9iZIldcY478"

# The name of your Alexa device
device_name = "Adam's Echo Dot"  # Replace with your device name

# Morning check in
result = alexa_api.execute_command("textcommand", "recover demo bot", refresh_token, device_name)
result = alexa_api.execute_command("textcommand", "morning check in", refresh_token, device_name)

# Afternoon check in
result = alexa_api.execute_command("textcommand", "recover demo bot", refresh_token, device_name)
result = alexa_api.execute_command("textcommand", "morning check in", refresh_token, device_name)
