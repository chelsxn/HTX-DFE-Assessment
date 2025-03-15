# HTX-DFE-Assessment

## Overview:
An image processing pipeline API that automatically processes images, generates thumbnails, extracts
metadata, and provides analysis through API endpoints.

Built using

## Project Struture:
```plaintext
HTX-DFE-Assessment/
├── app/
│   ├── main.py             # Main python file
│   ├── models.py           # Database or data model definitions
│   ├── services.py         # Image processing, AI analysis, etc.
│   ├── database.py         # Database connection 
│   ├── schemas.py          # Pydantic schemas for request/response
├── requirements.txt        # Required dependencies to install
├── processing_log.txt      # Log file to log success and failures
├── images.db               # Database
├── README.md
└── run.sh
```

## Requirements:

## Setup Instructions

1. **Clone the Repository:**

   ```bash
   git clone <your-repo-url>
   cd image-processing-api
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
   DATABASE_URL = "sqlite:////HTX/images.db"
   ```

5. **Run the API:**

   ```bash
   ./run.sh
   
   or
   
   uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```
