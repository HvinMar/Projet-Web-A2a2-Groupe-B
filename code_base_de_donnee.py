# -*- coding: utf-8 -*-
"""
Created on Sun Jun  7 17:18:51 2020

@author: Amandine
"""

from zipfile import ZipFile
import json

#fonction permettant de récupérer l'infobox d'un pays
def get_zip_info(country):
    with ZipFile('{}.zip'.format('asia'),'r') as z:
    
        # infobox du pays
        return json.loads(z.read('{}'.format(country)))
    
def get_name(wp_info):
    
    #Cas particuliers
    if 'common_name' in wp_info and wp_info['common_name'] == 'Kazakhstan':
        return 'Republic of Kazakhstan'
    
    if 'common_name' in wp_info and wp_info['common_name'] == 'Nepal':
        return 'Republic of Nepal'
    
    if 'common_name' in wp_info and wp_info['common_name'] == 'Palestine':
        return 'State of Palestine'
    
    if 'common_name' in wp_info and wp_info['common_name'] == 'Sri Lanka':
        return 'Democratic Socialist Republic of Sri Lanka'
    
    # cas général
    if 'conventional_long_name' in wp_info:
        name = wp_info['conventional_long_name']        
        return name

    # FIX manuel (l'infobox ne contient pas l'information)
    if 'common_name' in wp_info and wp_info['common_name'] == 'Singapore':
        return 'Republic of Singapore'
 
    # Aveu d'échec, on ne doit jamais se retrouver ici
    print('Could not fetch country name {}'.format(wp_info))
    return None
 
import re

def get_capital(wp_info):
    
    # cas général
    if 'capital' in wp_info:
        
        # parfois l'information récupérée comporte plusieurs lignes
        # on remplace les retours à la ligne par un espace
        capital = wp_info['capital'].replace('\n',' ')
        
        # le nom de la capitale peut comporter des lettres, des espaces,
        # ou l'un des caractères ',.()|- compris entre crochets [[...]]
        m = re.match(".*?\[\[([\w\s',(.)|-]+)\]\]", capital)
        
        # on récupère le contenu des [[...]]
        capital = m.group(1)
        
        return capital
    
    #cas particulier
    if 'common_name' in wp_info and wp_info['common_name'] == 'Palestine':
        return 'Ramallah'
        
    # Aveu d'échec, on ne doit jamais se retrouver ici
    print(' Could not fetch country capital {}'.format(wp_info))
    return None

def get_coords(wp_info):

    # S'il existe des coordonnées dans l'infobox du pays
    # (cas le plus courant)
    if 'coordinates' in wp_info:

        # (?i) - ignorecase - matche en majuscules ou en minuscules
        # ça commence par "{{coord" et se poursuit avec zéro ou plusieurs
        #   espaces suivis par une barre "|"
        # après ce motif, on mémorise la chaîne la plus longue possible
        #   ne contenant pas de },
        # jusqu'à la première occurence de "}}"
        m = re.match('(?i).*{{coord\s*\|([^}]*)}}', wp_info['coordinates'])

        # l'expression régulière ne colle pas, on affiche la chaîne analysée pour nous aider
        # mais c'est un aveu d'échec, on ne doit jamais se retrouver ici
        if m == None :
            print(' Could not parse coordinates info {}'.format(wp_info['coordinates']))
            return None

        # cf. https://en.wikipedia.org/wiki/Template:Coord#Examples
        # on a récupère une chaîne comme :
        # 57|18|22|N|4|27|32|W|display=title
        # 44.112|N|87.913|W|display=title
        # 44.112|-87.913|display=title
        str_coords = m.group(1)

        # on convertit en numérique et on renvoie
        if str_coords[0:1] in '0123456789':
            return cv_coords(str_coords)
        
    #Pour les pays dont les coordonnées ne sont pas renseignées, on les précise 
    # nous même dans le même format    
    if 'common_name' in wp_info and wp_info['common_name'] == 'Yemen':
        return cv_coords('15|15|N|48|25|E')
    
    if 'common_name' in wp_info and wp_info['common_name'] == 'the Philippines':
        return cv_coords('14|35|N|120|58|E')
    
    if 'common_name' in wp_info and wp_info['common_name'] == 'Palestine':
        return cv_coords('31|57|N|35|13|E')
    
    if 'common_name' in wp_info and wp_info['common_name'] == 'Maldives':
        return cv_coords('3|15|N|73|00|E')
    
    if 'common_name' in wp_info and wp_info['common_name'] == 'Malaysia':
        return cv_coords('2|30|N|112|30|E')
        
    # Aveu d'échec, on ne doit jamais se retrouver ici
    print(' Could not fetch country coordinates {}'.format(get_name(wp_info)))
    return None

def cv_coords(str_coords):
    # on découpe au niveau des "|" 
    c = str_coords.split('|')

    # on extrait la latitude en tenant compte des divers formats
    lat = float(c.pop(0))
    if (c[0] == 'N'):
        c.pop(0)
    elif ( c[0] == 'S' ):
        lat = -lat
        c.pop(0)
    elif ( len(c) > 1 and c[1] == 'N' ):
        lat += float(c.pop(0))/60
        c.pop(0)
    elif ( len(c) > 1 and c[1] == 'S' ):
        lat += float(c.pop(0))/60
        lat = -lat
        c.pop(0)
    elif ( len(c) > 2 and c[2] == 'N' ):
        lat += float(c.pop(0))/60
        lat += float(c.pop(0))/3600
        c.pop(0)
    elif ( len(c) > 2 and c[2] == 'S' ):
        lat += float(c.pop(0))/60
        lat += float(c.pop(0))/3600
        lat = -lat
        c.pop(0)

    # on fait de même avec la longitude
    lon = float(c.pop(0))
    if (c[0] == 'W'):
        lon = -lon
        c.pop(0)
    elif ( c[0] == 'E' ):
        c.pop(0)
    elif ( len(c) > 1 and c[1] == 'W' ):
        lon += float(c.pop(0))/60
        lon = -lon
        c.pop(0)
    elif ( len(c) > 1 and c[1] == 'E' ):
        lon += float(c.pop(0))/60
        c.pop(0)
    elif ( len(c) > 2 and c[2] == 'W' ):
        lon += float(c.pop(0))/60
        lon += float(c.pop(0))/3600
        lon = -lon
        c.pop(0)
    elif ( len(c) > 2 and c[2] == 'E' ):
        lon += float(c.pop(0))/60
        lon += float(c.pop(0))/3600
        c.pop(0)
    
    # on renvoie un dictionnaire avec les deux valeurs
    return {'lat':lat, 'lon':lon }

