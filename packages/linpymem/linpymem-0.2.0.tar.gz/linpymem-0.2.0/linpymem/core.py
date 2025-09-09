import os
import psutil
import struct
import fcntl
import ctypes
import subprocess

"""
LinPyMem
=====================

This module provides a Python interface to the linpmem kernel driver.

https://github.com/Velocidex/Linpmem

Requires:
    - linpmem.ko built from source (must be signed if Secure Boot enabled; can self-sign and enroll the public key into MOK)
    - Root access or elevated privileges.

Author: gionetti <its.only.a.matter.of.time.000@gmail.com>
Repo: https://github.com/gionetti/linpymem
License: MIT
"""

def _IOWR(type, number, size):
    return (0xC0000000 | ((ord(type) & 0xFF) << 8) | (ord(number) & 0xFF) | ((size & 0x1FFF) << 16))

PAGE_SIZE = 4096
LINPMEM_DATA_TRANSFER_SIZE = struct.calcsize("QQQQBBBBxxxx")
LINPMEM_VTOP_INFO_SIZE = struct.calcsize("QQQQ")
LINPMEM_CR3_INFO_SIZE = struct.calcsize("QQ")

# IOCTL commands exposed by linpmem driver
IOCTL_LINPMEM_READ_PHYSADDR = _IOWR('a', 'a', LINPMEM_DATA_TRANSFER_SIZE)
IOCTL_LINPMEM_VTOP_TRANSLATION_SERVICE = _IOWR('a', 'b', LINPMEM_VTOP_INFO_SIZE)
IOCTL_LINPMEM_QUERY_CR3 = _IOWR('a', 'c', LINPMEM_CR3_INFO_SIZE)

# Access mode enum for physical memory reading
class PhysAccessMode:
    PHYS_BYTE_READ = 1
    PHYS_WORD_READ = 2
    PHYS_DWORD_READ = 4
    PHYS_QWORD_READ = 8
    PHYS_BUFFER_READ = 9

