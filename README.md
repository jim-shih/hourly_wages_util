# cal_api_test

1. follow the steps from [google official documentation](https://developers.google.com/calendar/api/quickstart/python) to build the environment and get the credentials.json file
2. put it into the credentials folder
3. run the shift_event_creation.py file, the authentication process will be done automatically
4. the script will create your shift events in your calendar


## TODOs
1) Create a Docker compose file to 
    - Build the environment
    - Run the Vue app
    - Run the Redis server
    - Run the Celery worker
2) Build a web interface to
    - Have a button to trigger the shift events creation
    - Have an image to show the shift events in the calendar
    - Have a button to create the shift events in the calendar

## Note:

Please note that the current data/_ files are all related to the current job that I am working for, so if you are not in the same company w/ me, you need to change the data/_ files accordingly.
