import json
import sys
from pathlib import Path

import pandas as pd


def generate_shift_data(year: int, month: int, shift_string: str) -> pd.DataFrame:
    """
    Generate a DataFrame with shift data from a string of shifts.

    Args:
        year (int): The year for the shift data.
        month (int): The month for the shift data.
        shift_string (str): A string containing shift information.

    Returns:
        pd.DataFrame: A DataFrame with date and shift columns.
    """
    shift_list = shift_string.split()
    start_date = f"{year}-{month:02d}-01"
    date_range = pd.date_range(start=start_date, periods=len(shift_list), freq="D")
    return pd.DataFrame({"date": date_range, "shift": shift_list})


def create_shift_json(df: pd.DataFrame, date_format: str = "%Y-%m-%d") -> dict:
    """
    Create a JSON-compatible dictionary from a DataFrame of shift data.

    Args:
        df (pd.DataFrame): DataFrame containing date and shift information.
        date_format (str): Format string for dates. Defaults to "%Y-%m-%d".

    Returns:
        dict: A dictionary with dates as keys and shifts as values.
    """
    return {row["date"].strftime(date_format): row["shift"] for _, row in df.iterrows()}


def save_json(data: dict, filename: str) -> None:
    """
    Save data as a JSON file.

    Args:
        data (dict): The data to be saved.
        filename (str): The path where the JSON file will be saved.
    """
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)


def get_short_month(year: int, month: int) -> str:
    """
    Get a short string representation of year and month.

    Args:
        year (int): The year.
        month (int): The month.

    Returns:
        str: A string in the format "yyyy-mm".
    """
    return f"{year}-{month:02d}"


def main():
    if len(sys.argv) != 3:
        print("Usage: python create_shift_from_text.py <yyyy-mm> <shift_string>")
        sys.exit(1)

    date_arg, shift_string = sys.argv[1], sys.argv[2]

    try:
        year, month = map(int, date_arg.split("-"))
        if not (1 <= month <= 12):
            raise ValueError("Month must be between 1 and 12")
    except ValueError:
        print("Invalid date format. Please use yyyy-mm (e.g., 2024-09)")
        sys.exit(1)

    # Generate shift data
    shift_df = generate_shift_data(year, month, shift_string)

    # Create JSON data
    json_data = create_shift_json(shift_df)

    # Get short month name
    short_month = get_short_month(year, month)

    # Save JSON file
    filename = Path(f"./data/{short_month}_shift.json")

    # if the file exists, ask for confirmation
    if filename.exists():
        response = input(
            f"{filename} already exists. Do you want to overwrite it? (y/n): "
        )
        if response.lower() != "y":
            print("Exiting...")
            sys.exit(1)

    save_json(json_data, str(filename))

    print(f"Shift data for {short_month} {year} has been saved to {filename}")


if __name__ == "__main__":
    main()
