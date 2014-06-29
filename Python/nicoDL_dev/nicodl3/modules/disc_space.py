#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ctypes import *

def free_disk_space(drive=None):
    """
    free_disk_space(drive)

    return
      (available, total, TotalFreeBytes) "GB"
               Œ©‚Â‚©‚ç‚È‚¢‚Æ‚«‚Í0
    """
    free_bytes_available       = c_ulonglong()
    total_number_of_bytes      = c_ulonglong()
    total_number_of_free_bytes = c_ulonglong()
    a = windll.kernel32.GetDiskFreeSpaceExA(
        drive,
        byref(free_bytes_available),
        byref(total_number_of_bytes),
        byref(total_number_of_free_bytes)
        )
    free_bytes_available = free_bytes_available.value / (1024**3)  # GB‚É’¼‚·
    total_number_of_bytes = total_number_of_bytes.value / (1024**3)  # GB‚É’¼‚·
    total_number_of_free_bytes = total_number_of_free_bytes.value / (1024**3)  # GB‚É’¼‚·
    return (free_bytes_available, total_number_of_bytes, total_number_of_free_bytes)

if __name__ == '__main__':
    print free_disk_space(r'e:\\')[0], 'GB'

