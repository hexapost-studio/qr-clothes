# QR Clothes Server Prototype

This project demonstrates a server-side workflow that detects a QR code in an uploaded
image, computes its perspective, places a 3D model accordingly, and returns a rendered
image. The pipeline uses Python with OpenCV for detection and Blender for 3D rendering.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Ensure Blender is installed and accessible via the `blender` command.

## Running

```bash
python app.py
```

Send a `POST` request to `/render` with form data:

- `image`: image file containing a QR code.
- `model` (optional): path to a `.obj` model to place.

The server responds with the rendered PNG.

## Notes

- If `pyzbar` is unavailable, OpenCV's built-in QRCode detector is used as a fallback.
- The Blender script uses a simple cube if no model is provided.
