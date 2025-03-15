from pydantic import BaseModel

class ImageMetadata(BaseModel):
    dimensions: str
    file_format: str
    file_size: int
    date_time: str
    # exif, etc. if needed
