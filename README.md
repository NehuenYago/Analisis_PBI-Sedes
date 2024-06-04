# Estudio de la relación PBI - Embajadas

## Resumen

En este trabajo nos propusimos entender la relación entre el PBI per cápita de un país y la cantidad de sedes que Argentina tiene en dicho país. Para ello hemos recopilado tablas púbicas que contengan datos acerca del PBI de los países del mundo como también información sobre ellos, por ejemplo la región a la que pertenecen, y también información acerca de las sedes que Argentina tiene en el mundo. A partir de éstas tablas hemos hecho un análisis exploratorio de estas como así de la calidad de los datos y, en consecuencia, una limpieza de los atributos que consideramos clave a la hora de analizar esta relación. Hemos generado un Modelo Entidad-Relación y su respectivo DER (Diagrama de Entidad Relación) Luego creamos dataframes vacíos que corresponden al DER, y por último hemos importado los datos que consideramos relevantes.
A partir de estos datos, utilizamos SQL para generar reportes que muestran distintas relaciones entre los países, el PBI, su región y las redes que utilizan para su comunicación como también gráficos que nos ayudaron a visualizar y entender la información que hemos recopilado y limpiado.
Por último llegamos a la conclusión que a pesar que el PBI per cápita es un factor importante a la hora de analizar la cantidad de sedes de un país, esta relación no es lineal y no es el único factor relevante para entender la relación entre la cantidad de sedes que tiene un país.

## Contenido del repositorio

- Tablas originales públicas descargadas.
- Tablas propias generadas en 3ra forma normal con los datos necesarios para la realización del trabajo.
- Reportes generados con SQL para comprender y analizar la relación entre las tablas propias.
- Un informe en .pdf donde se detalla el trabajo realizado, se muestran los reportes, los gráficos y la conclusión.
- Archivo `main.py` donde se encuentra todo el código utilizado para limpiar las tablas originales, generar las tablas, los reportes, y los gráficos.

## Para ejecutar el código

Utilizamos las librerías pandas, inline_sql, matplotlib y seaborn. Para ejecutar el código recomendamos el gestor de paquetes y entornos [Conda](https://docs.conda.io/en/latest/).
