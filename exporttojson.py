import sys
import re
import json

class Message:
    def __init__(self, date, time, sender, message):
        self.date = date
        self.time = time
        self.sender = sender
        self.message = message

    def append(self, toappend):
        self.message = self.message + toappend

message_scan_regex = re.compile(r"^(\d{1,2}/\d{1,2}/\d{1,2}, \d+:\d+ (A|P)M)")
message_with_sender_regex = re.compile(r"^((?P<date>(\d{1,2}/\d{1,2}/\d{1,2})), (?P<time>(\d+:\d+ (A|P)M))) - (?P<sender>(.+?)): (?P<message>[\s\S]*)")
message_system_regex = re.compile(r"^((?P<date>(\d{1,2}/\d{1,2}/\d{1,2})), (?P<time>(\d+:\d+ (A|P)M))) - (?P<message>[\s\S]*)")

def is_empty_string(s):
    return not s or not s.strip

def process_message(s):

    # Check if it is a system message
    if message_with_sender_regex.match(s):
        matcher = message_with_sender_regex.match(s)
        date = matcher.group("date")
        time = matcher.group("time")
        sender = matcher.group("sender")
        message = matcher.group("message")

        return Message(date, time, sender, message)
    elif message_system_regex.match(s):
        matcher = message_system_regex.match(s)
        date = matcher.group("date")
        time = matcher.group("time")
        sender = "System"
        message = matcher.group("message")

        return Message(date, time, sender, message)
    else:
        print(s)
        print(len(s))
        raise ValueError



if len(sys.argv) != 3:
    print("Wrong format")
    print("Format: exporttojson.py [source txt file] [result JSON file]")
    exit(-1)

try:
    with open(sys.argv[1], "r") as f:
        messages = []

        for line in f:
            if message_scan_regex.match(line) and (not is_empty_string(line)):
                messages.append(process_message(line))
            else:
                messages[-1].append(line)

        # Convert to dicts for JSON serialization
        message_dicts = [m.__dict__ for m in messages]

        with open(sys.argv[2], "w") as fw:
            fw.write(json.dumps(message_dicts))
    

except Exception as e:
    print("Error occured while parsing")
    print(e)
