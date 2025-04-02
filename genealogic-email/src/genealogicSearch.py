import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
import json
import os
import params
import matplotlib.pyplot as plt


for person_id, details in params.data.items():
    params.G.add_node(person_id, name=details["name"])
    for child_id in details["children"]:
        params.G.add_edge(person_id, child_id)
    for parent_id in details["parents"]:
        params.G.add_edge(person_id, parent_id)
    for partner_id in details["partner"]:
        params.G.add_edge(person_id, partner_id)

# Diccionario para mapear parejas a subgrafos
grouped_partners = {}

# Agregar nodos y relaciones
for key, data in params.data.items():
    # Si tiene pareja, agregar a un subgrafo
    if data["partner"]:
        pareja_id = tuple(sorted([key] + data["partner"]))  # Identificador único para la pareja
        if pareja_id not in grouped_partners:
            subgraph = params.G_graph.add_subgraph(
                name=f'cluster_{"_".join(pareja_id)}',
                style='dashed',
                color="#4B0082",  # Violeta oscuro
                fillcolor="white",  # Fondo blanco
                penwidth=2  # Grosor del borde
            )
            grouped_partners[pareja_id] = subgraph
        subgraph = grouped_partners[pareja_id]
        subgraph.add_node(key, label = data["name"].replace("\n","\\n"), shape="box")

    else:
        params.G_graph.add_node(key, label = data["name"].replace("\n", "\\n"), shape="box")  # Agregar nodo individual si no tiene pareja

    # Agregar conexiones a los hijos
    for child in data["children"]:
        params.G_graph.add_edge(key, child)


def draw_graph(highlight_nodes=[], filename = "tree"):

    params.G_graph.get_node(highlight_nodes[0]).attr["style"] = "filled"
    params.G_graph.get_node(highlight_nodes[0]).attr["fillcolor"] = "#B0E57C"  # Verde pastel
    params.G_graph.get_node(highlight_nodes[len(highlight_nodes)-1]).attr["style"] = "filled"
    params.G_graph.get_node(highlight_nodes[len(highlight_nodes)-1]).attr["fillcolor"] = "#B0E57C"  # Verde pastel


    for nodo in highlight_nodes[1:len(highlight_nodes)-1]:
        if nodo in params.G_graph.nodes():
            params.G_graph.get_node(nodo).attr["style"] = "filled"
            params.G_graph.get_node(nodo).attr["fillcolor"] = "#FFFF99"  # Verde pastel
    
    # Configurar el diseño del gráfico
    params.G_graph.layout(prog="dot")  # Disposición en árbol
    file_path = os.path.join(params.LOAD_FOLDER, filename)
    params.G_graph.draw(f"{file_path}.png")  # Guardar imagen

    # Mostrar la imagen con Matplotlib
    plt.imread(f"{file_path}.png")

    for nodo in highlight_nodes:
        params.G_graph.get_node(nodo).attr["style"] = "filled"
        params.G_graph.get_node(nodo).attr["fillcolor"] = "white"  # Verde pastel



def check_siblings(id1, id2):
    if params.data[id1]["parents"] == params.data[id2]["parents"]:
        return True
    
    return False

def check_parents(id1, id2):
    if id2 in params.data[id1]["parents"]:
        return True
    
    return False

def check_child(id1, id2):
    if id2 in params.data[id1]["children"]:
        return True
    
    return False

def check_significant(id1, id2):
    if id2 in params.data[id1]["partner"]:
        return True
    
    return False

