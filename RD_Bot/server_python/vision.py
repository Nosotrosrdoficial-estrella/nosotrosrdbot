def get_ui_nodes(device_ip="127.0.0.1:62001"):
import uiautomator2 as u2
import re

def get_clickable_nodes(device_ip="127.0.0.1:62001"):
    d = u2.connect(device_ip)
    d.dump_hierarchy()
    nodes = d.xpath('//*[@clickable="true"]').all()
    result = []
    for node in nodes:
        text = node.attrib.get('text', '')
        resource_id = node.attrib.get('resource-id', '')
        content_desc = node.attrib.get('content-desc', '')
        bounds = node.attrib.get('bounds', '')
        # Calcular centro
        match = re.findall(r"\d+", bounds)
        if len(match) == 4:
            x1, y1, x2, y2 = map(int, match)
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        else:
            cx, cy = None, None
        result.append({
            'text': text,
            'resource_id': resource_id,
            'content_desc': content_desc,
            'center': (cx, cy),
            'bounds': bounds
        })
    return result

def buscar_precios_y_boton_aceptar(device_ip="127.0.0.1:62001", paquete_objetivo=None):
    d = u2.connect(device_ip)
    # Validar paquete activo
    if paquete_objetivo and d.info.get('currentPackageName') != paquete_objetivo:
        print(f"No es la app objetivo: {d.info.get('currentPackageName')}")
        return None
    nodos = get_clickable_nodes(device_ip)
    precios = []
    for n in nodos:
        if re.search(r"(RD\$|\$)\s*\d+", n['text']):
            precios.append(n)
    # Buscar botón 'Aceptar' más cercano a un precio
    for precio in precios:
        min_dist = float('inf')
        boton_cercano = None
        for n in nodos:
            if re.search(r"aceptar|tomar viaje|accept", n['text'], re.I) or 'accept' in n['resource_id'].lower():
                if precio['center'][0] is not None and n['center'][0] is not None:
                    dist = abs(precio['center'][1] - n['center'][1])
                    if dist < min_dist:
                        min_dist = dist
                        boton_cercano = n
        if boton_cercano:
            print(f"Precio: {precio['text']} en {precio['center']} | Botón: {boton_cercano['text']} en {boton_cercano['center']}")
            return precio, boton_cercano
    print("No se encontró botón de aceptar cerca de un precio.")
    return None

if __name__ == "__main__":
    # Ejemplo de uso
    print(get_clickable_nodes())
    buscar_precios_y_boton_aceptar(paquete_objetivo="com.nosotrosrd.app")
