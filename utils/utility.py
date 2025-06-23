"""
Module with various utility functions for the backend.

This module has utility functions that can be used in many places such as FastAPI, LLM, Database, etc.
"""

# Python Standard Library imports
import time
from datetime import datetime
from pathlib import Path
from functools import wraps

# Third-party Library imports
import yaml


def load_config() -> dict[str, str | int | float]:
    """
    Function to load configuration from config.yaml file.
    
    Returns:
        LLM and FastAPI settings with types such as string, integer, and float
    """
    config_path = Path(__file__).parents[1] / "config.yaml"
    
    with open(config_path, mode="r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    return config


def print_time(func):
    """
    Decorator that prints start time, end time, and elapsed time for any function.
    
    Args:
        func: The function to be timed
        
    Returns:
        The wrapped function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Record start time
        start_time_raw = time.time()
        start_time_formatted = datetime.fromtimestamp(start_time_raw).strftime('%Y-%m-%d %H:%M:%S.%f')

        result = func(*args, **kwargs)

        # Record end time
        end_time_raw = time.time()
        end_time_formatted = datetime.fromtimestamp(end_time_raw).strftime('%Y-%m-%d %H:%M:%S.%f')

        elapsed_time = end_time_raw - start_time_raw
        hours = int(elapsed_time // 3600)
        minutes = int((elapsed_time % 3600) // 60)
        seconds = elapsed_time % 60

        start_time_end_time = f"Start time: {start_time_formatted}, End time: {end_time_formatted}"
        equal_line = "=" * len(start_time_end_time)

        print()
        print(equal_line)
        print(start_time_end_time)
        if hours == 0 and minutes == 0:
            print(f"Elapsed time: {seconds} seconds")
        elif hours == 0:
            print(f"Elapsed time: {minutes} minutes, {seconds} seconds")
        else:
            print(f"Elapsed time: {hours} hours, {minutes} minutes, {seconds} seconds")
        print(equal_line)
        print()

        return result
    return wrapper