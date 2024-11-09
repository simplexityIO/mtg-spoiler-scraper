# Imports
import sys
import requests
from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag
import re
import time
import math
import sys
import traceback

# Extract input parameters
max_iterations = math.inf if len(sys.argv) < 2 else int(sys.argv[1])

# Initialize variables
print_is_on = True
divider = "-" * 40
max_attempts = 4 # Amazon doesn't like bots accessing their site not using their API and Mythic Spoiler might not either
search_url = "http://mythicspoiler.com/newspoilers.html"
latest_card_id = None
recently_found_spoilers = False
attempt_num = 1
iteration_num = 1
normal_delay_amount = 1 # 1 minute
recently_found_delay_amount = 3 # 3 minutes
ifttt_key = "XXXXXXXXXXXXXXXXXXXXXX" # Todo: Locally add back for testing
ifttt_webhook_url = "https://maker.ifttt.com/trigger/send_notification/with/key/" + ifttt_key
num_consec_rejections = 0
num_consec_rejections_alert_point = 7
hour_on = 8 # 8:00am  -- Note: Current implementation cannot handle on time being later than off time (ie. during the night)
min_on = 0
hour_off = 16 # 4:30pm
min_off = 30
no_weekends = False # Note: Current implementation assumes not starting during weekend

# Send push notification through IFTTT
def send_push_notification(message, key=ifttt_key, url=ifttt_webhook_url):
    json_data = {"value1": message}
    requests.post(url, json=json_data) # Send push notification

# Handle crashes gracefully
try:
    # Execute once a minute
    while True:
        # Get website HTML
        r = requests.get(search_url)
        while(not r.ok and attempt_num < max_attempts):
            r = requests.get(search_url)
            attempt_num += 1
            time.sleep(3)
        # soup = BeautifulSoup(r.text, 'lxml') # html.parser, html5lib
        soup = BeautifulSoup(r.text, 'html.parser')

        # Check if was able to access Mythic Spoiler
        if r.ok:
            # Initialize local variables
            first_date_end_comment = soup.find(string=re.compile("END DATE"))
            first_card_id = first_date_end_comment.findNext().find("a").attrs["href"]
            
            # Determine if new spoilers on page
            if first_card_id != latest_card_id:
                latest_card_id = first_card_id
                recently_found_spoilers = True
                notification_message = "Found new spoilers @ %s" % time.strftime("%m/%d/%y %I:%M:%S")
                print(">>> %s\n" % notification_message)
                send_push_notification(notification_message)

            # Zero out counter for number of consecutive rejections
            num_consec_rejections = 0

        # Unable to access Mythic Spoiler in the given number of attempts
        else:
            # Print out
            print("Unable to access Mythic Spoiler (%s attempts made)." % max_attempts)
            print("Verify manually at %s" % search_url)
            print()

            # Increment counter for number of consecutive rejections and send alert if rejected too many times
            num_consec_rejections += 1
            if num_consec_rejections >= num_consec_rejections_alert_point:
                notification_message = "MTG webscraper has been rejected %s times consecutively..." % num_consec_rejections
                send_push_notification(notification_message)

        # Check to see if reached max amount of iterations
        if iteration_num >= max_iterations:
            break
        else:
            iteration_num += 1

        # Delay for a bit (more if recently notified of spoilers) and also pause during off-hours
        curr_time = time.localtime()
        curr_hour = curr_time.tm_hour
        curr_min = curr_time.tm_min
        curr_weekday = curr_time.tm_wday
        curr_time_greater_than_off_time = curr_hour >= hour_off and curr_min >= min_off
        curr_time_less_than_on_time = curr_hour < hour_on and curr_min < min_on
        is_weekend = curr_weekday >= 5
        if curr_time_greater_than_off_time or curr_time_less_than_on_time or (is_weekend and no_weekends):
            if print_is_on:
                print("Pausing during off hours...")
            if is_weekend and no_weekends:
                delay_amount = 48 * 60 # Assumes not starting during weekend
            elif curr_time_greater_than_off_time:
                delay_amount = 24*60 - (curr_hour*60 + curr_min) + (hour_on*60 + min_on)
            elif curr_time_less_than_on_time:
                delay_amount = (hour_on*60 + min_on) - (curr_hour*60 + curr_min)
            recently_found_spoilers = False
        elif recently_found_spoilers:
            delay_amount = recently_found_delay_amount
            recently_found_spoilers = False
        else:
            delay_amount = normal_delay_amount
        if print_is_on:
            if delay_amount == 1.0:
                print("Delaying for 1 minute...\n")
            else:
                print("Delaying for %s minutes...\n" % delay_amount)
        time.sleep(60 * delay_amount)
            
# Catch all exceptions
except Exception as e:
    notification_message = "MTG webscraper crashed:\n"
    error_lines = traceback.format_exception(type(e), e, sys.exc_info()[2])
    for line in error_lines:
        notification_message += line
    send_push_notification(notification_message)
    raise
