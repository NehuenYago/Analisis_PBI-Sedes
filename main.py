#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 25 15:26:35 2024

Autores: 
Ehrhorn, Leonard
Olmos, Francisco José
Romero Abuin, Nehuen Yago

Este archivo contiene el proceso de importación de tablas de representaciones argentinas
y tablas de información sobre los países del mundo a tablas propias, así como el proceso de limpieza.
Luego, con las tablas generadas por nosotros, realizamos diferentes reportes SQL y gráficos.
El objetivo es estudiar si hay relación entre la cantidad de sedes diplomáticas que tiene
Argentina en diferentes países y los PBI de estos en el año 2022.
"""



#%%
"""
Importacion de librerias que vamos a utilizar para el desarrollo del Trabajo Practico
"""

import pandas as pd
from inline_sql import sql_val, sql

import matplotlib.pyplot as plt
import seaborn as sns

carpeta = "TablasOriginales/"


#%%

"""
Leemos los dataframes de las tablas originales, 
procedemos a crear un diccionario y una funcion para observar las columnas que tiene cada dataframe
"""

tablas_originales = dict()

gdp = pd.read_csv(carpeta+"API_NY.GDP.PCAP.CD_DS2_en_csv_v2_73.csv")
gdp_metadata = pd.read_csv(carpeta+"Metadata_Country_API_NY.GDP.PCAP.CD_DS2_en_csv_v2_73.csv")
lista_sedes_datos = pd.read_csv(carpeta+"lista-sedes-datos.csv")
lista_secciones = pd.read_csv(carpeta+"lista-secciones.csv")
lista_sedes = pd.read_csv(carpeta+"lista-sedes.csv")

tablas_originales['gdp'] = gdp
tablas_originales['gdp_metadata'] = gdp_metadata
tablas_originales['lista_sedes_datos'] = lista_sedes_datos
tablas_originales['lista_secciones'] = lista_secciones
tablas_originales['lista_sedes'] = lista_sedes_datos

"""
Printeamos todas las columnas
"""

print(tablas_originales.keys())

def print_columns(tablas:dict)-> None:
    for df in tablas.keys():
        print(f"columnas de {df}:\n {tablas[df].columns.tolist()}\n")
        
print_columns(tablas=tablas_originales)

"""
Ahora procedemos a importar las tablas originales a las nuevas, según el modelo relacional que armamos.
"""

#%%
"""
Limpieza y Modelado de la tabla Seccion
"""

seccion = lista_secciones[['sede_id', 'sede_desc_castellano']]
seccion.columns = ['Id_sede', 'Descripcion']

"""
Aunque interpretamos que una sección se identifica unívocamente por el tipo
y la sede a la que pertenece, hay escasas repeticiones. Procedemos a removerlas. 
"""

filtro_distinc =  """
                  SELECT DISTINCT *
                  FROM seccion
                  """
                  
seccion = sql^filtro_distinc
seccion.to_csv('TablasLimpias/seccion.csv', index=False)

#%%
"""
Modelado de la tabla Pais
"""

pbi = gdp[['Country Name', 'Country Code', '2022']]
pbi = pbi[pbi[['Country Name', 'Country Code', '2022']].notna().all(axis=1)]

gdp_metadata = gdp_metadata[['Country Code', 'Region']]

pais = pbi.merge(gdp_metadata, on='Country Code', how='left')
pais.columns = ['Pais', 'Id_pais', 'PBI', 'Region']

pais = pais.dropna(subset=['Region'])

pais.to_csv('TablasLimpias/pais.csv', index=False)



#%%
"""
Modelado de la tabla Sede
"""

sede = lista_sedes[lista_sedes['estado'] != 'Inactivo']

sede = sede[['sede_id', 'sede_desc_castellano', 'pais_iso_3']]
sede.columns = ['Id', 'Descripcion', 'Id_pais']

sede.to_csv('TablasLimpias/sede.csv', index=False)


#%%
"""
Limpieza y Modelado de la tabla Red Social
"""

print("Cantidad de nulls en la columna de redes sociales: ", lista_sedes_datos['redes_sociales'].isna().sum())

lista_sedes_datos['redes_sociales'] = lista_sedes_datos['redes_sociales'].astype(str).apply(lambda x: x.split(' '))  
lista_sedes_datos['redes_sociales'] = lista_sedes_datos['redes_sociales'].apply(lambda x: [value for value in x if value != "//" and value != ""])
lista_sedes_datos['redes_sociales'] = lista_sedes_datos['redes_sociales'].apply(lambda x: 'nan' if 'nan' in x else x)

"""
Ejecutamos la separación de url del atributo redes_sociales
"""
lista_sedes_datos = lista_sedes_datos[lista_sedes_datos['redes_sociales'] != 'nan']

red_social = lista_sedes_datos.explode('redes_sociales')

red_social = red_social[['sede_id', 'redes_sociales']]
red_social.columns = ['Id_sede', 'Url']

"""
Una vez hecha la separación de Url, construimos el atributo Nombre_red a partir del atributo Url
"""

red_social['Nombre_red'] = red_social['Url'].apply(lambda x: x.split('//')[-1].split('/')[0])
red_social['Nombre_red'] = red_social['Nombre_red'].apply(lambda x: 'www.instagram.com' if x.startswith('@') else x)
red_social['Nombre_red'] = red_social['Nombre_red'].apply(lambda x: 'www.instagram.com' if x == 'instagram.com' else x)
red_social['Nombre_red'] = red_social['Nombre_red'].apply(lambda x: 'www.facebook.com' if x == 'facebook.com' else x)
red_social['Nombre_red'] = red_social['Nombre_red'].apply(lambda x: 'www.twitter.com' if x == 'twitter.com' else x)

def parse_red_social(url:str):
    if url.startswith('www.'):
        url = url.split('.')[1].capitalize()
    return url

red_social['Nombre_red'] = red_social['Nombre_red'].apply(parse_red_social)

"""
Después de separar las Url, faltaba eliminar aquellas filas donde el atributo Url
no corresponde a una cuenta. Lo hacemos ahora.
"""

red_social_filtro = """
                    SELECT *
                    FROM red_social
                    WHERE Url LIKE '%@%' OR Url LIKE '%.com%'
                    """
red_social = sql^red_social_filtro

red_social.to_csv('TablasLimpias/red_social.csv', index=False)



#%%
"""
Luego de guardar cada tabla en /TablasLimpias procedemos a levantarlas nuevamente para hacer el analisis
"""

seccion = pd.read_csv('TablasLimpias/seccion.csv',)
pais = pd.read_csv('TablasLimpias/pais.csv')
sede = pd.read_csv('TablasLimpias/sede.csv')
red_social = pd.read_csv('TablasLimpias/red_social.csv')

#%%

"""
Reportes SQL
"""

#%%
"""
Ejercicio 1