def check_close_family(path):
    if len(path) == 2:
        if check_significant(path[0], path[1]):
            return "Pareja"
        elif check_child(path[0], path[1]):
            return "Padre - Madre"
        elif check_parents(path[0], path[1]):
            return "Hijo - Hija"
    elif len(path) == 3:
        if check_siblings(path[0], path[2]):
            return "Hermano - Hermana"
        elif check_parents(path[0], path[1]) and check_child(path[2], path[1]):
            return "Nieto - Nieta"
        elif check_parents(path[2], path[1]) and check_child(path[0], path[1]):
            return "Abuelo - Abuela"
        elif check_significant(path[0], path[1]) and check_parents(path[1], path[2]):
            return "Yerno - Nuera"
        elif check_child(path[0], path[1]) and check_significant(path[1], path[2]):
            return "Suegro - Suegra"
        elif check_parents(path[0], path[1]) and check_parents(path[2], path[1]):
            return "Hermanastro/a"
    elif len(path) == 4:
        if check_siblings(path[0], path[2]) and check_significant(path[2], path[3]):
            return "Cuñado - Cuñada"
        if check_siblings(path[1], path[3]):
            return "Sobrino - Sobrina"
        elif check_siblings(path[0], path[2]):
            return "Tio - Tia"
        elif check_child(path[0], path[1]) and check_significant(path[1], path[3]):
            return "Suegro - Suegra"
        elif check_parents(path[1], path[0]) and check_parents(path[2], path[1]) and check_child(path[2], path[3]):
            return "Bisabuelo - Bisabuela"
        elif check_parents(path[2], path[3]) and check_parents(path[1], path[2]) and check_child(path[1], path[0]):
            return "Bisnieto - Bisnieta"
    elif len(path) == 5:
        if check_siblings(path[1], path[3]) and check_significant(path[0], path[1]):
            return "Tio - Tia"
        elif check_siblings(path[1], path[3]):
            return "Primo - Prima"
        elif (check_siblings(path[0], path[2]) and check_parents(path[3], path[2]) and check_parents(path[4], path[3])):
            return "Tio/a Abuelo/a"
        elif check_parents(path[0], path[1]) and check_parents(path[1], path[2]) and check_siblings(path[2], path[4]):
            return "Sobrino/a nieto/a"
        elif check_parents(path[0], path[1]) and check_parents(path[1], path[2]) and check_parents(path[2], path[3]) and check_parents(path[3], path[4]):
            return "Tataranieto/a"
        elif check_child(path[0], path[1]) and check_child(path[1], path[2]) and check_child(path[2], path[3]) and check_child(path[3], path[4]):
            return "Tatarabuelo/a"

    elif len(path) == 6:
        if check_siblings(path[0], path[2]):
            return "Tio/a bisabuelo/a"
        elif check_parents(path[0], path[1]) and check_parents(path[1], path[2]) and check_parents(path[2], path[3]) and check_parents(path[3], path[4]) and check_parents(path[4], path[5]):
            return "Trastataranieto/a"
        elif check_child(path[0], path[1]) and check_child(path[1], path[2]) and check_child(path[2], path[3]) and check_child(path[3], path[4]) and check_child(path[4], path[5]):
            return "Trastatarabuelo/a"
    elif len(path) == 7:
        if check_siblings(path[0], path[2]):
            return "Tio/a tatarabuelo/a"
    
    return None

def political_family(path):
    if check_significant(path[0], path[1]) and check_significant(path[len(path)-1], path[len(path)-2]):
        temp = check_close_family(path[1:len(path)-1])
        if temp == None:
            return check_far_family(path[1:len(path)-1])
        else:
            return (temp + " politico/a")
    elif check_significant(path[0], path[1]):
        temp = check_close_family(path[1:len(path)])
        if temp == None:
            return check_far_family(path[1:len(path)])
        else:
            return (temp + " politico/a")
    elif check_significant(path[len(path)-1], path[len(path)-2]):
        temp = check_close_family(path[0:len(path)-1])
        if temp == None:
            return check_far_family(path[0:len(path)-1])
        else:
            return (temp + " politico/a")
        
    return None

