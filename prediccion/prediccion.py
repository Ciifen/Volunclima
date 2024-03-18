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
# Paletas de colores en formato RGB 
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
""" paleta_precipitacion = np.array([
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
]) / 255.0 """
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
    """
    Genera un gráfico de contorno relleno con datos geoespaciales.

    Esta función utiliza Matplotlib para generar un gráfico de contorno relleno con datos geoespaciales proporcionados en forma de arrays 2D x, y y z.
    Los contornos se generan a partir de los niveles especificados y se colorean según la paleta de colores proporcionada.

    Args:
        x (array_like): Coordenadas x de los puntos de los datos.
        y (array_like): Coordenadas y de los puntos de los datos.
        z (array_like): Valores z asociados a las coordenadas x e y.
        levels (array_like): Niveles de contorno para dibujar líneas y colores.
        col (array_like): Paleta de colores a utilizar para el relleno de los contornos.
        xlim (array_like): Límites del eje x del gráfico.
        ylim (array_like): Límites del eje y del gráfico.
        zlim (array_like): Límites de los valores z que se mostrarán en el gráfico.
        antialiased (bool, optional): Controla si las líneas son antialiasadas. Por defecto, True.
        key_axes (array_like, optional): Posiciones de las marcas de los ejes en la barra de colores.
        color_palette (array_like, optional): Paleta de colores para la interpolación.
        plot_axes (function, optional): Función para personalizar los ejes del gráfico.
        ic_label (str, optional): Etiqueta para el índice de correlación.
        key_title (str, optional): Título de la barra de colores.
        nombre_png (str, optional): Nombre del archivo PNG donde se guardará el gráfico.
        valor_minimo (float, optional): Valor mínimo para los datos z.
        valor_maximo (float, optional): Valor máximo para los datos z.
        medida (str, optional): Etiqueta de la medida mostrada en la barra de colores.
        pais (str, optional): País o región para personalizar el gráfico. Por defecto, 'sudam'.

    Returns:
        None

    Raises:
        None
    """
    fig, ax = plt.subplots( subplot_kw={'projection': ccrs.PlateCarree()})
    ax.set_aspect('auto')  # Ajustar la relación de aspecto
    
    # Ajustar la extensión del mapa a la región de tus datos
    ax.set_extent([xlim[0], xlim[1], ylim[0], ylim[1]], crs=ccrs.PlateCarree())
    # Interpola la paleta de colores para obtener más tonos
    smooth_color_palette = mcolors.to_rgba_array(color_palette)
    new_colormap = mcolors.LinearSegmentedColormap.from_list('smooth_colormap', smooth_color_palette, N=1000)

    # Ajustar los valores de z para asegurarse de que estén dentro del rango que quieres mostrar
    z_clipped = np.clip(z, valor_minimo, valor_maximo)

    # Crear la normalización de límites para asignar colores a los niveles
    c = plt.contourf(x, y, z_clipped, levels=levels, cmap=new_colormap, antialiased=antialiased, vmin=zlim[0], vmax=zlim[1])
    #norm = BoundaryNorm(levels, ncolors=new_colormap.N, clip=True)
    #c = ax.pcolormesh(x, y, z_clipped,norm=norm, cmap=new_colormap, shading='auto')


    if pais=="sudam":
        ax.add_feature(cfeature.BORDERS, linewidth=0.5)
        ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
    else:
        ax.add_feature(cfeature.BORDERS, linewidth=1.2)
        ax.add_feature(cfeature.COASTLINE, linewidth=1.2)
        ax.add_feature(cfeature.STATES, linewidth=0.5)

    cbar = plt.colorbar(c, ax=ax)
    if(pais=="EC" or pais=="VE" or pais=="GA"):
        cbar.ax.set_title(medida, fontweight='bold', fontsize=12)
    else:
        cbar.ax.set_title(medida, fontweight='bold', fontsize=8)

    if key_axes is not None and any(key_axes):
        cbar.set_ticks(key_axes)
        if (pais=="EC" or pais=="VE" or pais=="GA"):
            cbar.ax.set_yticklabels(['{:.0f}'.format(label) if label == 0 else '>{:.0f}'.format(label) if label == valor_maximo else '<{:.0f}'.format(label) if label == valor_minimo else '{:.0f}'.format(label) for label in key_axes],fontsize=12)
        else:
            cbar.ax.set_yticklabels(['{:.0f}'.format(label) if label == 0 else '>{:.0f}'.format(label) if label == valor_maximo else '<{:.0f}'.format(label) if label == valor_minimo else '{:.0f}'.format(label) for label in key_axes])

    if plot_axes:
        plot_axes(ax)
    
    if (pais=="EC"):
        ticks_x,ticks_y=2,1
        fig.set_size_inches((8,6))
        # Cambiar el tamaño de los valores en el eje x
        ax.tick_params(axis='x', labelsize=12)
        # Cambiar el tamaño de los valores en el eje y
        ax.tick_params(axis='y', labelsize=12)

    elif (pais=="CL"):
        ticks_x,ticks_y=4,4
        fig.set_size_inches((2.5,6))
    elif (pais=="VE"):
        ticks_x,ticks_y=3,2
        fig.set_size_inches((9.5,7))
        # Cambiar el tamaño de los valores en el eje x
        ax.tick_params(axis='x', labelsize=12)
        # Cambiar el tamaño de los valores en el eje y
        ax.tick_params(axis='y', labelsize=12)

    elif (pais=="CO"):
        ticks_x,ticks_y=3,3
        fig.set_size_inches((6,6))
    elif (pais=="BO"):
        ticks_x,ticks_y=3,3
        fig.set_size_inches((6,6))

    else:
        fig.set_size_inches((7,6))
        ticks_x,ticks_y=20,20
        # Cambiar el tamaño de los valores en el eje x
        ax.tick_params(axis='x', labelsize=12)
        # Cambiar el tamaño de los valores en el eje y
        ax.tick_params(axis='y', labelsize=12)
    # Establecer ticks de latitud y longitud cada 20 grados y quitar etiquetas
    ax.set_yticks(np.arange(ylim[0], ylim[1] + 1, ticks_y), crs=ccrs.PlateCarree())
    ax.set_xticks(np.arange(xlim[0], xlim[1] + 1, ticks_x), crs=ccrs.PlateCarree())
    ax.yaxis.tick_left()
    ax.xaxis.tick_bottom()
    lon_formatter = LongitudeFormatter(zero_direction_label=True)
    lat_formatter = LatitudeFormatter()
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)

    if(pais=="EC" or pais=="VE" or pais=="GA"):
        titulosize=14
        letrasize=12
    else:
        titulosize=10
        letrasize=8
    # Título en negrita
    font_properties = {'family': 'sans-serif', 'style': 'italic', 'weight': 'bold', 'size': titulosize}
    plt.title(key_title,**font_properties, pad=13)

    # Configuración de la fuente y el estilo
    font_properties = {'family': 'sans-serif', 'style': 'italic', 'weight': 'bold', 'size': letrasize}

    # Añade etiquetas personalizadas con fuente "sans-serif" y estilo "bold italic"
    if ic_label:
        font_properties = {'family': 'sans-serif', 'style': 'italic', 'weight': 'bold', 'size': letrasize}
        plt.text(0, 1, ic_label, transform=ax.transAxes, **font_properties, verticalalignment='bottom', horizontalalignment='left')

    plt.text(1, 1, "Res: 1° x 1°", transform=ax.transAxes, **font_properties, verticalalignment='bottom', horizontalalignment='right')

    if (pais=="CL"):
        plt.text(-0.6, -0.10, 'ECMWF ENSEMBLE* MEAN', transform=ax.transAxes, **font_properties, ha='left', va='bottom')
        plt.text(1.6, -0.10, 'Elaborado por: CIIFEN', transform=ax.transAxes, **font_properties, ha='right', va='bottom')
        font_properties = {'family': 'sans-serif', 'style': 'italic', 'size': 8}
        plt.text(-0.6, -0.14, '*Ensemble de 51 miembros', transform=ax.transAxes, **font_properties, ha='left', va='bottom')
    else:
        if(pais=="GA"):
            font_properties = {'family': 'sans-serif', 'style': 'italic', 'weight': 'bold', 'size': 11}
        plt.text(0, -0.10, 'ECMWF ENSEMBLE* MEAN', transform=ax.transAxes, **font_properties, ha='left', va='bottom')
        plt.text(1, -0.10, 'Elaborado por: CIIFEN', transform=ax.transAxes, **font_properties, ha='right', va='bottom')
        if(pais=="EC" or pais=="VE" ):
            letrasize=12
        elif(pais=="GA"):
            letrasize=10
        else:
            letrasize=8
        
        font_properties = {'family': 'sans-serif', 'style': 'italic', 'size': letrasize}
        
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
    """
    Genera un pronóstico climático mensual de temperatura, precipitación o sus respectivas anomalias y crea un gráfico de contorno relleno para visualizar 
    los datos en una región específica con la función filled_contour()

    Args:
        start_date (str): Fecha de inicio del pronóstico en formato 'YYYY-MM-DD'.
        end_date (str): Fecha de fin del pronóstico en formato 'YYYY-MM-DD'.
        nombre_png (str): Nombre del archivo PNG para guardar la figura.
        parameter (xarray.DataArray): Conjunto de datos climáticos.
        valor_minimo (float): Valor mínimo para los datos.
        valor_maximo (float): Valor máximo para los datos.
        ajuste_valor_maximo (float): Ajuste adicional al valor máximo.
        division_color (float): Intervalo para la paleta de colores.
        division_valor (int): Intervalo para etiquetas en el colorbar.
        titulo (str): Título para el gráfico.
        paleta (array_like): Paleta de colores para la visualización.
        ic_label (str): Etiqueta para identificar el índice climático.
        medida (str): Unidad de medida de los datos.
        pais (str): País o región para personalizar el gráfico.
        coord (list): Coordenadas de la región de interés en el formato [lon_min, lon_max, lat_min, lat_max].

    Returns:
        None
    """

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

