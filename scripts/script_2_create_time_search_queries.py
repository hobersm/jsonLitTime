import itertools
from num2words import num2words
import json
import os

# Helper function to convert 24-hour time to 12-hour time with AM/PM
def to_12hr_time(hour, minute):
    suffix = "AM" if hour < 12 else "PM"
    hour_12 = hour % 12
    if hour_12 == 0:
        hour_12 = 12
    return f"{hour_12}:{minute:02d} {suffix}"

def to_12hr_time2(hour, minute):
    suffix = "am" if hour < 12 else "pm"
    hour_12 = hour % 12
    if hour_12 == 0:
        hour_12 = 12
    return f"{hour_12}:{minute:02d}{suffix}"

# Function to generate search queries for a given time
def generate_search_queries(time):
    hour, minute = map(int, time.split(':'))
    minute_word = num2words(minute).replace('-', ' ')
    minute_word_with_o = f"o {minute_word}" if minute < 10 else minute_word
    queries = [
        # f'"{time}"',
        f'"{to_12hr_time2(hour, minute)}"',
        f'"{minute_word} minutes after {num2words(hour % 12 if hour % 12 else 12)}"',
        f'"{minute} minutes after {hour % 12 if hour % 12 else 12}"',
        f'"{num2words(60 - minute)} minutes to {num2words((hour + 1) % 12 if (hour + 1) % 12 else 12)}"',
        f'"{60 - minute} minutes to {((hour + 1) % 12) if (hour + 1) % 12 else 12}"',
        f'"{num2words(hour % 12 if hour % 12 else 12)} o\'clock"' if minute == 0 else '',
        f'"{num2words(hour)} {minute_word_with_o}"' if minute != 0 else '',
        f'"{to_12hr_time(hour, minute)}"'
    ]
    # Remove any empty strings from the list
    queries = [query for query in queries if query]
    return queries

# Main script
def main():
    # Get the current working directory
    current_directory = os.getcwd()
    file_path = os.path.join(current_directory+r'\scripts', 'missing_times.txt')

    with open(file_path, 'r') as file:
        times = file.readlines()

    # Remove newline characters
    times = [time.strip() for time in times]

    # Generate search queries for each time
    all_queries = []
    for time in times:
        for query in generate_search_queries(time):
            all_queries.append({'time': time, 'search_query': query})

    file_path = os.path.join(current_directory+r'\scripts', 'search_queries.json')

    # Write the search queries with time to a JSON file
    with open(file_path, 'w') as file:
        json.dump(all_queries, file, indent=2)

    print('Search queries with time have been written to search_queries.json')

# Run the script
if __name__ == '__main__':
    main()