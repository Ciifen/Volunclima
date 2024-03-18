import cdsapi
from datetime import datetime
import os
#area [N,W,S,E]
def generarDataset(database,nombre_archivo,year,month,variable=['2m_temperature', 'total_precipitation'],product_type='ensemble_mean',
leadtime_month=['2', '3', '4'],area=[ 30, -120, -60,-30]):
    """
    Genera un conjunto de datos a partir de una base de datos climática específica.

    Esta función utiliza la API de Copernicus Climate Data Store (CDS) para recuperar datos climáticos
    según los parámetros especificados y guarda el conjunto de datos resultante en un archivo NetCDF.

    Args:
        database (str): La base de datos climática de la cual recuperar los datos.
        nombre_archivo (str): El nombre del archivo NetCDF en el cual se guardará el conjunto de datos.
        year (int): El año para el cual se desean los datos climáticos.
        month (int): El mes (1-12) para el cual se desean los datos climáticos.
        variable (list, optional): La lista de variables climáticas deseadas. Por defecto, ['2m_temperature', 'total_precipitation'].
        product_type (str, optional): El tipo de producto de los datos. Por defecto, 'ensemble_mean'.
        leadtime_month (list, optional): La lista de meses de plazo para los datos. Por defecto, ['2', '3', '4'].
        area (list, optional): La región geográfica de la cual recuperar los datos. Especificada como [latN, lonW, latS, lonE].
                               Por defecto, [30, -120, -60, -30].

    Returns:
        None

    Raises:
        None
    """
    c = cdsapi.Client()
    c.retrieve(
        database,
        {
            'format': 'netcdf',
            'originating_centre': 'ecmwf',
            'system': '51',
            'variable': variable,
            'product_type': product_type,
            'year': year,
            'month': month,
            'leadtime_month': leadtime_month,
            'area': area,
        },
        nombre_archivo
    )


#esta funcion genera 3 meses en adelante desde el mes actual. con esto se saca el pronostico mensual y estacional
def generarTemperaturaEstacionalSuramerica(nombre_archivo='temperatura.nc',region=[ 30, -120, -60,-30],mes_str="",year_str=""):
    """
    Genera un archivo NetCDF con datos de temperatura estacional para la región de Sudamérica.

    Esta función utiliza la función `generarDataset` para obtener datos de temperatura estacional para la región de Sudamérica
    y guarda el conjunto de datos resultante en un archivo NetCDF.

    Args:
        nombre_archivo (str, optional): El nombre del archivo NetCDF en el cual se guardará el conjunto de datos.
                                        Por defecto, 'temperatura.nc'.
        region (list, optional): La región geográfica de la cual recuperar los datos. Especificada como [latN, lonW, latS, lonE].
                                 Por defecto, [30, -120, -60, -30].
        mes_str (str, optional): El mes como una cadena de texto (1-12) para el cual se desean los datos climáticos.
                                  Si no se proporciona, se utilizará el mes actual.
        year_str (str, optional): El año como una cadena de texto para el cual se desean los datos climáticos.
                                   Si no se proporciona, se utilizará el año actual.

    Returns:
        None

    Raises:
        None
    """
    try:
        # Obtener la fecha y hora actuales
        now = datetime.now()
        # Obtener el mes y el año como cadenas de texto
        if(mes_str=="" or year_str==""):
            mes_str = now.strftime("%m")  # %m devuelve el número del mes como una cadena de dos dígitos
            year_str = now.strftime("%Y")  # %Y devuelve el año con cuatro dígitos
        dirName = "/var/py/volunclima/salidas/datasets"
        nombre_archivo = dirName + "/" + nombre_archivo
        if not os.path.exists(dirName):
            os.makedirs(dirName)
        generarDataset('seasonal-monthly-single-levels',nombre_archivo,year_str,mes_str,'2m_temperature','ensemble_mean',['1', '2', '3', '4'],region)
    
    except Exception as e:
        print(f"Error al obtener datos para el archivo {nombre_archivo}: {e}")

#esta funcion genera 3 meses en adelante desde el mes actual. con esto se saca el pronostico mensual y estacional
def generarPrecipitacionEstacionalSuramerica(nombre_archivo='precipitacion.nc',region=[ 30, -120, -60,-30],mes_str="",year_str=""):
    """
    Genera un archivo NetCDF con datos de precipitación estacional para la región de Sudamérica.

    Esta función utiliza la función `generarDataset` para obtener datos de precipitación estacional para la región de Sudamérica
    y guarda el conjunto de datos resultante en un archivo NetCDF.

    Args:
        nombre_archivo (str, optional): El nombre del archivo NetCDF en el cual se guardará el conjunto de datos.
                                        Por defecto, 'precipitacion.nc'.
        region (list, optional): La región geográfica de la cual recuperar los datos. Especificada como [latN, lonW, latS, lonE].
                                 Por defecto, [30, -120, -60, -30].
        mes_str (str, optional): El mes como una cadena de texto (1-12) para el cual se desean los datos climáticos.
                                  Si no se proporciona, se utilizará el mes actual.
        year_str (str, optional): El año como una cadena de texto para el cual se desean los datos climáticos.
                                   Si no se proporciona, se utilizará el año actual.

    Returns:
        None

    Raises:
        None
    """
    try:
        # Obtener la fecha y hora actuales
        now = datetime.now()
        # Obtener el mes y el año como cadenas de texto
        if(mes_str=="" or year_str==""):
            mes_str = now.strftime("%m")  # %m devuelve el número del mes como una cadena de dos dígitos
            year_str = now.strftime("%Y")  # %Y devuelve el año con cuatro dígitos
        dirName = "/var/py/volunclima/salidas/datasets"
        nombre_archivo = dirName + "/" + nombre_archivo
        if not os.path.exists(dirName):
            os.makedirs(dirName)
        generarDataset('seasonal-monthly-single-levels',nombre_archivo,year_str,mes_str,'total_precipitation','ensemble_mean',['1', '2', '3', '4'],region)
    
    except Exception as e:
        print(f"Error al obtener datos para el archivo {nombre_archivo}: {e}")