def generarPrediccionMensualTemperatura(ruta_dataset,pais="sudam",coord=[-120, -30, -60, 30]):
    """
    Genera un pronóstico mensual de temperatura superficial del aire y crea un gráfico de contorno relleno para visualizar los datos en una región específica.

    Args:
        ruta_dataset (str): Ruta del conjunto de datos netCDF que contiene la temperatura superficial del aire.
        pais (str, optional): País o región para personalizar el gráfico. Por defecto es "sudam".
        coord (list, optional): Coordenadas de la región de interés en el formato [lon_min, lon_max, lat_min, lat_max]. Por defecto es [-120, -30, -60, 30].

    Returns:
        None
    """
    # Format the dates as strings
    fecha_inicial = getFechaInicial()
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

def generarPrediccionMensualPrecipitacion(ruta_dataset,pais="sudam",coord=[-120, -30, -60, 30]):
    """
    Genera un pronóstico mensual de precipitación acumulada y crea un gráfico de contorno relleno para visualizar los datos en una región específica.

    Args:
        ruta_dataset (str): Ruta del conjunto de datos netCDF que contiene la precipitación.
        pais (str, optional): País o región para personalizar el gráfico. Por defecto es "sudam".
        coord (list, optional): Coordenadas de la región de interés en el formato [lon_min, lon_max, lat_min, lat_max]. Por defecto es [-120, -30, -60, 30].

    Returns:
        None
    """
    # Format the dates as strings
    fecha_inicial = getFechaInicial()
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

