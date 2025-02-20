from datetime import datetime


def get_current_time() -> str:
    """Return a string format date now for filename."""
    current_datetime = datetime.now(tz="Europe/Oslo").strftime("%Y-%m-%d_%H-%M-%S")
    return str(current_datetime)
