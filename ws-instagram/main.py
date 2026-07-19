from dotenv import load_dotenv

import os

import pandas as pd
import random

from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import time

load_dotenv()

def esperar_elemento(driver, by, valor, es_varios_elementos= False, tiempo_espera= 60):
    """Espera hasta que un elemento sea visible en la página.

    Args:
        driver: Instancia del controlador de Selenium.
        by: Estrategia para localizar el elemento (por ejemplo, By.ID, By.XPATH).
        valor: Valor utilizado con la estrategia de localización.
        tiempo_espera: Tiempo máximo de espera en segundos (por defecto es 60 segundos).

    Returns:
        El elemento web una vez que es visible.
    """

    try:
        if not es_varios_elementos:
            elemento = WebDriverWait(driver, tiempo_espera).until(
                EC.visibility_of_element_located((by, valor))
            )
            return elemento    
        else:
            elementos = WebDriverWait(driver, tiempo_espera).until(
                EC.visibility_of_all_elements_located((by, valor))
            )
            return elementos
    except Exception as e:
        print(f"Error al esperar el elemento: {e}")
        return None


def delay(a= 1.2, b= 2.5):
    time.sleep(random.uniform(a, b))

def scroll_hasta_el_final(driver, pausa= 2, intentos_max= 3):
    # Desplazarse hasta el final de la página para cargar todo el contenido dinámico.
    ultimo_alto = driver.execute_script("return document.body.scrollHeight")
    intentos_sin_cambio = 0

    # Continuar desplazándose hasta que no haya más cambios en la altura de la página.
    while intentos_sin_cambio < intentos_max:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pausa)

        nuevo_alto = driver.execute_script("return document.body.scrollHeight")

        if nuevo_alto == ultimo_alto:
            intentos_sin_cambio += 1
        else:
            intentos_sin_cambio = 0
            ultimo_alto = nuevo_alto

options = webdriver.ChromeOptions()

# El --no-sandbox sirve para evitar problemas de permisos en entornos Linux.
options.add_argument("--no-sandbox")

# El --disable-dev-shm-usage ayuda a evitar problemas relacionados con el uso compartido de memoria en contenedores Docker.
options.add_argument("--disable-dev-shm-usage")

# User Agent realista sirve para evitar ser detectado como un bot porque muchos sitios web bloquean solicitudes con user agents sospechosos.
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

# Ocultar automatización.
# Estas opciones ayudan a que el navegador controlado por Selenium parezca más un navegador normal y menos un bot automatizado.
options.add_experimental_option("excludeSwitches", ["enable-automation"])
# Desactivar la extensión de automatización.
options.add_experimental_option("useAutomationExtension", False)
# Desactivar características de blink relacionadas con la automatización.
options.add_argument("--disable-blink-features=AutomationControlled")

usuario = os.getenv('IG_USERNAME')
password = os.getenv('IG_PASSWORD')

usuario_que_quiero_buscar = 'guticars.pe'

servicio = Service(executable_path= '../../services/chromedriver')
driver = webdriver.Chrome(service= servicio, options= options)

driver.get(f'https://www.instagram.com/')

elemento_usuario = esperar_elemento(driver, By.NAME, 'email')

if usuario:
    elemento_usuario.send_keys(usuario)  # Reemplaza con tu usuario de Instagram.

delay()
elemento_password = esperar_elemento(driver, By.NAME, 'pass')
if elemento_password:
    elemento_password.send_keys(password)  # Reemplaza con tu contraseña de Instagram.

delay()
boton_login = esperar_elemento(driver, By.XPATH, '//*[@id="login_form"]/div/div[1]/div/div[3]/div/div')
if boton_login:
    boton_login.click()

delay()
boton_lupa = esperar_elemento(driver, By.XPATH, '(//a[contains(@href, "#")])[1]')
if boton_lupa:
    boton_lupa.click()

elemento_busqueda = esperar_elemento(driver, By.XPATH, '//input[@placeholder="Busca"]')
if elemento_busqueda:
    elemento_busqueda.send_keys(usuario_que_quiero_buscar)

for intento in range(3):
    try:
        elemento = esperar_elemento(driver, By.XPATH, f'//a[contains(@href, "/{usuario_que_quiero_buscar}/")]')
        elemento.click()
        break
    except StaleElementReferenceException:
        print("Elemento stale, reintentando...")

scroll_hasta_el_final(driver, intentos_max= 2)
elementos_imgs = esperar_elemento(driver, By.XPATH, '//a[contains(@href,"/p/")]/div/div/img', es_varios_elementos= True)

# quit() al final para cerrar el navegador.
# driver.quit()

data = []
for img in elementos_imgs:
    data.append({
        'src': img.get_attribute('src'),
        'alt': img.get_attribute('alt')
    })

pd.DataFrame(data).to_csv(f'output/{usuario_que_quiero_buscar}.csv', index= False)

