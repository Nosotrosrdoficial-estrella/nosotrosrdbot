import easyocr
import uiautomator2 as u2

def ocr_buttons(device_ip="127.0.0.1:62001"):
    d = u2.connect(device_ip)
    img = d.screenshot(format='opencv')
    reader = easyocr.Reader(['es', 'en'])
    result = reader.readtext(img)
    return [text for _, text, _ in result if "RD$" in text or "Aceptar" in text]
