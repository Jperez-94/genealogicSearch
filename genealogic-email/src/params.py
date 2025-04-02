import networkx as nx
import logging
from datetime import datetime
import pygraphviz as pgv
from env import *

DEBUG_MODE = True

# Configure logging
log_filename = f"../log/log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(filename=log_filename, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

MASTER_EMAIL = MAIN_EMAIL
TOKEN_PATH = ENV_TOKEN_FILE
CRED_PATH = ENV_CREDENTIALS_FILE
SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",  # Required to read, modify, send, delete emails
    "https://www.googleapis.com/auth/gmail.labels",  # Required to manage labels
]

SAVE_FOLDER = "attachments"
LOAD_FOLDER = "treeimage"

data = DATABASE


# Tree variables
G = nx.DiGraph()
G_graph = pgv.AGraph(strict=True, directed=True)


# Email messages
MSG_INVALID_QRS = "No se detectaron códigos QR válidos."
MSG_NO_RELATION = "No se encontró una relación entre las personas."
MSG_STARTUP = "Servicio árbol genealógico iniciado."
MSG_RELATION = """Hola,
me complace comunicarle que {}.
Las personas que hacen posible esta relacion familiar son:
{}

Se adjunta una imagen con el árbol genealógico de la familia, resaltando la relacion consultada.
Saludos cordiales,

Familia Dominguez.
"""