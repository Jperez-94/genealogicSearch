from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os

def get_image_files_from_folder(folder_path):
    # Obtener todos los archivos de imagen en la carpeta y ordenarlos alfanuméricamente
    return sorted(
        [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith(('png', 'jpg', 'jpeg'))]
    )

def create_pdf_from_images(image_paths, output_pdf):
    # Dimensiones de una hoja A4 en píxeles (a 72 dpi)
    page_width, page_height = A4
    margin = 20  # Espacio con los bordes
    
    # Tamaño de cada imagen (suponiendo una cuadrícula de 2x3)
    img_width = (page_width - 3 * margin) / 2
    img_height = (page_height - 4 * margin) / 3
    
    c = canvas.Canvas(output_pdf, pagesize=A4)
    
    for i, img_path in enumerate(image_paths):
        if i % 6 == 0 and i > 0:
            c.showPage()  # Nueva página cada 6 imágenes
        
        img = Image.open(img_path)
        img.thumbnail((img_width, img_height))  # Redimensionar manteniendo proporción
        
        # Calcular posición en la cuadrícula 2x3
        col = (i % 6) % 2
        row = (i % 6) // 2
        
        x = margin + col * (img_width + margin)
        y = page_height - margin - (row + 1) * (img_height + margin)
        
        img.save(f"temp_{i}.jpg")  # Guardar temporalmente
        c.drawImage(f"temp_{i}.jpg", x, y, width=img_width, height=img_height)
    
    # Si la última página tiene menos de 6 imágenes, asegurarse de guardarla
    c.showPage()
    c.save()
    
    # Eliminar imágenes temporales
    for i in range(len(image_paths)):
        os.remove(f"temp_{i}.jpg")



# Uso: obtiene imágenes de una carpeta y genera el PDF
folder_path = "./qrs"  # Ruta de la carpeta con imágenes
image_files = get_image_files_from_folder(folder_path)
create_pdf_from_images(image_files, "qrs.pdf")