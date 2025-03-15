# HTX-DFE-Assessment

## Overview:
An image processing pipeline API that automatically processes images, generates thumbnails, extracts
metadata, and provides analysis through API endpoints.

The Image Processing API is designed to:
- Extract basic image metadata (dimensions, format, file size).
- Extract EXIF data from the image (if available; otherwise returns null).
- Generate an AI caption using the Hugging Face BLIP model.
- Store all processed data in a SQLite database.
- Generate two thumbnails (small and medium).
- Provide endpoints to list images, retrieve detailed information, and stream thumbnails.
- Log all processing steps and route-level events using Python’s logging module.

## Project Struture:
```plaintext
HTX-DFE-Assessment/
├── app/
│   ├── main.py             # Main python file.
│   ├── models.py           # Database or data model definitions.
│   ├── services.py         # Image processing, AI analysis, etc.
│   ├── database.py         # Database connection.
│   ├── schemas.py          # Pydantic schemas for request/response.
├── requirements.txt        # Required dependencies to install.
├── processing_log.txt      # Log file to log success and failures, created when run.sh is ran.
├── images.db               # Database, created when run.sh is ran.
├── README.md
└── run.sh                  # Bash script to run the Project.
```

## Requirements:

## Technology Stack:
- Python 3.x
- FastAPI – RESTful API framework
- SQLite – Local file-based database
- SQLAlchemy – ORM for database interactions
- Pillow – Image processing and EXIF extraction
- Transformers – Hugging Face library for AI captioning
- Uvicorn – ASGI server

## Setup Instructions

1. **Optional Clone the Repository or just download this file:**

   ```bash
   git clone <your-repo-url>
   cd HTX-DFE-Assessment
   ```

2. **Create and Activate a Virtual Environment:**

   ```bash
   python3-m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```
   
3. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the Database:**
   <br>Ensure that the database URL in app/database.py is correct. For example, it might be set to:
   ```bash
   DATABASE_URL = "sqlite:////HTX-DFE-Assessment/images.db"
   ```

5. **Run the API:**

   ```bash
   ./run.sh
   
   or
   
   uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```

## Accessing API:
1. **Access the API through localhost / 127.0.0.1(based on script) on port 8000**
   ```bash
   http://127.0.0.1:8000/docs
   ```
   <img width="1000" alt="Screenshot 2025-03-15 at 8 40 44 PM" src="https://github.com/user-attachments/assets/3fe54521-efe6-475f-a1cc-3371f7ed902b" />

## API EndPoints:
### 1. GET `/api/images`
**Description:**
Uploads an image and processes it. The API:

- Extracts basic image metadata (dimensions, format, file size).
-Extracts EXIF data (if available, returns null if not).
- Generates two thumbnails (small and medium).
- Generates an AI caption using the BLIP model.
- Stores all this information in a SQLite database.
- Returns a JSON response with metadata, EXIF data, caption, and thumbnail URLs.

**Request:**

- Method: POST
- Content-Type: multipart/form-data
- Form Fields:
   -image (file, required): The image file to upload (supports JPEG, PNG, etc.)

**Response Example (Web UI):**

<img width="1386" alt="image" src="https://github.com/user-attachments/assets/c27af610-19bd-46b7-84be-1a555dd55da6" />


### 2. GET /api/images
**Description:**  
Lists all processed images.

**Method:** `GET`

**Response Example (Web UI):**
<img width="1364" alt="image" src="https://github.com/user-attachments/assets/d96c6bc5-a00a-4cd3-b439-2ad4323b3741" />

### 3. GET api/images/{image_id}
**Description:**  
Retrieves detailed information about a specific image, including metadata, EXIF data, AI caption, and thumbnail URLs.

**Method:** `GET`

**Response Example (Web UI):**
<img width="1369" alt="image" src="https://github.com/user-attachments/assets/5349bcb4-0003-4cc4-bc0c-65962c819f9e" />

### 4. GET /api/images/{image_id}/thumbnails/{size}
**Description:**  
Streams the requested thumbnail image for the specified image ID and size (small or medium).

**Method:** `GET`

**Response Example (Web UI):**
<img width="1376" alt="image" src="https://github.com/user-attachments/assets/c82a2368-90b3-4a93-9297-f6e53a4ad7c1" />


### 5. GET /api/stats
**Description:**  
Returns processing statistics including total requests, success count, failure count, and average processing time.

**Method:** `GET`

**Response Example (Web UI):**
<img width="1371" alt="image" src="https://github.com/user-attachments/assets/283f05a6-9b2a-4921-ad36-282bf1f0a184" />

## Testing:
Ensure that you are in HTX-DFE-Assessment Root folder
   ```bash
   python3 -m pytest -v -s

   The following test will yield 3 pass test:
   1. An invalid txt file is passed, it will return and error and pass the test.
   2. A valid JPEG file is passed, it will return 200 and pass the test.
   3. A valid PNG file is passed, it will return 200 and pass the test.
   ```
**Response Example:** <br>
<img width="371" alt="image" src="https://github.com/user-attachments/assets/b23eb6cf-14fd-4bf1-b873-41e88e536f8e" />

### Uploading a file that is not png or jpg will result in a failure:
**Response Example (Web UI):**
<img width="1370" alt="image" src="https://github.com/user-attachments/assets/5ffaac0d-1563-43fb-ad48-1386092f2009" />




