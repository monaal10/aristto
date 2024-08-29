import logging
import fitz  # PyMuPDF
import io
from PIL import Image
import base64
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


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
        return response.content
    except requests.RequestException as e:
        print("The pdf link provided could not be downloaded", e)
        return ""


def extract_figures_from_paper(pdf_content):
    try:
        pdf_stream = io.BytesIO(pdf_content)

        # Open the PDF with PyMuPDF
        doc = fitz.open(stream=pdf_stream, filetype="pdf")
        figures = []
        # Iterate through each page
        for page_num in range(len(doc)):
            page = doc[page_num]

            # Get the images on the page
            images = page.get_images(full=True)

            # Iterate through each image
            for img_index, img in enumerate(images):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]

                # Get image extension
                ext = base_image["ext"]

                # Load it to PIL
                image = Image.open(io.BytesIO(image_bytes))

                # Convert image to base64
                buffered = io.BytesIO()
                image.save(buffered, format=image.format if image.format else "PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()

                figures.append(img_str)

        doc.close()
        return figures
    except Exception as e:
        raise ("Could not extract figures from paper", e)


def get_figures_and_tables(research_paper):
    logger.info("Getting figures and tables")
    url = research_paper["oa_url"]
    figures_and_tables = {}
    if url and url != "":
        path_to_pdf = download_pdf(url)
        if path_to_pdf != "":
            binary_images = extract_figures_from_paper(path_to_pdf)
            if len(binary_images) == 0:
                figures_and_tables[research_paper["open_alex_id"]] = []

            else:
                figures_and_tables[research_paper["open_alex_id"]] = binary_images
    return figures_and_tables

