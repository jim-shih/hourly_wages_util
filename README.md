# cal_api_test

## Overview
this project was developed while I worked at a part-time job in Taipei 101. 
- I got the shift schedule in image format, but I want the shift info integrated into my google calendar. So I developed this project to help me create the shift events automatically.
- The salary calculation is also difficult to do manually, so I also developed a script to help me calculate the salary based on the shift events.

## Prerequisites
### Get the credentials.json file on google cloud
1. follow the steps from [google official documentation](https://developers.google.com/calendar/api/quickstart/python) to build the environment and get the credentials.json file
2. put it into the credentials folder

## Run the project
### To set up the shift info
- extract the shift text from the image (I used a random website to do this)
- run the `utils/create_shift_from_text.py YYYY-MM {shift-text}` the shift-text is the text you extracted from the image(which requires to seperate the shift info by space)

### Steps to create the google calendar events
- run the `utils/shift_event_creation.py` file, the authentication process will be done automatically
- the script will create your shift events in your calendar

### Steps to calculate the salary
- run the `utils/shift_caculator.py YYYY-MM` file, the authentication process will be done automatically