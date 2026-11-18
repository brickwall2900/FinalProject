import time
import os
import random

def get_random_message_of_the_day(motd_filepath):
    ''' Try loading message the message of the day. '''

    if not os.path.exists(motd_filepath):
        return None

    motds = []
    with open(motd_filepath, "rt") as file:
        while True:
            line = file.readline()
            if len(line) <= 0:
                break

            if line.startswith("#"):
                continue

            line = line.strip()

            motds.append(line)
            
    localtime = time.localtime()
    random.seed(localtime.tm_wday + localtime.tm_year)
    return random.choice(motds)
