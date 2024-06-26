import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.colors as mcolors
from cartopy.mpl.gridliner import LongitudeFormatter, LatitudeFormatter
from datetime import datetime, timedelta
import re
import calendar
from matplotlib.colors import BoundaryNorm
import os
import cartopy.util as cutil
# Paleta de colores en formato RGB
paleta_precipitacion_anomalia = np.array([
    [84, 65, 60],
    [113, 70, 59],
    [145, 90, 80],
    [160, 130, 120],
    [200, 182, 177],
    [234, 227, 226],
    [255, 255, 255],
    [211, 250, 215],
    [162, 250, 177],
    [110, 225, 130],
    [29, 176, 60],
    [43, 119, 59],
    [13, 91, 30]
]) / 255.0
# Define la paleta de colores
paletaTemperatura = np.array([
    [0, 4, 100],
    [9, 27, 206],
    [23, 56, 236],
    [38, 89, 246],
    [48, 120, 255],
    [64, 155, 255],
    [86, 189, 255],
    [118, 226, 255],
    [161, 255, 255],
    [220, 255, 255],
    [255, 255, 255],
    [255, 255, 255],
    [255, 255, 255],
    [255, 255, 175],
    [255, 227, 79],
    [255, 188, 14],
    [255, 149, 0],
    [255, 112, 3],
    [255, 75, 1],
    [247, 41, 0],
    [233, 19, 0],
    [200, 6, 0],
    [111, 0, 0]
]) / 255.0

paleta_precipitacion = np.array([
    [255, 255, 255],
    [255, 255, 255],
    [32, 126, 245],
    [24, 106, 94],
    [145, 196, 133],
    [241, 186, 111],
    [201, 88, 74]
]) / 255.0

