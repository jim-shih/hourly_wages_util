import json
from datetime import datetime
import pandas as pd
from babel.dates import format_date


def generate_shift_data(year, month, shift_string):
    # Convert shift string to list and remove empty strings
    shift_list = [shift for shift in shift_string.split() if shift]

    # Generate date range
    start_date = f"{year}-{month:02d}-01"
    date_range = pd.date_range(start=start_date, periods=len(shift_list), freq="D")

    # Create DataFrame
    df = pd.DataFrame({"date": date_range, "shift": shift_list})

    return df


def create_shift_json(df, date_format="%Y-%m-%d"):
    return {row["date"].strftime(date_format): row["shift"] for _, row in df.iterrows()}


def save_json(data, filename):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)


def get_short_month(year, month):
    return format_date(datetime(year, month, 1), "MMM", locale="en").lower()


def main():
    # Configuration
    year = 2024
    month = 7
    shift_string = """X
    X
    X
    X
    X
    X
    C07
    X
    X
    X
    X
    X
    B07
    C07
    X
    X
    X
    X
    X
    C07
    C07
    X
    X
    X
    X X A02 B07
    X
    X X"""

    # Generate shift data
    shift_df = generate_shift_data(year, month, shift_string)

    # Create JSON data
    json_data = create_shift_json(shift_df)

    # Get short month name
    short_month = get_short_month(year, month)

    # Save JSON file
    filename = f"./data/{short_month}_shift.json"
    save_json(json_data, filename)

    print(
        f"Shift data for {short_month.capitalize()} {year} has been saved to {filename}"
    )


if __name__ == "__main__":
    main()
