import cdsapi
from datetime import datetime
import os
#area [N,W,S,E]
def generarDataset(database,nombre_archivo,year,month,variable=['2m_temperature', 'total_precipitation'],product_type='ensemble_mean',
leadtime_month=['2', '3', '4'],area=[ 30, -120, -60,-30]):
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


generarTemperaturaEstacionalSuramerica()
generarPrecipitacionEstacionalSuramerica()
generarAnomaliaTemperaturaEstacionalSuramerica()
generarAnomaliaPrecipitacionAnomaliaEstacionalSuramerica()