month_name_dict = {
    1: 'Enero',
    2: 'Febrero',
    3: 'Marzo',
    4: 'Abril',
    5: 'Mayo',
    6: 'Junio',
    7: 'Julio',
    8: 'Agosto',
    9: 'Septiembre',
    10: 'Octubre',
    11: 'Noviembre',
    12: 'Diciembre'
}

    
def filled_contour(x, y, z, levels, col, xlim, ylim, zlim, antialiased=True, key_axes=None, color_palette=None, plot_axes=None,
                   ic_label=None, key_title=None, nombre_png='prediccion.png', valor_minimo=None, valor_maximo=None, medida="",pais="sudam"):
    if pais=="pacec":
        fig, ax = plt.subplots( subplot_kw={'projection': ccrs.PlateCarree(central_longitude=180)})
        ax.set_extent([-60, 150, ylim[0], ylim[1]], crs=ccrs.PlateCarree(central_longitude=180))
        #np.set_printoptions(threshold=np.inf)  # Esto establece numpy para imprimir matrices completas
        z, x, y = cutil.add_cyclic(z.values,x=x, y=y)
        
    else:
        fig, ax = plt.subplots( subplot_kw={'projection': ccrs.PlateCarree()})
        ax.set_extent([xlim[0], xlim[1], ylim[0], ylim[1]], crs=ccrs.PlateCarree())
    ax.set_aspect('auto')  # Ajustar la relación de aspecto
    

    # Interpola la paleta de colores para obtener más tonos
    smooth_color_palette = mcolors.to_rgba_array(color_palette)
    new_colormap = mcolors.LinearSegmentedColormap.from_list('smooth_colormap', smooth_color_palette, N=1000)

    # Ajustar los valores de z para asegurarse de que estén dentro del rango que quieres mostrar
    z_clipped = np.clip(z, valor_minimo, valor_maximo)

    # Crear la normalización de límites para asignar colores a los niveles
    c = plt.contourf(x, y, z_clipped, levels=levels, cmap=new_colormap, antialiased=antialiased, vmin=zlim[0], vmax=zlim[1], transform=ccrs.PlateCarree())
    #norm = BoundaryNorm(levels, ncolors=new_colormap.N, clip=True)
    #c = ax.pcolormesh(x, y, z_clipped,norm=norm, cmap=new_colormap, shading='auto', vmin=zlim[0], vmax=zlim[1])


    if pais=="sudam":
        ax.add_feature(cfeature.BORDERS, linewidth=0.5)
        ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
    else:
        ax.add_feature(cfeature.BORDERS, linewidth=1.2)
        ax.add_feature(cfeature.COASTLINE, linewidth=1.2)
        ax.add_feature(cfeature.STATES, linewidth=0.5)

    cbar = plt.colorbar(c, ax=ax)
    cbar.ax.set_title(medida, fontweight='bold', fontsize=8)

    if key_axes is not None and any(key_axes):
        cbar.set_ticks(key_axes)
        cbar.ax.set_yticklabels(['{:.0f}'.format(label) if label == 0 else '>{:.0f}'.format(label) if label == valor_maximo else '<{:.0f}'.format(label) if label == valor_minimo else '{:.0f}'.format(label) for label in key_axes])

    if plot_axes:
        plot_axes(ax)
    
    if (pais=="EC"):
        ticks_x,ticks_y=2,1
        fig.set_size_inches((8,6))
    elif (pais=="CL"):
        ticks_x,ticks_y=4,4
        fig.set_size_inches((2.5,6))
    elif (pais=="VE"):
        ticks_x,ticks_y=3,2
        fig.set_size_inches((9.5,7))
    elif (pais=="CO"):
        ticks_x,ticks_y=3,3
        fig.set_size_inches((7,7))
    elif (pais=="BO"):
        ticks_x,ticks_y=3,3
        fig.set_size_inches((7,7))
    elif (pais=="pacec"):
        ticks_x,ticks_y=20,20
        fig.set_size_inches((20,7))
    else:
        fig.set_size_inches((7,6))
        ticks_x,ticks_y=20,20
    # Establecer ticks de latitud y longitud cada 20 grados y quitar etiquetas
    ax.set_yticks(np.arange(ylim[0], ylim[1] + 1, ticks_y), crs=ccrs.PlateCarree())
    if pais=="pacec":
        ax.set_xticks(np.arange(xlim[0], xlim[1] + 1, ticks_x), crs=ccrs.PlateCarree(central_longitude=180))
    else: 
        ax.set_xticks(np.arange(xlim[0], xlim[1] + 1, ticks_x), crs=ccrs.PlateCarree())
    ax.yaxis.tick_left()
    ax.xaxis.tick_bottom()
    lon_formatter = LongitudeFormatter(zero_direction_label=True)
    lat_formatter = LatitudeFormatter()
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)
        
    # Título en negrita
    font_properties = {'family': 'sans-serif', 'style': 'italic', 'weight': 'bold', 'size': 10}
    plt.title(key_title,**font_properties, pad=10)

    # Configuración de la fuente y el estilo
    font_properties = {'family': 'sans-serif', 'style': 'italic', 'weight': 'bold', 'size': 8}

    # Añade etiquetas personalizadas con fuente "sans-serif" y estilo "bold italic"
    if ic_label:
        font_properties = {'family': 'sans-serif', 'style': 'italic', 'weight': 'bold', 'size': 8}
        plt.text(0, 1, ic_label, transform=ax.transAxes, **font_properties, verticalalignment='bottom', horizontalalignment='left')

    plt.text(1, 1, "Res: 1° x 1°", transform=ax.transAxes, **font_properties, verticalalignment='bottom', horizontalalignment='right')
    
    if (pais=="CL"):
        plt.text(-0.6, -0.10, 'ECMWF ENSEMBLE* MEAN', transform=ax.transAxes, **font_properties, ha='left', va='bottom')
        plt.text(1.6, -0.10, 'Elaborado por: CIIFEN', transform=ax.transAxes, **font_properties, ha='right', va='bottom')
        font_properties = {'family': 'sans-serif', 'style': 'italic', 'size': 8}
        plt.text(-0.6, -0.14, '*Ensemble de 51 miembros', transform=ax.transAxes, **font_properties, ha='left', va='bottom')
    else:
        plt.text(0, -0.10, 'ECMWF ENSEMBLE* MEAN', transform=ax.transAxes, **font_properties, ha='left', va='bottom')
        plt.text(1, -0.10, 'Elaborado por: CIIFEN', transform=ax.transAxes, **font_properties, ha='right', va='bottom')
        font_properties = {'family': 'sans-serif', 'style': 'italic', 'size': 8}
        plt.text(0, -0.14, '*Ensemble de 51 miembros', transform=ax.transAxes, **font_properties, ha='left', va='bottom')

    dirName = "/var/py/volunclima/salidas/predicciones/"+pais
    nombre_png = dirName + "/" + nombre_png
    if not os.path.exists(dirName):
        os.makedirs(dirName)
    plt.savefig(nombre_png, dpi=300, bbox_inches='tight')

