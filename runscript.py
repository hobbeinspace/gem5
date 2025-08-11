import subprocess, os, re

GEM5 = "build/X86/gem5.opt"
CFG = "configs/learning_gem5/part1/two_level.py"
BENCHS = ["perlbench_s", "gcc_s", "mcf_s", "omnetpp_s", "xalancbmk_s", "x264_s", "deepsjeng_s", "cactuBSSN_s"]

def compile_and_get_opts(bench):
    specenv = os.path.expanduser("~/SPEC/cpu2017-1.1.0")
    cwd = os.path.join(specenv, f"benchspec/CPU/{bench}")
    os.chdir(cwd)
    subprocess.run("source shrc && go " + bench, shell=True, executable="/bin/bash")
    subprocess.run("rm -rf build && runcpu --fake --config gcc-linux-x86 " + bench, shell=True, executable="/bin/bash")
    build_dir = os.path.join(cwd, "build", "build_base_mytest-m64.0000")
    subprocess.run("cd " + build_dir + " && specmake", shell=True, executable="/bin/bash")
    run_dir = os.path.join(cwd, "run", "run_base_refspeed_mytest-m64.0000")
    output = subprocess.check_output("specinvoke -n", cwd=run_dir, shell=True, executable="/bin/bash", text=True)
    opts = " ".join(output.split()[1:])
    return build_dir + "/" + bench, opts

def extract_ipc(stats="m5out/stats.txt"):
    with open(stats) as f:
        for l in f:
            m = re.match(r"system\.cpu\.ipc\s+([0-9.]+)", l)
            if m: return float(m.group(1))
    return None

results = {}
for b in BENCHS:
    print(f"Processing {b}...")
    binary, options = compile_and_get_opts(b)
    cmd = [GEM5, CFG, f"--binary={binary}", "--maxtime=0.1", f"--options={options}"]
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)
    ipc = extract_ipc()
    results[b] = ipc
    print(f"{b} IPC = {ipc}")

print("\nSummary:")
for b, i in results.items():
    print(f"{b:<15} {i}")
