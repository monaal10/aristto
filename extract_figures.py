import os
import logging
import fitz  # PyMuPDF
import io
from PIL import Image
from upload_to_s3 import upload_to_s3
from utils.extract_image_utils import convert_image_to_binary, download_pdf, cleanup_pdfs

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)


def extract_figures_from_paper(pdf_path):
    output_folder = os.getcwd()
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Open the PDF
    pdf_document = fitz.open(pdf_path)

    # Iterate through each page
    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]

        # Get the images on the page
        images = page.get_images(full=True)

        # Iterate through each image
        for img_index, img in enumerate(images):
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]

            # Get image extension
            ext = base_image["ext"]

            # Load it to PIL
            image = Image.open(io.BytesIO(image_bytes))
            # Save the image
            image_filename = f"page{page_num + 1}_img{img_index + 1}.{ext}"
            image_path = os.path.join(output_folder, image_filename)
            image.save(image_path)

    pdf_document.close()


def convert_figures_to_binary():
    folder_path = os.getcwd()
    png_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.png')]
    binary_image_list = []
    for png_file in png_files:
        full_path = os.path.join(folder_path, png_file)

        # Convert the image to binary
        binary_image = convert_image_to_binary(full_path)
        binary_image_list.append(binary_image)

        # Delete the local file
        os.remove(full_path)
        logger.info(f"Deleted local file: {png_file}")
    logger.info(f"Processed and deleted {len(png_files)} PNG files.")
    return binary_image_list


def get_figures_and_tables(research_paper):
    logger.info("Getting figures and tables")
    url = research_paper["oa_url"]
    figures_and_tables = {}
    if url and url != "":
        path_to_pdf = download_pdf(url)
        if path_to_pdf != "":
            extract_figures_from_paper(path_to_pdf)
            s3_files = (upload_to_s3())
            if len(s3_files) == 0:
                figures_and_tables[research_paper["open_alex_id"]] = []

            else:
                figures_and_tables[research_paper["open_alex_id"]] = s3_files
                #figures_and_tables[research_paper["open_alex_id"]] = (convert_figures_to_binary())
    cleanup_pdfs()
    return figures_and_tables


if __name__ == "__main__":
    extract_figures_from_paper("2312.10997v5.pdf")