def get_leadername(wp_info):
    
    # cas général
    if 'leader_name1' in wp_info:
    
        leader_name1 = wp_info['leader_name1'].replace('\n',' ')
        
        m = re.match(".*?\[\[([\w\s',(.)|-]+)\]\]", leader_name1)
        
        leader_name1 = m.group(1)
        ln = leader_name1.split('|')
        
        return ln[len(ln)-1]
        
        return leader_name1
    
    # Aveu d'échec, on ne doit jamais se retrouver ici
    print(' Could not fetch country leader name ')
    return None

def get_leadertitle(wp_info):
    
    # cas général
    if 'leader_title1' in wp_info:
        
        leader_title1 = wp_info['leader_title1'].replace('\n',' ')
        
        m = re.match(".*?\[\[([\w\s',:(.)|-]+)\]\]", leader_title1)
        
        leader_title1 = m.group(1)
        lt = leader_title1.split('|')
        
        return lt[len(lt)-1] 
    
    # Aveu d'échec, on ne doit jamais se retrouver ici
    print(' Could not fetch country leader title ')
    return None

def get_currency(wp_info):
    
    # cas général
    if 'currency' in wp_info:
        
        # parfois l'information récupérée comporte plusieurs lignes
        # on remplace les retours à la ligne par un espace
        currency = wp_info['currency'].replace('\n',' ')
        
        # le nom de la capitale peut comporter des lettres, des espaces,
        # ou l'un des caractères ',.()|- compris entre crochets [[...]]
        m = re.match(".*?\[\[([\w\s',(.)|-]+)\]\]", currency)
        
        # on récupère le contenu des [[...]]
        currency = m.group(1)
        c = currency.split('|')
        
        return c[0] #on récupère le premier nom de la monnaie
        
        
    # Aveu d'échec, on ne doit jamais se retrouver ici
    print(' Could not fetch country currency {}'.format(get_name(wp_info)))
    return None

def get_area(wp_info):
    #cas particuliers (ne respectent pas la convention de notations des nombres)
    if 'common_name' in wp_info and wp_info['common_name'] == 'Azerbaijan':
        return '86,600'
    
    if 'common_name' in wp_info and wp_info['common_name'] == 'Jordan':
        return '89,342'
    
    if 'common_name' in wp_info and wp_info['common_name'] == 'Lebanon':
        return '10,452'
    
    if 'common_name' in wp_info and wp_info['common_name'] == 'Russia':
        return '17,098,246'
    
    if 'common_name' in wp_info and wp_info['common_name'] == 'Syria':
        return '185,180'
    
    #cas particulier (proposé deux superficies)
    if 'common_name' in wp_info and wp_info['common_name'] == 'Israel':
        return '22,145'
    
    #cas général
    if 'area_km2' in wp_info:
        return wp_info['area_km2']
    
    print(' Could not fetch country area {}'.format(get_name(wp_info)))
    
    
def get_population_density(wp_info):
    #cas particuliers
    if 'common_name' in wp_info and wp_info['common_name'] == 'Cyprus':
        return '123.4'
    
    if 'common_name' in wp_info and wp_info['common_name'] == 'India':
        return '413.21'
    
    if 'common_name' in wp_info and wp_info['common_name'] == 'Israel':
        return '445.26'
    
    if 'common_name' in wp_info and wp_info['common_name'] == 'Vietnam':
        return '276.03'
    
    #cas général
    if 'population_density_km2' in wp_info:
        return wp_info['population_density_km2']
    
    print(' Could not fetch country population density {}'.format(get_name(wp_info)))
    

with ZipFile('{}.zip'.format('asia'),'r') as z:
    for name in z.namelist():
        print(get_population_density(get_zip_info(name)))
        

import sqlite3
conn = sqlite3.connect('pays.sqlite')

def save_country(conn,country,info):

    # préparation de la commande SQL
    c = conn.cursor()

    sql = 'INSERT OR REPLACE INTO countries VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'

    # les infos à enregistrer
    name = get_name(info)
    print(name)
    capital = get_capital(info)
    leadertitle = get_leadertitle(info)
    leadername = get_leadername(info)
    currency = get_currency(info)
    coords = get_coords(info)
    area = get_area(info)
    pop_density = get_population_density(info)
    flag = country[0:-5]
    if name == 'Georgia': flag = 'Georgia'
    address = "/flags/{}.png".format(flag)

    # soumission de la commande (noter que le second argument est un tuple)
    c.execute(sql,(country, name, capital, leadertitle,leadername,currency,coords['lat'],coords['lon'],flag,area,pop_density,address))

    conn.commit()
    
with ZipFile('{}.zip'.format('asia'),'r') as z:
    for name in z.namelist():
        save_country(conn,name,get_zip_info(name))
        