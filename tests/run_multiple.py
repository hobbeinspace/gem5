import subprocess

command = ["build/X86/gem5.opt", "src/helloObject/run_hello.py"]  # Replace with your command and arguments

results = []
for i in range(10):  # Number of times to run
    result = subprocess.run(command, capture_output=True, text=True)
    output = result.stdout
    # Parse the output as needed, e.g. extract numbers, lines, etc.
    parsed = output.splitlines()  # Example: split output into lines
    results.append(parsed)

# Do something with the parsed results
for run_result in results:
    print(run_result)