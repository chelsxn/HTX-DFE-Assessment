from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session
import uuid
import datetime
import time
import io
import json
import logging
from PIL import Image, ExifTags

from .database import get_db, engine
from .models import Base, ImageRecord
from .services import generate_thumbnails, generate_caption, get_exif_data

# Configure route-level logging
logging.basicConfig(
    filename="app_log.txt",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="My API",
    version="1.0.0",
    description="Digital Forensics !",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1}
)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified.")

# In-memory stats for demonstration
STATS_DB = {
    "total_requests": 0,
    "success_count": 0,
    "failure_count": 0,
    "total_processing_time": 0.0
}

@app.post("/api/images/upload")
def upload_image(image: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload an image.
    1) Extract basic metadata (dimensions, format, size).
    2) Extract EXIF data (if available; otherwise null).
    3) Generate two thumbnails (small, medium).
    4) Generate an AI caption.
    5) Store all data in SQLite.
    6) Return a JSON response with metadata, EXIF data, caption, and thumbnail URLs.
    """
    start_time = time.time()
    STATS_DB["total_requests"] += 1

    try:
        raw_bytes = image.file.read()

        # Basic image info
        pil_img = Image.open(io.BytesIO(raw_bytes))
        width, height = pil_img.size
        img_format = (pil_img.format or "unknown").lower()
        size_bytes = len(raw_bytes)

        # Extract EXIF data (if available)
        exif_data = get_exif_data(raw_bytes)
        # If no EXIF data, exif_data remains None
        exif_json = json.dumps(exif_data) if exif_data is not None else None

        # Generate thumbnails
        thumb_data = generate_thumbnails(raw_bytes)

        # Generate AI caption
        caption_text = generate_caption(raw_bytes)

        # Create unique ID and processed timestamp
        image_id = f"img_{uuid.uuid4().hex[:8]}"
        processed_at = datetime.datetime.utcnow().isoformat() + "Z"

        # Build and insert DB record
        db_record = ImageRecord(
            image_id=image_id,
            status="processed",
            original_name=image.filename,
            uploaded_at=processed_at,
            width=width,
            height=height,
            format=img_format,
            size_bytes=size_bytes,
            caption=caption_text,
            exif_data=exif_json,
            thumb_small=thumb_data["thumb_small"],
            thumb_medium=thumb_data["thumb_medium"]
        )
        db.add(db_record)
        db.commit()
        db.refresh(db_record)

        elapsed = time.time() - start_time
        STATS_DB["success_count"] += 1
        STATS_DB["total_processing_time"] += elapsed
        logger.info("Successfully processed image_id=%s in %.2f sec", image_id, elapsed)

        # Build JSON response (exclude raw thumbnail bytes)
        response_body = {
            "status": "success",
            "data": {
                "image_id": image_id,
                "original_name": image.filename,
                "processed_at": processed_at,
                "metadata": {
                    "width": width,
                    "height": height,
                    "format": img_format,
                    "size_bytes": size_bytes
                },
                "exif_data": exif_data,  # Already a JSON-serializable dict or null
                "analysis": {
                    "caption": caption_text
                },
                "thumbnails": {
                    "small": f"http://localhost:8000/api/images/{image_id}/thumbnails/small",
                    "medium": f"http://localhost:8000/api/images/{image_id}/thumbnails/medium"
                }
            },
            "error": None
        }
        return JSONResponse(status_code=200, content=response_body)

    except Exception as e:
        elapsed = time.time() - start_time
        STATS_DB["failure_count"] += 1
        STATS_DB["total_processing_time"] += elapsed
        logger.error("Error processing upload: %s", str(e), exc_info=True)
        return JSONResponse(
            status_code=400,
            content={
                "status": "failure",
                "data": None,
                "error": str(e)
            }
        )

@app.get("/api/images")
def list_images(db: Session = Depends(get_db)):
    records = db.query(ImageRecord).all()
    items = [{"image_id": r.image_id, "original_name": r.original_name, "status": r.status} for r in records]
    logger.info("Listing %d images", len(items))
    return {"status": "success", "data": items, "error": None}

@app.get("/api/images/{image_id}")
def get_image_details(image_id: str, db: Session = Depends(get_db)):
    record = db.query(ImageRecord).filter_by(image_id=image_id).first()
    if not record:
        logger.warning("Image not found: %s", image_id)
        raise HTTPException(status_code=404, detail="Image not found")
    
    exif_dict = {}
    if record.exif_data:
        exif_dict = json.loads(record.exif_data)
    
    response_data = {
        "image_id": record.image_id,
        "original_name": record.original_name,
        "status": record.status,
        "processed_at": record.uploaded_at,
        "metadata": {
            "width": record.width,
            "height": record.height,
            "format": record.format,
            "size_bytes": record.size_bytes
        },
        "analysis": {"caption": record.caption},
        "exif_data": exif_dict,
        "thumbnails": {
            "small": f"http://localhost:8000/api/images/{record.image_id}/thumbnails/small",
            "medium": f"http://localhost:8000/api/images/{record.image_id}/thumbnails/medium"
        }
    }
    logger.info("Returning details for image_id=%s", image_id)
    return {"status": "success", "data": response_data, "error": None}

@app.get("/api/images/{image_id}/thumbnails/{size}")
def get_thumbnail(image_id: str, size: str, db: Session = Depends(get_db)):
    record = db.query(ImageRecord).filter_by(image_id=image_id).first()
    if not record:
        logger.warning("Thumbnail requested for non-existent image: %s", image_id)
        raise HTTPException(status_code=404, detail="Image not found")
    if size not in ["small", "medium"]:
        logger.warning("Invalid thumbnail size requested: %s", size)
        raise HTTPException(status_code=400, detail="Invalid thumbnail size")
    
    thumb_bytes = record.thumb_small if size == "small" else record.thumb_medium
    if not thumb_bytes:
        logger.warning("Thumbnail not available for image_id=%s, size=%s", image_id, size)
        raise HTTPException(status_code=404, detail="Thumbnail not available")
    
    media_type = f"image/{record.format or 'jpeg'}"
    logger.info("Streaming thumbnail (%s) for image_id=%s", size, image_id)
    return StreamingResponse(io.BytesIO(thumb_bytes), media_type=media_type)

@app.get("/api/stats")
def get_stats():
    total_req = STATS_DB["total_requests"]
    success_count = STATS_DB["success_count"]
    failure_count = STATS_DB["failure_count"]
    total_time = STATS_DB["total_processing_time"]
    avg_time = total_time / success_count if success_count > 0 else 0
    logger.info("Stats requested: total=%d, success=%d, failure=%d", total_req, success_count, failure_count)
    return {
        "status": "success",
        "data": {
            "total_requests": total_req,
            "success_count": success_count,
            "failure_count": failure_count,
            "average_processing_time": avg_time
        },
        "error": None
    }
