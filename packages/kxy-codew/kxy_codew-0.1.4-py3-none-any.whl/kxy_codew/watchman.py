import sys
import threading
import asyncio
import traceback

import requests

from src.kxy_codew.state import KXYState
from src.kxy_codew.config import CODEW_API_URL

kxy_state = KXYState()


def push_results(root_cause, traceback_str):
    try:
        upload_url = CODEW_API_URL + "/kxy/watchman"
        response = requests.post(upload_url, json={"root_cause": root_cause, "content": traceback_str}, headers={"secret": kxy_state.get_secret()}, timeout=5)
        if response.status_code != 200:
            print(f"[watchman] Failed to send error: {response.status_code} - {response.text}")
            return None
        return response.json().get("id")
    except requests.RequestException as e:
        print("[watchman] Error connecting to 7176")



def wake_up():

    def format_exception(exc_type, exc_value, exc_traceback):
        tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        # Take the last meaningful line for location
        last_line = tb_lines[-1].strip()  # e.g., 'NameError: name 'load_video_filew' is not defined'
        # Get the filename and line number from traceback
        tb_summary = traceback.extract_tb(exc_traceback)
        if tb_summary:
            last_frame = tb_summary[-1]
            filename = last_frame.filename
            lineno = last_frame.lineno
            funcname = last_frame.name
            root_cause = f"{exc_type.__name__}: {exc_value} in File \"{filename}\", line {lineno}, in {funcname}"
        else:
            root_cause = last_line

        return root_cause, "\n".join(tb_lines)

    def log_exception(exc_type, exc_value, exc_traceback):
        print("[watchman] Unhandled Exception")
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        format_exception_str, traceback_str = format_exception(exc_type, exc_value, exc_traceback)
        push_results(format_exception_str, traceback_str)
        traceback.print_exception(exc_type, exc_value, exc_traceback)

    sys.excepthook = log_exception

    if hasattr(threading, 'excepthook'):
        threading.excepthook = lambda args: log_exception(
            args.exc_type, args.exc_value, args.exc_traceback
        )

    try:
        loop = asyncio.get_event_loop()
        loop.set_exception_handler(
            lambda loop, context: log_exception(
                type(context.get("exception")),
                context.get("exception"),
                context.get("exception").__traceback__
            ) if context.get("exception") else print(f"[watchman] Unhandled async error: {context}")
        )
    except RuntimeError:
        print("[watchman] Unhandled RUNTIME Exception")
        pass
