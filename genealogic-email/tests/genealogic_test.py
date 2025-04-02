import os
import sys
sys.path.append(os.path.abspath('../src'))

import params
from genealogicSearch import get_relationship


for person_id, details in params.data.items():
    params.G.add_node(person_id, name=details["name"])
    for child_id in details["children"]:
        params.G.add_edge(person_id, child_id)
    for parent_id in details["parents"]:
        params.G.add_edge(person_id, parent_id)
    for partner_id in details["partner"]:
        params.G.add_edge(person_id, partner_id)


counter = 0
for person_1 in params.data:
    for person_2 in params.data:
        if person_1 != person_2 and person_1 != "0" and person_2 != "0":
            counter += 1
            params.logger.info(f"T_{counter} Testing relationship between Person 1: {person_1} and Person 2: {person_2}")
            response = get_relationship(person_1, person_2)
            if "None" in response["relationship"]:
                params.logger.warning("The relationship item contains None.")
            elif len(response["path"]) == 0:
                params.logger.error("The path item is empty.")

# person_1 = "84"
# for person_2 in params.data:
#     if person_1 != person_2 and person_1 != "0" and person_2 != "0":
#         counter += 1
#         print(f"{counter}# Conexion entre {params.data[person_1]["name"].replace("\n", " ")} y {params.data[person_2]["name"].replace("\n", " ")}")
#         response = get_relationship(person_1, person_2)
#         if "None" in response["relationship"]:
#             print("---------> Relacion no encontrada")
#         elif len(response["path"]) == 0:
#             print("---------> Relacion no encontrada")
#         else:
#             print(f"---------> {response['relationship'].replace("\n", " ")}")