#parametro puede ser temperatura, precipitacion, etc..
#division valor es cada cuantas unidades se divide
def generarPrediccion(start_date,end_date,nombre_png, parameter, valor_minimo, valor_maximo, ajuste_valor_maximo, division_color, division_valor, titulo, 
    paleta, ic_label, medida,pais,coord):
    # Selecciona la fecha de inicio y fin para el pronóstico mensual
    #start_date = '2023-11-01'
    #end_date = '2024-01-01'
    # Filtra el conjunto de datos para el rango de fechas
    parameter_monthly = parameter.sel(time=slice(start_date, end_date))
    # Promedia el parametro mensualmente
    parameter_monthly_mean = parameter_monthly.mean(dim='time')
    # Crea una malla de latitudes y longitudes
    lon, lat = np.meshgrid(parameter['longitude'], parameter['latitude'])
    lon_min=coord[0]
    lon_max=coord[1]
    lat_min=coord[2]
    lat_max=coord[3]
    if(start_date != end_date):     
        date_start = datetime.strptime(start_date, '%Y-%m-%d')
        date_end = datetime.strptime(end_date, '%Y-%m-%d')
        year_start = date_start.year
        month_start = date_start.month
        year_end = date_end.year
        month_end = date_end.month
        month_name_start = month_name_dict[month_start]
        month_name_end = month_name_dict[month_end]
        keyt= titulo +'\n'+ month_name_start + ' ' + str(year_start) + ' a ' + month_name_end + ' ' + str(year_end)
    else:
        date_start = datetime.strptime(start_date, '%Y-%m-%d')
        year_start = date_start.year
        month_start = date_start.month
        month_name_start = month_name_dict[month_start]
        keyt=titulo + '\n'+ month_name_start + ' ' + str(year_start)

    cbar_range = np.arange(valor_minimo, valor_maximo+ajuste_valor_maximo, division_color)
    cbar_labels = np.arange(valor_minimo, valor_maximo+1, division_valor)

    # Llamada a la función para graficar
    filled_contour(lon, lat, parameter_monthly_mean, levels=cbar_range, col=paleta, xlim=(lon_min, lon_max), ylim=(lat_min, lat_max), 
    zlim=(valor_minimo, valor_maximo), key_axes=cbar_labels, color_palette=paleta, plot_axes=None,
    ic_label=ic_label, key_title=keyt, nombre_png=nombre_png, valor_minimo=valor_minimo, valor_maximo=valor_maximo, medida=medida, pais=pais)

