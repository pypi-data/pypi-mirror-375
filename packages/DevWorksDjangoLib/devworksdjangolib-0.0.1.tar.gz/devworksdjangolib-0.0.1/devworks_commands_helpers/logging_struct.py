"""
gunicorn --bind 127.0.0.1:9000 \
  --config guniconfig.py CertiScanAccount.wsgi:application 2>&1 | python logging_struct.py
"""

import fileinput
import json

HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKCYAN = '\033[96m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'


def level_icon(log):
    try:
        severity = log['severity']
    except KeyError:
        return "?"
    return severity[0]


def run():
    for line in fileinput.input():
        data = None
        try:
            data = json.loads(line)
        except json.decoder.JSONDecodeError:
            print(f"X | {line}", end='')
        if data:
            icon = level_icon(data)
            name = data["name"]
            time = data["timestamp"]
            msg = data['message']
            request_id = data.get('request_id', '')
            print(f"{HEADER}{icon} | {name} | {time} | {request_id}{ENDC}")
            if not msg:
                msg = ""
            print(f"\t{msg.strip()}")
            exc_info = data.get('exc_info', None)
            if exc_info:
                print(f"{FAIL}{exc_info.strip()}{ENDC}")


if __name__ == "__main__":
    print("In main")
    run()
