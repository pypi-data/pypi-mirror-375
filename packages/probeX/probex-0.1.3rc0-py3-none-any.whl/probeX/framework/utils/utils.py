import os
from datetime import datetime

__PROBE_HOME = os.environ.get('PROBE_HOME', None)


def get_now_time_str():
    now = datetime.now()
    return now.strftime("%Y%m%d-%H%M%S")


def print_table(table_data):
    data = table_data[1::]
    headers = table_data[0]
    column_widths = [max(len(str(row[i])) for row in [headers] + data) for i in range(len(headers))]
    def print_separator():
        print("+" + "+".join("-" * (w + 2) for w in column_widths) + "+")

    def print_row(row):
        print("| " + " | ".join(str(row[i]).ljust(column_widths[i]) for i in range(len(row))) + " |")
    print_separator()
    print_row(headers)
    print_separator()
    for row in data:
        print_row(row)
    print_separator()