#esta funcion genera 3 meses en adelante desde el mes actual. con esto se saca el pronostico mensual y estacional
def generarAnomaliaTemperaturaEstacionalSuramerica(nombre_archivo='temperatura_anomalia.nc',region=[ 30, -120, -60,-30],mes_str="",year_str=""):
    """
    Genera un archivo NetCDF con datos de anomalía de temperatura estacional para la región de Sudamérica.

    Esta función utiliza la función `generarDataset` para obtener datos de anomalía de temperatura estacional para la región de Sudamérica
    y guarda el conjunto de datos resultante en un archivo NetCDF.

    Args:
        nombre_archivo (str, optional): El nombre del archivo NetCDF en el cual se guardará el conjunto de datos.
                                        Por defecto, 'temperatura_anomalia.nc'.
        region (list, optional): La región geográfica de la cual recuperar los datos. Especificada como [latN, lonW, latS, lonE].
                                 Por defecto, [30, -120, -60, -30].
        mes_str (str, optional): El mes como una cadena de texto (1-12) para el cual se desean los datos climáticos.
                                  Si no se proporciona, se utilizará el mes actual.
        year_str (str, optional): El año como una cadena de texto para el cual se desean los datos climáticos.
                                   Si no se proporciona, se utilizará el año actual.

    Returns:
        None

    Raises:
        None
    """
    try:
        # Obtener la fecha y hora actuales
        now = datetime.now()
        # Obtener el mes y el año como cadenas de texto
        if(mes_str=="" or year_str==""):
            mes_str = now.strftime("%m")  # %m devuelve el número del mes como una cadena de dos dígitos
            year_str = now.strftime("%Y")  # %Y devuelve el año con cuatro dígitos
        dirName = "/var/py/volunclima/salidas/datasets"
        nombre_archivo = dirName + "/" + nombre_archivo
        if not os.path.exists(dirName):
            os.makedirs(dirName)    
        generarDataset('seasonal-postprocessed-single-levels',nombre_archivo,year_str,mes_str,'2m_temperature_anomaly','ensemble_mean',['1', '2', '3', '4'],region)
    
    except Exception as e:
            print(f"Error al obtener datos para el archivo {nombre_archivo}: {e}")


#esta funcion genera 3 meses en adelante desde el mes actual. con esto se saca el pronostico mensual y estacional
def generarAnomaliaPrecipitacionAnomaliaEstacionalSuramerica(nombre_archivo='precipitacion_anomalia.nc',region=[ 30, -120, -60,-30],mes_str="",year_str=""):
    """
    Genera un archivo netCDF conteniendo la anomalía de la tasa acumulada de precipitación para una región específica en Suramérica.

    Args:
        nombre_archivo (str, optional): Nombre del archivo netCDF de salida. Por defecto es 'precipitacion_anomalia.nc'.
        region (list, optional): Lista de coordenadas [latitud_min, longitud_min, latitud_max, longitud_max] que define la región de interés. Por defecto es [30, -120, -60, -30].
        mes_str (str, optional): Cadena que representa el mes para el cual se generará la anomalía de precipitación. Por defecto es el mes actual.
        year_str (str, optional): Cadena que representa el año para el cual se generará la anomalía de precipitación. Por defecto es el año actual.

    Returns:
        None
    """
    try:
        # Obtener la fecha y hora actuales
        now = datetime.now()
        # Obtener el mes y el año como cadenas de texto
        if(mes_str=="" or year_str==""):
            mes_str = now.strftime("%m")  # %m devuelve el número del mes como una cadena de dos dígitos
            year_str = now.strftime("%Y")  # %Y devuelve el año con cuatro dígitos
        dirName = "/var/py/volunclima/salidas/datasets"
        nombre_archivo = dirName + "/" + nombre_archivo
        if not os.path.exists(dirName):
            os.makedirs(dirName)
        generarDataset('seasonal-postprocessed-single-levels',nombre_archivo,year_str,mes_str,'total_precipitation_anomalous_rate_of_accumulation','ensemble_mean',['1', '2', '3', '4'],region)

    except Exception as e:
            print(f"Error al obtener datos para el archivo {nombre_archivo}: {e}")


#llamada a las funciones para generar los datasets. Para poder ejecutar las funciones hay que tener una cuenta que es necesario
    """
    llamada a las funciones para generar los datasets. Para poder ejecutar las funciones hay que tener una cuenta que es necesario
    una cuenta en https://cds.climate.copernicus.eu/ e instalar la api key en el dispositivo donde se este ejecutando el codigo
    """

generarTemperaturaEstacionalSuramerica()
generarPrecipitacionEstacionalSuramerica()
generarAnomaliaTemperaturaEstacionalSuramerica()
generarAnomaliaPrecipitacionAnomaliaEstacionalSuramerica()
