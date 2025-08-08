import subprocess
import re
import os

command = ["build/X86/gem5.opt", "configs/learning_gem5/part1/two_level.py"]  # Replace with your command and arguments

results = []
runtimes = []
# List of stats.txt files from multiple runs
stats_files = [
    "m5out/stats.txt"
]
def extract_hostInstRate(stats_file):
    with open(stats_file, 'r') as f:
        for line in f:
            match = re.match(r'system\.cpu\.ipc\s+([0-9.]+)', line)
            if match:
                return float(match.group(1))
    return None

rates = []
for i in range(5):  # Number of times to run
    result = subprocess.run(command, capture_output=True, text=True)
    output = result.stdout
    print(output)
    for stats_file in stats_files:
        if os.path.exists(stats_file):
            rate = extract_hostInstRate(stats_file)
            if rate is not None:
                rates.append(rate)
            print(rates)
    # Parse the output as needed, e.g. extract numbers, lines, etc.



if rates:
    avg = sum(rates) / len(rates)
    print(f"Average IPC: {avg:.6f}")
else:
    print("No hostInstRate values found.")