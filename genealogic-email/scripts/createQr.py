import qrcode
from env import DATABASE

# Número a codificar en el QR

for i in range(0,len(DATABASE)):

    # Crear el código QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(str(i))
    qr.make(fit=True)

    # Crear la imagen del código QR
    img = qr.make_image(fill="black", back_color="white")

    qr_name = f"qrcode_{"0"*(3-len(str(i)))}{str(i)}.png"
    # Guardar la imagen
    img.save(f"qrs/qrcode_{qr_name}.png")

    print(f"Código QR generado y guardado como '{qr_name}'")
