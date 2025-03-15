import logging
import hashlib
import io
import json
import base64
from PIL import Image, ExifTags
from transformers import pipeline

# Configure processing logs
logging.basicConfig(
    filename="processing_log.txt",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize the BLIP model for captioning using "image-to-text"
caption_pipeline = pipeline("image-to-text", model="Salesforce/blip-image-captioning-large")

def compute_sha256(file_bytes: bytes) -> str:
    """Compute SHA-256 hash of the image bytes."""
    sha256_hash = hashlib.sha256()
    sha256_hash.update(file_bytes)
    return sha256_hash.hexdigest()

def exif_data_to_serializable(value):
    """
    Recursively convert:
      - IFDRational objects → float
      - bytes → base64-encoded string
    so that the EXIF data becomes JSON-serializable.
    """
    if isinstance(value, dict):
        return {k: exif_data_to_serializable(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [exif_data_to_serializable(item) for item in value]
    else:
        if type(value).__name__ == "IFDRational":
            return float(value)
        if isinstance(value, bytes):
            return base64.b64encode(value).decode("utf-8")
        return value

def get_exif_data(file_bytes: bytes) -> dict:
    """
    Extract EXIF data from an image.
    Returns a dictionary of EXIF data or None if not available.
    """
    try:
        pil_img = Image.open(io.BytesIO(file_bytes))
        exif = pil_img._getexif()
        if not exif:
            logger.info("No EXIF data found.")
            return None
        exif_info = {}
        for tag_id, raw_val in exif.items():
            tag_name = ExifTags.TAGS.get(tag_id, tag_id)
            exif_info[tag_name] = raw_val
        exif_info = exif_data_to_serializable(exif_info)
        logger.info("Extracted EXIF data: %s", exif_info)
        return exif_info
    except Exception as e:
        logger.error("Error extracting EXIF data: %s", e)
        return None

def generate_thumbnails(file_bytes: bytes) -> dict:
    """
    Generate two thumbnails (small and medium) from the image bytes.
    Logs the process.
    """
    pil_img = Image.open(io.BytesIO(file_bytes))
    width, height = pil_img.size
    img_format = pil_img.format or "Unknown"
    
    logger.info("Generating thumbnails for image (%d x %d) in format %s", width, height, img_format)
    
    thumbs = {}
    # Generate small thumbnail
    small_img = pil_img.copy()
    small_img.thumbnail((128, 128))
    buf_small = io.BytesIO()
    small_img.save(buf_small, format=img_format)
    thumb_small = buf_small.getvalue()
    thumbs["small"] = thumb_small
    logger.info("Generated small thumbnail: size %s, bytes %d", small_img.size, len(thumb_small))
    
    # Generate medium thumbnail
    medium_img = pil_img.copy()
    medium_img.thumbnail((400, 400))
    buf_medium = io.BytesIO()
    medium_img.save(buf_medium, format=img_format)
    thumb_medium = buf_medium.getvalue()
    thumbs["medium"] = thumb_medium
    logger.info("Generated medium thumbnail: size %s, bytes %d", medium_img.size, len(thumb_medium))
    
    return {
        "width": width,
        "height": height,
        "format": img_format.lower(),
        "thumb_small": thumbs["small"],
        "thumb_medium": thumbs["medium"]
    }

def generate_caption(file_bytes: bytes) -> str:
    """
    Generate an AI caption for the image using the BLIP model.
    Logs the result.
    """
    pil_img = Image.open(io.BytesIO(file_bytes))
    results = caption_pipeline(pil_img)
    caption = results[0].get("generated_text", "No caption generated") if results else "No caption generated"
    logger.info("Generated caption: %s", caption)
    return caption
