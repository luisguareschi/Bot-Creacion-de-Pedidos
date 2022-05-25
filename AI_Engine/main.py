# -*- coding: utf-8 -*-
"""
Created on Mon Apr 04 13:51:56 2022

@author: W8DE5P2 
"""

import cv2 as cv
import os
import pandas as pd
import json
import re
from AI_Engine.sample import modulo_general as modg
from AI_Engine.format_table import FormatTable

def main(proveedor: str, path_archivos: str, is_img_shown: bool = False, path_root: str = None) -> pd.DataFrame:
    """
    Metodo principal de extraccion de datos de proveedores
    Argumentos:
        proveedor: Nombre del proveedor del cual se extraera la informacion. Proveedores disponibles:
            - Engine Power Compoments
            - Thyssenkrupp Campo Limpo
            - WorldClass Industries
            - EMP
            - Thyssenkrupp Crankshaft
            - WorldClass Industries EU
        path_archivos: Ruta de la carpeta donde se encuentran los archivos o ruta del propio archivo
        is_img_shown: Variable para visualizar la extraccion de datos
        path_root: Ruta donde se encuentran las carpetas que vaya a usar la apliacacion (Config, Resultados, etc.)
    Returns:
        Dataframe de los datos extraidos. None si ha habido algun error
    """
    # Adaptacion de parametros
    path_archivos = os.path.normpath(path_archivos)
    if path_root is None:
        path_root = r"\\fcefactory1\PROGRAMAS_DE_PRODUCCION\6.Planificacion\Bot Creacion de Pedidos\ProjectFiles\Resources\AI_files"
    path_root = os.path.normpath(path_root)
    # %% Constantes
    PEDIDOS_WINDOW = 'PDF pedidos'
    COLUMNAS = ("archivo",) +\
               ("order_number", "client", "reference", "quantity", "ship_out_date", "arrival_date", "confidence")
    COLUMNAS = ("order_number", "client", "reference", "quantity", "ship_out_date", "arrival_date", "confidence")
    CAMPOS = ("order_number", "reference", "quantity", "ship_out_date", "arrival_date")
    HEIGHT_TO_SHOW = 800
    FORMATO_CAMPOS = {
        "order_number": r"^[a-zA-Z]*\d+$",
        "reference": r"^[a-zA-Z]+\d+$",
        "quantity": r"^[\d.,]+$",
        "ship_out_date": r"^(\d{1,2}\/)?\d{1,2}\/\d{2,4}$|"
                         r"^(\d{1,2}\.)?\d{1,2}\.\d{2,4}$|"
                         r"^(\d{1,2}\-)?\d{1,2}\-\d{2,4}$",
        "arrival_date": r"^(\d{1,2}\/)?\d{1,2}\/\d{2,4}$|"
                        r"^(\d{1,2}\.)?\d{1,2}\.\d{2,4}$|"
                        r"^(\d{1,2}\-)?\d{1,2}\-\d{2,4}$"
    }
    # Paths
    PATH_CONFIG = os.path.join(path_root, 'Config')
    PATH_RESULTADOS = os.path.join(path_root, 'Resultados')
    # Files
    FILE_TABLE_HEADER = r"header.jpg"
    FILE_TABLE_END = r"end.jpg"
    # Filepaths
    FILEPATH_PROVEEDORES_DATA = os.path.join(PATH_CONFIG, r"proveedoresData.json")
    print(FILEPATH_PROVEEDORES_DATA)

    # %% Definicion variables
    df = pd.DataFrame(columns=COLUMNAS)

    # Listo los archivos del directorio
    # proveedor = os.path.basename(os.path.normpath(pathArchivos))
    files = []
    if os.path.isdir(path_archivos):
        files = os.listdir(path_archivos)
        files = list(map(lambda name: os.path.join(path_archivos, name), files))
    else:
        files.append(path_archivos)

    # %% Main
    print("-------------- " + proveedor + " --------------")

    # Leo el diccionario con la informacion del proveedor
    proveedores_data = {}
    # Abro archivo JSON
    if os.path.exists(FILEPATH_PROVEEDORES_DATA):
        with open(FILEPATH_PROVEEDORES_DATA, 'r') as openfile:
            # Leo del archivo JSON
            proveedores_data = json.load(openfile)
    else:
        modg.close_windows("Archivo de datos de proveedores no existe")
        return

    # Compruebo que este el proveedor
    if proveedor not in proveedores_data:
        modg.close_windows("Archivo de datos de proveedores no contiene información del proveedor")
        return
    else:
        # Compruebo que sea un diccionario
        if not type(proveedores_data[proveedor]) is dict:
            modg.close_windows("El formato de la información del proveedor no es correcta")
            return
    proveedor_data = proveedores_data[proveedor]

    # Leo las imagenes de los headers y final de la tabla
    pathfile_table_header = os.path.join(PATH_CONFIG, proveedor, FILE_TABLE_HEADER)
    pathfile_table_end = os.path.join(PATH_CONFIG, proveedor, FILE_TABLE_END)
    img_table_header = cv.imread(pathfile_table_header, cv.IMREAD_GRAYSCALE)
    img_table_end = cv.imread(pathfile_table_end, cv.IMREAD_GRAYSCALE)

    # Recorro todos los archivos del directorio
    n_files = 0
    for filename in files:
        # Compruebo que el archivo sea PDF
        if not os.path.splitext(filename)[1].lower() == ".pdf":
            continue
        # if not filename == "10-02-2022_11h-06m.pdf":
        #     continue
        # if n_files > 5:
        #     break

        # Imprimo nombre del archivo
        print(filename + ":")

        # Conversion PDF a imagen
        img_list = modg.pdf_to_img(os.path.join(filename))

        if is_img_shown:
            # Calculo las dimensiones de la primera hoja
            shape_original = img_list[0].shape[:2]  # height, width
            shape_resized = (HEIGHT_TO_SHOW, round((shape_original[1] / shape_original[0]) * HEIGHT_TO_SHOW))
            # Muestro el PDF
            cv.imshow(PEDIDOS_WINDOW,
                      cv.resize(img_list[0], (shape_resized[1], shape_resized[0]), interpolation=cv.INTER_AREA))
            cv.waitKey(1)

        # Creo la lista de imagenes donde se encontrara la tabla
        img_table_info_list = []
        if proveedor_data["table_coordinates"] is not None:
            img_table_info_list = modg.create_table_info_list(img_list, img_table_header, img_table_end,
                                                              proveedor_data["table_coordinates"])
            if is_img_shown:
                for img_table_info in img_table_info_list:
                    cv.imshow("img_table",
                              cv.resize(img_table_info["roi"], None, fx=0.5, fy=0.5, interpolation=cv.INTER_AREA))
                    cv.waitKey(0)
                cv.destroyWindow("img_table")

        # Creo tuplas de los campos dentro y fuera de tabla
        campos_tabla, campos_hoja = [], []
        for campo in CAMPOS:
            config_campo = proveedor_data["fields"][campo]
            # Compruebo que la configuracion no es nula
            if config_campo is not None:
                if config_campo['in_table']:
                    campos_tabla.append(campo)
                else:
                    campos_hoja.append(campo)
        campos_tabla = tuple(campos_tabla)
        campos_hoja = tuple(campos_hoja)
        campos_validos = campos_hoja + campos_tabla

        # Recorremos cada pagina
        pag_campos_data = []
        for n_pag in range(len(img_list)):
            # Inicializo el diccionario de campos de la pagina
            pag_campos_data.append({})
            # Muestro hoja
            if is_img_shown:
                cv.imshow(PEDIDOS_WINDOW,
                          cv.resize(img_list[n_pag], (shape_resized[1], shape_resized[0]), interpolation=cv.INTER_AREA))
                cv.waitKey(1)
            # Log
            print("Num pag: " + str(n_pag + 1))
            # Leemos los campos en la pagina
            for campo in campos_validos:
                # Log
                print("Campo: " + campo)
                # Inicializo campo
                pag_campos_data[n_pag][campo] = None
                # Inicializo imagen de lectura
                img_read = None
                # Guardo configuracion de campo
                config_campo = proveedor_data["fields"][campo]
                # Compruebo que el campo se encuentra en la tabla o en la hoja
                if config_campo['in_table']:
                    # Tabla
                    if img_table_info_list[n_pag]["has_header"]:
                        img_read = img_table_info_list[n_pag]["roi"]
                else:
                    # Hoja
                    if config_campo["pag"] == "all" or config_campo["pag"] == n_pag + 1:
                        img_read = img_list[n_pag]
                # Leo los datos de la hoja
                if img_read is not None:
                    pag_campos_data[n_pag][campo] = modg.lectura_campo(img_read, config_campo["coordinates"],
                                                                       config_campo["method_ocr"],
                                                                       config_campo['regex'],
                                                                       config_campo['in_table'], is_img_shown)

            # Relleno el dataframe
            # Compruebo que las listas de los campos en tabla no estan vacios
            is_table_empty = False
            for campo_tabla in campos_tabla:
                # Si estan vacios no creo el dataframe
                if pag_campos_data[n_pag][campo_tabla] is None or len(pag_campos_data[n_pag][campo_tabla][0]) < 1:
                    is_table_empty = True
                    break
            # Si alguna lista de tabla no tiene valores, saltamos a la siguiente pagina
            if is_table_empty:
                continue
            # Compruebo que los valores en hoja no sean nulos
            for campo_hoja in campos_hoja:
                # Si el valor del campo es nulo, copio el valor de las paginas anteriores
                if pag_campos_data[n_pag][campo_hoja] is None:
                    for n_pag_prev in reversed(range(0, n_pag + 1)):
                        if pag_campos_data[n_pag_prev][campo_hoja] is not None:
                            pag_campos_data[n_pag][campo_hoja] = pag_campos_data[n_pag_prev][campo_hoja]
                            break

            # Extraigo el diccionario con el texto
            pag_campos_dict = {}
            for campo in pag_campos_data[n_pag]:
                if type(pag_campos_data[n_pag][campo][0]) is list:
                    pag_campos_dict[campo] = []
                    pag_campos_dict["conf_" + campo] = []
                    for i in range(len(pag_campos_data[n_pag][campo])):
                        pag_campos_dict[campo].append(pag_campos_data[n_pag][campo][i][0])
                        pag_campos_dict["conf_" + campo].append(pag_campos_data[n_pag][campo][i][1])
                else:
                    pag_campos_dict[campo] = pag_campos_data[n_pag][campo][0]
                    pag_campos_dict["conf_" + campo] = pag_campos_data[n_pag][campo][1]
            # Creo el dataframe con los datos extraidos de la pagina
            df_n = pd.DataFrame(pag_campos_dict)
            print(df_n)
            # Creo la lista de los nombres de las columnas auxiliares de confianza
            conf_columnas = [x for x in list(pag_campos_dict.keys()) if x.startswith("conf_")]
            print(df_n[conf_columnas])
            # Creo la columna de confianza
            df_n["confidence"] = df_n[conf_columnas].min(axis=1)
            df_n = pd.DataFrame(df_n, columns=COLUMNAS)
            # Relleno el valor de las columnas extra
            if "archivo" in COLUMNAS:
                df_n["archivo"] = filename
            df_n["client"] = proveedor
            # Recorro todas las filas del dataframe para comprobar si el formato del campo es correcto
            for i in range(len(df_n)):
                for campo in campos_validos:
                    # Aplico regex para comprobar el formato
                    reg_res = modg.regex_group(FORMATO_CAMPOS[campo], df_n.loc[i, campo])
                    # Si el formato no es correcto, el valor de confianza es -1
                    if reg_res is None or df_n.loc[i, campo] is None or len(reg_res) != len(df_n.loc[i, campo]):
                        print(campo + " format not matching: " + df_n.loc[i, campo])
                        df_n.loc[i, "confidence"] = -1
            # Uno el data frame con el dataframe global
            df = pd.concat([df, df_n], ignore_index=True)
            print("Dataframe pag " + str(n_pag + 1) + ":")
            print(df_n)

        # Elimino las ventanas de visualizacion
        if is_img_shown: cv.destroyWindow(PEDIDOS_WINDOW)

        n_files = n_files + 1

    # Sacar un promedio de la columna de confianza
    confidences = df['confidence'].to_list()
    if len(confidences) > 1:
        total_confidence = (sum(confidences)/len(confidences))/100  # Dividirlo por 100 para tener valores entre [0-1]
        total_confidence = round(total_confidence, 2)  # Redondear a 2 decimales
        df['confidence'] = [total_confidence]*len(confidences)

    # Formatear las columnas de la tabla
    df = FormatTable(orders=df).format()


    # Imprimo el dataframe
    print()
    print()
    print("Dataframe total:")
    print(df.to_string())
    # Guardo el dataframe en un EXCEL para su visualizacion
    path_dataframe = os.path.join(PATH_RESULTADOS, proveedor)
    if not os.path.exists(path_dataframe):
        os.makedirs(path_dataframe)
    df.to_excel(os.path.join(path_dataframe, "dataFrame.xlsx"))

    # Borro ventanas
    modg.close_windows("Aplicacion terminada")
    return df


# proveedor = "Engine Power Compoments"
# proveedor = "EMP"
# proveedor = "Thyssenkrupp Crankshaft"
# proveedor = "ESP"
# proveedor = "Thyssenkrupp Campo Limpo"
# proveedor = "WorldClass Industries"
#
# path_root = r"C:\Users\W8DE5P2\OneDrive-Deere&Co\OneDrive - Deere & Co\Desktop\Proveedores"
# path_archivos = r"orders_history\Thyssen Krupp Cranks_5500044982_DZ104463"
# path_archivos = r"extra\Thyssenkrupp Campo Limpo"
# path_archivos = r"extra\Thyssenkrupp Campo Limpo\20-04-2022_09h-22m.pdf"
# path_archivos = r"CLIIENTES JOHN DEERE\Thyssenkrupp Campo Limpo"
# path_archivos = r"CLIIENTES JOHN DEERE\WorldClass Industries"
# path_archivos = os.path.join(path_root, path_archivos)
#
# main(proveedor, path_archivos, is_img_shown=False, path_root=".")
