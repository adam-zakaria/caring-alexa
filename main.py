import alexa_api

# Define your Alexa refresh token
refresh_token = "Atnr|EwICIGUPzdrtbJcLvf__PudRQ8iEJCadd4nc4tmJP8w1FxpKs9REGnQiwWaUWaWQ0T7shEVsEQdxEkoV94jpSkOXmsb4WuDb1XrM5tzGMoM2LbYEM5BGT8HkrM2EjxAzHPHaM7Kw7wAEEh4IvL3v2yj4xw8L0rSw79YCfqA_fPXEZ0yfiPHvn5XhDTCJof8y-hRVqm2UuahjRLrkI4H5qOp5V7t0zGd2-2LMmMUXxzYGfzYAvK0Muzk4TyYGd09uoMdvHhX6SrXj65w0XSIJIhMMb0Ii8A4ttbiMDAnmWmCJP7w7i63CCBfzlhSC9iZIldcY478"

# Retrieve the list of Alexa devices
devices = alexa_api.get_device_list(refresh_token)
print(devices)

# Make Alexa speak a custom message
#alexa_api.execute_command("speak", "Hello, how can I help you?", refresh_token, "Adam's Echo Dot")

# Send a text command to Alexa (e.g., open a skill)
#alexa_api.execute_command("textcommand", "Alexa, open my demo", refresh_token, "Adam'sEcho Dot")
alexa_api.execute_command("textcommand", "Alexa, open space facts", refresh_token, "Adam's Echo Dot")
