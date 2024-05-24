import requests
import json
import time
from tqdm import tqdm
from collections import deque
import os

# List of your API keys
#
api_keys = ['AIzaSyAIEaSrLnhTfK1SibL-XYOapm-REFVE7ac', 'AIzaSyD1f3NbesnumEPu-oRxwMsbJT44QfvXkTs', 'AIzaSyDE_l_-yoNIGRmcmiNvg2bXQQqH7Pga27I', 'AIzaSyBnkaKkie_rArAX0l3jh1j0Aeh7jhaU3Dc']
search_base_url = 'https://www.googleapis.com/books/v1/volumes'
quota_limit_per_key = 1000-23  # Set your quota limit per key here
requests_per_minute = 99  # Set the number of requests per minute limit here

# Function to perform a search query using the Google Books API
def search_books(query, current_key):
    params = {
        'q': query,
        'printType': 'books',
        'filter': 'paid-ebooks',
        'orderBy': 'relevance',
        'maxResults': 20,
        "langRestrict": "en",
        'key': current_key
    }
    try:
        response = requests.get(search_base_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')
    return {}

# Main script
def main():
    # Get the current working directory
    current_directory = os.getcwd()
    file_path = os.path.join(current_directory+r'\scripts', 'search_queries.json')

    with open(file_path, 'r') as file:
        queries = json.load(file)

    results = []
    request_times = deque(maxlen=requests_per_minute)  # Queue to store request times
    current_key_index = 0
    request_count_per_key = 0  # Track the number of requests made with the current API key

    for query_obj in tqdm(queries, desc='Searching', unit='query'):
        query = query_obj['search_query']
        time_value = query_obj['time']

        # Check if we need to sleep
        if len(request_times) >= requests_per_minute:
            elapsed_time = time.time() - request_times[0]
            if elapsed_time <= 60:
                time.sleep(61 - elapsed_time)

        # Check if the quota limit per key has been reached
        if request_count_per_key >= quota_limit_per_key:
            current_key_index += 1  # Switch to the next API key
            request_count_per_key = 0  # Reset request count for the new API key
            request_times.clear()  # Clear the queue for the new API key
            if current_key_index >= len(api_keys):
                print('All API keys quota limits reached. Stopping further searches.')
                break
            print(f'Switching to next API key: {current_key_index + 1}')

        result = search_books(query, api_keys[current_key_index])
        request_times.append(time.time())  # Add the current time to the queue
        request_count_per_key += 1  # Increment the request count for the current API key

        if 'items' in result:
            for item in result['items']:
                try:
                    # Attempt to extract the title, if available
                    title = item['volumeInfo'].get('title', 'Title not found')
                    authors = ', '.join(item['volumeInfo'].get('authors', ['Unknown Author']))
                    # Extract the text snippet if available
                    text_snippet = item.get('searchInfo', {}).get('textSnippet', 'Snippet not found')
                    url_preview = item['volumeInfo'].get('previewLink', 'Link not found')
                    categories = ', '.join(item['volumeInfo'].get('categories', ['Unknown Category']))
                    results.append({
                        'time': time_value,
                        'search_query': query,
                        'title': title,
                        'author': authors,
                        'categories':categories,
                        'snippet': text_snippet,  # Include the snippet in the results
                        'url': url_preview
                    })
                except KeyError as e:
                    print(f'KeyError: {e} in {item}')
        else:
            print(f'No results found for: {query}')
    
    file_path = os.path.join(current_directory+r'\scripts', 'book_quotes_results.json')

    with open(file_path, 'w') as file:
        json.dump(results, file, ensure_ascii=False, indent=2)

    print(f'Search results have been written to book_quotes_results.json. Total API requests made: {request_count_per_key}')

# Run the script
if __name__ == '__main__':
    main()