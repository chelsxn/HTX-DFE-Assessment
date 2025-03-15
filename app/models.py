from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, LargeBinary

Base = declarative_base()

class ImageRecord(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(String, unique=True, index=True)
    status = Column(String)  # e.g., "processed"
    original_name = Column(String)
    uploaded_at = Column(String)  # or DateTime
    width = Column(Integer)
    height = Column(Integer)
    format = Column(String)
    size_bytes = Column(Integer)
    caption = Column(Text)         # AI-generated caption
    exif_data = Column(Text)       # JSON string representation of EXIF data
    thumb_small = Column(LargeBinary)  # Raw bytes for small thumbnail
    thumb_medium = Column(LargeBinary) # Raw bytes for medium thumbnail
