import uiautomator2 as u2
import re

def find_buttons(device_ip="127.0.0.1:62001"):
    d = u2.connect(device_ip)
    d.dump_hierarchy()
    nodes = d.xpath('//*[@clickable="true"]').all()
    result = []
    for node in nodes:
        text = node.attrib.get('text', '')
        if re.search(r'(RD\$|Aceptar)', text, re.I):
            bounds = node.attrib.get('bounds', '')
            result.append({'text': text, 'bounds': bounds})
    return result
