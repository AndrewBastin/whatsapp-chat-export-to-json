#!/usr/bin/env python3

import sys
import re
import json

from loguru import logger


class BackupWppMessage:
    def __init__(self, date, time, sender, message):
        self.date = date
        self.time = time
        self.sender = sender
        self.message = message

    def append(self, toappend):
        self.message = self.message + toappend


class MessageProcessor:
    def __init__(self):  # , file_path: str):
        # self.__file_path = file_path
        self.__messages = []

        self.message_system_regex = re.compile(
            r"^(?P<date>\d{2}/\d{2}/\d{4}) (?P<time>\d{2}:\d{2}) - (?P<sender>[\w\s]+): (?P<message>[\s\S]*)"
        )

    def __process_message(self, message: str) -> BackupWppMessage | None:
        # Check if it is a system message
        if self.message_system_regex.match(message):
            matcher = self.message_system_regex.match(message)

            if not matcher:
                return None

            date = matcher.group("date")
            time = matcher.group("time")
            sender = "System"
            message = matcher.group("message")

            logger.debug(f"Message system: {date} {time} - {sender}: {message}")
            return BackupWppMessage(date, time, sender, message)
        else:
            print(message)
            print(len(message))
            raise ValueError

    def process_file(self, file_path: str) -> list[BackupWppMessage] | None:
        try:
            with open(file_path, "r") as f:
                processed_message: BackupWppMessage | None = None
                for line in f:
                    line = f.readline()

                    if line == "" or line == "\n":
                        logger.info("Empty line")
                        continue

                    m = self.message_system_regex.match(line)

                    if m:
                        if processed_message:
                            self.__messages.append(processed_message)
                        processed_message = self.__process_message(line)

                    elif processed_message:
                        logger.debug(
                            f"Appending {line} to message {processed_message.__dict__}"
                        )
                        processed_message.append(line)

                # finish
                if processed_message:
                    self.__messages.append(processed_message)

        except Exception as e:
            print("Error occurred while parsing")
            print(e)

        return self.__messages


processor = MessageProcessor()


if len(sys.argv) not in [2, 3]:
    print("Wrong format")
    print("Format: exporttojson.py [source txt file] [result JSON file]")
    print("\tOR")
    print("Format: exporttojson.py [source txt file]")
    print("This prints out the JSON to stdout")
    exit(-1)


try:
    messages = processor.process_file(sys.argv[1])

    if not messages:
        logger.error("No messages found")
        exit(1)

    # Convert to dicts for JSON serialization
    message_dicts = [m.__dict__ for m in messages]

    if len(sys.argv) == 3:
        with open(sys.argv[2], "w") as fw:
            fw.write(json.dumps(message_dicts))
    else:
        print(json.dumps(message_dicts))


except Exception as e:
    print("Error occured while parsing")
    print(e)
