from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image, ImageDraw, ImageFont
import time
import os
import re

def capture_reddit_post(
    url, 
    screenshot_output='title_screenshot.png', 
    text_output='post_content.txt', 
    translate_page=False, 
    custom_screenshot=False
):
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

        # Abrir la URL (traducida si corresponde)
        driver.get(url)
        if translate_page:
            translate_url = f"https://translate.google.com/translate?sl=auto&tl=en&u={url}"
            driver.get(translate_url)

        # Esperar explícitamente a que la página cargue
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Esperar a que se cargue el contenedor del post
        post_selector = f'//*[@id="t3_{code}"]'
        post_element = wait.until(EC.presence_of_element_located((By.XPATH, post_selector)))

        # Extraer título y contenido del post
        try:
            title = post_element.find_element(By.TAG_NAME, "h1").text
            content_xpath = f'//*[@id="t3_{code}-post-rtjson-content"]'
            content_element = driver.find_element(By.XPATH, content_xpath)
            content = content_element.text
            # Guardar el contenido en un archivo txt
            create_post_txt(text_output,title,content)
        except Exception as e:
            print(f"Error extracting content: {str(e)}")
            title = "Could not extract title"
            content = "Could not extract content"

        # Crear la captura personalizada o recortada
        if custom_screenshot:
            create_custom_screenshot(title, screenshot_output)
        else:
            # Captura recortada
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", post_element)
            time.sleep(1)
            driver.save_screenshot(screenshot_path)

            # Obtener las dimensiones del post
            dimensions = driver.execute_script("""
                const element = arguments[0];
                const rect = element.getBoundingClientRect();
                return {
                    x: rect.left,
                    y: rect.top,
                    width: rect.width,
                    height: rect.height,
                    scale: window.devicePixelRatio
                };
            """, post_element)

            # Recortar la imagen
            with Image.open(screenshot_path) as img:
                scale = dimensions['scale']
                crop_box = (
                    int(dimensions['x'] * scale),
                    int(dimensions['y'] * scale),
                    int((dimensions['x'] + dimensions['width']) * scale),
                    int((dimensions['y'] + dimensions['height']) * scale)
                )
                cropped_img = img.crop(crop_box)
                cropped_img.save(screenshot_output)
                print(f"Title screenshot saved as {screenshot_output}")

    except Exception as e:
        print(f"Error processing the post: {str(e)}")

    finally:
        driver.quit()
        # if os.path.exists(screenshot_path):
        #     os.remove(screenshot_path)

from PIL import Image, ImageDraw, ImageFont

def create_post_txt(text_output,title,content):
    try:
        # Guardar el contenido en un archivo txt
        with open(text_output, 'w', encoding='utf-8') as f:
            f.write(f"{title}\n\n")
            f.write(content)
        print(f"Content saved to {text_output}")
    except Exception as e:
        print(f"Error extracting content: {str(e)}")
        title = "Could not extract title"
        content = "Could not extract content"

def create_custom_screenshot(title, output_path):
    """
    Genera una captura personalizada usando un fondo predefinido con ajuste de texto inteligente.
    
    Args:
        title (str): El título del post de Reddit
        output_path (str): Ruta de salida para la imagen generada
    """
    try:
        # Abrir la imagen de fondo
        background = Image.open("title_background.png")
        draw = ImageDraw.Draw(background)

        # Configurar fuente base
        font_path = r"C:\Users\srcol\OneDrive\Documents\StableProjectorz\stable-diffusion-webui-forge\system\python\Lib\site-packages\matplotlib\mpl-data\fonts\ttf\DejaVuSans-Bold.ttf"
        
        # Función para encontrar el tamaño de fuente óptimo
        def get_optimal_font_size(text, max_width, max_height):
            font_size = 50  # Tamaño inicial
            font = ImageFont.truetype(font_path, font_size)
            
            while font_size > 10:
                # Dividir el texto en líneas
                lines = []
                words = text.split()
                current_line = words[0]
                
                for word in words[1:]:
                    test_line = current_line + " " + word
                    bbox = draw.textbbox((0, 0), test_line, font=font)
                    line_width = bbox[2] - bbox[0]
                    
                    if line_width <= max_width:
                        current_line = test_line
                    else:
                        lines.append(current_line)
                        current_line = word
                
                lines.append(current_line)
                
                # Calcular dimensiones totales
                line_bboxes = [draw.textbbox((0, 0), line, font=font) for line in lines]
                total_text_height = sum(bbox[3] - bbox[1] for bbox in line_bboxes)
                max_line_width = max(bbox[2] - bbox[0] for bbox in line_bboxes)
                
                # Verificar si el texto se ajusta
                if max_line_width <= max_width and total_text_height <= max_height:
                    return font_size, lines
                
                font_size -= 2
                font = ImageFont.truetype(font_path, font_size)
            
            return 10, lines  # Tamaño mínimo si no se ajusta

        # Calcular dimensiones máximas
        margin = 40  # Margen de espacio alrededor del texto
        max_width = background.width - (2 * margin)
        max_height = background.height - (2 * margin)

        # Obtener tamaño de fuente óptimo y líneas
        font_size, lines = get_optimal_font_size(title, max_width, max_height)
        font = ImageFont.truetype(font_path, font_size)

        # Calcular posición vertical
        line_bboxes = [draw.textbbox((0, 0), line, font=font) for line in lines]
        total_text_height = sum(bbox[3] - bbox[1] for bbox in line_bboxes)
        
        # Calcular posición inicial vertical
        start_y = (background.height - total_text_height) // 2

        # Dibujar cada línea
        current_y = start_y
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            
            # Calcular posición horizontal centrada
            x = (background.width - line_width) // 2
            
            # Dibujar línea
            draw.text((x, current_y), line, fill="white", font=font)
            
            # Avanzar a la siguiente línea
            current_y += bbox[3] - bbox[1]

        # Guardar imagen
        background.save(output_path)
        print(f"Custom screenshot saved as {output_path}")
    
    except Exception as e:
        print(f"Error creating custom screenshot: {str(e)}")

if __name__ == "__main__":
    url = input("Enter the Reddit post link: ")
    capture_reddit_post(url, translate_page=True, custom_screenshot=True)