def generarPrediccionMensualTemperatura(ruta_dataset,fecha_inicial,pais="sudam",coord=[-120, -30, -60, 30]):
    # Format the dates as strings
    # Abre el conjunto de datos netcdf
    #file_path='download.nc'
    dataset = xr.open_dataset(ruta_dataset)
    # Selecciona la variable de temperatura superficial del aire (t2m)
    temperature = dataset['t2m']
    # Convierte la temperatura de Kelvin a Celsius
    temperature_celsius = temperature - 273.15
    #obtener IC (cuando se obtuvo el dataset)
    ic_label =  getIC(dataset)
    #nombre archivo
    nombre_archivo='pron_tsaireECMWF_' + pais + '_mens.png'
    #generar prediccion
    generarPrediccion(fecha_inicial, fecha_inicial,nombre_archivo, temperature_celsius, -10, 38, 1, 1, 4,
    'Predicción Mensual de Temperatura Superficial del Aire(\u00B0C)', paletaTemperatura, ic_label, '°C',pais,coord)
    dataset.close()

def generarPrediccionMensualPrecipitacion(ruta_dataset,fecha_inicial,pais="sudam",coord=[-120, -30, -60, 30]):
    # Format the dates as strings
    # Abre el conjunto de datos netcdf
    #file_path='download.nc'
    dataset = xr.open_dataset(ruta_dataset)
    # Selecciona la variable de precipitacion
    precipitacion = dataset['tprate']
    dias_en_mes = getDiasConRangoFechas(fecha_inicial, fecha_inicial)
    # Convierte la precipitación de m/s a mm/mes
    precipitacion_mm_mes = precipitacion * (1000 * 3600 * 24 * dias_en_mes)
    #obtener IC (cuando se obtuvo el dataset)
    ic_label =  getIC(dataset)
    #nombre archivo
    nombre_archivo='pron_prcpECMWF_' + pais + '_mens.png'
    #generar prediccion
    generarPrediccion(fecha_inicial, fecha_inicial,nombre_archivo, precipitacion_mm_mes, 0, 500, 1, 12.5, 50,
    'Predicción Mensual de Precipitación Acumulada (mm/mes)', paleta_precipitacion, ic_label, 'mm',pais,coord)
    dataset.close()

def generarPrediccionEstacionalTemperatura(ruta_dataset,fecha_inicial,fecha_final,pais="sudam",coord=[-120, -30, -60, 30]):

    # Abre el conjunto de datos netcdf
    #file_path='download.nc'
    dataset = xr.open_dataset(ruta_dataset)
    # Selecciona la variable de temperatura superficial del aire (t2m)
    temperature = dataset['t2m']
    # Convierte la temperatura de Kelvin a Celsius
    temperature_celsius = temperature - 273.15
    #obtener IC (cuando se obtuvo el dataset)
    ic_label =  getIC(dataset)
    #nombre archivo
    nombre_archivo='pron_tsaireECMWF_' + pais + '_estac.png'
    #generar prediccion
    generarPrediccion(fecha_inicial, fecha_final,nombre_archivo, temperature_celsius, -10, 38, 1, 1, 4,
    'Predicción Estacional de Temperatura Superficial del Aire(\u00B0C)', paletaTemperatura, ic_label, '°C',pais,coord)
    dataset.close()

def generarPrediccionEstacionalPrecipitacion(ruta_dataset,fecha_inicial,fecha_final,pais="sudam",coord=[-120, -30, -60, 30]):

    # Abre el conjunto de datos netcdf
    #file_path='download.nc'
    dataset = xr.open_dataset(ruta_dataset)
    # Selecciona la variable de precipitacion
    precipitacion = dataset['tprate']
    dias_en_mes = getDiasConRangoFechas(fecha_inicial, fecha_inicial)
    # Convierte la precipitación de m/s a mm/mes
    precipitacion_mm_mes = precipitacion * (1000 * 3600 * 24 * dias_en_mes)
    #obtener IC (cuando se obtuvo el dataset)
    ic_label =  getIC(dataset)
    #nombre archivo
    nombre_archivo='pron_prcpECMWF_' + pais + '_estac.png'
    #generar prediccion
    generarPrediccion(fecha_inicial, fecha_final,nombre_archivo, precipitacion_mm_mes, 0, 500, 1, 12.5, 50,
    'Predicción Estacional de Precipitación Acumulada (mm/mes)', paleta_precipitacion, ic_label, 'mm',pais,coord)
    dataset.close()