def generarPrediccionEstacionalTemperatura(ruta_dataset,pais="sudam",coord=[-120, -30, -60, 30]):
    """
    Genera un pronóstico estacional de temperatura superficial del aire y crea un gráfico de contorno relleno para visualizar los datos en una región específica.

    Args:
        ruta_dataset (str): Ruta del conjunto de datos netCDF que contiene la temperatura superficial del aire.
        pais (str, optional): País o región para personalizar el gráfico. Por defecto es "sudam".
        coord (list, optional): Coordenadas de la región de interés en el formato [lon_min, lon_max, lat_min, lat_max]. Por defecto es [-120, -30, -60, 30].

    Returns:
        None
    """
    fecha_inicial = getFechaInicial()
    fecha_final = getFechaFinal()
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

def generarPrediccionEstacionalPrecipitacion(ruta_dataset,pais="sudam",coord=[-120, -30, -60, 30]):
    """
    Genera un pronóstico estacional de precipitación acumulada y crea un gráfico de contorno relleno para visualizar los datos en una región específica.

    Args:
        ruta_dataset (str): Ruta del conjunto de datos netCDF que contiene la variable de precipitación.
        pais (str, optional): País o región para personalizar el gráfico. Por defecto es "sudam".
        coord (list, optional): Coordenadas de la región de interés en el formato [lon_min, lon_max, lat_min, lat_max]. Por defecto es [-120, -30, -60, 30].

    Returns:
        None
    """
    fecha_inicial = getFechaInicial()
    fecha_final = getFechaFinal()
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




