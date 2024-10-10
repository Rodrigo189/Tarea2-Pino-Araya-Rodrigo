# Integrantes:
# Rodrigo Pino Araya 21.446.391-1

import requests          # Para realizar solicitudes HTTP a la API de búsqueda de MAC
import getopt            # Para manejar argumentos de línea de comandos
import sys               # Para acceder a los argumentos y manejar salidas del programa
import time              # Para medir tiempos de respuesta
import subprocess        # Para ejecutar comandos del sistema, específicamente el comando 'arp -a'
import re                # Para manejar expresiones regulares y procesar la salida del comando 'arp'

def get_vendor_from_mac(mac):
    """
    Obtiene el nombre del fabricante (vendor) asociado a una dirección MAC utilizando la API de maclookup.app.
    Args:
        mac (str): Dirección MAC a consultar.
    Returns:
        str or None: Nombre del fabricante si se encuentra, de lo contrario None.
    """
    # Normaliza la dirección MAC eliminando ':' y '-', y convirtiéndola a minúsculas
    mac = mac.replace(":", "").replace("-", "").lower()
    # Construye la URL de la API con la dirección MAC normalizada
    url = f"https://api.maclookup.app/v2/macs/{mac}/company/name"
    try:
        # Realiza una solicitud GET a la API
        response = requests.get(url)
    except requests.exceptions.RequestException as e:
        # Maneja posibles excepciones de conexión
        print(f"Error de conexión: {e}")
        return None

    # Verifica si la respuesta HTTP fue exitosa (código de estado 200)
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return None

    # La respuesta es texto plano con el nombre del fabricante
    return response.text.strip()  # Retorna el nombre del fabricante limpio

def display_vendor_info(vendor_name, mac):
    """
    Muestra en la consola la dirección MAC y el nombre del fabricante.
    Args:
        vendor_name (str): Nombre del fabricante.
        mac (str): Dirección MAC.
    """
    print(f"MAC address : {mac}")
    if vendor_name and vendor_name.lower() != "not found":
        print(f"Fabricante : {vendor_name}")
    else:
        print("Fabricante : Not found")

def get_arp_table():
    """
    Obtiene la tabla ARP del sistema ejecutando el comando 'arp -a'.
    Returns:
        list: Lista de tuplas con (MAC, Tipo) para cada entrada ARP.
    """
    try:
        # Ejecuta el comando 'arp -a' y decodifica la salida usando 'cp1252' (común en Windows)
        arp_output = subprocess.check_output("arp -a", shell=True).decode('cp1252')
    except subprocess.CalledProcessError as e:
        # Maneja errores al ejecutar el comando 'arp'
        print(f"Error al ejecutar arp: {e}")
        return []
    except UnicodeDecodeError as e:
        # Maneja errores de decodificación de la salida del comando
        print(f"Error de decodificación: {e}")
        return []

    # Expresión regular para extraer MAC y Tipo de cada línea de la salida del comando 'arp'
    arp_entries = re.findall(r'(\d+\.\d+\.\d+\.\d+)\s+([\da-fA-F:-]+)\s+([\w\s]+)', arp_output)
    return arp_entries  # Retorna la lista de entradas ARP extraídas

def process_mac(mac):
    """
    Procesa una dirección MAC específica: obtiene el fabricante y muestra la información junto con el tiempo de respuesta.
    Args:
        mac (str): Dirección MAC a procesar.
    """
    start_time = time.time()  # Registra el tiempo de inicio
    vendor_name = get_vendor_from_mac(mac)  # Obtiene el fabricante de la MAC
    response_time = time.time() - start_time  # Calcula el tiempo de respuesta
    display_vendor_info(vendor_name, mac)  # Muestra la información del fabricante
    print(f"Tiempo de respuesta: {int(response_time * 1000)}ms")  # Muestra el tiempo de respuesta en ms

def process_arp():
    """
    Procesa todas las entradas de la tabla ARP del sistema, obteniendo y mostrando el fabricante para cada dirección MAC.
    """
    print("MAC/Vendor:")  # Imprime el encabezado de la salida
    arp_entries = get_arp_table()  # Obtiene la tabla ARP
    if not arp_entries:
        # Informa si no se encontraron entradas o hubo un error al obtenerlas
        print("No se encontraron entradas en la tabla ARP o hubo un error al obtenerlas.")
        return
    for entry in arp_entries:
        _, mac, _ = entry  # Desempaqueta la entrada ARP
        vendor_name = get_vendor_from_mac(mac)  # Obtiene el fabricante de la MAC
        vendor_name = vendor_name if vendor_name else 'Unknown'  # Asigna 'Unknown' si no se encuentra el fabricante
        print(f"{mac} / {vendor_name}")  # Imprime la información en formato "IP / MAC / Vendor"

def main(argv):
    """
    Función principal que maneja los argumentos de línea de comandos y dirige la ejecución del programa.
    Args:
        argv (list): Lista de argumentos de línea de comandos.
    """
    try:
        # Define las opciones cortas y largas que el script acepta
        opts, args = getopt.getopt(argv, "hm:a", ["mac=", "arp", "help"])
    except getopt.GetoptError:
        # Informa sobre el uso correcto si hay un error en los argumentos
        print("Uso: OUILookup.py --mac <mac> | --arp | [--help]")
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            # Muestra la ayuda de uso
            print("Uso: OUILookup.py --mac <mac> | --arp | [--help]")
            sys.exit()
        elif opt in ("-m", "--mac"):
            # Procesa una dirección MAC específica
            process_mac(arg)
        elif opt in ("--arp"):
            # Procesa todas las entradas de la tabla ARP
            process_arp()
        else:
            # Informa si se proporciona una opción no válida
            print("Opción no válida")
            sys.exit(2)

if __name__ == "__main__":
    # Ejecuta la función principal pasando los argumentos de línea de comandos (excluyendo el nombre del script)
    main(sys.argv[1:])
