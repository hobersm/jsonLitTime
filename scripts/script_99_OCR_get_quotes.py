from PIL import Image
import pytesseract

# If you don't have tesseract executable in your PATH, include the following:
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Mat_H\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

# Load the cropped screenshot
cropped_image = Image.open('element_screenshot.png')

# Extract text from the cropped image
extracted_text = pytesseract.image_to_string(cropped_image)

# Print the extracted text
print(extracted_text)

# Save the extracted text to a text file
with open('output_text.txt', 'w', encoding='utf-8') as txt_file:
    txt_file.write(extracted_text)

print("Extracted text saved to 'output_text.txt'")

# Close the image
cropped_image.close()