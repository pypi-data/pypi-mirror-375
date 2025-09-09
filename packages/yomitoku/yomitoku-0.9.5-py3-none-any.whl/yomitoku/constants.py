import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SUPPORT_OUTPUT_FORMAT = ["json", "csv", "html", "markdown", "md", "pdf"]
SUPPORT_INPUT_FORMAT = ["jpg", "jpeg", "png", "bmp", "tiff", "tif", "pdf"]
MIN_IMAGE_SIZE = 32
WARNING_IMAGE_SIZE = 720

PALETTE = [
    [255, 0, 0],
    [0, 255, 0],
    [0, 0, 255],
    [255, 255, 0],
    [0, 255, 255],
    [255, 0, 255],
    [128, 0, 0],
    [0, 128, 0],
    [0, 0, 128],
    [255, 128, 0],
    [0, 255, 128],
    [128, 0, 255],
    [128, 255, 0],
    [0, 128, 255],
    [255, 0, 128],
    [255, 128, 128],
    [128, 255, 128],
    [128, 128, 255],
    [255, 255, 128],
    [255, 128, 255],
    [128, 255, 255],
    [128, 128, 128],
]
