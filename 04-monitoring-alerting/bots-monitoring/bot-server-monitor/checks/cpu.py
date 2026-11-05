import os
import psutil


def get_cpu():
    # 0.5s interval provides an accurate CPU percentage snapshot
    percent = psutil.cpu_percent(interval=0.5)
    logical_cores = psutil.cpu_count(logical=True) or 1
    physical_cores = psutil.cpu_count(logical=False) or logical_cores

    load_avg = os.getloadavg() if hasattr(os, "getloadavg") else (0.0, 0.0, 0.0)

    freq = None
    try:
        cpu_freq = psutil.cpu_freq()
        if cpu_freq:
            freq = {
                "current": cpu_freq.current,
                "min": cpu_freq.min,
                "max": cpu_freq.max,
            }
    except Exception:
        pass

    return {
        "percent": percent,
        "logical_cores": logical_cores,
        "physical_cores": physical_cores,
        "load_1m": load_avg[0],
        "load_5m": load_avg[1],
        "load_15m": load_avg[2],
        "freq": freq,
    }