def generarPrediccionAnomaliaMensualTemperatura(ruta_dataset,fecha_inicial,pais="sudam",coord=[-120, -30, -60, 30]):
    # Format the dates as strings
    # Abre el conjunto de datos netcdf
    #file_path='download.nc'
    dataset = xr.open_dataset(ruta_dataset)
    # Selecciona la variable de temperatura superficial del aire (t2m)
    temperature = dataset['t2a']
    # Convierte la temperatura de Kelvin a Celsius
    temperature_celsius = temperature 
    #obtener IC (cuando se obtuvo el dataset)
    ic_label =  getIC(dataset)
    #nombre archivo
    nombre_archivo='pron_tsaireECMWF_' + pais + '_mens_anom.png'
    #generar prediccion
    generarPrediccion(fecha_inicial, fecha_inicial,nombre_archivo, temperature_celsius, -4, 4, 0.25, 0.25, 1,
    'Predicción Mensual de Anomalía de Temperatura Superficial del Aire(\u00B0C)', paletaTemperatura, ic_label, '°C',pais,coord)
    dataset.close()

def generarPrediccionAnomaliaMensualPrecipitacion(ruta_dataset,fecha_inicial,pais="sudam",coord=[-120, -30, -60, 30]):
    # Format the dates as strings
    # Abre el conjunto de datos netcdf
    #file_path='download.nc'
    dataset = xr.open_dataset(ruta_dataset)
    # Selecciona la variable de precipitacion
    precipitacion = dataset['tpara']
    dias_en_mes = getDiasConRangoFechas(fecha_inicial, fecha_inicial)
    # Convierte la precipitación de m/s a mm/mes
    precipitacion_mm_mes = precipitacion * (1000 * 3600 * 24 * dias_en_mes)
    #obtener IC (cuando se obtuvo el dataset)
    ic_label =  getIC(dataset)
    #nombre archivo
    nombre_archivo='pron_prcpECMWF_' + pais + '_mens_anom.png'
    #generar prediccion
    generarPrediccion(fecha_inicial, fecha_inicial,nombre_archivo, precipitacion_mm_mes, -100, 100, 1, 10, 50,
    'Predicción Mensual de Anomalía de Precipitación Acumulada (mm/mes)', paleta_precipitacion_anomalia, ic_label, 'mm',pais,coord)
    dataset.close()

def generarPrediccionAnomaliaEstacionalTemperatura(ruta_dataset,fecha_inicial,fecha_final,pais="sudam",coord=[-120, -30, -60, 30]):

    # Abre el conjunto de datos netcdf
    #file_path='download.nc'
    dataset = xr.open_dataset(ruta_dataset)
    # Selecciona la variable de temperatura superficial del aire (t2m)
    
    temperature = dataset['t2a']
    # Convierte la temperatura de Kelvin a Celsius
    temperature_celsius = temperature
    #obtener IC (cuando se obtuvo el dataset)
    ic_label =  getIC(dataset)
    #nombre archivo
    nombre_archivo='pron_tsaireECMWF_' + pais + '_estac_anom.png'
    #generar prediccion
    generarPrediccion(fecha_inicial, fecha_final,nombre_archivo, temperature_celsius, -4, 4, 0.25, 0.25, 1,
    'Predicción Estacional Anomalía de Temperatura Superficial del Aire(\u00B0C)', paletaTemperatura, ic_label, '°C',pais,coord)
    dataset.close()