Para cada país informar cantidad de sedes, cantidad de secciones en
promedio que poseen sus sedes y el PBI per cápita del país en 2022. El
orden del reporte debe respetar la cantidad de sedes (de manera
descendente)
"""

consulta_sedes = """
                  SELECT pais.Pais, SUM(CASE WHEN sede.Id IS NULL THEN 0 ELSE 1 END) AS sedes
                  FROM pais
                  LEFT OUTER JOIN sede
                  ON sede.Id_pais = pais.Id_pais
                  GROUP BY Pais
                 """
sedes_por_pais = sql^consulta_sedes

#ahora calculamos la cantidad de secciones por país, suponiendo que las sedes sin secciones
#registradas tienen 0 secciones.
sedes_con_paises = """
                    SELECT pais.Pais, sede.Id AS id_sede
                    FROM pais
                    INNER JOIN sede
                    ON sede.Id_pais = pais.Id_pais
                   """
sedes_paises = sql^sedes_con_paises
cant_secciones_pais = """
                        SELECT Pais, SUM(CASE WHEN seccion.Descripcion IS NULL THEN 0 ELSE 1 END) AS secciones
                        FROM sedes_paises
                        LEFT OUTER JOIN seccion
                        ON sedes_paises.Id_sede = seccion.Id_sede 
                        GROUP BY Pais  
                      """
secciones_por_pais = sql^cant_secciones_pais

#notar que sólo calculamos secciones de los países que tienen alguna sede

sedes_secciones_paises = """
                          SELECT sedes_por_pais.Pais, sedes, CASE WHEN secciones IS NULL THEN 0 ELSE secciones/sedes END AS secciones_promedio
                          FROM sedes_por_pais
                          LEFT OUTER JOIN secciones_por_pais
                          ON sedes_por_pais.Pais = secciones_por_pais.Pais
                         """
sede_seccion_pais = sql^sedes_secciones_paises

agregar_pbi = """
                SELECT sede_seccion_pais.*, pais.PBI
                FROM sede_seccion_pais
                INNER JOIN pais
                ON pais.Pais = sede_seccion_pais.Pais
                ORDER BY sedes DESC, sede_seccion_pais.Pais ASC
              """
sedes_secciones_pbi = sql^agregar_pbi

#el dataframe sedes_secciones_pbi resuelve el Ejercicio 1.


#%%
"""
Ejercicio 2