def generarPrediccionAnomaliaMensualTemperatura(ruta_dataset,pais="sudam",coord=[-120, -30, -60, 30]):
    """
    Genera un pronóstico mensual de la anomalía de temperatura superficial del aire y crea un gráfico de contorno relleno para visualizar los datos en una región específica.

    Args:
        ruta_dataset (str): Ruta del conjunto de datos netCDF que contiene la variable de temperatura superficial del aire.
        pais (str, optional): País o región para personalizar el gráfico. Por defecto es "sudam".
        coord (list, optional): Coordenadas de la región de interés en el formato [lon_min, lon_max, lat_min, lat_max]. Por defecto es [-120, -30, -60, 30].

    Returns:
        None
    """
    # Format the dates as strings
    fecha_inicial = getFechaInicial()
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

def generarPrediccionAnomaliaMensualPrecipitacion(ruta_dataset,pais="sudam",coord=[-120, -30, -60, 30]):
    """
    Genera un pronóstico mensual de la anomalía de precipitación acumulada y crea un gráfico de contorno relleno para visualizar los datos en una región específica.

    Args:
        ruta_dataset (str): Ruta del conjunto de datos netCDF que contiene la variable de precipitación.
        pais (str, optional): País o región para personalizar el gráfico. Por defecto es "sudam".
        coord (list, optional): Coordenadas de la región de interés en el formato [lon_min, lon_max, lat_min, lat_max]. Por defecto es [-120, -30, -60, 30].

    Returns:
        None
    """
    # Format the dates as strings
    fecha_inicial = getFechaInicial()
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

def generarPrediccionAnomaliaEstacionalTemperatura(ruta_dataset,pais="sudam",coord=[-120, -30, -60, 30]):
    """
    Genera un pronóstico estacional de la anomalía de temperatura superficial del aire y crea un gráfico de contorno relleno para visualizar los datos en una región específica.

    Args:
        ruta_dataset (str): Ruta del conjunto de datos netCDF que contiene la variable de temperatura.
        pais (str, optional): País o región para personalizar el gráfico. Por defecto es "sudam".
        coord (list, optional): Coordenadas de la región de interés en el formato [lon_min, lon_max, lat_min, lat_max]. Por defecto es [-120, -30, -60, 30].

    Returns:
        None
    """
    fecha_inicial = getFechaInicial()
    fecha_final = getFechaFinal()
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