def generarPrediccionAnomaliaEstacionalPrecipitacion(ruta_dataset,fecha_inicial,fecha_final,pais="sudam",coord=[-120, -30, -60, 30]):
    # Abre el conjunto de datos netcdf
    #file_path='download.nc'
    dataset = xr.open_dataset(ruta_dataset)
    # Selecciona la variable de precipitacion
    precipitacion = dataset['tpara']
    dias_en_mes = getDiasConRangoFechas(fecha_inicial, fecha_inicial)
    # Convierte la precipitación de m/s a mm/mes
    precipitacion_mm_mes = precipitacion * (1000 * 3600 * 24 * dias_en_mes)
    #obtener IC (cuando se obtuvo el dataset)
    ic_label =  getIC(dataset)
    #nombre archivo
    nombre_archivo='pron_prcpECMWF_' + pais + '_estac_anom.png'
    #generar prediccion
    generarPrediccion(fecha_inicial, fecha_final,nombre_archivo, precipitacion_mm_mes, -100, 100, 1, 10, 50,
    'Predicción Estacional de Anomalía de Precipitación Acumulada (mm/mes)', paleta_precipitacion_anomalia, ic_label, 'mm',pais,coord)
    dataset.close()



#funcion que devuelve un string "%Y-%m-%d", con el dia 1 de el siguiente mes de la fecha actual
def getFechaInicial():
    # Get the current date and time
    now = datetime.now()
    next_month_str=datetime.now()
    # Calculate the next month and four months ahead dates
    next_month_num = int(now.month)+1  
    # If the new month is greater than 12, subtract 12 and add 1 to the year
    if next_month_num > 12:
        next_month_num = next_month_num - 12
        next_month_str = now.replace(month=next_month_num, year=now.year + 1, day=1)
    else:
        next_month_str = now.replace(month=next_month_num, day=1) 
    return next_month_str.strftime("%Y-%m-%d")

#funcion que devuelve un string "%Y-%m-%d", con el dia 1 de dentro de 3 meses de la fecha actual
def getFechaFinal():
    # Get the current date and time
    now = datetime.now()
    three_months_ahead_str=datetime.now()
    # Calculate three months ahead dates
    three_months_ahead_num = int(now.month) + 3
    if three_months_ahead_num > 12:
        three_months_ahead_num = three_months_ahead_num - 12
        three_months_ahead_str = three_months_ahead_str.replace(month=three_months_ahead_num, year=now.year + 1, day=1)
    else:
        three_months_ahead_str = three_months_ahead_str.replace(month=three_months_ahead_num, day=1)
    return three_months_ahead_str.strftime("%Y-%m-%d")

#obtiene fecha de obtencion del dataset
def getIC(dataset):
    # Verifica si existe el atributo 'history' en el conjunto de datos
    if 'history' in dataset.attrs:
        # Extrae la cadena que contiene información sobre la fecha de obtencion de informacion
        history_str = dataset.attrs['history']
        # Busca la fecha en el formato adecuado (ajusta según el formato real en tu caso)
        date_match = history_str[:10]
        if date_match:
            # Obtiene la fecha encontrada
            download_date = datetime.strptime(date_match, '%Y-%m-%d')        
            # Utiliza la fecha en el texto de IC
            ic_text = f"IC: {download_date}"
            # Imprime la cadena para verificar
            print(ic_text)
            return f"IC: {download_date.strftime('%Y%b')}".upper()
            #return f"IC: {download_date.strftime('%Y')}MAR".upper()
        else:
            print("No se encontró una fecha en el atributo 'history'.")
            return ""
    else:
        print("El atributo 'history' no está presente en el conjunto de datos.")
        return ""