Reportar agrupando por región geográfica: a) la cantidad de países en que
Argentina tiene al menos una sede y b) el promedio del PBI per cápita 2022
de dichos países. Ordenar por el promedio del PBI per Cápita.

"""

incorporar_sedes = """
                    SELECT pais.Id_pais AS iso_pais, pais.region, sede.id AS id_sede
                    FROM pais
                    INNER JOIN sede
                    ON sede.Id_pais = pais.Id_pais
                   """
sedes_por_pais = sql^incorporar_sedes
consulta_paises_con_sede = """
                            SELECT DISTINCT Region, iso_pais
                            FROM sedes_por_pais 
                           """
paises_con_sede = sql^consulta_paises_con_sede
cant_paises_con_sede = """
                        SELECT Region, COUNT(*) AS cantidad_paises_con_sede
                        FROM paises_con_sede
                        GROUP BY Region
                       """
paises_con_sede_por_region = sql^cant_paises_con_sede
#el dataframe paises_con_sede_por_region responde el item a)

#comienza el item b)
consulta_pbi_pais_sede = """
                          SELECT pais.Id_pais, pais.region, pais.pbi
                          FROM pais
                          INNER JOIN paises_con_sede
                          ON pais.Id_pais = paises_con_sede.iso_pais
                         """
pbi_paises_con_sede = sql^consulta_pbi_pais_sede
consulta_prom_region = """
                        SELECT Region, AVG(PBI) AS PBI_promedio_U$S
                        FROM pbi_paises_con_sede
                        GROUP BY Region
                        ORDER BY PBI_promedio_U$S
                       """
promedio_pbi_region_paises_con_sede = sql^consulta_prom_region
#el dataframe promedio_pbi_region_paises_con_sede resuelve el item b).

consulta_region_sedes_pbi = """
                    SELECT paises_con_sede_por_region.region AS Region, cantidad_paises_con_sede AS Paises_con_sedes_Argentinas, promedio_pbi_region_paises_con_sede.PBI_promedio_U$S
                    FROM paises_con_sede_por_region 
                    INNER JOIN promedio_pbi_region_paises_con_sede
                    ON paises_con_sede_por_region.region = promedio_pbi_region_paises_con_sede.region
                    ORDER BY promedio_pbi_region_paises_con_sede.PBI_promedio_U$S DESC
                   """
region_sedes_pbi = sql^consulta_region_sedes_pbi
#el dataframe region_sedes_pbi resuelve el Ejercicio 2

#%%
"""
Ejercicio 3

Para saber cuál es la vía de comunicación de las sedes en cada país, nos
hacemos la siguiente pregunta: ¿Cuán variado es, en cada el país, el tipo de
redes sociales que utilizan las sedes? Se espera como respuesta que para
cada país se informe la cantidad de tipos de redes distintas utilizadas.
"""

consulta_redes_pais = """
                       SELECT p.Pais, COUNT(DISTINCT Nombre_red) as cant_de_redes_diferentes     
                       FROM red_social r
                       JOIN sede s ON r.Id_sede = s.Id
                       JOIN pais p ON s.Id_pais = p.Id_pais
                       GROUP BY p.Pais;
                      """
     

redes_por_pais = sql^consulta_redes_pais
#el dataframe redes_por_pais resuelve el Ejercicio 3

#%%

"""
Ejercicio 4

