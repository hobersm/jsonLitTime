from selenium import webdriver
from selenium.webdriver.common.by import By
from PIL import Image
from io import BytesIO

# Set up the Chrome WebDriver options
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Run in headless mode (without opening a UI window)
options.add_argument('--disable-gpu')  # Disable GPU hardware acceleration
options.add_argument('--window-size=1920x1080')  # Set the window size

# Path to your ChromeDriver
chrome_driver_path = r'C:\Users\Mat_H\OneDrive\Documents\Chrome\chromedriver-win64\chromedriver-win64\chromedriver.exe'

# Create a ChromeService object
cService = webdriver.ChromeService(executable_path=chrome_driver_path)

# Initialize the WebDriver with the specified options
driver = webdriver.Chrome(service=cService, options=options)

# Navigate to the URL
driver.get('http://books.google.ca/books?id=wxjIDwAAQBAJ&pg=PT8&dq=%221:03am%22&hl=&as_brr=6&as_pt=BOOKS&cd=13&source=gbs_api')

# Find the element by XPath using the new method
element = driver.find_element(By.XPATH, '/html/body/div[8]/div[2]/div/div[3]/div/div[1]/div/div/div[1]/div[2]/div/div[8]/div')

# Get the location and size of the element
location = element.location
size = element.size

# Take a screenshot of the entire page
screenshot = driver.get_screenshot_as_png()

# Crop the screenshot to get only the element
im = Image.open(BytesIO(screenshot))
left = location['x']
top = location['y']
right = location['x'] + size['width']
bottom = location['y'] + size['height']

im = im.crop((left, top, right, bottom))  # defines crop points

# Save the cropped screenshot to a file
im.save('element_screenshot.png')

# Close the WebDriver
driver.quit()
