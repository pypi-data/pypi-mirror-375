import ctypes
import os
import platform
from enum import IntEnum
from typing import List


class HardwareIdAlgorithm(IntEnum):
    """Enumeration of available hardware ID algorithms."""

    Default = 0
    WindowsHardwareFingerprintId = 1
    WindowsComputerSystemProductId = 2
    WindowsCryptographyId = 3
    LinuxMachineId = 4
    CloudPlatformsId = 5


def _load_native_library():
    system = platform.system().lower()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    lib_paths = {
        "windows": os.path.join(base_dir, "lib", "hardware_id_generator.dll"),
        "darwin": os.path.join(base_dir, "lib", "libhardware_id_generator.so"),
        "linux": os.path.join(base_dir, "lib", "libhardware_id_generator.so"),
    }

    if system not in lib_paths or not os.path.exists(lib_paths[system]):
        raise OSError(f"Unsupported platform or missing library for {system}")

    native_lib = ctypes.CDLL(lib_paths[system], mode=ctypes.RTLD_LOCAL)
    native_lib.get_hardware_id.argtypes = [ctypes.c_int]
    native_lib.get_hardware_id.restype = ctypes.c_char_p
    native_lib.get_logs.argtypes = [ctypes.POINTER(ctypes.c_int)]
    native_lib.get_logs.restype = ctypes.POINTER(ctypes.c_char_p)
    native_lib.get_version.argtypes = []
    native_lib.get_version.restype = ctypes.c_char_p

    return native_lib


_native_lib = _load_native_library()


def get_hardware_id(algorithm: HardwareIdAlgorithm) -> str:
    """Compute and return the hardware ID based on the specified algorithm.

    Args:
        algorithm (HardwareIdAlgorithm): The algorithm to use for computing the hardware ID.

    Returns:
        str: The computed hardware ID.

    Raises:
        RuntimeError: If the hardware ID computation fails.
    """
    result = _native_lib.get_hardware_id(algorithm)
    if not result:
        raise RuntimeError("Failed to compute the hardware ID")
    return result.decode("utf-8")


def get_logs() -> List[str]:
    """
    Retrieve the logs collected by the system.

    Returns:
        List[str]: A list of log messages.

    Raises:
        RuntimeError: If log retrieval fails.
    """
    num_log_lines = ctypes.c_int()
    log_lines_ptr = _native_lib.get_logs(ctypes.byref(num_log_lines))

    if not log_lines_ptr:
        raise RuntimeError("Failed to retrieve logs")

    logs = [log_lines_ptr[i].decode("utf-8") for i in range(num_log_lines.value)]
    return logs


def get_version() -> str:
    """
    Retrieve the version of the hardware ID module.

    Returns:
        str: The version string.

    Raises:
        RuntimeError: If the version retrieval fails.
    """
    result = _native_lib.get_version()
    if not result:
        raise RuntimeError("Failed to retreive hardware ID module version")
    return _native_lib.get_version().decode("utf-8")
