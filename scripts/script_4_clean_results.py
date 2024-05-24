import json
from bs4 import BeautifulSoup
import os
import re

# Function to clean HTML tags and decode HTML entities in the snippet
def clean_snippet(snippet):
    # Decode HTML entities and remove HTML tags
    cleaned_text = BeautifulSoup(snippet, "html.parser").get_text()
    # Manually replace Unicode escape sequences with actual characters
    # cleaned_text = cleaned_text.encode('utf-8').decode('unicode_escape')

    # Fix spacing issues around punctuation
    cleaned_text = re.sub(r'\s+([?.!",;:])', r'\1', cleaned_text)
    cleaned_text = re.sub(r'([?.!",;:])\s+', r'\1 ', cleaned_text)

    # Remove non-breaking space entities and Unicode non-breaking spaces
    return cleaned_text.replace('&nbsp;', ' ').replace('\xa0', ' ')

# Function to clean the search_query element by removing backslashes and double quotes
def clean_search_query(query):
    # Remove backslashes and double quotes
    return query.replace('\\"', '').replace('"', '')

# Get the current working directory and create file_path
current_directory = os.getcwd()
file_path = os.path.join(current_directory+r'\scripts', 'book_quotes_results.json')

# Load the original JSON data
with open(file_path, 'r') as file:
    data = json.load(file)

quoteclock_json_format = 0

# Process and clean the data
cleaned_data = []
for entry in data:
    if quoteclock_json_format:
        cleaned_entry = {
            "Time": entry.get("time", "Time not found"),
            "Quote_Time": clean_search_query(entry.get("search_query", "Search query not found")),
            "Quote": clean_snippet(entry.get("snippet", "Snippet not found")) if "snippet" in entry else "Snippet not found",
            "Title": entry.get("title", "Title not found"),
            "Author": entry.get("author", "Author not found")
        }
        cleaned_data.append(cleaned_entry)
    else:
        cleaned_entry = {
            "Time": entry.get("time", "Time not found"),
            "Quote_Time": clean_search_query(entry.get("search_query", "Search query not found")),
            "Quote": clean_snippet(entry.get("snippet", "Snippet not found")) if "snippet" in entry else "Snippet not found",
            "Title": entry.get("title", "Title not found"),
            "Author": entry.get("author", "Author not found"),
            "Categories": entry.get("categories", "Categories not found"),
            "URL": entry.get("url", "URL nsot found"),
            "SELECT": None
        }
        if 'Fiction' in cleaned_entry["Categories"]:
            cleaned_data.append(cleaned_entry)

file_path = os.path.join(current_directory+r'\scripts', 'book_quotes_results_cleaned.json')

# Save the cleaned and reformatted data to a new JSON file
with open(file_path, 'w') as file:
    if quoteclock_json_format:
        # Writing JSON data as a single line for each entry
        for item in cleaned_data:
            file.write(json.dumps(item) + ",\n")
    else:
        json.dump(cleaned_data, file, ensure_ascii=False, indent=0)

print('The cleaned book quotes have been saved to book_quotes_results_cleaned.json')