class LinPyMem:
    """
    Provides an interface to read physical memory via virtual-to-physical address translation
    using CR3 page tables and custom IOCTL-based kernel driver access.
    """

    def __init__(self, 
                 ko_module_path: str = None, 
                 device_path: str = "/dev/linpmem", 
                 process_name: str = None, 
                 pid: int = None, 
                 vm_pathname: str = None):
        """
        Initializes the LinPyMem memory reader instance.

        This sets up parameters for accessing a target process's physical memory by translating
        virtual addresses through its CR3 page table. Either `pid` or `process_name` must be provided.

        Args:
            ko_module_path (str, optional): Path to the linpmem kernel module (`.ko` file). If specified,
                the module will be automatically loaded in `__enter__()`.
            device_path (str, optional): Path to the character device exposed by the driver (default: `/dev/linpmem`).
            process_name (str, optional): Name of the process whose memory should be accessed.
            pid (int, optional): PID of the target process. If `None`, will attempt to resolve from `process_name`.
            vm_pathname (str, optional): Optional pathname of a specific memory-mapped object (e.g., binary or shared object)
                to extract its virtual memory regions.

        Raises:
            ValueError: If neither `pid` nor `process_name` is provided.
            FileNotFoundError: If the process or driver device cannot be found.
            RuntimeError: If CR3 or virtual memory bounds cannot be determined.
        """
        self.ko_module_path = ko_module_path

        self.device_path = device_path
        self.process_name = process_name
        self.pid = pid if pid is not None else self.get_pid_by_process_name(self.process_name)
        self.vm_pathname = vm_pathname
        self.pathname_vm_regions = self.get_pathname_virtual_address_range(self.pid, self.vm_pathname)
        if self.pathname_vm_regions:
            start, size = self.pathname_vm_regions[0]
            self.process_vm_start_addr = start
            self.process_vm_size = size
            self.process_vm_end_addr = start + size

        if self.ko_module_path:
            self.setup_driver(self.ko_module_path, self.device_path)
        self.cr3 = self.get_cr3_for_process(self.pid)

    def __enter__(self):
        """
        Enters the context manager

        Returns:
            LinPyMem: The initialized memory reader instance.

        Raises:
            RuntimeError: If the driver fails to load or the device path is not created.
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exits the context manager and removes the kernel driver module.

        This ensures the driver is unloaded and any temporary device files
        or resources are cleaned up.

        Args:
            exc_type (Type[BaseException] | None): Exception type (if raised).
            exc_value (BaseException | None): Exception instance (if raised).
            traceback (TracebackType | None): Traceback object (if an exception was raised).

        Returns:
            None
        """
        self.remove_driver(self.device_path)

    def insert_kernel_module(self, module_path: str):
        """
        Inserts a kernel module: 
        > sudo insmod /home/workspace/Linpmem/linpmem.ko
        """
        command = ['sudo', 'insmod', module_path]
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"[linpymem] -> Kernel module '{module_path}' inserted successfully.")
        else:
            stderr = result.stderr.strip()
            if "File exists" in stderr:
                print(f"[linpymem] -> Kernel module '{module_path}' already inserted. Continuing.")
            else:
                raise Exception(f"Error inserting kernel module '{module_path}': {stderr}")

    def get_driver_major_number(self, driver_name: str) -> int:
        """
        Fetches kernel driver major number from /proc/devices
        """
        major_number = None
        try:
            with open('/proc/devices', 'r') as f:
                lines = f.readlines()

            in_char_devices = False
            for line in lines:
                line = line.strip()
                if 'Character devices:' in line:
                    in_char_devices = True
                    continue
                elif 'Block devices:' in line:
                    in_char_devices = False
                    continue

                if in_char_devices and line:
                    parts = line.split()
                    if len(parts) == 2:
                        major, name = parts
                        if name == driver_name:
                            major_number = int(major)
                            break

            if major_number is not None:
                return major_number
            else:
                raise Exception(f"Driver '{driver_name}' not found in /proc/devices.")

        except Exception as e:
            print(f"[linpymem] -> Error reading /proc/devices: {e}")
            return None

    def create_device_node(self, major_number: int, device_path: str):
        """
        Creates device from inserted kernel module and driver major number: 
        > sudo mknod /dev/linpmem c 42 0
        """
        if os.path.exists(device_path):
            print(f"[linpymem] -> Device node '{device_path}' already exists. Skipping creation.")
            return

        character_device = 'c'
        minor_number = '0'
        command = ['sudo', 'mknod', device_path, character_device, str(major_number), minor_number]
        try:
            subprocess.run(command, check=True)
            print(f"[linpymem] -> Device node '{device_path}' created successfully.")
        except subprocess.CalledProcessError as e:
            raise Exception(f"Error creating device node '{device_path}': {e}")

    def setup_driver(self, module_path: str, device_path: str):
        """
        Inserts the kernel module, retrieves the major number, and creates the device node.
        """
        driver_name = os.path.basename(device_path)
        self.insert_kernel_module(module_path)
        major = self.get_driver_major_number(driver_name)
        if major is None:
            raise Exception(f"Could not find major number for driver '{driver_name}' after insertion.")
        self.create_device_node(major, device_path)

    def remove_driver(self, device_path: str):
        """
        Removes the device node and unloads the kernel module using rmmod.
        """
        if os.path.exists(device_path):
            try:
                os.remove(device_path)
                print(f"[linpymem] -> Device node '{device_path}' removed successfully.")
            except Exception as e:
                print(f"[linpymem] -> Error removing device node '{device_path}': {e}")
        else:
            print(f"[linpymem] -> Device node '{device_path}' does not exist. Skipping removal.")

        try:
            driver_name = os.path.basename(device_path)
            subprocess.run(['sudo', 'rmmod', driver_name], check=True)
            print(f"[linpymem] -> Kernel module '{driver_name}' removed successfully.")
        except subprocess.CalledProcessError as e:
            if "No such file or directory" in str(e) or f"Module {driver_name} not found" in str(e):
                print(f"[linpymem] -> Kernel module '{driver_name}' is not loaded. Skipping removal.")
            else:
                raise Exception(f"Error removing kernel module '{driver_name}': {e}")

    def get_pid_by_process_name(self, process_name: str) -> int:
        """
        Iterates through processes to find process id
        """
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == process_name:
                return int(proc.info['pid'])
            
        raise Exception(f"Process '{process_name}' not found.")

    def get_pathname_virtual_address_range(self, pid: int, pathname: str) -> list[tuple[int, int]]:
        """
        Extracts the virtual memory regions associated with a given pathname from a process's memory map.

        Scans `/proc/<pid>/maps` to find all contiguous virtual memory regions mapped to the specified
        binary or shared object path. Returns a list of address ranges where each entry is a tuple
        of (start address, region size).

        Args:
            pid (int): The process ID to inspect.
            pathname (str): The pathname to match within the memory map (e.g., `/usr/bin/myapp`, `.so`, etc.).

        Returns:
            list[tuple[int, int]]: A list of (start_address, size) tuples for each matching region.

        Raises:
            Exception: If the `/proc/<pid>/maps` file cannot be read (e.g., process doesn't exist or permission denied).

        Notes:
            this will generally return a list of size 1 unless the specified pathname is not in a contiguous virtual memory range

        Example:
            >>> reader.get_pathname_virtual_address_range(1234, "/usr/lib/libc.so.6")
            [(0xcafebabe, 0x10000), (0xdeadbeef, 0x2000)]
        """
        try:
            with open(f'/proc/{pid}/maps', 'r') as maps_file:
                base_address = 0
                end_address = 0
                pathname_regions = []
                for line in maps_file:
                    address_range = line.split(' ')[0].split('-')
                    if pathname in line and base_address == 0:
                        base_address = int(address_range[0], 16)
                        end_address = int(address_range[1], 16)
                    elif pathname in line and base_address != 0:
                        end_address = int(address_range[1], 16) 
                    elif pathname not in line and base_address != 0:
                        pathname_regions.append((base_address, end_address-base_address))
                        base_address = 0
                        end_address = 0
                return pathname_regions
        except FileNotFoundError:
            raise Exception(f"Process with PID {pid} not found or permission denied.")

    def read_physical_memory(self, phys_addr: int, mode: PhysAccessMode, readbuffer_size: int = 0) -> tuple:
        """
        Reads physical memory from the specified physical address.

        Supports both direct primitive reads (byte, word, dword, qword) and buffer reads 
        across page boundaries with dynamic chunking. For buffer reads, the function ensures 
        the requested number of bytes are read correctly even if the range spans multiple 
        physical memory pages.

        Args:
            phys_addr (int): The starting physical memory address to read from.
            mode (PhysAccessMode): The access mode to use (e.g., PHYS_QWORD_READ, PHYS_BUFFER_READ).
            readbuffer_size (int, optional): Number of bytes to read in buffer mode. Must be positive 
                if `mode` is `PHYS_BUFFER_READ`. Defaults to 0.

        Returns:
            tuple:
                - bytes or int: The raw bytes read (in buffer mode) or primitive value (in scalar modes).
                - int: The number of bytes read (or mode repeated if scalar mode).
                - int: The requested buffer size (or mode repeated if scalar mode).

        Raises:
            ValueError: If `PHYS_BUFFER_READ` mode is used with `readbuffer_size <= 0`.
            IOError: If the ioctl operation fails during read.

        Notes:
            - This function interacts directly with linpmem driver via ioctl.
            - If a buffer read spans multiple pages, reads are broken into chunks to avoid page faults.

        Example:
            >>> reader.read_physical_memory(0x1234ABCD, PhysAccessMode.PHYS_BUFFER_READ, 64)
            (b'\\x01\\x02...', 64, 64)
        """
        
        ignored = 0
        out_value = 0  # This will hold the output for non-buffer reads
        write_access = 0  # Unused
        reserved1 = 0  # Reserved
        reserved2 = 0  # Reserved

        if mode == PhysAccessMode.PHYS_BUFFER_READ:
            if readbuffer_size <= 0:
                raise ValueError("For PHYS_BUFFER_READ mode, you must specify a positive buffer size.")

            result = bytearray()
            remaining = readbuffer_size
            current_addr = phys_addr

            with open(self.device_path, "rb", buffering=0) as f:
                while remaining > 0:
                    max_chunk = min(PAGE_SIZE - (current_addr % PAGE_SIZE), remaining)
                    chunk_buffer = ctypes.create_string_buffer(max_chunk)
                    chunk_ptr = ctypes.addressof(chunk_buffer)

                    data_transfer = bytearray(struct.pack(
                        "QQQQBBBBxxxx",  # 4 pad bytes needed for 64 bit alignment
                        current_addr,    # (_IN_) The physical address you want to read from.
                        ignored,         # (_OUT_) The read value. On return, this will contain either the read byte, word, dword or qword; or zero on error.
                        chunk_ptr,       # (_INOUT_) (buffer access mode) The usermode program must provide the buffer!
                        max_chunk,       # (_INOUT_) (buffer access mode) The usermode buffer size. Output will be less than input when a page boundary is encountered.
                        mode,            # (_IN_) Access mode type: byte, word, dword, qword, buffer.
                        write_access,    # Unused, set to 0.
                        reserved1,       # Reserved, set to 0.
                        reserved2        # Reserved, set to 0.
                    ))

                    fcntl.ioctl(f, IOCTL_LINPMEM_READ_PHYSADDR, data_transfer)
                    _, _, _, out_readbuffer_size, _, _, _, _ = struct.unpack("QQQQBBBBxxxx", data_transfer)

                    result += chunk_buffer.raw[:out_readbuffer_size]

                    if out_readbuffer_size < max_chunk:
                        break

                    current_addr += out_readbuffer_size
                    remaining -= out_readbuffer_size

            return (bytes(result), len(result), readbuffer_size)
        else:
            data_transfer = bytearray(struct.pack(
                "QQQQBBBBxxxx",  # 4 pad bytes needed for 64 bit alignment
                phys_addr,       # (_IN_) The physical address you want to read from.
                out_value,       # (_OUT_) The read value. On return, this will contain either the read byte, word, dword or qword; or zero on error.
                ignored,         # (_INOUT_) (buffer access mode) The usermode program must provide the buffer!
                ignored,         # (_INOUT_) (buffer access mode) The usermode buffer size. Output will be less than input when a page boundary is encountered.
                mode,            # (_IN_) Access mode type: byte, word, dword, qword, buffer.
                write_access,    # Unused, set to 0.
                reserved1,       # Reserved, set to 0.
                reserved2        # Reserved, set to 0.
            ))

            with open(self.device_path, "rb", buffering=0) as f:
                fcntl.ioctl(f, IOCTL_LINPMEM_READ_PHYSADDR, data_transfer)
                _, out_value, _, _, _, _, _, _ = struct.unpack("QQQQBBBBxxxx", data_transfer)
                return (out_value, mode, mode)
    
    def virtual_to_physical(self, virt_addr: int, cr3: int = 0) -> tuple[int, int]:
        """
        Translates a virtual address to its corresponding physical address using a CR3 page table base.

        This method interacts with linpmem kernel-mode driver to perform virtual-to-physical address translation,
        which is critical for reading memory of another process or inspecting raw page table mappings.

        Args:
            virt_addr (int): The virtual address to translate.
            cr3 (int, optional): The CR3 register value (base of the page table) to use for translation.
                If 0, the driver's default CR3 will be used. Use a non-zero value when targeting a
                specific process's address space.

        Returns:
            tuple[int, int]:
                - phys_addr (int): The translated physical address corresponding to the virtual address.
                - pte_virt_addr (int): The virtual address of the page table entry (PTE) used during translation.

        Raises:
            IOError: If the ioctl call to the driver fails.
            struct.error: If unpacking the result buffer fails.

        Example:
            >>> phys, pte = reader.virtual_to_physical(0x7ffd8c123000, cr3=0x1aa000)
            >>> print(hex(phys))  # 0x3fe3d000
        """
        with open(self.device_path, "rb", buffering=0) as f:
            vtop_info = bytearray(struct.pack(
                "QQQQ", 
                virt_addr, # (_IN_) The virtual address in question.
                cr3,       # (_IN_OPT_) Optional: specify a custom CR3 (of a foreign process) to be used in the translation service.
                0,         # (_OUT_) Returns the physical address you wanted.
                0          # (_OUT_) Returns the PTE virtual address, too.
            ))
            fcntl.ioctl(f, IOCTL_LINPMEM_VTOP_TRANSLATION_SERVICE, vtop_info)
            _, _, phys_addr, page_table_entry_virt_addr = struct.unpack("QQQQ", vtop_info)
            return phys_addr, page_table_entry_virt_addr

    def get_cr3_for_process(self, pid: int) -> int:
        """
        Retrieves the CR3 register (page table base) for a given process ID.

        This CR3 value represents the root of the process's page table hierarchy and
        is essential for performing virtual-to-physical address translation when reading
        memory from another process's address space.

        Args:
            pid (int): The process ID (PID) of the target process whose CR3 register should be retrieved.

        Returns:
            int: The CR3 value (physical address of the top-level page table).

        Raises:
            IOError: If the ioctl call fails or the driver is not available.
            struct.error: If the response structure cannot be unpacked correctly.

        Example:
            >>> cr3 = reader.get_cr3_for_process(1234)
            >>> print(hex(cr3))  # e.g., 0x1a4e000
        """
        with open(self.device_path, "rb", buffering=0) as f:
            cr3_info = bytearray(struct.pack(
                "QQ",
                pid, # (_IN_) A (foreign) process (pid_t) from which you want the CR3.
                0    # (_OUT_) returned CR3 value.
            ))
            fcntl.ioctl(f, IOCTL_LINPMEM_QUERY_CR3, cr3_info)
            _, cr3 = struct.unpack("QQ", cr3_info)
            return cr3

    def read_bytes(self, addr: int, size: int) -> bytes:
        """
        Reads a sequence of bytes from virtual memory.

        Args:
            addr (int): Virtual address to read from.
            size (int): Number of bytes to read.

        Returns:
            bytes: Raw byte sequence read from memory.
        """
        phys, _ = self.virtual_to_physical(addr, self.cr3)
        data, _, _ = self.read_physical_memory(phys, PhysAccessMode.PHYS_BUFFER_READ, size)
        return data

    def read_ptr(self, addr: int) -> int:
        """
        Reads an 8-byte pointer (QWORD) from virtual memory.

        Args:
            addr (int): Virtual address to read from.

        Returns:
            int: 64-bit pointer value.
        """
        phys, _ = self.virtual_to_physical(addr, self.cr3)
        val, _, _ = self.read_physical_memory(phys, PhysAccessMode.PHYS_QWORD_READ)
        return val
    
    def read_short(self, addr: int) -> int:
        """
        Reads a 2-byte unsigned short from virtual memory.

        Args:
            addr (int): Virtual address to read from.

        Returns:
            int: Unsigned 16-bit integer.
        """
        phys, _ = self.virtual_to_physical(addr, self.cr3)
        data, _, _ = self.read_physical_memory(phys, PhysAccessMode.PHYS_BUFFER_READ, 2)
        return struct.unpack("H", data)[0]

    def read_int(self, addr: int) -> int:
        """
        Reads a 4-byte signed integer from virtual memory.

        Args:
            addr (int): Virtual address to read from.

        Returns:
            int: Signed 32-bit integer.
        """
        phys, _ = self.virtual_to_physical(addr, self.cr3)
        data, _, _ = self.read_physical_memory(phys, PhysAccessMode.PHYS_BUFFER_READ, 4)
        return struct.unpack("i", data)[0]

    def read_float(self, addr: int) -> float:
        """
        Reads a 4-byte float from virtual memory.

        Args:
            addr (int): Virtual address to read from.

        Returns:
            float: Floating point value.
        """
        phys, _ = self.virtual_to_physical(addr, self.cr3)
        data, _, _ = self.read_physical_memory(phys, PhysAccessMode.PHYS_BUFFER_READ, 4)
        return struct.unpack("f", data)[0]

    def read_double(self, addr: int) -> float:
        """
        Reads an 8-byte double from virtual memory.

        Args:
            addr (int): Virtual address to read from.

        Returns:
            float: Double-precision floating point value.
        """
        phys, _ = self.virtual_to_physical(addr, self.cr3)
        data, _, _ = self.read_physical_memory(phys, PhysAccessMode.PHYS_BUFFER_READ, 8)
        return struct.unpack("d", data)[0]
    
    def read_vec3_float(self, addr: int) -> tuple[float, float, float]:
        """
        Reads a 3-component float vector from virtual memory.

        Args:
            addr (int): Virtual address to read from.

        Returns:
            tuple[float, float, float]: A 3D float vector (x, y, z).
        """
        phys, _ = self.virtual_to_physical(addr, self.cr3)
        data, _, _ = self.read_physical_memory(phys, PhysAccessMode.PHYS_BUFFER_READ, 12)
        return struct.unpack('3f', data)

    def read_vec3_double(self, addr: int) -> tuple[float, float, float]:
        """
        Reads a 3-component double vector from virtual memory.

        Args:
            addr (int): Virtual address to read from.

        Returns:
            tuple[float, float, float]: A 3D double vector (x, y, z).
        """
        phys, _ = self.virtual_to_physical(addr, self.cr3)
        data, _, _ = self.read_physical_memory(phys, PhysAccessMode.PHYS_BUFFER_READ, 24)
        return struct.unpack('3d', data)

    def read_utf_string(self, addr: int, max_len: int = 1024) -> str:
        """
        Reads a null-terminated UTF-8 string from virtual memory.

        Args:
            addr (int): Virtual address of the string.
            max_len (int, optional): Maximum length to read. Defaults to 1024.

        Returns:
            str: UTF-8 decoded string.
        """
        result = bytearray()
        while len(result) < max_len:
            try:
                phys, _ = self.virtual_to_physical(addr, self.cr3)
                byte_value, _, _ = self.read_physical_memory(phys, PhysAccessMode.PHYS_BYTE_READ)
            except:
                break

            if byte_value == 0:
                break

            result.append(byte_value)
            addr += 1

        return result.decode("utf-8", errors="ignore")
    
    def view_memory_region(self, start_address: int, size: int, row_size: int = 16):
        """
        Prints a memory region in a simple table
        """
        try:
            phys, _ = self.virtual_to_physical(start_address, self.cr3)
            data, _, _ = self.read_physical_memory(phys, PhysAccessMode.PHYS_BUFFER_READ, size)

            print(f"\n[linpymem] -> Memory Region from 0x{start_address:x}:")

            for i in range(0, len(data), row_size):
                address = start_address + i
                row_bytes = data[i:i + row_size]
                hex_values = ' '.join(f'{b:02x}' for b in row_bytes)
                ascii_repr = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in row_bytes)
                print(f"0x{address:016x}: {hex_values:<48}  {ascii_repr}")

            print("")

        except Exception as e:
            print(f"[linpymem] -> Failed to read memory at 0x{start_address:x}: {e}")