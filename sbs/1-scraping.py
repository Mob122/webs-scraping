from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

import pandas as pd
import random
import time

def esperar_y_encontrar_elemento(driver, xpath, timeout= 60):
    try:
        element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        return element
    except TimeoutException:
        print(f"Elemento no encontrado o no clicleable: {xpath}")
        return None

prefs = {
    "download.default_directory": r"/home/martin/Descargas/sbs",
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True,
}

if __name__ == "__main__":
    options = webdriver.firefox.options.Options()

    # options.binary_location = r"/usr/bin/brave-browser"  # Ruta típica en Linux/Ubuntu.

    options.add_argument('--start-maximized')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-popup-blocking')
    # options.add_experimental_option("prefs", prefs)
    
    driver = webdriver.Remote(
        command_executor= 'http://localhost:4444/wd/hub', # Docker Selenium Grid URL.
        options= options
    )

    driver.get("https://www.sbs.gob.pe/app/pp/INT_CN/Paginas/Busqueda/BusquedaPortal.aspx")    
    
    # 1. Aplicar Filtros con esperas explícitas
    input_estado_norma = esperar_y_encontrar_elemento(driver, '//*[@id="ctl00_ContentPlaceHolder1_rcbEstadoNorma_Input"]')
    if input_estado_norma:
        input_estado_norma.click()
        time.sleep(1)

    selector_filtro_vigente = esperar_y_encontrar_elemento(driver, '//*[@id="ctl00_ContentPlaceHolder1_rcbEstadoNorma_DropDown"]/div/ul/li[3]')
    if selector_filtro_vigente:
        selector_filtro_vigente.click()
        time.sleep(1.5)

    input_sistema = esperar_y_encontrar_elemento(driver, '//*[@id="ctl00_ContentPlaceHolder1_rcbCompendio_Input"]')
    if input_sistema:
        input_sistema.click()
        time.sleep(1)

    selector_sistema = esperar_y_encontrar_elemento(driver, '//*[@id="ctl00_ContentPlaceHolder1_rcbCompendio_DropDown"]/div/ul/li[12]')
    if selector_sistema:
        selector_sistema.click()
        time.sleep(1.5)

    input_busqueda = esperar_y_encontrar_elemento(driver, '//*[@id="ctl00_ContentPlaceHolder1_rbSearch_input"]')
    if input_busqueda:
        input_busqueda.click()
        # Espera crucial para que la tabla inicial termine de cargar tras el botón Buscar.
        time.sleep(3)  

    input_tamanio_pagina = esperar_y_encontrar_elemento(driver, '//*[@id="ctl00_ContentPlaceHolder1_rdgUltimaVersionNormas_ctl00_ctl03_ctl01_PageSizeComboBox_Input"]')
    if input_tamanio_pagina:
        input_tamanio_pagina.click()
        time.sleep(1.5)

    selector_tamanio_pagina = esperar_y_encontrar_elemento(driver, '//*[@id="ctl00_ContentPlaceHolder1_rdgUltimaVersionNormas_ctl00_ctl03_ctl01_PageSizeComboBox_DropDown"]/div/ul/li[3]')

    if selector_tamanio_pagina:
        selector_tamanio_pagina.click()
        time.sleep(8)

    # Obtener cantidad de páginas.
    strong_ctd_paginas = esperar_y_encontrar_elemento(driver, "//strong[2]")
    ctd_paginas = int(strong_ctd_paginas.text) if strong_ctd_paginas else 1
    print(f"Total de páginas detectadas: {ctd_paginas}")
    
    registros = []

    for pagina in range(ctd_paginas):
        print(f"Procesando: Página {pagina + 1} de {ctd_paginas}")
        
        # Guardamos el contenedor principal de la tabla actual para controlar el PostBack mas tarde.
        try:
            tabla_contenedor = driver.find_element(By.XPATH, "//div[contains(@id, 'rdgUltimaVersionNormas')]")
        except:
            tabla_contenedor = None
            
        # Esperar a que las filas estén presentes y visibles.
        xpath_filas = "//tr[contains(@id,'ctl00_ContentPlaceHolder1_rdgUltimaVersionNormas_ctl00') and not(contains(@id,'Header'))]"
        WebDriverWait(driver, 60).until(EC.visibility_of_any_elements_located((By.XPATH, xpath_filas)))
        ls_filas = driver.find_elements(By.XPATH, xpath_filas)
        
        # Extraer datos de la página actual.
        for fila in ls_filas:
            try:
                celdas = fila.find_elements(By.TAG_NAME, "td")            
                if len(celdas) < 10: 
                    continue
                    
                fila_registros = [celda.text for celda in celdas[1:10]]
                enlace = fila.find_element(By.XPATH, ".//a[contains(@id,'_Adjuntos2DOCLink')]").get_attribute('href')

                registro = {
                    "numero_norma": fila_registros[0],
                    "version": fila_registros[1],
                    "sumilla": fila_registros[2],
                    "tipo": fila_registros[3],
                    "estado": fila_registros[4],
                    "sistema": fila_registros[5],
                    "fecha_publicacion": fila_registros[6],
                    "fecha_emision": fila_registros[7],
                    "enlace": enlace
                }       
                registros.append(registro)
            except StaleElementReferenceException:
                # Si el DOM se mueve durante la lectura, evita que el script muera.
                continue

        # Navegación a la siguiente página.
        if pagina < ctd_paginas - 1:
            # Selector más robusto para el botón siguiente de Telerik (clase .rgPageNext).
            xpath_siguiente = "//input[@title='Next Page' or @class='rgPageNext']"
            button_siguiente = esperar_y_encontrar_elemento(driver, xpath_siguiente)
            
            if button_siguiente:
                # Intentar click normal primero para respetar eventos del navegador.
                try:
                    button_siguiente.click()
                except:
                    driver.execute_script("arguments[0].click();", button_siguiente)
                
                # CONTROL DE POSTBACK ABSOLUTO.
                # 1. Esperamos a que la tabla anterior empiece a destruirse o volverse obsoleta.
                if tabla_contenedor:
                    try:
                        WebDriverWait(driver, 15).until(EC.staleness_of(tabla_contenedor))
                    except TimeoutException:
                        pass
                
                # 2. Espera de cortesía obligatoria para portales gubernamentales.
                time.sleep(random.uniform(2, 6))
            else:
                print("No se pudo interactuar con el botón Siguiente. Rompiendo ciclo para salvar datos.")
                break
        
    driver.quit()

    # Guardar resultados.
    if registros:
        df = pd.DataFrame(registros)
        df.to_csv("output/sbs_sujetos_obligados_supervisados_otros_supervisores.csv", index= False)
        print(f"Scraping finalizado con éxito. {len(registros)} filas guardadas.")
    else:
        print("No se recolectaron registros.")