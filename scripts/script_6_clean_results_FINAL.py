import json
import os

def process_quotes(input_file, existing_prefix, output_prefix, base_path):
    """
    Processes quotes, merges with existing files, and saves in the correct format.
    Uses Quote_Long from input for the Quote field in the output.
    """

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    hourly_data = {}
    for hour in range(24):
        hourly_data[f"{hour:02d}"] = []

    # Load Existing Files and Merge
    for hour in range(24):
        hour_str = f"{hour:02d}"
        existing_filename = os.path.join(base_path, f"{hour_str}{existing_prefix}.json")
        output_filename = os.path.join(base_path, f"{hour_str}{output_prefix}.json")

        try:
            with open(existing_filename, 'r', encoding='utf-8') as infile:
                # Load existing data and convert to a list if needed
                existing_data = json.load(infile)
                if isinstance(existing_data, dict):
                    hourly_data[hour_str] = [existing_data]
                elif isinstance(existing_data, list):
                    hourly_data[hour_str] = existing_data
        except FileNotFoundError:
            hourly_data[hour_str] = []

    # Add new quotes, using Quote_Long for the Quote field
    for time_key, quotes in data.items():
        for quote_entry in quotes:
            if quote_entry.get("USE") == 1:
                hour = time_key.split(":")[0]
                new_quote = {
                    "Time": quote_entry["Time"],
                    "Quote_Time": quote_entry["Quote_Time"],
                    "Quote": quote_entry["Quote_Long"],  # Use Quote_Long here
                    "Title": quote_entry["Title"],
                    "Author": quote_entry["Author"]
                }
                hourly_data[hour].append(new_quote)

    # Sort and save with newlines and commas
    for hour in range(24):
        hour_str = f"{hour:02d}"
        output_filename = os.path.join(base_path, f"{hour_str}{output_prefix}.json")

        hourly_data[hour_str].sort(key=lambda x: int(x["Time"].split(":")[1]))

        with open(output_filename, 'w', encoding='utf-8') as outfile:
            outfile.write("[\n")
            for i, entry in enumerate(hourly_data[hour_str]):
                json.dump(entry, outfile, ensure_ascii=False, separators=(',', ':'))
                if i < len(hourly_data[hour_str]) - 1:
                    outfile.write(",")
                outfile.write("\n")
            outfile.write("]")

        print(f"Wrote to {output_filename}")

    print("Done!")

if __name__ == '__main__':
    input_json_file = r"C:\Users\Mat_H\OneDrive\Documents\GitHub\jsonLitTime\scripts\results\book_quotes_results_extended.json"
    existing_file_prefix = ""
    output_file_prefix = "" #"C"
    base_directory = r"C:\Users\Mat_H\OneDrive\Documents\GitHub\jsonLitTime"
    process_quotes(input_json_file, existing_file_prefix, output_file_prefix, base_directory)