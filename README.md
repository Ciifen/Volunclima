### Volunclima

Este repositorio contiene código relacionado con la generación de boletines climáticos y predicciones meteorológicas para la región de Suramérica.

### Archivos

#### Boletines

1. **plottingVolunclima.py**: Este archivo contiene funciones para la visualización de datos climáticos, incluyendo gráficos y mapas.

2. **boletinVolunclima.py**: Aquí se encuentran las funciones principales para la generación de boletines climáticos, que incluyen análisis de datos y creación de informes.

3. **accesoDatosVolunclima.py**: Proporciona funciones para acceder y procesar datos climáticos de diferentes fuentes.

4. **VolunclimaBoletines.py**: Este archivo actúa como un punto de entrada para ejecutar el proceso de generación de boletines climáticos.

#### Predicciones

1. **generar.py**: Contiene funciones para generar archivos y datos del climate data store mediante el cds api con predicciones meteorológicas.

2. **prediccion.py**: Aquí se encuentran las funciones principales para generar predicciones meteorológicas con los datos generados en generar.py, incluyendo la generación de anomalías y pronósticos estacionales.

### Dependencias

Hay dos archivos de dependencias porque se tuvo que buildear el python con openssl correctamente para ejecutar las descargas de los archivos necesarios en los pronósticos.
Mientas el python tenga el openssl buildeado correctamente y con el certificado correspondiente, es suficiente con tener las dependencias de los dos archivos en un solo entorno.

### A tener en cuenta

- Para poder ejecutar las funciones de las predicciones hay que tener una cuenta que es necesaria una cuenta en https://cds.climate.copernicus.eu/ e instalar la api key en el dispositivo donde se este ejecutando el código.

- Para los boletines y las predicciones cambiar todas las rutas para adaptarlas a las propias.

