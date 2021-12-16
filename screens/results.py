#!/bin/env python

#Muestra los resultados obtenidos por los scrapers
#Admite filtrado de búsqueda dentro de los subtítulos hallados
#Marca los subtítulos ya descargados
#Selecciona subtítulo deseado y pasa a la pantalla de descarga

import os
from termcolor import colored
from modules.admin_db import *
from modules.strings_fitting import phrase_fitting, \
        centered_phrase_fitting, colored_centered_filter
from modules.menu import menu
from modules.columns_number import columns_number_func
from modules.scrapers.subtitles.spanish.opensubtitles import opensubtitles
from modules.scrapers.subtitles.spanish.subdivx import subdivx

def results():
    #Resultados por pagina (rpp)
    rpp = read_settings("results_per_page")
    os.system("clear")

    #Recuperar scrapers a utilizar
    scrapers = read_settings("sub_getters").split(",")
    scrapers.reverse()

    #Evita buscar 2 veces seguidas lo mismo
    if (read_settings("sub_search_changed") == 1) and \
            (read_settings("sub_words") != "") and \
            (read_settings("selected_video_name") != ""):

        #Reiniciar filtro
        edit_settings("subs_filter", "")

        #Recuperar palabras de búsqueda
        palabras = read_settings("sub_words").split(",")

        #obtener subtítulos
        get_subs = {
                "opensubtitles": opensubtitles,
                "subdivx": subdivx,
                }

        hallados = []
        for scraper in scrapers:
            hallados += get_subs[scraper](palabras)
        #Agrega status
        for sub in hallados:
            sub += [0]
        edit_scraped_list('subtitles', 'replace', list_=hallados)
        edit_settings("sub_search_changed", "0")

    #Subtítulos con indices asignados
    raw_subs = read_scraped_list('subtitles')
    subs = [list(raw_subs[indice]) + [indice] for indice in range(len(raw_subs))]
    print(subs)
    #Actualizando info de pantalla en base de datos
    edit_settings("previous_menu", str(read_settings("menu")))
    edit_settings("menu","results")

    filtro = read_settings("subs_filter")
    pagina = 1
    while True:
        #Pantalla resultados
        numcols = columns_number_func()

        #Definiendo colores de lineas
        linea_azul = colored(numcols*"=", 'blue', attrs=['bold', 'dark'])
        linea_roja = colored(numcols*"=", 'red', attrs=['bold', 'dark'])
        linea_amarilla = colored(numcols*"=", 'yellow', attrs=['bold', 'dark'])

        #Subs filtrados
        lista_filtro_str = " ".join(filtro.split(","))
        lista_filtro = lista_filtro_str.split(" ")
        while '' in lista_filtro:
            lista_filtro.remove('')
        subs_filtrados = [sub for sub in subs if len([palabra_filtro \
                for palabra_filtro in lista_filtro if palabra_filtro.lower() \
                in sub[0].lower() + sub[1].lower() + sub[2].lower()]) == len(lista_filtro)]
        subs_filtrados = [subs_filtrados[x]+[x] for x in range(len(subs_filtrados))]

        #Total de paginas
        total_paginas = len(subs_filtrados)//rpp
        if total_paginas*rpp < len(subs_filtrados):
            total_paginas += 1

        #Subs de la página actual
        if pagina == 1:
            subs_pagina = subs_filtrados[rpp*pagina-1::-1]
        else:
            subs_pagina = subs_filtrados[(rpp*pagina)-1:((pagina-1)*rpp)-1:-1]

        titulo = "RESULTADOS"
        print(linea_azul)
        print(((numcols-len(titulo))//2)*" " + titulo)
        print(linea_azul)

        for x in range(len(subs_pagina)):
            #Marca en blanco el subtítulo actual
            #Marca en rojo el resto de subs descargados
            fondo = 'on_red'
            if subs_pagina[x][3] == 2:
                fondo = 'on_white'
            #Marca los subtítulos descargados
            if subs_pagina[x][3] != 0:
                ID = colored("ID ", 'cyan', fondo, attrs=['bold', 'dark']) + \
                        colored(str(subs_pagina[x][4]), 'green', fondo, \
                        attrs=['bold', 'dark'])
            else:
                ID = colored("ID ", 'cyan', attrs=['bold', 'dark']) + \
                        colored(str(subs_pagina[x][4]), 'green', \
                        attrs=['bold', 'dark'])

            print(linea_amarilla)
            print(str(subs_pagina[x][5]) + ": " + ID + " -> " + subs_pagina[x][0])
            print(numcols * "-")
            print(centered_phrase_fitting(numcols, subs_pagina[x][1]))
            print()
            by = [scraper for scraper in scrapers if scraper in subs_pagina[x][2]][0]
            by_color = colored(by, 'cyan', attrs=['bold'])
            print((numcols - len(by)) * " " + by_color)

        #Si no hay subtitulos, envia mensaje
        if len(subs) == 0:
            msj = "\n\nNingún subtítulo hallado...\n\n"
            print(phrase_fitting(numcols, msj))
            print(linea_azul)
        #Si no hay subtitulos filtrados, envia mensaje
        elif len(subs_filtrados) == 0:
            msj = "\n\nNingún subtítulo coincide con el " + \
                    "filtro ingresado en esta pantalla, " + \
                    "prueba con otras palabras...\n\n"
            print(phrase_fitting(numcols, msj))
            print(linea_azul)
        #Si hay subtitulos, cierra con línea amarilla
        else:
            print(linea_amarilla)

        print(linea_roja)
        #Nombre del video
        #Si no hay video seleccionado, envía mensaje
        print(colored(centered_phrase_fitting(numcols, "Video a subtitular:"), \
                'white', attrs=['bold']))

        if read_settings("selected_video_name") == "":
            msj = "Cuando lo selecciones, aquí aparecerá el " + \
                    "nombre del video para ayudarte a filtrar palabras..."
            print(phrase_fitting(numcols, msj))
        #Imprime video seleccionado
        else:
            print(centered_phrase_fitting(numcols, read_settings("selected_video_name")))
        print(linea_roja)
        #ruta
        str_Ruta =  colored("Ruta:", 'white', attrs=['bold'])
        print(centered_phrase_fitting(numcols+13, str_Ruta))
        #Si no hay video seleccionado, arroja el sig mensaje
        if read_settings("selected_video_name") == "":
            msj = "Aquí aparecerá la ruta del video que selecciones..."
            print(phrase_fitting(numcols, msj))
        #Si hay video seleccionado, imprime su ruta
        else:
            print(read_settings("selected_video_route"))
        #Imprime filtros
        print(linea_roja)
        print(colored(centered_phrase_fitting(numcols, "Filtros:"), 'white', attrs=['bold']))
        colored_filters = colored_centered_filter(numcols, \
                " ".join(lista_filtro))
        if len(lista_filtro) > 0:
            print(colored_filters)
        print(linea_roja)

        i = menu(numcols, "Página: " + str(pagina) + " de " + \
                str(total_paginas)  + " - " + str(len(subs_filtrados))  + " subs")

        #Determina cuales IDs pueden ser descargados
        dict_descargables = {
                "page": subs_pagina,
                "avaliables": subs,
                "filtered": subs_filtrados
                }
        descargable = dict_descargables[read_settings("downloadable_ids")]

        #Si es alguna pantalla del menu
        if i[0] == "menu":
            return i[1]

        #Si es enter
        elif i[1] == "":
            if pagina < total_paginas:
                pagina += 1
            else:
                pagina = 1
        
        #Si retrocede pantalla
        elif i[1] == "..":
            if total_paginas == 0:
                pagina = 1
            elif pagina == 1:
                pagina = total_paginas
            else:
                pagina -= 1

        #Si elige un subtitulo
        elif i[1].isdigit() and (int(i[1]) in [sub[4] for sub in descargable]):
            edit_settings("downloadable_sub_url", subs[int(i[1])][2])
            
            edit_scraped_list('subtitles', 'downloaded')
            edit_scraped_list('subtitles', id_=subs[int(i[1])][4], status=2)
            return 'download'

        #Filtrado de palabras
        else:
            filtro = i[1]
            edit_settings("subs_filter", filtro)
            pagina = 1
