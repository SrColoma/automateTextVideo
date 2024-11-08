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

        # Abrir la URL
        driver.get(url)

        # Convertir la URL para utilizar Google Translate
        translate_url = f"https://translate.google.com/translate?sl=auto&tl=en&u={url}"

        # Abrir la URL traducida
        driver.get(translate_url)

        # Esperar explícitamente a que la página cargue
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        time.sleep(4)  # Esperar para que aparezca la opción de traducir


        # Esperar explícitamente a que el contenedor del post se cargue
        post_selector = f'//*[@id="t3_{code}"]'
        post_element = wait.until(
            EC.presence_of_element_located((By.XPATH, post_selector))
        )

        # Esperar a que se cargue el contenido
        time.sleep(1)

        # Extraer el título y contenido del post
        try:
            title = post_element.find_element(By.TAG_NAME, "h1").text

            # # Buscar y hacer clic en el botón "Read more" si existe
            # try:
            #     read_more = driver.find_element(By.XPATH, "//button[contains(text(), 'read more')]")
            #     driver.execute_script("arguments[0].click();", read_more)
            #     time.sleep(1)  # Esperar a que se expanda el contenido
            # except Exception as e:
            #     print("No se encontró botón 'read more' o ya está expandido")

            # Extraer el contenido completo
            content_xpath = f'//*[@id="t3_{code}-post-rtjson-content"]'
            content_element = driver.find_element(By.XPATH, content_xpath)
            content = content_element.text
            
            # Guardar el contenido en un archivo txt
            with open(text_output, 'w', encoding='utf-8') as f:
                f.write(f"{title}\n\n")
                f.write("\n")
                f.write(content)

            print(f"Content saved to {text_output}")

            # Ocultar el contenido usando JavaScript
            driver.execute_script("arguments[0].style.display = 'none';", content_element)
            time.sleep(1)  # Esperar a que se actualice la vista

        except Exception as e:
            print(f"Error extracting content: {str(e)}")
            content = "Could not extract post content"

        # Desplazarse al elemento y esperar a que se estabilice
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", post_element)
        time.sleep(1)

        # Obtener las dimensiones y posición exactas del elemento completo
        dimensions = driver.execute_script("""
            const element = arguments[0];
            const rect = element.getBoundingClientRect();
            const computedStyle = window.getComputedStyle(element);

            // Obtener el padding del elemento
            const paddingTop = parseInt(computedStyle.paddingTop);
            const paddingBottom = parseInt(computedStyle.paddingBottom);

            return {
                x: rect.left + window.pageXOffset,
                y: rect.top + window.pageYOffset,
                width: rect.width,
                height: rect.height + paddingTop + paddingBottom,
                scale: window.devicePixelRatio || 1
            };
        """, post_element)

        # Capturar la pantalla completa
        driver.save_screenshot(screenshot_path)

        # Procesar la imagen
        with Image.open(screenshot_path) as img:
            # Usar el factor de escala del dispositivo
            scale_factor = dimensions['scale']

            # Añadir un pequeño margen para asegurar que capturamos todo el contenido
            margin = 5 * scale_factor

            # Ajustar las coordenadas según el factor de escala y añadir margen
            crop_box = (
                max(0, int(dimensions['x'] * scale_factor - margin)),
                max(0, int(dimensions['y'] * scale_factor - margin)),
                min(img.width, int((dimensions['x'] + dimensions['width']) * scale_factor + margin)),
                min(img.height, int((dimensions['y'] + dimensions['height']) * scale_factor + margin))
            )

            # Recortar y guardar
            cropped_img = img.crop(crop_box)
            cropped_img.save(screenshot_output)
            print(f"Title screenshot saved as {screenshot_output}")

    except Exception as e:
        print(f"Error processing the post: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        driver.quit()
        if os.path.exists(screenshot_path):
            os.remove(screenshot_path)

if __name__ == "__main__":
    url = input("Enter the Reddit post link: ")
    capture_reddit_post(url)