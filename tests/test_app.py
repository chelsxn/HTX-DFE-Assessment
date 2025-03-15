import pytest
from fastapi.testclient import TestClient
from app.main import app
from PIL import Image
import io

client = TestClient(app)

#Creating jpeg for test
def create_minimal_jpeg() -> bytes:
    """Generate a minimal valid JPEG image in memory."""
    # Create a simple 10x10 red image.
    img = Image.new("RGB", (10, 10), color="red")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()

#Creating png for test
def create_minimal_png() -> bytes:
    """Generate a minimal valid PNG image in memory."""
    from PIL import Image
    import io
    # Create a 10x10 blue image.
    img = Image.new("RGB", (10, 10), color="blue")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

#Invalid file, returns error, if so will pass
def test_upload_invalid_file():
    """
    Test uploading an invalid file (a text file) which should return a 400 or 422 error.
    """
    response = client.post(
        "/api/images/upload",
        files={"image": ("test.txt", b"hello, not an image", "text/plain")}
    )
    # Expecting an error status code
    assert response.status_code in (400, 422), f"Expected error code, got {response.status_code}"

#Valid jpeg file, returns 200, if so will pass
def test_upload_valid_jpeg():
    """
    Test uploading a valid JPEG image generated in memory.
    The API should accept it and return a 200 response with the proper JSON structure.
    """
    # Generate a minimal valid JPEG image in memory.
    fake_jpeg_data = create_minimal_jpeg()

    response = client.post(
        "/api/images/upload",
        data={"examiner_name": "ExaminerTest"},
        files={"image": ("generated.jpg", fake_jpeg_data, "image/jpeg")}
    )
    # Print output for debugging; remove or comment out later
    print("Status Code:", response.status_code)
    print("Response Body:", response.text)
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert data["status"] == "success", f"Response status not success: {data}"
    
    record = data["data"]
    assert "image_id" in record, "Missing 'image_id' in response data"
    assert "metadata" in record, "Missing 'metadata' in response data"
    
    # Since the API converts the format to lowercase, we expect "jpeg"
    assert record["metadata"]["format"] == "jpeg", f"Expected 'jpeg', got {record['metadata']['format']}"

#Valid png file, returns 200, if so will pass
def test_upload_valid_png():
    """
    Test uploading a valid PNG image.
    The API should accept it and return a 200 response with the proper JSON structure.
    """
    fake_png_data = create_minimal_png()

    response = client.post(
        "/api/images/upload",
        data={"examiner_name": "ExaminerPNGTest"},
        files={"image": ("test.png", fake_png_data, "image/png")}
    )
    # Uncomment these for debugging if needed:
    # print("Status Code:", response.status_code)
    # print("Response Body:", response.text)
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert data["status"] == "success", f"Response status not success: {data}"
    record = data["data"]
    assert "image_id" in record, "Missing 'image_id' in response data"
    assert "metadata" in record, "Missing 'metadata' in response data"
    # Expect the format to be "png" (lowercase) based on our API implementation.
    assert record["metadata"]["format"] == "png", f"Expected 'png', got {record['metadata']['format']}"
