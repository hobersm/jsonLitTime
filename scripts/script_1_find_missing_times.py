import json
import os

# Function to generate all possible minutes in a day
def generate_all_minutes():
    all_minutes = []
    for hour in range(24):
        for minute in range(60):
            all_minutes.append(f'{hour:02d}:{minute:02d}')
    return all_minutes

# Function to find missing times in a single JSON file
def find_missing_times_in_file(file_path, all_minutes):
    with open(file_path, 'r') as file:
        data = json.load(file)
        for entry in data:
            time = entry['Time']
            if time in all_minutes:
                all_minutes.remove(time)
    return all_minutes

# Main script
def main():
    all_minutes = generate_all_minutes()

    # Get the current working directory
    current_directory = os.getcwd()

    # Get the parent directory
    # parent_directory = os.path.dirname(current_directory)

    # Loop through the files
    for i in range(24): 
        file_name = f'{i:02d}.json'
        file_path = os.path.join(current_directory, file_name)
        if os.path.exists(file_path):
            all_minutes = find_missing_times_in_file(file_path, all_minutes)

    file_path = os.path.join(current_directory+r'\scripts', 'missing_times.txt')
    # Write the missing times to a text file
    with open(file_path, 'w') as file:
        for time in all_minutes:
            file.write(f'{time}\n')

    print('The missing times have been written to missing_times.txt')

# Run the script
if __name__ == '__main__':
    main()
