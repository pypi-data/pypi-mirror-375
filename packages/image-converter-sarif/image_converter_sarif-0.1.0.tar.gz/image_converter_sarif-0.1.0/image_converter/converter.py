from PIL import Image
import os

def convert_image(input_path, output_path, output_format='JPEG'):
    """
    Convert an image to a different format.

    :param input_path: Path to the input image
    :param output_path: Path to save the converted image
    :param output_format: Output format (e.g., 'JPEG', 'PNG')
    """
    with Image.open(input_path) as img:
        img.save(output_path, output_format)
