import csv
import os

args = os.sys.argv
if len(args) != 2:
    print("Usage: python evaluation.py <path_to_csv>")
    exit(1)

csv_path = args[1]
if not os.path.isfile(csv_path):
    print(f"Error: File '{csv_path}' does not exist.")
    exit(1)

with open(csv_path, "r") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

if not rows or "commit_tick" not in rows[0]:
    print("Error: CSV file does not contain 'commit_tick' column or is empty.")
    exit(1)

num_insts = len(rows)
first_commit = int(rows[0]["commit_tick"])
last_commit = int(rows[-1]["commit_tick"])
total_ticks = last_commit - first_commit

# Clock is 3GHz = 3e9 Hz, so 1 cycle = 1/3e9 seconds = 333.33 picoseconds
# gem5 default tick = 1 picosecond, so 1 cycle = 333.33 ticks
ticks_per_cycle = 333.333  # 3GHz clock

total_cycles = total_ticks / ticks_per_cycle
cpi = total_cycles / num_insts if num_insts > 0 else 0

print(f"=== CPI Calculation from Trace ===")
print(f"Total Instructions: {num_insts:,}")
print(f"First Commit Tick:  {first_commit:,}")
print(f"Last Commit Tick:   {last_commit:,}")
print(f"Total Ticks:        {total_ticks:,}")
print(f"Total Cycles:       {total_cycles:,.2f}")
print(f"CPI:                {cpi:.4f}")
print(f"IPC:                {1/cpi:.4f}" if cpi > 0 else "IPC: N/A")