#obtiene los dias (int) en un rango de fecha dado
def getDiasConRangoFechas(start_date_str, end_date_str):
    # Convertimos las fechas en objetos date
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    # Calcular 1 mes despues de end date
    next_month_num = int(end_date.month)  + 1
    # If the new month is greater than 12, subtract 12 and add 1 to the year
    if next_month_num > 12:
        next_month_num = next_month_num - 12
        end_date = end_date.replace(month=next_month_num, year=end_date.year + 1, day=1)
    else:
        end_date = end_date.replace(month=next_month_num, day=1) 

    # Sumamos 1 a cada uno de los días para incluir ambas fechas en el rango si las fechas no son iguales, si no no se suma porque es la misma
    if (start_date_str == end_date_str):   
        num_days_in_range = (end_date - start_date).days
    else:
        num_days_in_range = (end_date - start_date).days + 1

    return num_days_in_range


#generarPrediccionMensualTemperatura('temperatura_ecuador.nc','pron_tsaireECMWF_sudam_mens.png')

#generarPrediccionEstacionalTemperatura('temperatura.nc','pron_tsaireECMWF_EC_estac.png',"EC",[longitud_min, longitud_max, lat_min, lat_max])

""" #chile
generarPrediccionMensualTemperatura('/var/py/volunclima/salidas/datasets/temperatura.nc',"CL",[-78, -63, -57, -17])
generarPrediccionEstacionalTemperatura('/var/py/volunclima/salidas/datasets/temperatura.nc',"CL",[-78, -63, -57, -17])
generarPrediccionMensualPrecipitacion('/var/py/volunclima/salidas/datasets/precipitacion.nc',"CL",[-78, -63, -57, -17])
generarPrediccionEstacionalPrecipitacion('/var/py/volunclima/salidas/datasets/precipitacion.nc',"CL",[-78, -63, -57, -17])

#colombia
generarPrediccionMensualTemperatura('/var/py/volunclima/salidas/datasets/temperatura.nc',"CO",[-79, -66, -5, 13])
generarPrediccionEstacionalTemperatura('/var/py/volunclima/salidas/datasets/temperatura.nc',"CO",[-79, -66, -5, 13])
generarPrediccionMensualPrecipitacion('/var/py/volunclima/salidas/datasets/precipitacion.nc',"CO",[-79, -66, -5, 13])
generarPrediccionEstacionalPrecipitacion('/var/py/volunclima/salidas/datasets/precipitacion.nc',"CO",[-79, -66, -5, 13])

#ecuador
generarPrediccionMensualTemperatura('/var/py/volunclima/salidas/datasets/temperatura.nc',"EC",[-82, -74, -5, 2])
generarPrediccionEstacionalTemperatura('/var/py/volunclima/salidas/datasets/temperatura.nc',"EC",[-82, -74, -5, 2])
generarPrediccionMensualPrecipitacion('/var/py/volunclima/salidas/datasets/precipitacion.nc',"EC",[-82, -74, -5, 2])
generarPrediccionEstacionalPrecipitacion('/var/py/volunclima/salidas/datasets/precipitacion.nc',"EC",[-82, -74, -5, 2])

#venezuela
generarPrediccionMensualTemperatura('/var/py/volunclima/salidas/datasets/temperatura.nc',"VE",[-74, -57, 0, 13])
generarPrediccionEstacionalTemperatura('/var/py/volunclima/salidas/datasets/temperatura.nc',"VE",[-74, -57, 0, 13])
generarPrediccionMensualPrecipitacion('/var/py/volunclima/salidas/datasets/precipitacion.nc',"VE",[-74, -57, 0, 13])
generarPrediccionEstacionalPrecipitacion('/var/py/volunclima/salidas/datasets/precipitacion.nc',"VE",[-74, -57, 0, 13]) 

#bolivia
generarPrediccionMensualTemperatura('/var/py/volunclima/salidas/datasets/temperatura.nc',"BO",[-69.625, -57.375, -22.875, -9.625])
generarPrediccionEstacionalTemperatura('/var/py/volunclima/salidas/datasets/temperatura.nc',"BO",[-69.625, -57.375, -22.875, -9.625])
generarPrediccionMensualPrecipitacion('/var/py/volunclima/salidas/datasets/precipitacion.nc',"BO",[-69.625, -57.375, -22.875, -9.625])
generarPrediccionEstacionalPrecipitacion('/var/py/volunclima/salidas/datasets/precipitacion.nc',"BO",[-69.625, -57.375, -22.875, -9.625])"""

