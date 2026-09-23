import psutil


def get_memory():
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()

    return {
        "total": memory.total,
        "used": memory.used,
        "available": memory.available,
        "percent": memory.percent,
        "swap_total": swap.total,
        "swap_used": swap.used,
        "swap_percent": swap.percent,
    }
