import textwrap
import shutil
import os
import sys
import random
from datetime import datetime, timedelta

# === Enable ANSI colors (Windows 10+ safe fallback)
if os.name == 'nt':
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except Exception:
        pass

USE_COLORS = sys.stdout.isatty()
YELLOW = '\033[33m' if USE_COLORS else ''
CYAN = '\033[36m' if USE_COLORS else ''
RESET = '\033[0m' if USE_COLORS else ''

# === Table formatting functions ===

def print_header(col_widths: dict):
    headers = [f"{CYAN}{key[:col_widths[key]].ljust(col_widths[key])}{RESET}" for key in col_widths]
    print('| ' + ' | '.join(headers) + ' |')
    print('|' + '|'.join('-' * (w + 2) for w in col_widths.values()) + '|')

def print_row(col_widths: dict, record: dict):
    wrapped_cells = []
    for key in col_widths:
        full_width = col_widths[key]
        wrap_width = full_width  # use full width for accurate fitting

        val = record.get(key, {}).get("value", "")
        if isinstance(val, list):
            val = ' '.join(str(x) for x in val)
        else:
            val = str(val)

        wrapped = textwrap.wrap(val, width=wrap_width) or ['']
        wrapped_cells.append(wrapped)

    row_height = max(len(cell) for cell in wrapped_cells)

    for i in range(row_height):
        line = []
        for idx, key in enumerate(col_widths):
            cell_lines = wrapped_cells[idx]
            cell_line = cell_lines[i] if i < len(cell_lines) else ''
            line.append(cell_line.ljust(col_widths[key]))
        print('| ' + ' | '.join(line) + ' |')

def print_vertical(record: dict):
    print(f"{YELLOW}--- Record ---{RESET}")
    for key, val in record.items():
        v = val.get("value", "")
        if isinstance(v, list):
            v = ' '.join(str(x) for x in v)
        print(f"{CYAN}{key}:{RESET} {v}")
    print('-' * shutil.get_terminal_size().columns)

def compute_max_col_widths(records: list[dict]) -> dict:
    col_widths = {}
    for record in records:
        for key, val in record.items():
            v = val.get("value", "")
            if isinstance(v, list):
                v = ' '.join(str(x) for x in v)
            else:
                v = str(v)
            col_widths[key] = max(col_widths.get(key, 0), len(key), len(v))
    return col_widths

def estimate_table_width(col_widths: dict) -> int:
    return sum((w + 2) for w in col_widths.values()) + 1

def auto_print_records(col_widths: dict, records: list[dict]):
    terminal_width = shutil.get_terminal_size().columns
    estimated_width = estimate_table_width(col_widths)

    if terminal_width < estimated_width:
        for record in records:
            print_vertical(record)
    else:
        print_header(col_widths)
        for i, record in enumerate(records):
            print_row(col_widths, record)
            if i < len(records) - 1:
                print('+' + '+'.join(['-' * (w + 2) for w in col_widths.values()]) + '+')

# === Auto-generated generic sample data ===

def generate_generic_data(n=10):
    names = ["alice", "bob", "charlie", "dana", "edward", "frank", "grace", "heidi"]
    domains = ["example.com", "mail.test.org", "demo.local"]
    roles = [["user"], ["admin", "user"], ["read", "write", "moderator"], ["guest"], ["auditor", "reporter"]]
    notes_samples = [
        "This user has access to sensitive systems. Monitor usage.",
        "Created via self-service portal. Needs review.",
        "Known to submit long requests frequently.",
        "No recent activity detected.",
        "Requested access to beta features."
    ]
    base_time = datetime(2024, 6, 1, 8, 30)

    records = []
    for i in range(n):
        name = random.choice(names)
        domain = random.choice(domains)
        email = f"{name}@{domain}"
        role_list = random.choice(roles)
        last_login = (base_time + timedelta(minutes=random.randint(0, 10000))).strftime("%Y-%m-%d %H:%M")
        notes = random.choice(notes_samples)

        record = {
            "Username": {"value": name},
            "Email": {"value": email},
            "Roles": {"value": role_list},
            "LastLogin": {"value": last_login},
            "Notes": {"value": notes}
        }
        records.append(record)

    return records

# === Run ===
records = generate_generic_data(10)
col_widths = compute_max_col_widths(records)
auto_print_records(col_widths, records)
