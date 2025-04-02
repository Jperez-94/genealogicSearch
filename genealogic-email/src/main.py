import os
import time
import base64
import params
from params import MSG_RELATION
import networkx as nx
import json
from genealogicSearch import get_relationship
from qr_detection import getQrData
from mailServer import *

# TODO: Respuesta a peticiones incorrectas. Emaill vacio
# TODO: Borrar todo lo que haya en la carpeta treeimage

for person_id, details in params.data.items():
    params.G.add_node(person_id, name=details["name"])
    for child_id in details["children"]:
        params.G.add_edge(person_id, child_id)
    for parent_id in details["parents"]:
        params.G.add_edge(person_id, parent_id)
    for partner_id in details["partner"]:
        params.G.add_edge(person_id, partner_id)

# Folder to save attachments
os.makedirs(params.SAVE_FOLDER, exist_ok=True)

def removeImgage(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        params.logger.info(f"Imagen {file_path} eliminada.")
    else:
        params.logger.warning("La imagen no existe.")

# Main loop
def main():
    params.logger.info("Starting Gmail monitoring...")
    # Loop to check and remove files in the attachments folder
    for filename in os.listdir(params.SAVE_FOLDER):
        file_path = os.path.join(params.SAVE_FOLDER, filename)
        removeImgage(file_path)

    service = authenticate_gmail()
    send_emailback(service, params.MASTER_EMAIL, params.MSG_STARTUP)
    processed_emails = []
    relaunch = False

    # TODO: poner un contador para responder solicitudes de X en X, con pausas de 20 segundos
    while True:
        try:
            params.logger.info("Checking for new emails...")
            unread_emails = get_unread_emails(service)
            if unread_emails:
                for email in unread_emails:
                    try:
                        params.logger.info(f"Processing email: {email['id']}")
                        process_result = process_email(service, email["id"])
                        params.logger.info(f"Email processed: {process_result}")
                        if "sender" not in process_result or "file_path" not in process_result:
                            params.logger.error(f"Unexpected process result format: {process_result}")
                            mark_as_read(service, email["id"])
                            continue
                        else:
                            if any(email["file_path"] == process_result["file_path"] for email in processed_emails):
                                params.logger.warning(f"Email {process_result} duplicado.")
                                mark_as_read(service, email["id"])
                            else:
                                params.logger.info(f"Email {process_result} añadido a la lista")
                                processed_emails.append(process_result)
                    except Exception as e:
                        params.logger.error(f"Error al procesar email: {e}")
                    
                    params.logger.info(f"Emails validos en lista: {len(processed_emails)}")
                
                params.logger.info(f"Emails validos: {len(processed_emails)}")
                num_emails = len(processed_emails)
                for _ in range(num_emails):
                    email = processed_emails[0]
                    params.logger.info(f"Procesando email: {email}")
                    params.logger.info(f"Emails restantes: {len(processed_emails)}")
                    params.logger.info("Procesando imagen...")
                    params.logger.info(f"Imagen de {email['sender']}: {email['file_path']}")

                    if not os.path.isfile(email['file_path']):
                        processed_emails.remove(email)
                        params.logger.error(f"La imagen {email['file_path']} no existe.")
                    else:
                        people_ids = getQrData(email['file_path'])
                        if people_ids:
                            params.logger.info(f"IDs de personas: {people_ids}")
                            request = get_relationship(people_ids[0], people_ids[1])
                            if len(request["path"]) == 0:
                                send_emailback(service, email["sender"], params.MSG_NO_RELATION)
                                params.logger.warning("No se encontró una relación entre las personas.")
                            else:
                                params.logger.info(f"Relacion: {request["relationship"]}")
                                response = MSG_RELATION.format(request["relationship"].replace("\n"," "), " - ".join([p.replace("\n", " ") for p in request["path"]]))
                                send_emailback(service, email["sender"], response, request["tree"])
                        else:
                            send_emailback(service, email["sender"], params.MSG_INVALID_QRS)
                            params.logger.warning("No se detectaron códigos QR válidos.")

                        removeImgage(email['file_path'])
                        params.logger.info(f"Email {email} procesado y eliminado.")
                        processed_emails.remove(email)
            else:
                params.logger.info("No new unread emails.")
            
            params.logger.info("Waiting for new emails...")
            time.sleep(120)  # Check every 10 seconds
        except nx.exception.NetworkXNoPath:
            params.logger.error("No se encontró una relación entre las personas.")
        except KeyboardInterrupt:
            params.logger.info("Stopping Gmail monitoring.")
            break
        except ConnectionResetError:
            params.logger.error("Error de conexión. Reintentando en 10 segundos...")
            relaunch = True
            break
        except Exception as e:
            params.logger.error(f"Error: {e}")
    
    if relaunch:
        params.logger.warning("Reintentando conexión en 60 segundos...")
        time.sleep(60)
        relaunch = False
        main()

if __name__ == "__main__":
    main()
