import subprocess
import os
import pty
import sys
from datetime import datetime
import re
from ying.thirdparty.telegram import send_message, edit_message_text
from ying.utils.runtime import format_host_banner
from ying.config import settings

ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

send_telegram_last_time = None
RATE_LIMIT_MODE_APPEND = 5
RATE_LIMIT_MODE_REPLACE = 1


def send_data_to_telegram(data, message_id, rt=RATE_LIMIT_MODE_REPLACE):
    global send_telegram_last_time
    if send_telegram_last_time is not None:
        if (datetime.now() - send_telegram_last_time).seconds < rt:
            return message_id

    chat_id = settings.get("tg_chat_id", None)
    if chat_id is None:
        raise ValueError("tg_chat_id is not configured, please add it.")

    if message_id is None:
        message_id = send_message(chat_id, data)
    edit_message_text(chat_id, message_id, data)
    send_telegram_last_time = datetime.now()

    return message_id


def run_command(command, mode='a'):
    """
    mode: a - append, r - replace
    """
    master_fd, slave_fd = pty.openpty()

    process = subprocess.Popen(
        command,
        shell=True,
        stdin=subprocess.PIPE,
        stdout=slave_fd,
        stderr=slave_fd,
        close_fds=True,
    )

    os.close(slave_fd)

    host_banner = format_host_banner()

    telegram_message_id = None
    filtered_output = ""

    MAX_MESSAGE_LENGTH = 4096
    while True:
        try:
            output = os.read(master_fd, 1024)
            if not output:
                break
            sys.stdout.buffer.write(output)
            sys.stdout.buffer.flush()

            rt_sec = RATE_LIMIT_MODE_REPLACE
            if mode == 'a':
                filtered_output += ansi_escape.sub("", output.decode("utf-8"))
                rt_sec = RATE_LIMIT_MODE_APPEND
            else:
                filtered_output = ansi_escape.sub("", output.decode("utf-8"))

            # send to telegram
            text = f'`{datetime.now().strftime("[%H:%M:%S]")} {host_banner}`\n'
            text += f"$ `{command}`\n"
            text_len = len(text)
            if len(filtered_output) + text_len > MAX_MESSAGE_LENGTH:
                cutted_output = filtered_output[-(MAX_MESSAGE_LENGTH - text_len):]
                text += f"```\n{cutted_output}```"
                filtered_output = cutted_output
            else:
                text += f"```\n{filtered_output.lstrip()}```"
            telegram_message_id = send_data_to_telegram(text, telegram_message_id, rt_sec)

        except OSError:
            break

    process.wait()
