import subprocess
import time
from linpymem import LinPyMem, PhysAccessMode

def test_read_known_struct():

    # Start the process and capture stdout
    # binary compiled using: g++ -g test_target.cpp -o test_target
    proc = subprocess.Popen(
        ["./test_target"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    try:
        binary_self_reported_pid = int(proc.stdout.readline().strip().split(": ")[1])
        time.sleep(1)

        with LinPyMem(ko_module_path="/home/bob/Documents/workspace/Linpmem/linpmem.ko", process_name="test_target", vm_pathname="test_target") as reader:

            pid = reader.pid
            base, size = reader.pathname_vm_regions[0]
            end = base + size
            cr3 = reader.cr3
            reader.view_memory_region(base + 0x2018, 0x40)

            magic = reader.read_int(base + 0x1228)
            ratio = reader.read_float(base + 0x2054)
            vec = reader.read_vec3_double(base + 0x2058)
            text = reader.read_utf_string(base + 0x2018, max_len=len("Holding values in memory. You may inspect with LinPyMem."))
            phys, _ = reader.virtual_to_physical(base, reader.cr3)
            entire_binary_from_multiple_pages, multipage_bytes_read, multipage_bytes_expected = reader.read_physical_memory(phys, PhysAccessMode.PHYS_BUFFER_READ, size)
            
            assert pid == binary_self_reported_pid
            assert cr3 > 0
            assert end-base == size
            assert size == 0x5000
            assert magic == 0x13371337
            assert abs(ratio - 3.14159) < 0.001
            assert all(abs(a - b) < 0.001 for a, b in zip(vec, [1.0, 2.0, 3.0]))
            assert text == "Holding values in memory. You may inspect with LinPyMem."
            assert multipage_bytes_read == multipage_bytes_expected
            assert multipage_bytes_read == 0x5000
            assert len(entire_binary_from_multiple_pages) == 0x5000

    finally:
        proc.terminate()
        proc.wait()

if __name__ == "__main__":
    test_read_known_struct()