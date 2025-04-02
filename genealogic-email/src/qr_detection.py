import cv2
import params
from pyzbar.pyzbar import decode

def getQrData(imagePath):
    params.logger.info(f"Loading image from path: {imagePath}")
    # Load the image
    image = cv2.imread("{}".format(imagePath))

    if image is None:
        params.logger.error(f"Failed to load image from path: {imagePath}")
        return None

    # Resize the image to fit expected dimensions for analysis
    expected_width = 600
    expected_height = 500
    image = cv2.resize(image, (expected_width, expected_height))
    params.logger.info("Image resized for analysis")

    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    params.logger.info("Image converted to grayscale")

    # Apply GaussianBlur to reduce image noise and improve QR code detection
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    params.logger.info("GaussianBlur applied to image")

    # Decode the QR code
    qr_codes = decode(blurred)
    qr_elements = []

    # Process detected QR codes
    for qr in qr_codes:
        qr_data = qr.data.decode("utf-8")
        params.logger.info(f"QR Code Data: {qr_data}")
        qr_elements.append(qr_data)

    if len(qr_elements) == 2:
        params.logger.info("Two QR codes detected and processed")
        return qr_elements
    else:
        params.logger.warning("Less than two QR codes detected or more that two")
        return None