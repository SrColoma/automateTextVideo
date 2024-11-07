# video automatico con python

clonacion de voz con f5 tts
audio captions con wisper
video con moviepy

## pasos:

instalar requerimentos txt
ajustar imagemagick
set audiocharacters - se necesita una voz de < de 15s para la clonacion
set texto - se agrega el texto que quiere decir

## luego

quiero poner video de fondo

## modificaciones

El archivo moviepy/video/fx/resize.py:37
resized_pil = pil_img.resize(new_size[::-1], Image.ANTIALIAS)
fue reemplazado por:
resized_pil = pil_img.resize(new_size[::-1], Image.LANCZOS)