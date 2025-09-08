from __future__ import annotations

import ctypes
from ctypes import wintypes

# Windows Job Object minimal wrapper via ctypes

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

# Constants
JOB_OBJECT_LIMIT_WORKINGSET = 0x00000001
JOB_OBJECT_LIMIT_PROCESS_TIME = 0x00000002
JOB_OBJECT_LIMIT_ACTIVE_PROCESS = 0x00000008
JOB_OBJECT_LIMIT_PROCESS_MEMORY = 0x00000100
JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000

PROCESS_ALL_ACCESS = 0x1F0FFF

JobObjectExtendedLimitInformation = 9

# Structures
class LARGE_INTEGER(ctypes.Structure):
    _fields_ = [("QuadPart", ctypes.c_longlong)]


class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("PerProcessUserTimeLimit", LARGE_INTEGER),
        ("PerJobUserTimeLimit", LARGE_INTEGER),
        ("LimitFlags", wintypes.DWORD),
        ("MinimumWorkingSetSize", ctypes.c_size_t),
        ("MaximumWorkingSetSize", ctypes.c_size_t),
        ("ActiveProcessLimit", wintypes.DWORD),
        ("Affinity", ctypes.c_size_t),
        ("PriorityClass", wintypes.DWORD),
        ("SchedulingClass", wintypes.DWORD),
    ]


class IO_COUNTERS(ctypes.Structure):
    _fields_ = [
        ("ReadOperationCount", ctypes.c_ulonglong),
        ("WriteOperationCount", ctypes.c_ulonglong),
        ("OtherOperationCount", ctypes.c_ulonglong),
        ("ReadTransferCount", ctypes.c_ulonglong),
        ("WriteTransferCount", ctypes.c_ulonglong),
        ("OtherTransferCount", ctypes.c_ulonglong),
    ]


class JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BasicLimitInformation", JOBOBJECT_BASIC_LIMIT_INFORMATION),
        ("IoInfo", IO_COUNTERS),
        ("ProcessMemoryLimit", ctypes.c_size_t),
        ("JobMemoryLimit", ctypes.c_size_t),
        ("PeakProcessMemoryUsed", ctypes.c_size_t),
        ("PeakJobMemoryUsed", ctypes.c_size_t),
    ]


# API prototypes
kernel32.CreateJobObjectW.restype = wintypes.HANDLE
kernel32.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]

kernel32.SetInformationJobObject.restype = wintypes.BOOL
kernel32.SetInformationJobObject.argtypes = [
    wintypes.HANDLE,
    wintypes.INT,
    ctypes.c_void_p,
    wintypes.DWORD,
]

kernel32.AssignProcessToJobObject.restype = wintypes.BOOL
kernel32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]

kernel32.OpenProcess.restype = wintypes.HANDLE
kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]

kernel32.CloseHandle.restype = wintypes.BOOL
kernel32.CloseHandle.argtypes = [wintypes.HANDLE]

kernel32.TerminateJobObject.restype = wintypes.BOOL
kernel32.TerminateJobObject.argtypes = [wintypes.HANDLE, wintypes.UINT]


class JobHandle:
    def __init__(self, handle: int | None):
        self.handle = handle

    def valid(self) -> bool:
        return bool(self.handle)

    def close(self) -> None:
        if self.handle:
            kernel32.CloseHandle(self.handle)
            self.handle = None

    def terminate(self, exit_code: int = 1) -> None:
        if self.handle:
            kernel32.TerminateJobObject(self.handle, exit_code)


def create_job(max_seconds: int | None = None, max_memory_mb: int | None = None, active_process_limit: int = 1) -> JobHandle:
    h = kernel32.CreateJobObjectW(None, None)
    if not h:
        return JobHandle(None)

    info = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
    flags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE

    # Time limit (per process user time)
    if max_seconds and max_seconds > 0:
        flags |= JOB_OBJECT_LIMIT_PROCESS_TIME
        # 100-nanosecond intervals
        info.BasicLimitInformation.PerProcessUserTimeLimit.QuadPart = int(max_seconds * 10_000_000)

    # Memory limit (per-process)
    if max_memory_mb and max_memory_mb > 0:
        flags |= JOB_OBJECT_LIMIT_PROCESS_MEMORY
        info.ProcessMemoryLimit = int(max_memory_mb) * 1024 * 1024

    # Process count
    if active_process_limit and active_process_limit > 0:
        flags |= JOB_OBJECT_LIMIT_ACTIVE_PROCESS
        info.BasicLimitInformation.ActiveProcessLimit = active_process_limit

    info.BasicLimitInformation.LimitFlags = flags

    res = kernel32.SetInformationJobObject(
        h,
        JobObjectExtendedLimitInformation,
        ctypes.byref(info),
        ctypes.sizeof(info),
    )
    if not res:
        kernel32.CloseHandle(h)
        return JobHandle(None)

    return JobHandle(h)


def assign_pid_to_job(job: JobHandle, pid: int) -> bool:
    if not job.valid():
        return False
    ph = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    if not ph:
        return False
    try:
        ok = kernel32.AssignProcessToJobObject(job.handle, ph)
        return bool(ok)
    finally:
        kernel32.CloseHandle(ph)
