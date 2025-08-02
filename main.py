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
CYAN = '\033[36m' if USE_COLORS else ''
RESET = '\033[0m' if USE_COLORS else ''

# === Table formatting functions ===

def calculate_column_widths(records, max_width=30, padding=3):
    """Compute column widths based on terminal size and proportional scaling."""
    # Base calculation: find max content size for each column
    col_widths = {}
    for record in records:
        for key, val in record.items():
            v = val.get("value", "")
            if isinstance(v, list):
                v = ' '.join(str(x) for x in v)
            else:
                v = str(v)
            col_widths[key] = min(max(col_widths.get(key, 0), len(key), len(v)), max_width)

    # Get terminal width
    term_width = shutil.get_terminal_size().columns
    table_base_width = sum(col_widths.values()) + len(col_widths) * padding + 1

    # If table fits, return as is
    if table_base_width <= term_width:
        return col_widths

    # Scale down proportionally to fit terminal width
    scale = (term_width - len(col_widths) * padding - 1) / sum(col_widths.values())
    for key in col_widths:
        new_width = max(10, int(col_widths[key] * scale))  # Minimum width = 10
        col_widths[key] = new_width

    return col_widths

def print_header(col_widths: dict):
    headers = [f"{CYAN}{key[:col_widths[key]].ljust(col_widths[key])}{RESET}" for key in col_widths]
    print('| ' + ' | '.join(headers) + ' |')
    print('|' + '|'.join('-' * (w + 2) for w in col_widths.values()) + '|')

def print_row(col_widths: dict, record: dict):
    wrapped_cells = []
    for key in col_widths:
        width = col_widths[key]
        val = record.get(key, {}).get("value", "")
        if isinstance(val, list):
            val = ' '.join(str(x) for x in val)
        else:
            val = str(val)
        wrapped = textwrap.wrap(val, width=width) or ['']
        wrapped_cells.append(wrapped)

    # Find tallest cell
    row_height = max(len(cell) for cell in wrapped_cells)

    # Print each line of the row
    for i in range(row_height):
        line_parts = []
        for idx, key in enumerate(col_widths):
            cell_lines = wrapped_cells[idx]
            cell_line = cell_lines[i] if i < len(cell_lines) else ''
            line_parts.append(cell_line.ljust(col_widths[key]))
        print('| ' + ' | '.join(line_parts) + ' |')

def auto_print_records(col_widths: dict, records: list[dict]):
    print_header(col_widths)
    for i, record in enumerate(records):
        print_row(col_widths, record)
        if i < len(records) - 1:
            print('+' + '+'.join(['-' * (w + 2) for w in col_widths.values()]) + '+')

# === Generate extremely long data for stress testing ===

def generate_extreme_long_data(n=3):
    names = ["alice", "bob", "charlie", "dana", "edward"]
    domains = ["example.com", "mail.test.org", "demo.local"]
    roles = [
        ["admin", "superuser", "developer", "qa", "auditor", "network-engineer", "security-specialist"],
        ["user", "tester", "beta-tester", "analyst", "researcher", "compliance-officer"],
        ["read", "write", "moderator", "content-manager", "team-lead", "product-owner"]
    ]

    long_text = (
        "This is an extremely long piece of text intended for stress testing the wrapping feature of our table display. "
        "It contains multiple sentences, unnecessary verbosity, and additional redundant information so that the length "
        "exceeds normal expectations by a significant margin, thereby forcing the algorithm to handle wrapping gracefully."
    )

    base_time = datetime(2024, 6, 1, 8, 30)

    records = []
    for i in range(n):
        name = random.choice(names)
        domain = random.choice(domains)
        email = f"{name}.with.super.long.email.identifier.{''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(50))}@{domain}"
        role_list = random.choice(roles)
        last_login = (base_time + timedelta(minutes=random.randint(0, 100000))).strftime("%Y-%m-%d %H:%M")
        notes = (long_text + " ") * random.randint(3, 6)

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
records = generate_extreme_long_data(3)
col_widths = calculate_column_widths(records, max_width=35)
auto_print_records(col_widths, records)
