#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import os, csv
import re

indir  = '.'

items_data = [()]
viviendas = {}
fallos = []

count = 0

viviendas = {}


def characteristics(tipo, texto, num, fuente):
    buscar = texto in str(fuente)
    if buscar == True:
        viviendas[num][tipo] = 1
    else:
        viviendas[num][tipo] = 0


variables = [("air_conditioning", "Air conditioning"),
            ("wardrobes", "Fitted wardrobes"),
            ("lift", "With lift"),
            ("exterior", "exterior"),
            ("garden", "Garden"),
            ("swimming_pool", "Swimming pool"),
            ("terrace", "Terrace"),
            ("storeroom", "Storeroom"),
            ("garage", "Parking space included in the price "),
            ("good_condition", "good condition"),
            ("needs_renovating", "needs renovating")
            ]


for fn in os.listdir(indir):

    try:

        r = open(fn, 'r')
        soup = BeautifulSoup(r, 'lxml')
        items_class = soup.find_all("div", class_="info-data")

        #id
        id_piso = ''
        items_id = soup.find_all("h3", class_="txt-bold txt-soft")
        for i in items_id:
            if 'Share listing' in i.get_text():
                x = re.split(' ', i.get_text())
                id_piso = x[-1]
            else:
                pass

        #span
        soup_item = BeautifulSoup(str(items_class[0]), 'lxml')
        items_span = soup_item.find_all("span")

        #ubicacion
        lat = ''
        lon = ''
        items_script = soup.find_all("script")
        for s in items_script:
            if "latitude" in s.get_text():
                for f in re.split('[{,]', s.get_text()):
                    if "latitude" in f:
                        lat = f
                    elif "longitude" in f:
                        lon = f
                    else:
                        pass
            else:
                pass

        #nombre ubicacion
        dist = ''
        subd = ''
        items_dist = soup.find_all("div", id = "addressPromo")
        soup2 = BeautifulSoup(str(items_dist), 'lxml')
        for l in soup2.find_all("li"):
            if "Subdistrict" in l.get_text():
                subd = l
            elif "District" in l.get_text():
                dist = l
            else:
                pass

        #compartir ubicacion
        mensaje = "The advertiser prefers not to show the exact address"
        loc_mensaje = soup.find_all("div", id = "static-map-container")[0].get_text()
        advertiser =  mensaje in loc_mensaje

        #nueva vivienda
        items_tag = soup.find_all("div", class_="info-tags")
        new_tag = "New development" in items_tag[0].get_text()

        #seccion
        items_section = soup.find_all("section", id = "details")

        #todo
        items_data[0] = ((str(id_piso), items_span, (lat, lon),
                        items_section, (dist, subd), advertiser,
                        new_tag
                        ))



    except:
        fallos.append((fn, 'fuente'))


    for i in items_data:
        viviendas[str(i[0])] = {}


#pruebas char


    for i in items_data:


        precio = i[1][1].get_text()
        try:
          viviendas[i[0]]["price"] = int(precio.replace(",", ""))
        except:
          viviendas[i[0]]["price"] = ''
          fallos.append((fn, 'precio'))

        metros = i[1][3].get_text()
        viviendas[i[0]]["ms"] = int(metros.replace(".", ""))

        hab = i[1][5].get_text()
        viviendas[i[0]]["rooms"] = hab

        try:
          piso = i[1][7].get_text()
          #regla para bajos
        except:
          piso = "ground"
        try:
          viviendas[i[0]]["floor"] = str(piso)
        except:
          viviendas[i[0]]["floor"] = ''
          fallos.append((fn, 'piso'))


        texto_lat = i[2][0].split('"')
        latitud = texto_lat[1]
        viviendas[i[0]]["lat"] = float(latitud)

        texto_lon = i[2][1].split('"')
        longitud = texto_lon[1]
        viviendas[i[0]]["lon"] = float(longitud)

        try:
          distrito = i[4][0].get_text()
          viviendas[i[0]]["district"] = str(distrito).replace("District ", "")
        except:
          viviendas[i[0]]["district"] = ''
          fallos.append((fn, 'distrito'))

        try:
          subdistrito = i[4][1].get_text()
          viviendas[i[0]]["subdistrict"] = str(subdistrito).replace("Subdistrict ", "")
        except:
          viviendas[i[0]]["subdistrict"] = ''
          fallos.append((fn, 'barrio'))

        casa = i[0]

        for v in variables:
            try:
              characteristics(v[0], v[1], casa, i[3][0].get_text)
            except:
               characteristics(v[0], v[1], casa, '')
               fallos.append((fn, 'caract'))

        if i[6] == True:
            viviendas[i[0]]["new_dev"] = 1
        else:
            viviendas[i[0]]["new_dev"] = 0

        compartir = i[5]
        if compartir == True:
            viviendas[i[0]]["share_loc"] = 0
        else:
            viviendas[i[0]]["share_loc"] = 1

        count += 1
        print count


variables_tot = ["id", "price", "ms", "rooms", "floor", "lat", "lon",
                 "air_conditioning", "wardrobes", "lift", "exterior",
                 "garden", "swimming_pool", "terrace",
                 "storeroom", "garage",
                 "district", "subdistrict",
                 "share_loc", "needs_renovating", "good_condition",
                 "new_dev"
                 ]

print fallos
print len(fallos)
print len(items_data)


with open("viviendas_test.csv", "w") as toWrite:
    writer = csv.writer(toWrite, delimiter=",")
    writer.writerow(variables_tot)
    for a in viviendas.keys():
        writer.writerow([a, viviendas[a]["price"], viviendas[a]["ms"],
                        viviendas[a]["rooms"], viviendas[a]["floor"],
                        viviendas[a]["lat"], viviendas[a]["lon"],
                        viviendas[a]["air_conditioning"], viviendas[a]["wardrobes"],
                        viviendas[a]["lift"], viviendas[a]["exterior"],
                        viviendas[a]["garden"], viviendas[a]["swimming_pool"],
                        viviendas[a]["terrace"],
                        viviendas[a]["storeroom"], viviendas[a]["garage"],
                        viviendas[a]["district"], viviendas[a]["subdistrict"],
                        viviendas[a]["share_loc"], viviendas[a]["needs_renovating"],
                        viviendas[a]["good_condition"], viviendas[a]["new_dev"]
                        ])
