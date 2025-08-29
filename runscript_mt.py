import subprocess
import os
import re
import shlex

# Absolute paths
SPEC_DIR = "/gem5/cpu2017-1.1.0"
GEM5_DIR = "/gem5/gem5"
GEM5_BINARY = os.path.join(GEM5_DIR, "build/X86/gem5.opt")
CONFIG_SCRIPT = os.path.join(GEM5_DIR, "configs/deprecated/example/se.py")
# CONFIG_SCRIPT = os.path.join(GEM5_DIR, "configs/learning_gem5/part1/two_level.py")

# Benchmarks to run (SPECspeed versions)
benchmarks = [
    "600.perlbench_s",
    "602.gcc_s",
    "605.mcf_s", 
    "620.omnetpp_s",
    "623.xalancbmk_s",
    "625.x264_s",
    "631.deepsjeng_s",
    "607.cactuBSSN_s"
]

names = [
    "perlbench_s",
    "cpugcc_s",
    "mcf_s",
    "omnetpp_s",
    "cpuxalan_s",
    "x264_s",
    "deepsjeng_s",
    "cactuBSSN_s"
]

def run_with_spec_env(command, cwd=None):
    full_cmd = f"source {SPEC_DIR}/shrc && {command}"
    return subprocess.run(
        ["bash", "-c", full_cmd],
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )


# # # Step 2: Build benchmarks
# for bench in benchmarks:
#     print(f"=== Building {bench} ===")
#     name=bench.split(".")[1]
#     result = run_with_spec_env(f"runcpu --fake --config=gcc-linux-x86-mt.cfg {name}", cwd=SPEC_DIR)
#     if result.returncode != 0:
#         print(f"Error building {bench}:\n{result.stderr}")
#     else:
#         print(f"Built {bench} successfully.")


# for bench in benchmarks:
#     print(f"=== Running specmake for {bench} ===")
#     name=bench.split(".")[1]
#     if(name!="x264_s"):
#         result = run_with_spec_env(f"specmake", cwd=os.path.join(SPEC_DIR,"benchspec", "CPU", bench,"build","build_base_mytest-m64.0000"))

#     else:
#         result = run_with_spec_env(f"specmake {name} TARGET={name}", cwd=os.path.join(SPEC_DIR,"benchspec", "CPU", bench,"build","build_base_mytest-m64.0000"))
#     if result.returncode != 0:
#         print(f"Error running specmake for {bench}:\n{result.stderr}")
#     else:
#         print(f"specmake done for {bench}")

# Step 3 & 4: Run benchmarks in gem5 and extract IPC
ipc_results = {}
for i,bench in enumerate(benchmarks):
    print(f"=== Preparing {bench} ===")
    
    run_dir_path = os.path.join(SPEC_DIR, "benchspec", "CPU", bench)
    if not os.path.exists(run_dir_path):
        print(f"No run directory found for {bench} at {run_dir_path}, skipping.")
        continue

    # Get specinvoke command line
    result = run_with_spec_env("specinvoke -n", cwd=os.path.join(run_dir_path, "run","run_base_refspeed_mytest-m64.0000"))
    if result.returncode != 0:
        print(f"Error running specinvoke for {bench}:\n{result.stderr}")
        continue

    lines= result.stdout  
    lines = [line for line in lines.splitlines() if not line.startswith("#")]
    line=lines[0]
    # Skip comments or empty lines
    parts = shlex.split(line)
    if ">" in parts:
        gt_index = parts.index(">")
        parts = parts[:gt_index]  # remove redirection and after

    parts=parts[1:]
    name=names[i]
    binary_path = run_dir_path+ "/build/build_base_mytest-m64.0000/"+name
    run_dir=os.path.join(run_dir_path, "run","run_base_refspeed_mytest-m64.0000")
    #binary_args = " ".join(spec_cmd[1:])

    print(f"Running {bench} in gem5...")
    options=" ".join(parts)
    gem5_cmd = [
        GEM5_BINARY,
        CONFIG_SCRIPT,
        "--cpu-type=X86O3CPU",
        "--num-cpus=4",
        "--mem-type=Ramulator2",
        "--mem-size=16GB",
        "--caches",
        "--l2cache",
        "--l1i_size=16kB",
        "--l1d_size=16kB",
        "--l2_size=512kB",
        f"--cmd={binary_path}",
        "--maxtime=0.01",
        f"--options={options}",
    ]
    print(gem5_cmd)
    subprocess.run(gem5_cmd, cwd=run_dir)

    # Read IPC from m5out/stats.txt
    stats_file = os.path.join(run_dir, "m5out", "stats.txt")
    ipc_val = None
    with open(stats_file, "r") as f:
        for line in f:
            match = re.match(r'system\.cpu\.ipc\s+([0-9.]+)', line)
            if match:
                ipc_val = float(match.group(1))
                break

    ipc_results[bench] = ipc_val
    print(f"{bench} ipc: {ipc_val}")
    exit(0)

print("\n=== ipc Summary ===")
for bench, ipc in ipc_results.items():
    print(f"{bench}: {ipc}")