Confeccionar un reporte con la información de redes sociales, donde se
indique para cada caso: el país, la sede, el tipo de red social y url utilizada.
Ordenar de manera ascendente por nombre de país, sede, tipo de red y
finalmente por url.
"""

query_redes_pais = """
                    SELECT p.Pais, s.Id as Sede, r.Nombre_red as Red_Social, r.Url as URL
                    FROM red_social r
                    JOIN sede s ON r.Id_sede = s.Id
                    JOIN pais p ON s.Iso = p.Iso
                    ORDER BY p.Pais ASC, Sede ASC, Red_Social ASC, URL ASC
                   """
redes_sociales_por_pais = sql^query_redes_pais
#El dataframe redes_sociales_por_pais resuelve el Ejercicio 4.


#%%
"""
Visualizaciones
"""

#%%
"""
Ejercicio 1

Cantidad de sedes por región geográfica. Mostrarlos ordenados de manera
decreciente por dicha cantidad.
"""
query_sede_region = """
                     SELECT p.Region AS region, COUNT(region) as cant_sedes
                     FROM sede s
                     LEFT JOIN pais p ON s.Id_pais = p.Id_pais
                     WHERE p.Region IS NOT NULL
                     GROUP BY p.Region
                     ORDER BY cant_sedes DESC;
                    """
        
sede_por_region = sql^query_sede_region
print(type(sede_por_region))


"""
BarPlots
"""

plt.figure(figsize=(10, 6))  
sns.set_style("whitegrid", {"grid.color": ".1", "grid.linestyle": ":"})
plt.bar(sede_por_region['region'], sede_por_region['cant_sedes'],  alpha=0.9, color='orange')

# Leyendas
plt.xlabel('Region')
plt.ylabel('Numero de Sedes')
plt.title('Numero de Sedes por Region')

# Mejorar la legibilidad
plt.xticks(rotation=45, ha='right')
#%%

"""
Ejercicio 2

Boxplot, por cada región geográfica, del PBI per cápita 2022 de los países
donde Argentina tiene una delegación. Mostrar todos los boxplots en una
misma figura, ordenados por la mediana de cada región.
"""
consulta_pbi_delegaciones = """
        SELECT  p.PBI, p.Region
        FROM sede s
        JOIN pais p ON s.Id_pais = p.Id_pais
        WHERE p.PBI IS NOT NULL
        GROUP BY s.Id_pais, p.PBI, p.Pais, p.Region
        ORDER BY PBI DESC;
        """
        
pbi_region = sql^consulta_pbi_delegaciones

median_pbi_by_region = pbi_region.groupby('Region')['PBI'].median().sort_values()

cmap = sns.color_palette("viridis", as_cmap=True)

"""
BoxPlots
"""

plt.figure(figsize=(10, 6))
sns.set_style("whitegrid", {"grid.color": ".1", "grid.linestyle": ":"})
sns.boxplot(data=pbi_region, x='Region', y='PBI', order=median_pbi_by_region.index, palette = "husl",
            showmeans=True, meanprops={"marker":"s","markerfacecolor":"white", "markeredgecolor":"black"})

# Leyendas
plt.xlabel('Region')
plt.ylabel('PBI')
plt.title('Boxplots del PBI por Region')

# Mejorar la legibilidad
plt.xticks(rotation=45, ha='right')

#%%
"""
Ejercicio 3

Relación entre el PBI per cápita de cada país (año 2022 y para todos los
países que se tiene información) y la cantidad de sedes en el exterior que
tiene Argentina en esos países.

"""
consulta_pbi_sedes = """
        SELECT  p.Pais, p.PBI, COUNT(p.Pais) as cant_sedes, 
        FROM sede s
        JOIN pais p ON s.Id_pais = p.Id_pais
        WHERE p.PBI IS NOT NULL
        GROUP BY s.Id_pais, p.PBI, p.Pais, p.Region
        ORDER BY cant_sedes DESC;
        """
        
pbi_pais_sede = sql^consulta_pbi_sedes

"""
ScatterPlot
"""

plt.figure(figsize=(10, 6))
sns.set_style("whitegrid", {"grid.color": ".1", "grid.linestyle": ":"})
sns.scatterplot(data=pbi_pais_sede, x='cant_sedes', y='PBI', alpha=0.9, hue='Pais', legend=False, size='cant_sedes', sizes=(20, 2000))

# Leyendas
plt.xlabel('Numero de Sedes')
plt.ylabel('PBI')
plt.title('Relacion entre el numero de Sedes y el PBI')

#%%

