# 1
## Script
recover demo bot

Hello, thanks for checking in. How are you?

what is my schedule

Hi there! How can I assist you today? If you need help with your schedule or setting a reminder, feel free to let me know!

what is my schedule

## Notes
This is weird...asking about schedule, it seems to default to some canned response..hmmm, it doesnt seem to be canned because it's not in the code base.

## Solution
This is working now - likely thanks to the Amazon ALU even though the utterance was not an exact match, it was still matching the RecordID Intent.

# 2 

## Script
recover demo bot

Hello, thanks for checking in. How are you?

good you

I'm doing great, thank you! How can I assist you today?

what is my schedule

Good afternoon, John! Looks like you just had your call with family, and evening medication is coming up at 8:00 PM. Here are a couple of notifications for you: - Reminder: Don't forget to drink water throughout the day. - Schedule Change: Your doctor's appointment for tomorrow has been rescheduled to 10:00 AM. Is there anything else you need help with?

## Notes

The afternoon checkin is getting hit. This is likely due to the prompt.txt - the prompt.txt

And it seems it is the lambda doing this, because of the json request.

But 'Good afternoon, John'... is not canned, so....

Okay...from the ASK console, intent can be seen:

			"name": "AfternoonProactiveReminderIntent",
Though

'What is my schedule?'
is very far off from the 
          "samples": [
            "afternoon check in",
            "afternoon reminder",
            "afternoon feeling check"
          ]
But maybe semantically it's not.


### Conversation History
assistant: Hello, thanks for checking in. How are you?
user: good you
assistant: I'm doing great, thank you! How can I assist you today?
user: {"type": "afternoon_checkin", "context": {"username": "John", "time": "05:36 PM"}, "schedule": [{"activity": "Afternoon tea", "date_time": "3:30 PM"}, {"activity": "Call with family", "date_time": "5:00 PM"}, {"activity": "Evening medication", "date_time": "8:00 PM"}], "notifications": [{"type": "reminder", "message": "Don't forget to drink water throughout the day"}, {"type": "schedule_change", "message": "Your doctor's appointment for tomorrow has been rescheduled to 10:00 AM"}]}
assistant: Good afternoon, John!

Looks like you just had your call with family, and evening medication is coming up at 8:00 PM.

Here are a couple of notifications for you:
- Reminder: Don't forget to drink water throughout the day.
- Schedule Change: Your doctor's appointment for tomorrow has been rescheduled to 10:00 AM.

Is there anything else you need help with?

# 3
Okay...great progress. But it seems to be hallucinating the schedule.
The plan was to remove the schedule code from the check ins and feed it to the LLM on each conversation...


I can give you a detailed look at your entire week's schedule! Here's what's coming up: **Monday:** - 9:00 AM: Team Meeting - 11:00 AM: Project Review - 2:00 PM: Client Call **Tuesday:** - 10:00 AM: Research Time - 1:00 PM: Lunch with Sarah - 3:30 PM: Workshop **Wednesday:** - 8:00 AM: Gym Session - 12:00 PM: Webinar - 5:00 PM: Dinner with Family **Thursday:** - 9:30 AM: Design Review - 11:30 AM: Feedback Session - 4:00 PM: Yoga Class **Friday:** - 10:00 AM: Presentation Prep - 2:30 PM: Board Meeting - 6:00 PM: Relaxation Time **Saturday:** - 1:00 PM: Community Event - 4:00 PM: Grocery Shopping **Sunday:** - 11:00 AM: Brunch with Friends - 3:00 PM: Planning for Next Week Let me know if there's anything specific you'd like reminders for or if you want more details on any of these!

