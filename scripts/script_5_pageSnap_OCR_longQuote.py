import json
import pytesseract
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from io import BytesIO
from tqdm import tqdm
import os
import re

# Function to clean and format the filename
def format_filename(s):
    return s.replace(':', '-')

# Function to extract a longer quote from the OCR text
def extract_long_quote(ocr_text, original_quote, select_val):
    # Create a translation table for similar characters
    translation_table = str.maketrans('o0', 'oo')

    # Flatten the OCR text by replacing newlines with spaces
    ocr_text_flat = ocr_text.replace('\n', ' ')

    # Fix spacing issues around punctuation
    ocr_text_flat = re.sub(r'\s+([?.!",;:])', r'\1', ocr_text_flat)
    ocr_text_flat = re.sub(r'([?.!",;:])\s+', r'\1 ', ocr_text_flat)
    # Replace multiple spaces with a single space
    ocr_text_flat = re.sub(r' +', ' ', ocr_text_flat)

    # Remove leading and trailing spaces
    trimmed_quote = original_quote.strip()
    # Trim leading and trailing periods (if more than one) from the original quote
    # trimmed_quote = original_quote.strip('. ')
    trimmed_quote = re.sub(r'^\.{2,}', '', trimmed_quote)
    trimmed_quote = re.sub(r'\.{2,}$', '', trimmed_quote)

    # Convert the OCR text and trimmed quote to lowercase for finding positions
    # and apply the translation table
    ocr_text_flat_lower = ocr_text_flat.lower().translate(translation_table)
    trimmed_quote_lower = trimmed_quote.lower().translate(translation_table)

    # Remove spaces and dashes - doesn't work currently since it changes the indexes
    # ocr_text_flat_lower = re.sub(r"[\s-]+", "", ocr_text_flat_lower)
    # trimmed_quote_lower = re.sub(r"[\s-]+", "", trimmed_quote_lower)
    
    # Get the first and last 20 characters of the trimmed quote in lowercase
    start_snippet = trimmed_quote_lower[:20]
    end_snippet = trimmed_quote_lower[-20:]

    # Find the start and end positions of the snippets in the flattened lowercase OCR text
    start_index_snippet = ocr_text_flat_lower.find(start_snippet)
    end_index_snippet = ocr_text_flat_lower.rfind(end_snippet)

    # If either snippet is not found, return an error message
    if start_index_snippet == -1:
        return "Quote not found in OCR text"
    elif end_index_snippet == -1:
        select_val = 3

    # Adjust the end index to the end of the snippet
    end_index_snippet += len(end_snippet)

    # Extract the context before and after the quote from the original OCR text
    start_extended = ocr_text_flat.rfind('.', 0, start_index_snippet)
    if start_extended == -1 or ocr_text_flat[start_extended-1] == '.':
        start_extended = start_index_snippet
    else:
        start_extended += 1  # Include the period

    end_extended = ocr_text_flat.find('.', end_index_snippet)
    if end_extended == -1 or ocr_text_flat[end_extended-1] == '.':
        end_extended = end_index_snippet
    else:
        end_extended += 1  # Include the period

    if select_val == 1:
        # Construct the extended quote using the original cases
        extended_quote = ocr_text_flat[start_extended:start_index_snippet] + trimmed_quote + ocr_text_flat[end_index_snippet:end_extended]
    elif select_val == 2:
        # Construct the extended quote using the ocr_text only
        extended_quote = ocr_text_flat[start_extended:end_extended]
    elif select_val == 3:
        # Construct the extended quote using the ocr_text at start, and then only the original quote
        extended_quote = ocr_text_flat[start_extended:start_index_snippet] + trimmed_quote
    else:
        # Just take the exact original quote (this should be done before this function call for performance increase)
        extended_quote = original_quote
    # Strip leading and trailing whitespace from the extended quote
    extended_quote = extended_quote.strip()

    return extended_quote