def check_far_family(path):
    if len(path) > 5:
        distance = len(path) - 5
        temp = check_close_family(path[0:5])
        if temp == "Primo - Prima":
            if distance == 1:
                return "Tio/a segundo/a"
            elif distance == 2:
                return "Primo/a segundo/a"
            elif distance == 3:
                return "Sobrino/a tercero/a"
            elif distance == 4:
                return "Sobrino/a nieto/a tercero/a"
        elif temp == "Tio/a Abuelo/a":
            if distance == 1:
                return "Tio/a abuelo/a segundo/a"
            elif distance == 2:
                return "Tio/a tercero"
            elif distance == 3:
                return "Primo/a tercero/a"
            elif distance == 4:
                return "Sobrino/a cuarto/a"
        else:
            temp = check_close_family(path[distance:len(path)])
            if temp == "Primo - Prima":
                if distance == 1:
                    return "Sobrino/a segundo/a"
                elif distance == 2:
                    return "Sobrino/a nieto/a segundo/a"
                elif distance == 3:
                    return "Sobrino/a bisnieto/a segundo/a"
            elif temp == "Tio/a Abuelo/a":
                if distance == 1:
                    return "Tio/a segundo/a"
                elif distance == 2:
                    return "Primo/a segundo/a"
                elif distance == 3:
                    return "Sobrino/a tercero/a"
                elif distance == 4:
                    return "Sobrino/a nieto/a tercero/a"
            elif temp == "Sobrino/a nieto/a":
                if distance == 1:
                    return "Sobrino/a bisnieto/a"
                elif distance == 2:
                    return "Sobrino/a tataranieto/a"
    if len(path) > 6:
        distance = len(path) - 6
        temp = check_close_family(path[distance:len(path)])
        if temp == "Tio/a bisabuelo/a":
            if distance == 1:
                return "Tio/a abuelo/a segundo/a"
            elif distance == 2:
                return "Tio/a tercero/a"
            elif distance == 3:
                return "Primo/a tercero/a"
            elif distance == 4:
                return "Sobrino/a cuarto/a"
    if len(path) > 7:
        distance = len(path) - 7
        temp = check_close_family(path[distance:len(path)])
        if temp == "Tio/a tatarabuelo/a":
            if distance == 1:
                return "Tio/a bisabuelo/a segundo/a"
            elif distance == 2:
                return "Tio/a abuelo/a tercero/a"
            elif distance == 3:
                return "Tio/a cuarto/a"
            elif distance == 4:
                return "Primo/a cuarto/a"
    
    return None



def determine_relationship(path):
    relationship = None
    relationship = check_close_family(path)

    if relationship == None:
        relationship = political_family(path)
 
    if relationship == None:
        relationship = check_far_family(path)
    


    return relationship

def find_relationship(person1, person2):
    try:
        path = nx.shortest_path(params.G, person1, person2)
        # temp_path = [node for node in path if node != "0"]
        params.logger.info(f"Path found: {path}")
        relationship = determine_relationship(path)
        if relationship == None:
            relationship = political_family(path)
        path_names = [params.data[person_id]["name"] for person_id in path if person_id != "0"]
        return {
            "relationship": f"{params.data[person1]['name']} es {relationship} de {params.data[person2]['name']}",
            "path": path_names,
            "path_id": path
        }
    except nx.NetworkXNoPath:
        try:
            path = nx.shortest_path(params.G, person2, person1)
            # temp_path = [node for node in path if node != "0"]
            params.logger.info(f"Path found: {path}")
            relationship = determine_relationship(path)
            path_names = [params.data[person_id]["name"] for person_id in path if person_id != "0"]
            return {
                "relationship": f"{params.data[person2]['name']} es {relationship} de {params.data[person1]['name']}",
                "path": path_names,
                "path_id": path
            }
        except nx.NetworkXNoPath:
            params.logger.warning("No direct relationship found.")
            return {
                "relationship": "No hay relación directa.",
                "path": [],
                "path_id": []
            }
    except KeyError as e:
        params.logger.error(f"KeyError: {e}")
        return {
            "relationship": "Uno o ambos IDs no existen en la base de datos.",
            "path": [],
            "path_id": []
        }

def get_relationship(id1: str, id2: str):
    params.logger.info(f"Getting relationship between {id1} and {id2}")
    if id1 == id2:
        params.logger.warning("¡Te has escaneado a ti mismo! Tal vez buscas tu doble perdido...")
        return {"relationship": "te has escaneado a ti mismo. Tal vez buscas tu doble perdido...", "path": ["Tu y solamente tu"], "path_id" : []}
    
    response = {}
    if id1 == "66" or id2 == "66":
        if id1 == "67" or id1 == "68":
            response = find_relationship(id1, id2)
        else:
            return {"relationship": "No hay relacion directa registrada. Consulte con el administrador", "path": [], "path_id": []}  
    else:
        response = find_relationship(id1, id2)
    filename = ""
    
    if params.DEBUG_MODE == False:
        if len(response["path_id"]) > 0:
            filename = (f"{(response["path"])[0]}{(response["path"])[len(response["path"])-1]}".replace(" ", "")).replace("\n","")
            draw_graph(response["path_id"], filename)

    params.logger.info(f"Relationship found: {(response['relationship']).replace("\n"," ")}")
    
    return {"relationship": response["relationship"], "path": response["path"], "tree" : f"{params.LOAD_FOLDER}/{filename}.png"}


# Falta el politico de esta combinacion
# print(get_relationship("8","26"))
