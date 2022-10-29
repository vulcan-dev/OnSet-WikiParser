from datetime import datetime
import math
import signal
import sys
import threading
import time
import re
from threading import Thread
from bs4 import BeautifulSoup
import requests
import json
import argparse

serverPage = "https://dev.playonset.com/index.php?title=Template:ServerFunctions&action=edit"
clientPage = "https://dev.playonset.com/index.php?title=Template:ClientFunctions&action=edit"
serverEventPage = "https://dev.playonset.com/index.php?title=Template:ServerEvents&action=edit"
clientEventPage = "https://dev.playonset.com/index.php?title=Template:ClientEvents&action=edit"

#################### Functions #####################
def get_function(page):
    r = requests.get(page)
    soup = BeautifulSoup(r.text, "html.parser")
    ta = soup.find("textarea")
    if ta is None:
        return None
    lines = soup.find("textarea").text.splitlines()

    if len(lines) < 4:
        return None

    fn_info_split = lines[0].split("|")

    func = {
        "params": [],
        "context": fn_info_split[2],
        "introduced": fn_info_split[3][:-2]
    }

    for line in lines[1:]:
        if line == "" or not line.startswith("{{"):
            # Example, todo...
            continue

        data_split = line.split("|")

        if data_split[0] == "{{FuncDescription":
            func["description"] = data_split[1][:-2]
        elif data_split[0] == "{{FuncSyntax":
            func["syntax"] = data_split[1][:-2]
        elif data_split[0] == "{{FuncParam":
            param = {
                "name": data_split[1],
                "description": data_split[2]
            }
            func["params"].append(param)
        elif data_split[0] == "{{FuncReturnValue":
            func["return"] = data_split[1][:-2]

    return func

category = ""

def get_functions_thread(lines, functions, thread_id, thread_count):
    global category
    for line in lines:
        if thread_count <= 1 and line.startswith("===") or thread_count <= 1 and line.startswith("=="):
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [{thread_id}/{thread_count}]: Category - {line[3:-3]}")
            category = line[3:-3]
            continue
        elif line.startswith("*"):
            if line[1] == " ":
                function_name = line[4:-2]
            else:
                function_name = line[3:-2]

            print(f"[{datetime.now().strftime('%H:%M:%S')}] [{thread_id}/{thread_count}]: {function_name}")
            func = get_function("https://dev.playonset.com/index.php?title=" + function_name + "&action=edit")
            if func is not None:
                functions[function_name] = func
                functions[function_name]["category"] = category if category != "" else "Unknown due to thread timing"
        elif line.startswith("{{"):
            if ":" in line:
                template_name = line.split(":")[1][:-2]
            else:
                template_name = line[2:-2]

            template_page = "https://dev.playonset.com/index.php?title=Template:" + template_name + "&action=edit"
            template_functions = get_functions(template_page, thread_count)

            for template_function in template_functions:
                functions[template_function] = template_functions[template_function]

            category = ""
        else:
            category = ""

def get_functions(page, thread_count):
    functions = {}

    r = requests.get(page)
    soup = BeautifulSoup(r.text, "html.parser")

    textarea = soup.find("textarea")
    lines = textarea.text.splitlines()

    threads = []
    for i in range(thread_count):
        threads.append(Thread(target=get_functions_thread, args=(lines[i::thread_count], functions, i, thread_count)))

    for thread in threads:
        thread.daemon = True
        thread.start()

    for thread in threads:
        thread.join()

    return functions

###################### Events ######################
def get_events(page, thread_count):
    events = {}
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Getting events from {page}...")

    r = requests.get(page)
    soup = BeautifulSoup(r.text, "html.parser")

    textarea = soup.find("textarea")
    lines = textarea.text.splitlines()

    threads = []
    for i in range(thread_count):
        threads.append(Thread(target=get_functions_thread, args=(lines[i::thread_count], events, i, thread_count)))

    for thread in threads:
        thread.daemon = True
        thread.start()

    for thread in threads:
        thread.join()

    return events

def get_events_thread(lines, events, thread_id, thread_count):
    for line in lines:
        if line.startswith("{{"):
            if ":" in line:
                template_name = line.split(":")[1][:-2]
            else:
                template_name = line[2:-2]

            template_page = "https://dev.playonset.com/index.php?title=Template:" + template_name + "&action=edit"
            template_functions = get_functions(template_page, thread_count)

            for template_function in template_functions:
                events[template_function] = template_functions[template_function]
        elif line.startswith("*"):
            print(line)
            event_name = re.search(r"[a-zA-Z-0-9]+", line).group(0)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [{thread_id}/{thread_count}]: Event - {event_name}")
            event = get_function("https://dev.playonset.com/wiki/" + event_name)
            if event is not None:
                events[event_name] = event

def get_events(page, thread_count):
    r = requests.get(page)
    soup = BeautifulSoup(r.text, "html.parser")

    textarea = soup.find("textarea")
    lines = textarea.text.splitlines()

    threads = []
    events = {}
    for i in range(thread_count):
        threads.append(Thread(target=get_events_thread, args=(lines[i::thread_count], events, i, thread_count)))

    for thread in threads:
        thread.daemon = True
        thread.start()

    for thread in threads:
        thread.join()

    return events

parser = argparse.ArgumentParser()
parser.add_argument("-o", "--output", help="output file", default="functions.json")
parser.add_argument("-g", "--generate", help="generate functions.json", action="store_true")
parser.add_argument("-t", "--threads", help="number of threads", default=1, type=int)
parser.add_argument("-p", "--prettify", help="prettify json", default=False, action="store_true")

done = False

def main_thread(args):
    global done
    start_time = time.time()
    data = {
        "server": get_functions(serverPage, args.threads),
        "client": get_functions(clientPage, args.threads),
        "server_events": get_events(serverEventPage, args.threads),
        "client_events": get_events(clientEventPage, args.threads)
    }

    with open(args.output, "w") as f:
        if args.prettify:
            json.dump(data, f, indent=4)
        else:
            json.dump(data, f, separators=(",", ":"))

    done = True
    end_time = time.time()
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Finished in {time.strftime('%H:%M:%S', time.gmtime(end_time - start_time))}")

def signal_handler(sig, frame):
    print("Exiting...")
    sys.exit(0)

def main():
    args = parser.parse_args()
    if not args.generate:
        parser.print_help()
        return

    signal.signal(signal.SIGINT, signal_handler)

    thread = Thread(target=main_thread, args=(args,))
    thread.daemon = True
    thread.start()

    while not done:
        time.sleep(1)

if __name__ == "__main__":
    main()