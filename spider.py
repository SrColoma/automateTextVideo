from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
import time
import os
import re

def capture_reddit_post(url, screenshot_output='title_screenshot.png', text_output='post_content.txt'):
    # Configurar opciones para el navegador
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--lang=en-US")

    # Descargar automáticamente ChromeDriver
    service = Service(ChromeDriverManager().install())

    # Iniciar el navegador
    driver = webdriver.Chrome(service=service, options=chrome_options)
    screenshot_path = "full_screenshot.png"

    try:
        # Extraer el código único de la URL
        match = re.search(r'comments/([^/]+)', url)
        if not match:
            print("No se pudo extraer el código de la URL.")
            return
        code = match.group(1)
        print(f"Código extraído de la URL: {code}")

        # Convertir la URL para utilizar Google Translate
        translate_url = f"https://translate.google.com/translate?sl=auto&tl=en&u={url}"

        # Abrir la URL traducida
        driver.get(translate_url)

        # Esperar explícitamente a que la página traducida cargue
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Esperar unos segundos adicionales para que la traducción se aplique completamente
        time.sleep(5)

        # Esperar explícitamente a que el contenedor del post se cargue
        post_selector = f'//*[@id="t3_{code}"]'
        post_element = wait.until(
            EC.presence_of_element_located((By.XPATH, post_selector))
        )

        # Extraer el título y contenido del post
        try:
            title = post_element.find_element(By.TAG_NAME, "h1").text

            # Buscar y hacer clic en el botón "Read more" si existe
            try:
                read_more = driver.find_element(By.XPATH, "//button[contains(text(), 'read more')]")
                driver.execute_script("arguments[0].click();", read_more)
                time.sleep(1)  # Esperar a que se expanda el contenido
            except Exception:
                print("No se encontró botón 'read more' o ya está expandido")

            # Extraer el contenido completo
            content_xpath = f'//*[@id="t3_{code}-post-rtjson-content"]'
            content_element = driver.find_element(By.XPATH, content_xpath)
            content = content_element.text

            # Guardar el contenido en un archivo txt
            with open(text_output, 'w', encoding='utf-8') as f:
                f.write(f"Title: {title}\n\n")
                f.write("Content:\n")
                f.write(content)

            print(f"Content saved to {text_output}")

            # Ocultar el contenido usando JavaScript
            driver.execute_script("arguments[0].style.display = 'none';", content_element)
            time.sleep(1)

        except Exception as e:
            print(f"Error extracting content: {str(e)}")

        # Desplazarse al elemento y esperar a que se estabilice
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", post_element)
        time.sleep(1)

        # Capturar la pantalla completa
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved as {screenshot_output}")

    except Exception as e:
        print(f"Error processing the post: {str(e)}")

    finally:
        driver.quit()
        if os.path.exists(screenshot_path):
            os.remove(screenshot_path)

if __name__ == "__main__":
    url = input("Enter the Reddit post link: ")
    capture_reddit_post(url)
