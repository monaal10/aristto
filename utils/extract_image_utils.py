from bson.binary import Binary
import requests
import os
import base64
from PIL import Image
import io


def convert_image_to_binary(image_path):
    # Open the image
    with Image.open(image_path) as img:
        # Create a byte stream
        buffered = io.BytesIO()
        # Save the image to the byte stream in JPEG format
        img.save(buffered, format="JPEG")
        # Get the byte string and encode it
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        # Create the data URI

    return img_str


def convert_binary_to_image(image_data):

    image = Image.open(io.BytesIO(image_data))
    return image


def download_pdf(url):
    try:
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.44/72.124 Safari/537.36'
        headers = {
            'User-Agent': user_agent
        }
        # Send a GET request to the URL
        response = requests.get(url, headers=headers)

        # Check if the request was successful
        response.raise_for_status()

        # Check if the content type is PDF
        if 'application/pdf' in response.headers.get('Content-Type', ''):
            filename = url.split('/')[-1]

            # If the URL doesn't end with a filename, use a default name
            if not filename.lower().endswith('.pdf'):
                filename = 'downloaded_file.pdf'

            # Get the current directory
            current_dir = os.getcwd()

            # Create the full output path
            output_path = os.path.join(current_dir, filename)
            # Write the content to a file
            with open(output_path, 'wb') as file:
                file.write(response.content)
            print(f"PDF successfully downloaded: {output_path}")
            return output_path
        else:
            print("The URL does not point to a PDF file.")
            return ""

    except requests.RequestException as e:
        print("The pdf link provided could not be downloaded", e)
        return ""

def cleanup_pdfs():
    folder_path = os.getcwd()
    pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]
    for pdf_file in pdf_files:
        full_path = os.path.join(folder_path, pdf_file)
        os.remove(full_path)
    return
