import uiautomator2 as u2
import easyocr
import re

def extract_distance_and_zone(device_ip="127.0.0.1:62001"):
    d = u2.connect(device_ip)
    img = d.screenshot(format='opencv')
    reader = easyocr.Reader(['es', 'en'])
    result = reader.readtext(img)
    distancia = None
    zona = None
    for _, text, _ in result:
        # Busca patrones como "3.2 km" o "Zona: Centro"
        dist_match = re.search(r"(\d+[\.,]?\d*)\s*km", text, re.I)
        zona_match = re.search(r"zona[:\s]+([\w\s]+)", text, re.I)
        if dist_match:
            distancia = float(dist_match.group(1).replace(",", "."))
        if zona_match:
            zona = zona_match.group(1).strip()
    return distancia, zona