def generarPrediccionAnomaliaEstacionalPrecipitacion(ruta_dataset,pais="sudam",coord=[-120, -30, -60, 30]):
    """
    Genera un pronóstico estacional de la anomalía de precipitación acumulada y crea un gráfico de contorno relleno para visualizar los datos en una región específica.

    Args:
        ruta_dataset (str): Ruta del conjunto de datos netCDF que contiene la variable de precipitación.
        pais (str, optional): País o región para personalizar el gráfico. Por defecto es "sudam".
        coord (list, optional): Coordenadas de la región de interés en el formato [lon_min, lon_max, lat_min, lat_max]. Por defecto es [-120, -30, -60, 30].

    Returns:
        None
    """
    fecha_inicial = getFechaInicial()
    fecha_final = getFechaFinal()
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
    next_month_num = int(now.month)  
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
    three_months_ahead_num = int(now.month) + 2
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


"""
Llamada a las funciones para generar los pronosticos para el boletín de volunclima. 
Antes de poder ejecutarlas hay que generar los datasets con generar.py
"""


#chile
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
#
#bolivia
generarPrediccionMensualTemperatura('/var/py/volunclima/salidas/datasets/temperatura.nc',"BO",[-69.8, -57.375, -23, -9.625])
generarPrediccionEstacionalTemperatura('/var/py/volunclima/salidas/datasets/temperatura.nc',"BO",[-69.8, -57.375, -23, -9.625])
generarPrediccionMensualPrecipitacion('/var/py/volunclima/salidas/datasets/precipitacion.nc',"BO",[-69.8, -57.375, -23, -9.625])
generarPrediccionEstacionalPrecipitacion('/var/py/volunclima/salidas/datasets/precipitacion.nc',"BO",[-69.8, -57.375, -23, -9.625]) 

#galapagos
generarPrediccionMensualTemperatura('/var/py/volunclima/salidas/datasets/temperatura.nc',"GA",[-92, -89, -1.5, 1])
generarPrediccionEstacionalTemperatura('/var/py/volunclima/salidas/datasets/temperatura.nc',"GA",[-92, -89, -1.5, 1])
generarPrediccionEstacionalPrecipitacion('/var/py/volunclima/salidas/datasets/precipitacion.nc',"GA",[-92, -89, -1.5, 1])
generarPrediccionMensualPrecipitacion('/var/py/volunclima/salidas/datasets/precipitacion.nc',"GA",[-92, -89, -1.5, 1])


"""
Llamada a las funciones para generar los pronosticos para el boletín de sequias. 
Antes de poder ejecutarlas hay que generar los datasets con generar.py
"""
#generarPrediccionEstacionalTemperatura(nombre_dataset,nombre_png)
""" generarPrediccionMensualTemperatura('/var/py/volunclima/salidas/datasets/temperatura.nc','sudam')
generarPrediccionMensualPrecipitacion('/var/py/volunclima/salidas/datasets/precipitacion.nc','sudam')
generarPrediccionEstacionalTemperatura('/var/py/volunclima/salidas/datasets/temperatura.nc','sudam')
generarPrediccionEstacionalPrecipitacion('/var/py/volunclima/salidas/datasets/precipitacion.nc','sudam')

generarPrediccionAnomaliaMensualTemperatura('/var/py/volunclima/salidas/datasets/temperatura_anomalia.nc','sudam')
generarPrediccionAnomaliaMensualPrecipitacion('/var/py/volunclima/salidas/datasets/precipitacion_anomalia.nc','sudam')
generarPrediccionAnomaliaEstacionalTemperatura('/var/py/volunclima/salidas/datasets/temperatura_anomalia.nc','sudam')
generarPrediccionAnomaliaEstacionalPrecipitacion('/var/py/volunclima/salidas/datasets/precipitacion_anomalia.nc','sudam') """