# Get the current working directory
current_directory = os.getcwd()
file_path = os.path.join(current_directory+r'\scripts', 'book_quotes_results_cleaned.json')

# Read the cleaned JSON data
with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Initialize the WebDriver
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920x2500') # Set a larger height for the window to capture more content vertically
chrome_driver_path = r'C:\Users\Mat_H\OneDrive\Documents\Chrome\chromedriver-win64\chromedriver-win64\chromedriver.exe'
cService = webdriver.ChromeService(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=cService, options=options)

# List of possible XPaths
xpaths = [
    '/html/body/div[8]/div[2]/div/div[3]/div/div[1]/div/div/div[1]/div[2]/div/div[8]/div',
    '/html/body/div[9]/div[2]/div/div[3]/div/div[1]/div/div/div[1]/div[2]/div/div[8]/div'
]

# Iterate through the entries and process those with SELECT == 1
# new_data = []
# for entry in tqdm(data, desc='Processing entries', unit='entry'):
# for i, entry in enumerate(data, start=1):

# Track Successful Find Count
successCount = 0
totalCount = 0

# Iterate through the grouped entries by time
new_data = {}
for time_key, entries in tqdm(data.items(), desc='Processing entries', unit='time_group'):
    new_data[time_key] = []  # Initialize a list for the new data grouped by time
    for entry in entries:

        select_val = entry.get('SELECT')
        if select_val in (1,2,3,4):
            totalCount+=1
            # Format the filename
            filename_base = format_filename(f"{entry['Time']}_{entry['Author']}")
            image_filename = f"{filename_base}.png"
            text_filename = f"{filename_base}.txt"

            image_file_path = os.path.join(current_directory+r'\scripts\results', image_filename)
            text_file_path = os.path.join(current_directory+r'\scripts\results', text_filename)

            if select_val != 4:
                # Try each XPath until the element is found
                element_found = False
                for xpath in xpaths:
                    try:
                        driver.get(entry['URL'])
                        element = driver.find_element(By.XPATH, xpath)
                        location = element.location
                        size = element.size
                        screenshot = driver.get_screenshot_as_png()
                        im = Image.open(BytesIO(screenshot))
                        im = im.crop((location['x'], location['y'], location['x'] + size['width'], location['y'] + size['height']))
                        element_found = True
                        break
                    except NoSuchElementException:
                        continue

                if not element_found:
                    print(f"Element not found for URL: {entry['URL']}")
                    continue

                # Run OCR on the image
                pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Mat_H\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
                extracted_text = pytesseract.image_to_string(im)

                # Extract a longer quote
                long_quote = extract_long_quote(extracted_text, entry['Quote'], select_val)
            elif select_val == 4:
                # If SELECT was set to 4, just take the original quote as the 'long_quote'
                long_quote = entry['Quote']
            # If Quote found, save page image, OCR text, and append entry with long quote
            if long_quote != "Quote not found in OCR text":
                successCount+=1
                if select_val != 4:
                    im.save(image_file_path)
                    with open(text_file_path, 'w', encoding='utf-8') as txt_file:
                        txt_file.write(extracted_text)
                    entry['Quote_Long'] = long_quote
                    entry['USE'] = None
                else:
                    entry['Quote_Long'] = long_quote
                    entry['USE'] = 1
                # new_data.append(entry)
                new_data[time_key].append(entry)  # Append the entry to the list for the current time group

# Close the WebDriver
driver.quit()

print(f'Found {successCount}/{totalCount} entries successfully --> {round((successCount/totalCount)*100)}% Success Rate')

output_file_path = os.path.join(current_directory+r'\scripts\results', 'book_quotes_results_extended.json')

# Save the new data to a new JSON file
with open(output_file_path, 'w', encoding='utf-8') as file:
    json.dump(new_data, file, ensure_ascii=False, indent=1)

print("Script execution completed.")