""" generarPrediccionMensualTemperatura('/var/py/volunclima/salidas/datasets/temperatura.nc',"CL",[-78, -63, -57, -17])
generarPrediccionMensualTemperatura('/var/py/volunclima/salidas/datasets/temperatura.nc',"CO",[-79, -66, -5, 13])
generarPrediccionMensualTemperatura('/var/py/volunclima/salidas/datasets/temperatura.nc',"EC",[-82, -74, -5, 2])
generarPrediccionMensualTemperatura('/var/py/volunclima/salidas/datasets/temperatura.nc',"VE",[-74, -57, 0, 13])
generarPrediccionMensualTemperatura('/var/py/volunclima/salidas/datasets/temperatura.nc',"BO",[-69.8, -57.375, -23, -9.625]) """



""" lon_leftup=-69.625
		lat_leftup=-9.625
		lon_rightdown=-57.375
		lat_rightdown=-22.875 """

#generarPrediccionEstacionalTemperatura(nombre_dataset,nombre_png)
generarPrediccionMensualTemperatura('/var/py/volunclima/salidas/datasets/temperatura.nc',getFechaInicial(),'sudam',coord=[-120, -30, -60, 30])
generarPrediccionMensualPrecipitacion('/var/py/volunclima/salidas/datasets/precipitacion.nc',getFechaInicial(),'sudam',coord=[-120, -30, -60, 30])
generarPrediccionEstacionalTemperatura('/var/py/volunclima/salidas/datasets/temperatura.nc',getFechaInicial(),getFechaFinal(),'sudam',coord=[-120, -30, -60, 30])
generarPrediccionEstacionalPrecipitacion('/var/py/volunclima/salidas/datasets/precipitacion.nc',getFechaInicial(),getFechaFinal(),'sudam',coord=[-120, -30, -60, 30])

generarPrediccionAnomaliaMensualTemperatura('/var/py/volunclima/salidas/datasets/temperatura_anomalia.nc',getFechaInicial(),'sudam',coord=[-120, -30, -60, 30])
generarPrediccionAnomaliaMensualPrecipitacion('/var/py/volunclima/salidas/datasets/precipitacion_anomalia.nc',getFechaInicial(),'sudam',coord=[-120, -30, -60, 30])
generarPrediccionAnomaliaEstacionalTemperatura('/var/py/volunclima/salidas/datasets/temperatura_anomalia.nc',getFechaInicial(),getFechaFinal(),'sudam',coord=[-120, -30, -60, 30])
generarPrediccionAnomaliaEstacionalPrecipitacion('/var/py/volunclima/salidas/datasets/precipitacion_anomalia.nc',getFechaInicial(),getFechaFinal(),'sudam',coord=[-120, -30, -60, 30])

generarPrediccionMensualPrecipitacion('/var/py/volunclima/salidas/datasets/precipitacion.nc',getFechaInicial(),'pacec',coord=[-60, 150, -60, 30])
generarPrediccionEstacionalPrecipitacion('/var/py/volunclima/salidas/datasets/precipitacion.nc',getFechaInicial(),getFechaFinal(),'pacec',coord=[-60, 150, -60, 30])
generarPrediccionAnomaliaMensualPrecipitacion('/var/py/volunclima/salidas/datasets/precipitacion_anomalia.nc',getFechaInicial(),'pacec',coord=[-60, 150, -60, 30])
generarPrediccionAnomaliaEstacionalPrecipitacion('/var/py/volunclima/salidas/datasets/precipitacion_anomalia.nc',getFechaInicial(),getFechaFinal(),'pacec',coord=[-60, 150, -60, 30])