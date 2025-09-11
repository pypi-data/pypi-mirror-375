# Image Converter

A simple Python package for converting images between different formats using Pillow.

## Installation

```bash
pip install image-converter
```

## Usage

```python
from image_converter import convert_image

convert_image('input.png', 'output.jpg', 'JPEG')
```

## Function

- `convert_image(input_path, output_path, output_format='JPEG')`: Converts the image at input_path to the specified format and saves it to output_path.

## Dependencies

- Pillow

## License

MIT License
