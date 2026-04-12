# Lógica de negocio: filtros de precio y cálculo de rentabilidad

def filtrar_precios(nodos, umbral):
    return [n for n in nodos if extraer_precio(n['text']) >= umbral]

def extraer_precio(texto):
    try:
        return float(texto.replace('RD$', '').replace(',', '').strip())
    except:
        return 0.0

def calcular_rentabilidad(precio, distancia):
    # Ejemplo simple
    return precio / (distancia + 1)

# Ejemplo de uso
if __name__ == "__main__":
    nodos = [
        {'text': 'RD$ 1200', 'bounds': '[100,200][200,300]'},
        {'text': 'RD$ 800', 'bounds': '[300,400][400,500]'}
    ]
    print(filtrar_precios(nodos, 1000))
    print(calcular_rentabilidad(1200, 10))
