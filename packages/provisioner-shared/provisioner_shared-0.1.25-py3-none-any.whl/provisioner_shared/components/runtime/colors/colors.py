#!/usr/bin/env python3

RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
WHITE = "\033[1;37m"
MAGENTA = "\033[1;35m"
LIGHT_CYAN = "\033[0;36m"
BRIGHT_BLACK = "\u001b[30;1m"
NONE = "\033[0m"

HEADER = "\033[95m"
OKBLUE = "\033[94m"
OKCYAN = "\033[96m"
OKGREEN = "\033[92m"
WARNING = "\033[93m"
FAIL = "\033[91m"
ENDC = "\033[0m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"


def color_text(text: str, color: str) -> str:
    return f"{color}{text}{NONE}"
