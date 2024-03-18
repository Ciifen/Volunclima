#links: https://matplotlib.org/3.1.0/gallery/misc/zorder_demo.html
import accesoDatosVolunclima as acc
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import pandas as pd
import numpy as np
import math
import matplotlib as mpl
import datetime as dt
from calendar import monthrange
import matplotlib.gridspec as gridspec
import os

def graficarPercepcionSequiaMensual(yyyy,mm,isoCty, dfStations, dfValues):
	"""
	Esta función genera un gráfico de percepción de sequía para un país en un mes y año específicos.
	Se proporciona información detallada sobre la ubicación geográfica de las estaciones meteorológicas
	y los valores de percepción de sequía correspondientes.

	Esta función grafica de forma especial a Colombia y Ecuador.

	Args:
		yyyy (int): El año para el cual se desea generar el gráfico de percepción de sequía.
		mm (int): El número de mes (1-12) para el cual se desea generar el gráfico de percepción de sequía.
		isoCty (str): El código ISO del país para el cual se generará el gráfico.
						Los códigos de los países son: EC (Ecuador), VE (Venezuela),
						CO (Colombia), CH (Chile), BO (Bolivia).
		dfStations (DataFrame): Un DataFrame que contiene la información de las estaciones meteorológicas.
		dfValues (DataFrame): Un DataFrame que contiene los valores de percepción de sequía para cada estación.

	Returns:
		None

	Raises:
		None
	"""
	#Quitar estaciones con datos del df de todas las estaciones para que se vea mejor el mapa (no superponer los marcadores)
	cond = dfStations['id'].isin(dfValues['id'])
	dfStations.drop(dfStations[cond].index, inplace = True)	

	#Determinando los rangos de valores
	lstIntervals = [-4,-3,-2,-1,1,2,3,4]#más húmedo...más seco.
	lsLngVals = dfValues.long.to_list()
	lsLatVals = dfValues.lat.to_list()
	lsTotVals = dfValues.total.to_list()
	strMonth = acc.obtenerAcronimoMes(int(mm))+"/"+str(int(yyyy))
	lstColors = ['#408ebf','#72c0da','#acddec','#5bbe9d','#fcce4f','#fd8c1c','#f1430e']
	""" if isoCty=='EC':
		plt.figure(figsize=(4.8,4.6), dpi=300)#Width, height in inches. 480px, 461px
		plt.suptitle('Percepción de sequía en Ecuador ('+strMonth+')')
		lon_leftup=-81
		lat_leftup=1.5
		lon_rightdown=-76.25
		lat_rightdown=-5
		map = Basemap(anchor='W', projection='merc',llcrnrlat=lat_rightdown,urcrnrlat=lat_leftup,llcrnrlon=lon_leftup,urcrnrlon=lon_rightdown,resolution='i')#lat_ts=7,resolution='i'
		map.drawparallels(np.arange(-5, 2, 1),labels=[True,False,False,False])
		map.drawmeridians(np.arange(-81,-74, 1),labels=[False,False,False,True])
		map.drawcoastlines(linewidth=1.2)
		map.drawstates(linewidth=0.5)
		map.drawcountries(linewidth=1.2) """
	if isoCty=='CL':
		plt.figure(figsize=(3.6, 4.8), dpi=300)#Width, height in inches. 480px, 461px
		plt.suptitle('Percepción de sequía en Chile \n('+strMonth+')')
		lon_leftup=-80.875
		lat_leftup=-17.625
		lon_rightdown=-63.375
		lat_rightdown=-56.875
		map = Basemap(anchor='W', projection='merc',llcrnrlat=lat_rightdown,urcrnrlat=lat_leftup,llcrnrlon=lon_leftup,urcrnrlon=lon_rightdown,resolution='i')#lat_ts=7,resolution='i'
		map.drawparallels(np.arange(-57, -18, 4),labels=[True,False,False,False])
		map.drawmeridians(np.arange(-82,-62, 6),labels=[False,False,False,True])
		map.drawcoastlines(linewidth=0.5)
		map.drawstates(linewidth=0.5)
		map.drawcountries(linewidth=1.2)
	elif isoCty=='VE':
		plt.figure(figsize=(6.8, 4.0), dpi=300)#Width, height in inches. 480px, 461px
		plt.suptitle('Percepción de sequía en Venezuela\n('+strMonth+')')
		lon_leftup=-73.375
		lat_leftup=12.125
		lon_rightdown=-58.125
		lat_rightdown=0.625
		map = Basemap(anchor='W', projection='merc',llcrnrlat=lat_rightdown,urcrnrlat=lat_leftup,llcrnrlon=lon_leftup,urcrnrlon=lon_rightdown,resolution='i')#lat_ts=7,resolution='i'
		map.drawparallels(np.arange(0, 13, 2),labels=[True,False,False,False])
		map.drawmeridians(np.arange(-74, -57, 3),labels=[False,False,False,True])
		map.readshapefile('map_shapes/Estados_Venezuela','map_shapes',drawbounds=1, color='black', default_encoding='iso-8859-15')
	elif isoCty=='BO':
		plt.figure(figsize=(5.6,3.2), dpi=300)#Width, height in inches. 480px, 461px
		plt.suptitle('Percepción de sequía en Bolivia (Tarija - '+strMonth+')')
		""" lon_leftup=-69.725
		lat_leftup=-9.625
		lon_rightdown=-57.375
		lat_rightdown=-22.975 """
		lon_leftup=-65.375
		lat_leftup=-20.725
		lon_rightdown=-62.175
		lat_rightdown=-23
		map = Basemap(anchor='W', projection='merc',llcrnrlat=lat_rightdown,urcrnrlat=lat_leftup,llcrnrlon=lon_leftup,urcrnrlon=lon_rightdown,resolution='i')#lat_ts=7,resolution='i'
		map.drawcoastlines(linewidth=1.2)
		map.drawstates(linewidth=0.5)
		map.drawcountries(linewidth=1.2)
		map.drawparallels(np.arange(-23, -20, 0.8),labels=[True,False,False,False])
		map.drawmeridians(np.arange(-65,-62, 1.1),labels=[False,False,False,True])
		""" map.drawparallels(np.arange(-23, -9, 2),labels=[True,False,False,False])
		map.drawmeridians(np.arange(-70,-56, 2),labels=[False,False,False,True]) """
	elif isoCty == 'CO':
		# Dividir el área de Colombia en tres secciones (debido a que los puntos estan concentrados en 3 diferentes secciones y el mapa es muy grande para apreciar los puntos sin hacer zoom)
		sections = 3
		lon_leftup_list = [-74.1,-76,-78]
		lon_rightdown_list = [-72.8,-74.5,-75.7]
		lat_rightdown_list = [7.5,4.8,0.9]
		lat_leftup_list = [11,5.8,3.4]
		fig = plt.figure(figsize=(5.1, 5.1), dpi=300)
		fig.suptitle('Percepción de sequía en Colombia ('+strMonth+')')
		for i in range(sections):
			
			if(i==0):
				ax = fig.add_subplot(2, 2, 1)
				ax.set_title('Cesar')
				ax.set_position([0.07, 0.25, 0.7, 0.6])  # [left, bottom, width, height]
			elif(i==1):
				ax = fig.add_subplot(2, 2, 2)
				ax.set_title('Caldas')
				ax.set_position([0.32,  0.6, 0.29, 0.3])  # [left, bottom, width, height]
			else:
				ax = fig.add_subplot(2, 2, 4)
				ax.set_title('Cauca')
				ax.set_position([0.32,  0.25, 0.29, 0.3])  # [left, bottom, width, height]

			lon_leftup = lon_leftup_list[i]
			lon_rightdown = lon_rightdown_list[i]
			lat_rightdown = lat_rightdown_list[i]
			lat_leftup = lat_leftup_list[i]

			map = Basemap(
				ax=ax, anchor='W', projection='merc',
				llcrnrlat=lat_rightdown, urcrnrlat=lat_leftup,
				llcrnrlon=lon_leftup, urcrnrlon=lon_rightdown,
				resolution='i'
			)

			#map.drawparallels(np.arange(lat_rightdown, lat_leftup + 1, 0.5), labels=[True, False, False, False], fontsize=7)
			#map.drawmeridians(np.arange(lon_leftup, lon_rightdown + 1, 0.5), labels=[False, False, False, True], fontsize=7)
			map.drawcoastlines(linewidth=0.5)
			map.drawstates(linewidth=0.5)
			map.drawcountries(linewidth=1.2)
			map.drawmapboundary(fill_color='#cce6ff')
			map.fillcontinents(color='#ffffff',lake_color='#cce6ff')
			lsLng = dfStations.long.to_list()
			lsLat = dfStations.lat.to_list()
			x, y = map(lsLng, lsLat)
			map.scatter(x, y, marker='.',color='#cccccc', s=10, zorder=3)#https://basemaptutorial.readthedocs.io/en/latest/plotting_data.html
			cCmap = (mpl.colors.ListedColormap(lstColors).with_extremes(under='#315481', over='#97221c'))#https://matplotlib.org/stable/tutorials/colors/colorbar_only.html#cCmap = (mpl.colors.ListedColormap(lstColors))
			cNorm = mpl.colors.BoundaryNorm(lstIntervals, cCmap.N)
			valX, valY = map(lsLngVals, lsLatVals)
			map.scatter(valX, valY, c=lsTotVals, marker='^', s=20, cmap=cCmap, norm=cNorm, zorder=10)
	elif isoCty == 'EC':
		# Se divide el gráfico en 2 subplots, una para ecuador y otra para galápagos
		sections = 2
		lon_leftup_list = [-81,-92]
		lon_rightdown_list = [-76.25,-89]
		lat_rightdown_list = [-5,-1.5]
		lat_leftup_list = [1.5,1]
		""" lon_leftup_list = [-92,-81]
		lon_rightdown_list = [-89,-76.25]
		lat_rightdown_list = [-1.5,-5]
		lat_leftup_list = [1,1.5] """
		fig = plt.figure(figsize=(5,5), dpi=300)
		fig.suptitle('Percepción de sequía en Ecuador ('+strMonth+')')
		for i in range(sections):
			
			if(i==0):
				ax = fig.add_subplot(2, 1, 1)
				ax.set_position([0.07, 0.2, 0.6, 0.7])  # [left, bottom, width, height]
			else:
				ax = fig.add_subplot(2, 1, 2)
				ax.set_position([0.65,  0.17, 0.29, 0.3])  # [left, bottom, width, height]


			lon_leftup = lon_leftup_list[i]
			lon_rightdown = lon_rightdown_list[i]
			lat_rightdown = lat_rightdown_list[i]
			lat_leftup = lat_leftup_list[i]

			map = Basemap(
				ax=ax, anchor='W', projection='merc',
				llcrnrlat=lat_rightdown, urcrnrlat=lat_leftup,
				llcrnrlon=lon_leftup, urcrnrlon=lon_rightdown,
				resolution='i'
			)
			if(i==0):
				map.drawparallels(np.arange(-5, 2, 1),labels=[True,False,False,False])
				map.drawmeridians(np.arange(-81,-74, 1),labels=[False,False,False,True])
			#map.drawparallels(np.arange(lat_rightdown, lat_leftup + 1, 0.5), labels=[True, False, False, False], fontsize=7)
			#map.drawmeridians(np.arange(lon_leftup, lon_rightdown + 1, 0.5), labels=[False, False, False, True], fontsize=7)
			map.drawcoastlines(linewidth=0.5)
			map.drawstates(linewidth=0.5)
			map.drawcountries(linewidth=1.2)
			map.drawmapboundary(fill_color='#cce6ff')
			map.fillcontinents(color='#ffffff',lake_color='#cce6ff')
			lsLng = dfStations.long.to_list()
			lsLat = dfStations.lat.to_list()
			x, y = map(lsLng, lsLat)
			map.scatter(x, y, marker='.',color='#cccccc', s=10, zorder=3)#https://basemaptutorial.readthedocs.io/en/latest/plotting_data.html
			cCmap = (mpl.colors.ListedColormap(lstColors).with_extremes(under='#315481', over='#97221c'))#https://matplotlib.org/stable/tutorials/colors/colorbar_only.html#cCmap = (mpl.colors.ListedColormap(lstColors))
			cNorm = mpl.colors.BoundaryNorm(lstIntervals, cCmap.N)
			valX, valY = map(lsLngVals, lsLatVals)
			map.scatter(valX, valY, c=lsTotVals, marker='^', s=20, cmap=cCmap, norm=cNorm, zorder=10)
	else:
		plt.figure(figsize=(4.8, 4.8), dpi=300)#Width, height in inches. 480px, 461px
		plt.suptitle('Percepción de sequía en XXXX ('+strMonth+')')
		lon_leftup=-81.125
		lat_leftup=1.375
		lon_rightdown=-75.125
		lat_rightdown=-5.125
		map = Basemap(anchor='W', projection='merc',llcrnrlat=lat_rightdown,urcrnrlat=lat_leftup,llcrnrlon=lon_leftup,urcrnrlon=lon_rightdown,resolution='i')#lat_ts=7,resolution='i'
		map.drawparallels(np.arange(-5, 2, 1),labels=[True,False,False,False])
		map.drawmeridians(np.arange(-81,-74, 1),labels=[False,False,False,True])

	if(isoCty == 'CO'):
		loc=(0.5,0.5)
		box_to_anchor=(1.2,0.85)
	elif(isoCty == 'EC'):
		loc=(0.5,0.5)
		box_to_anchor=(0,1.45)
	else:
		box_to_anchor=(1,1)
		loc="upper left"
		map.drawmapboundary(fill_color='#cce6ff')
		map.fillcontinents(color='#ffffff',lake_color='#cce6ff')
		lsLng = dfStations.long.to_list()
		lsLat = dfStations.lat.to_list()
		x, y = map(lsLng, lsLat)
		map.scatter(x, y, marker='.',color='#cccccc', s=10, zorder=3)#https://basemaptutorial.readthedocs.io/en/latest/plotting_data.html	
		cCmap = (mpl.colors.ListedColormap(lstColors).with_extremes(under='#315481', over='#97221c'))#https://matplotlib.org/stable/tutorials/colors/colorbar_only.html#cCmap = (mpl.colors.ListedColormap(lstColors))
		cNorm = mpl.colors.BoundaryNorm(lstIntervals, cCmap.N)	
		valX, valY = map(lsLngVals, lsLatVals)
		map.scatter(valX, valY, c=lsTotVals, marker='^', s=20, cmap=cCmap, norm=cNorm, zorder=10)

	lstIntervalsLbls = ['Humedad muy alta','Humedad alta','Humedad moderada','Humedad baja', 'Neutro o normal', 'Anormalmente seco', 'Sequía severa', 'Sequía extrema', 'Sequía excepcional','Sin datos']#En el cuador de equivalencia de procesamiento de respuestas del dr. Lobato, no se presenta la fase "Sequia moderada", pasa directo de "Anormalmente Seco" a "Sequía Severa"
	custom_lines = [
				mpl.lines.Line2D([0], [0], color='#315481', lw=5),
				mpl.lines.Line2D([0], [0], color=lstColors[0], lw=5),
				mpl.lines.Line2D([0], [0], color=lstColors[1], lw=5),
				mpl.lines.Line2D([0], [0], color=lstColors[2], lw=5),
				mpl.lines.Line2D([0], [0], color=lstColors[3], lw=5),
				mpl.lines.Line2D([0], [0], color=lstColors[4], lw=5),
				mpl.lines.Line2D([0], [0], color=lstColors[5], lw=5),
				mpl.lines.Line2D([0], [0], color=lstColors[6], lw=5),
				mpl.lines.Line2D([0], [0], color='#97221c', lw=5),
				mpl.lines.Line2D([0], [0], color='#cccccc', lw=5)]
	plt.legend(bbox_to_anchor=box_to_anchor, loc=loc,handles=custom_lines, labels=lstIntervalsLbls,title="   Intensidad de sequía   ",title_fontsize='small',fontsize='x-small')#https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.legend.html#matplotlib.axes.Axes.legend
	dirName="/var/py/volunclima/salidas/seq/"+isoCty
	if not os.path.exists(dirName):
		os.makedirs(dirName)
	plt.savefig(dirName+"/Volunclima-"+isoCty+'-SequiaMensual-'+str(yyyy)+'_'+str(mm)+'.png')# hay 480px width, 461px height
	plt.show()


def graficarPrecipitacionMensual(yyyy,mm,isoCty, dfStations, dfValues):
	"""
	La función grafica la precipitación mensual para el país especificado en el mes dado,
	utilizando la biblioteca Basemap de Matplotlib. Se crean diferentes marcadores y
	colores para representar la calidad de los datos de precipitación (excelente, media y mínima).
	La figura resultante se guarda como un archivo PNG y se muestra en pantalla.

	Esta función grafica de forma especial a Colombia y Ecuador.

	Parámetros:
	- yyyy (int): Año para el cual se desea graficar la precipitación.
	- mm (int): Mes para el cual se desea graficar la precipitación.
	- isoCty (str): El código ISO del país para el cual se generará el gráfico.
						Los códigos de los países son: EC (Ecuador), VE (Venezuela),
						CO (Colombia), CH (Chile), BO (Bolivia).
	- dfStations (DataFrame): DataFrame que contiene información de las estaciones meteorológicas.
	- dfValues (DataFrame): DataFrame que contiene los valores de precipitación para cada estación.

	Devuelve:
	- None
	"""
	#Le pongo coordenadas a las esaciones con datos
	numMonthDays = pd.DataFrame()
	indexMinMaxQC = pd.DataFrame()
	indexMinMidQC = pd.DataFrame()
	dfValuesGoodQC = pd.DataFrame()
	dfValuesMidQC = pd.DataFrame()
	dfValuesMinQC = pd.DataFrame()
	if len(dfValues.index)>0:########################
		dfValues['lat'] = dfValues.apply (lambda row: float(dfStations.loc[dfStations['id']==row.id]['lat'].values[0]), axis=1)
		dfValues['long'] = dfValues.apply (lambda row: float(dfStations.loc[dfStations['id']==row.id]['long'].values[0]), axis=1)
		#Quitar estaciones con datos del df de todas las estaciones para que se vea mejor el mapa (no superponer los marcadores)
		cond = dfStations['id'].isin(dfValues['id'])
		dfStations.drop(dfStations[cond].index, inplace = True)	

		numMonthDays = monthrange(yyyy, mm)[1]
		indexMinMaxQC = numMonthDays - int(round(numMonthDays*0.20,0))#usaré circulos para calidad excelente (mayor o igual a 24 días tomados, equivale al 20% de datos faltantes, que es considerado como buena calidad), 
		indexMinMidQC = numMonthDays - int(round(numMonthDays*0.50,0))#cuadraditos para calidad media (entre 15 y 24 dias monitoreados, o sea hasta 50% faltantes) 
		dfValuesGoodQC = dfValues.loc[dfValues.dias>=indexMinMaxQC]
		dfValuesMidQC = dfValues.loc[(dfValues.dias>=indexMinMidQC) & (dfValues.dias<indexMinMaxQC)]
		dfValuesMinQC = dfValues.loc[dfValues.dias<indexMinMidQC]

	strMonth = acc.obtenerAcronimoMes(int(mm))+"/"+str(int(yyyy))
	qcTitle = 'Días/mes monitoreados'
	qcLegend = '★ Más del 80%\n■ Entre 80% y 50%\n● Menos del 50%'
	""" if isoCty=='EC':
		plt.figure(figsize=(5,4.8), dpi=300)#plt.figure(figsize=(4.8, 4.6), dpi=300)#Width, height in inches. 480px, 461px
		plt.suptitle('Total de Precipitación mensual de Volunclima en Ecuador\n('+strMonth+')')
		lon_leftup=-81
		lat_leftup=1.5
		lon_rightdown=-76.25
		lat_rightdown=-5
		plt.text(0.69, 0.3, qcTitle, fontsize=8, transform=plt.gcf().transFigure)
		plt.text(0.69, 0.22, qcLegend, fontsize='x-small', transform=plt.gcf().transFigure)#x,y,text #5,4.8; width, height
		map = Basemap(anchor='W', projection='merc',llcrnrlat=lat_rightdown,urcrnrlat=lat_leftup,llcrnrlon=lon_leftup,urcrnrlon=lon_rightdown,resolution='i')#lat_ts=7,resolution='i'
		map.drawparallels(np.arange(-5, 2, 1),labels=[True,False,False,False])
		map.drawmeridians(np.arange(-81,-74, 1),labels=[False,False,False,True])
		map.drawcoastlines(linewidth=1.2)
		map.drawstates(linewidth=0.5)
		map.drawcountries(linewidth=1.2) """

	if isoCty=='CL':
		plt.figure(figsize=(3.6, 4.8), dpi=300)#Width, height in inches. 480px, 461px
		plt.suptitle('Total de precipitación mensual de\nVolunclima en Chile ('+strMonth+')')
		lon_leftup=-80.875
		lat_leftup=-17.625
		lon_rightdown=-63.375
		lat_rightdown=-56.875
		plt.text(0.51, 0.38, qcTitle, fontsize=8, transform=plt.gcf().transFigure)
		plt.text(0.51, 0.31, qcLegend, fontsize='x-small', transform=plt.gcf().transFigure)#x,y,text #5,4.8; width, height
		map = Basemap(anchor='W', projection='merc',llcrnrlat=lat_rightdown,urcrnrlat=lat_leftup,llcrnrlon=lon_leftup,urcrnrlon=lon_rightdown,resolution='i')#lat_ts=7,resolution='i'
		map.drawparallels(np.arange(-57, -18, 4),labels=[True,False,False,False])
		map.drawmeridians(np.arange(-82,-62, 6),labels=[False,False,False,True])
		map.drawcoastlines(linewidth=0.5)
		map.drawstates(linewidth=0.5)
		map.drawcountries(linewidth=1.2)

	elif isoCty=='VE':
		plt.figure(figsize=(6.8, 4.0), dpi=300)#Width, height in inches. 480px, 461px
		plt.suptitle('Total de precipitación mensual de\nVolunclima en Venezuela ('+strMonth+')')
		lon_leftup=-73.375
		lat_leftup=12.125
		lon_rightdown=-58.125
		lat_rightdown=0.625
		plt.text(0.74, 0.3, qcTitle, fontsize=8, transform=plt.gcf().transFigure)
		plt.text(0.74, 0.22, qcLegend, fontsize='x-small', transform=plt.gcf().transFigure)
		map = Basemap(anchor='W', projection='merc',llcrnrlat=lat_rightdown,urcrnrlat=lat_leftup,llcrnrlon=lon_leftup,urcrnrlon=lon_rightdown,resolution='i')#lat_ts=7,resolution='i'
		map.drawparallels(np.arange(0, 13, 2),labels=[True,False,False,False])
		map.drawmeridians(np.arange(-74, -57, 3),labels=[False,False,False,True])
		map.readshapefile('map_shapes/Estados_Venezuela','map_shapes',drawbounds=1, color='black', default_encoding='iso-8859-15')
	elif isoCty=='BO':
		#plt.figure(figsize=(5.6,3.6), dpi=300)#Width, height in inches. 480px, 461px
		plt.figure(figsize=(5.6,3.2), dpi=300)#Width, height in inches. 480px, 461px
		plt.subplots_adjust(top=0.85)  # Ajusta los márgenes
		plt.suptitle('Total de precipitación mensual de Volunclima en Bolivia\n(Tarija - '+strMonth+')')
		""" lon_leftup=-69.625
		lat_leftup=-9.625
		lon_rightdown=-57.375
		lat_rightdown=-22.875 """
		lon_leftup=-65.375
		lat_leftup=-20.725
		lon_rightdown=-62.175
		lat_rightdown=-23
		plt.text(0.69, 0.14, qcTitle, fontsize=8, transform=plt.gcf().transFigure)
		plt.text(0.69, 0.04, qcLegend, fontsize='x-small', transform=plt.gcf().transFigure)#x,y,text #5,4.8; width, height
		map = Basemap(anchor='W', projection='merc',llcrnrlat=lat_rightdown,urcrnrlat=lat_leftup,llcrnrlon=lon_leftup,urcrnrlon=lon_rightdown,resolution='i')#lat_ts=7,resolution='i'
		map.drawcoastlines(linewidth=1.2)
		map.drawstates(linewidth=0.5)
		map.drawcountries(linewidth=1.2)
		map.drawparallels(np.arange(-23, -20, 0.8),labels=[True,False,False,False])
		map.drawmeridians(np.arange(-65,-62, 1.1),labels=[False,False,False,True])
		""" map.drawparallels(np.arange(-23, -9, 2),labels=[True,False,False,False])
		map.drawmeridians(np.arange(-70,-56, 2),labels=[False,False,False,True]) """
	elif isoCty == 'CO':
		# Dividir el área de Colombia en tres secciones (debido a que los puntos estan concentrados en 3 diferentes secciones y el mapa es muy grande para apreciar los puntos sin hacer zoom)
		sections = 3
		lon_leftup_list = [-74.1,-76,-78]
		lon_rightdown_list = [-72.8,-74.5,-75.7]
		lat_rightdown_list = [7.5,4.8,0.9]
		lat_leftup_list = [11,5.8,3.4]		
		fig = plt.figure(figsize=(5.1, 5.1), dpi=300)
		fig.suptitle('Total de precipitación mensual de Volunclima en Colombia\n('+strMonth+')')
		fig.text(0.65, 0.45, qcTitle, fontsize=8, transform=plt.gcf().transFigure)
		fig.text(0.65, 0.39, qcLegend, fontsize='x-small', transform=plt.gcf().transFigure)#x,y,text #5,4.8; width, height
		for i in range(sections):		
			if(i==0):
				ax = fig.add_subplot(2, 2, 1)
				ax.set_title('Cesar')
				ax.set_position([0.07, 0.25, 0.7, 0.6])  # [left, bottom, width, height]
			elif(i==1):
				ax = fig.add_subplot(2, 2, 2)
				ax.set_title('Caldas')
				ax.set_position([0.32,  0.6, 0.29, 0.3])  # [left, bottom, width, height]
			else:
				ax = fig.add_subplot(2, 2, 4)
				ax.set_title('Cauca')
				ax.set_position([0.32,  0.25, 0.29, 0.3])  # [left, bottom, width, height]

			lon_leftup = lon_leftup_list[i]
			lon_rightdown = lon_rightdown_list[i]
			lat_rightdown = lat_rightdown_list[i]
			lat_leftup = lat_leftup_list[i]

			map = Basemap(
				ax=ax, anchor='W', projection='merc',
				llcrnrlat=lat_rightdown, urcrnrlat=lat_leftup,
				llcrnrlon=lon_leftup, urcrnrlon=lon_rightdown,
				resolution='i'
			)

			#map.drawparallels(np.arange(lat_rightdown, lat_leftup + 1, 0.5), labels=[True, False, False, False], fontsize=7)
			#map.drawmeridians(np.arange(lon_leftup, lon_rightdown + 1, 0.5), labels=[False, False, False, True], fontsize=7)
			map.drawcoastlines(linewidth=0.5)
			map.drawstates(linewidth=0.5)
			map.drawcountries(linewidth=1.2)
			map.drawmapboundary(fill_color='#cce6ff')
			map.fillcontinents(color='#ffffff',lake_color='#cce6ff') 
			lsLngNoData = dfStations.long.to_list()
			lsLatNoData = dfStations.lat.to_list()
			noDataX, noDataY = map(lsLngNoData, lsLatNoData)
			map.scatter(noDataX, noDataY, marker='.',color='#cccccc', s=10, zorder=3)#https://basemaptutorial.readthedocs.io/en/latest/plotting_data.html
			lstIntervals = [1,50,100,150,200,250,300,350,400,450,500]
			#lstColors = ['#78483B', '#925B4C', '#A86B57', '#B69286','#C69F92',   '#71DC46','#6CD044','#64C040','#5EB23C','#57A438']#https://colorbrewer2.org/
			lstColors = ['#8fbef9','#1d7df2','#124a6d','#1b6a60','#569975','#8ec385','#c5be7a','#efb96e','#da8559','#cb5b4b']#https://colorbrewer2.org/
			#cCmap = (mpl.colors.ListedColormap(lstColors).with_extremes(under='#502C22', over='#4C8F31'))		#https://matplotlib.org/stable/tutorials/colors/colorbar_only.html
			cCmap = (mpl.colors.ListedColormap(lstColors).with_extremes(under='#000000', over='#9b0121'))		#https://matplotlib.org/stable/tutorials/colors/colorbar_only.html
			cNorm = mpl.colors.BoundaryNorm(lstIntervals, cCmap.N)
			cNorm = mpl.colors.BoundaryNorm(lstIntervals, cCmap.N)
			if len(dfValuesGoodQC.index)>0:#Good QC ########################
				lsLngGoodQC = dfValuesGoodQC.long.to_list()
				lsLatGoodQC = dfValuesGoodQC.lat.to_list()
				lsPrecGoodQC = dfValuesGoodQC.total.to_list()
				GoodQCX, GoodQCY = map(lsLngGoodQC, lsLatGoodQC)
				map.scatter(GoodQCX, GoodQCY, c=lsPrecGoodQC, marker='*', s=30, cmap=cCmap, norm=cNorm, zorder=10)#https://matplotlib.org/stable/api/markers_api.html

			if len(dfValuesMidQC.index)>0:
				lsLngMidQC = dfValuesMidQC.long.to_list()
				lsLatMidQC = dfValuesMidQC.lat.to_list()
				lsPrecMidQC = dfValuesMidQC.total.to_list()
				MidQCX, MidQCY = map(lsLngMidQC, lsLatMidQC)
				map.scatter(MidQCX, MidQCY, c=lsPrecMidQC, marker='s', s=10, cmap=cCmap, norm=cNorm, zorder=9)

			if len(dfValuesMinQC.index)>0:
				lsLngMinQC = dfValuesMinQC.long.to_list()
				lsLatMinQC = dfValuesMinQC.lat.to_list()
				lsPrecMinQC = dfValuesMinQC.total.to_list()
				MinQCX, MinQCY = map(lsLngMinQC, lsLatMinQC)
				map.scatter(MinQCX, MinQCY, c=lsPrecMinQC, marker='.', s=30, cmap=cCmap, norm=cNorm, zorder=8)
	elif isoCty == 'EC':
		# Se divide el gráfico en 2 subplots, una para ecuador y otra para galápagos
		sections = 2
		lon_leftup_list = [-81,-92]
		lon_rightdown_list = [-76.25,-89]
		lat_rightdown_list = [-5,-1.5]
		lat_leftup_list = [1.5,1]		
		fig = plt.figure(figsize=(5,5), dpi=300)
		fig.suptitle('Total de precipitación mensual de Volunclima en Ecuador\n('+strMonth+')')
		fig.text(0.65, 0.48, qcTitle, fontsize=8, transform=plt.gcf().transFigure)
		fig.text(0.65, 0.41, qcLegend, fontsize='x-small', transform=plt.gcf().transFigure)#x,y,text #5,4.8; width, height
		for i in range(sections):		
			if(i==0):
				ax = fig.add_subplot(2, 1, 1)
				ax.set_position([0.07, 0.16, 0.6, 0.73])  # [left, bottom, width, height]
			else:
				ax = fig.add_subplot(2, 1, 2)
				ax.set_position([0.65,  0.13, 0.29, 0.3])  # [left, bottom, width, height]

			lon_leftup = lon_leftup_list[i]
			lon_rightdown = lon_rightdown_list[i]
			lat_rightdown = lat_rightdown_list[i]
			lat_leftup = lat_leftup_list[i]

			map = Basemap(
				ax=ax, anchor='W', projection='merc',
				llcrnrlat=lat_rightdown, urcrnrlat=lat_leftup,
				llcrnrlon=lon_leftup, urcrnrlon=lon_rightdown,
				resolution='i'
			)
			if(i==0):
				map.drawparallels(np.arange(-5, 2, 1),labels=[True,False,False,False])
				map.drawmeridians(np.arange(-81,-74, 1),labels=[False,False,False,True])
			#map.drawparallels(np.arange(lat_rightdown, lat_leftup + 1, 0.5), labels=[True, False, False, False], fontsize=7)
			#map.drawmeridians(np.arange(lon_leftup, lon_rightdown + 1, 0.5), labels=[False, False, False, True], fontsize=7)
			map.drawcoastlines(linewidth=0.5)
			map.drawstates(linewidth=0.5)
			map.drawcountries(linewidth=1.2)
			map.drawmapboundary(fill_color='#cce6ff')
			map.fillcontinents(color='#ffffff',lake_color='#cce6ff')
			lsLngNoData = dfStations.long.to_list()
			lsLatNoData = dfStations.lat.to_list()
			noDataX, noDataY = map(lsLngNoData, lsLatNoData)
			map.scatter(noDataX, noDataY, marker='.',color='#cccccc', s=10, zorder=3)#https://basemaptutorial.readthedocs.io/en/latest/plotting_data.html
			lstIntervals = [1,50,100,150,200,250,300,350,400,450,500]
			#lstColors = ['#78483B', '#925B4C', '#A86B57', '#B69286','#C69F92',   '#71DC46','#6CD044','#64C040','#5EB23C','#57A438']#https://colorbrewer2.org/
			lstColors = ['#8fbef9','#1d7df2','#124a6d','#1b6a60','#569975','#8ec385','#c5be7a','#efb96e','#da8559','#cb5b4b']#https://colorbrewer2.org/
			#cCmap = (mpl.colors.ListedColormap(lstColors).with_extremes(under='#502C22', over='#4C8F31'))		#https://matplotlib.org/stable/tutorials/colors/colorbar_only.html
			cCmap = (mpl.colors.ListedColormap(lstColors).with_extremes(under='#000000', over='#9b0121'))		#https://matplotlib.org/stable/tutorials/colors/colorbar_only.html
			cNorm = mpl.colors.BoundaryNorm(lstIntervals, cCmap.N)
			if len(dfValuesGoodQC.index)>0:#Good QC ########################
				lsLngGoodQC = dfValuesGoodQC.long.to_list()
				lsLatGoodQC = dfValuesGoodQC.lat.to_list()
				lsPrecGoodQC = dfValuesGoodQC.total.to_list()
				GoodQCX, GoodQCY = map(lsLngGoodQC, lsLatGoodQC)
				map.scatter(GoodQCX, GoodQCY, c=lsPrecGoodQC, marker='*', s=30, cmap=cCmap, norm=cNorm, zorder=10)#https://matplotlib.org/stable/api/markers_api.html

			if len(dfValuesMidQC.index)>0:
				lsLngMidQC = dfValuesMidQC.long.to_list()
				lsLatMidQC = dfValuesMidQC.lat.to_list()
				lsPrecMidQC = dfValuesMidQC.total.to_list()
				MidQCX, MidQCY = map(lsLngMidQC, lsLatMidQC)
				map.scatter(MidQCX, MidQCY, c=lsPrecMidQC, marker='s', s=10, cmap=cCmap, norm=cNorm, zorder=9)

			if len(dfValuesMinQC.index)>0:
				lsLngMinQC = dfValuesMinQC.long.to_list()
				lsLatMinQC = dfValuesMinQC.lat.to_list()
				lsPrecMinQC = dfValuesMinQC.total.to_list()
				MinQCX, MinQCY = map(lsLngMinQC, lsLatMinQC)
				map.scatter(MinQCX, MinQCY, c=lsPrecMinQC, marker='.', s=30, cmap=cCmap, norm=cNorm, zorder=8)

	else:
		plt.figure(figsize=(4.8, 4.8), dpi=300)#Width, height in inches. 480px, 461px
		plt.suptitle('Total de precipitación mensual de Volunclima\n'+strMonth)
		lon_leftup=-81.125
		lat_leftup=1.375
		lon_rightdown=-75.125
		lat_rightdown=-5.125
		map = Basemap(anchor='W', projection='merc',llcrnrlat=lat_rightdown,urcrnrlat=lat_leftup,llcrnrlon=lon_leftup,urcrnrlon=lon_rightdown,resolution='i')#lat_ts=7,resolution='i'
		map.drawparallels(np.arange(-5, 2, 0.5),labels=[True,False,False,False], fontsize=1)
		map.drawmeridians(np.arange(-81,-74, 0.5),labels=[False,False,False,True], fontsize=1)

	if(isoCty == 'CO'):
		loc=(0.5,0.5)
		box_to_anchor=(0.65,0.5)
	elif(isoCty == 'EC'):
		loc=(0.5,0.5)
		box_to_anchor=(0,1.42)
	else:
		box_to_anchor=(1,1)
		loc="upper left"
		map.drawmapboundary(fill_color='#cce6ff')
		map.fillcontinents(color='#ffffff',lake_color='#cce6ff')
		lsLngNoData = dfStations.long.to_list()
		lsLatNoData = dfStations.lat.to_list()
		noDataX, noDataY = map(lsLngNoData, lsLatNoData)
		map.scatter(noDataX, noDataY, marker='.',color='#cccccc', s=10, zorder=3)#https://basemaptutorial.readthedocs.io/en/latest/plotting_data.html
		lstIntervals = [1,50,100,150,200,250,300,350,400,450,500]
		#lstColors = ['#78483B', '#925B4C', '#A86B57', '#B69286','#C69F92',   '#71DC46','#6CD044','#64C040','#5EB23C','#57A438']#https://colorbrewer2.org/
		lstColors = ['#8fbef9','#1d7df2','#124a6d','#1b6a60','#569975','#8ec385','#c5be7a','#efb96e','#da8559','#cb5b4b']#https://colorbrewer2.org/
		#cCmap = (mpl.colors.ListedColormap(lstColors).with_extremes(under='#502C22', over='#4C8F31'))		#https://matplotlib.org/stable/tutorials/colors/colorbar_only.html
		cCmap = (mpl.colors.ListedColormap(lstColors).with_extremes(under='#000000', over='#9b0121'))		#https://matplotlib.org/stable/tutorials/colors/colorbar_only.html
		cNorm = mpl.colors.BoundaryNorm(lstIntervals, cCmap.N)

		if len(dfValuesGoodQC.index)>0:#Good QC ########################
			lsLngGoodQC = dfValuesGoodQC.long.to_list()
			lsLatGoodQC = dfValuesGoodQC.lat.to_list()
			lsPrecGoodQC = dfValuesGoodQC.total.to_list()
			GoodQCX, GoodQCY = map(lsLngGoodQC, lsLatGoodQC)
			map.scatter(GoodQCX, GoodQCY, c=lsPrecGoodQC, marker='*', s=30, cmap=cCmap, norm=cNorm, zorder=10)#https://matplotlib.org/stable/api/markers_api.html

		if len(dfValuesMidQC.index)>0:
			lsLngMidQC = dfValuesMidQC.long.to_list()
			lsLatMidQC = dfValuesMidQC.lat.to_list()
			lsPrecMidQC = dfValuesMidQC.total.to_list()
			MidQCX, MidQCY = map(lsLngMidQC, lsLatMidQC)
			map.scatter(MidQCX, MidQCY, c=lsPrecMidQC, marker='s', s=10, cmap=cCmap, norm=cNorm, zorder=9)

		if len(dfValuesMinQC.index)>0:
			lsLngMinQC = dfValuesMinQC.long.to_list()
			lsLatMinQC = dfValuesMinQC.lat.to_list()
			lsPrecMinQC = dfValuesMinQC.total.to_list()
			MinQCX, MinQCY = map(lsLngMinQC, lsLatMinQC)
			map.scatter(MinQCX, MinQCY, c=lsPrecMinQC, marker='.', s=30, cmap=cCmap, norm=cNorm, zorder=8)

	lstIntervalsLbls = [
		'Mayor a ' + str(lstIntervals[10]), 
		str(lstIntervals[9]) + ' - ' + str(lstIntervals[10]), 
		str(lstIntervals[8]) + ' - ' + str(lstIntervals[9]), 
		str(lstIntervals[7]) + ' - ' + str(lstIntervals[8]),
		str(lstIntervals[6]) + ' - ' + str(lstIntervals[7]),
		str(lstIntervals[5]) + ' - ' + str(lstIntervals[6]),
		str(lstIntervals[4]) + ' - ' + str(lstIntervals[5]),
		str(lstIntervals[3]) + ' - ' + str(lstIntervals[4]),
		str(lstIntervals[2]) + ' - ' + str(lstIntervals[3]),
		str(lstIntervals[1]) + ' - ' + str(lstIntervals[2]),
		str(lstIntervals[0]) + ' - ' + str(lstIntervals[1]),
		'Menor a ' + str(lstIntervals[0]),
		'Sin datos'
		]

	#custom_lines = [mpl.lines.Line2D([0], [0], color='#4C8F31', lw=4),
	custom_lines = [mpl.lines.Line2D([0], [0], color='#9b0121', lw=4),
			mpl.lines.Line2D([0], [0], color=lstColors[9], lw=4),
			mpl.lines.Line2D([0], [0], color=lstColors[8], lw=4),
			mpl.lines.Line2D([0], [0], color=lstColors[7], lw=4),
			mpl.lines.Line2D([0], [0], color=lstColors[6], lw=4),
			mpl.lines.Line2D([0], [0], color=lstColors[5], lw=4),
			mpl.lines.Line2D([0], [0], color=lstColors[4], lw=4),
			mpl.lines.Line2D([0], [0], color=lstColors[3], lw=4),
			mpl.lines.Line2D([0], [0], color=lstColors[2], lw=4),
			mpl.lines.Line2D([0], [0], color=lstColors[1], lw=4),
			mpl.lines.Line2D([0], [0], color=lstColors[0], lw=4),
			#mpl.lines.Line2D([0], [0], color='#502C22', lw=4),
			mpl.lines.Line2D([0], [0], color='#000000', lw=4),
			mpl.lines.Line2D([0], [0], color='#cccccc', lw=4)]

	if(isoCty == 'CO'):
		fig.legend(bbox_to_anchor=box_to_anchor, loc=loc,handles=custom_lines, labels=lstIntervalsLbls,title="Precipitación (mm/mes)",title_fontsize='small',fontsize='x-small')#https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.legend.html#matplotlib.axes.Axes.legend
	else:
		plt.legend(bbox_to_anchor=box_to_anchor, loc=loc,handles=custom_lines, labels=lstIntervalsLbls,title="Precipitación (mm/mes)",title_fontsize='small',fontsize='x-small')#https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.legend.html#matplotlib.axes.Axes.legend

	dirName="/var/py/volunclima/salidas/prec/mapas/"+isoCty
	if not os.path.exists(dirName):
		os.makedirs(dirName)
	plt.savefig(dirName+"/Volunclima-"+isoCty+'-PrecMensual-'+str(yyyy)+'_'+str(mm)+'.png')# hay 480px width, 461px height
	plt.show()

def graficarPrecipitacionDiariaRed(datDate,isoCty,dfStations,dfValues,fltTrhld):
	"""
	Esta función genera mapas que muestran informes de precipitación diaria para varias regiones,
	incluyendo Ecuador, Chile, Venezuela, Bolivia y Colombia. Los mapas visualizan los datos de
	precipitación para la fecha especificada, mostrando la ubicación de las estaciones, los valores
	extremos de precipitación y una leyenda codificada por colores que representa diferentes niveles
	de precipitación.

	La configuración del mapa, la representación de datos, la creación de la leyenda y el guardado/
	visualización del mapa se manejan dentro de la función. Esta función depende de bibliotecas como
	matplotlib, numpy y Basemap para la representación del mapa y la visualización de datos.

	Parámetros:
	- datDate (datetime): Fecha para la cual se están trazando los datos de precipitación.
	- isoCty (str): Código ISO del país. Códigos de los países (EC=Ecuador, VE=Venezuela, CO=Colombia, CH=Chile, BO=Bolivia).
	- dfStations (DataFrame): DataFrame que contiene información sobre las estaciones meteorológicas.
	- dfValues (DataFrame): DataFrame que contiene los valores de precipitación para cada estación.
	- fltTrhld (float): Valor umbral para la precipitación extrema.

	Retorna:
	None
	"""
	strDat = "{:02d}".format(datDate.day)+"/"+acc.obtenerAcronimoMes(int(datDate.month))+"/"+str(datDate.year)
	if len(dfValues.index)>0:
		# dfValues['lat'] = dfValues.apply (lambda row: float(dfStations.loc[dfStations['id']==row.id]['lat'].values[0]), axis=1)
		# dfValues['long'] = dfValues.apply (lambda row: float(dfStations.loc[dfStations['id']==row.id]['long'].values[0]), axis=1)
		#Quitar estaciones con datos del df de todas las estaciones para que se vea mejor el mapa (no superponer los marcadores)
		cond = dfStations['id'].isin(dfValues['id'])
		dfStations.drop(dfStations[cond].index, inplace = True)

	if isoCty=='EC':
		plt.figure(figsize=(5,4.6), dpi=300)#plt.figure(figsize=(4.8, 4.6), dpi=300)#Width, height in inches. 480px, 461px
		plt.suptitle('Reportes de precipitación diaria de Volunclima Ecuador\n('+"{:02d}".format(datDate.day)+"/"+acc.obtenerAcronimoMes(int(datDate.month))+"/"+str(datDate.year)+')')
		lon_leftup=-81
		lat_leftup=1.5
		lon_rightdown=-76.25
		lat_rightdown=-5
		map = Basemap(anchor='W', projection='merc',llcrnrlat=lat_rightdown,urcrnrlat=lat_leftup,llcrnrlon=lon_leftup,urcrnrlon=lon_rightdown,resolution='i')#lat_ts=7,resolution='i'
		map.drawparallels(np.arange(-5, 2, 1),linewidth=0,dashes=(None,None),labels=[True,False,False,False])
		map.drawmeridians(np.arange(-81,-74, 1),linewidth=0,dashes=(None,None),labels=[False,False,False,True])
		map.drawcoastlines(linewidth=1.2)
		map.drawstates(linewidth=0.5)
		map.drawcountries(linewidth=1.2)
	elif isoCty=='CL':
		plt.figure(figsize=(3.6, 4.7), dpi=300)#Width, height in inches. 480px, 461px
		plt.suptitle('Reportes de precipitación diaria de\nVolunclima Chile ('+"{:02d}".format(datDate.day)+"/"+acc.obtenerAcronimoMes(int(datDate.month))+"/"+str(datDate.year)+')')
		lon_leftup=-80.875
		lat_leftup=-17.625
		lon_rightdown=-63.375
		lat_rightdown=-56.875
		map = Basemap(anchor='W', projection='merc',llcrnrlat=lat_rightdown,urcrnrlat=lat_leftup,llcrnrlon=lon_leftup,urcrnrlon=lon_rightdown,resolution='i')#lat_ts=7,resolution='i'
		map.drawparallels(np.arange(-57, -18, 4),linewidth=0,dashes=(None,None),labels=[True,False,False,False])
		map.drawmeridians(np.arange(-82,-62, 6),linewidth=0,dashes=(None,None),labels=[False,False,False,True])
		map.drawcoastlines(linewidth=0.5)
		map.drawstates(linewidth=0.5)
		map.drawcountries(linewidth=1.2)
	elif isoCty=='VE':
		strCty = "Venezuela"
		plt.figure(figsize=(6.6, 4.0), dpi=300)#Width, height in inches. 480px, 461px
		plt.suptitle('Reportes de precipitación diaria de Volunclima Venezuela\n('+"{:02d}".format(datDate.day)+"/"+acc.obtenerAcronimoMes(int(datDate.month))+"/"+str(datDate.year)+')')
		lon_leftup=-73.375
		lat_leftup=12.125
		lon_rightdown=-58.125
		lat_rightdown=0.625
		map = Basemap(anchor='W', projection='merc',llcrnrlat=lat_rightdown,urcrnrlat=lat_leftup,llcrnrlon=lon_leftup,urcrnrlon=lon_rightdown,resolution='i')#lat_ts=7,resolution='i'
		map.drawparallels(np.arange(0, 13, 2),linewidth=0,dashes=(None,None),labels=[True,False,False,False])
		map.drawmeridians(np.arange(-74, -57, 3),linewidth=0,dashes=(None,None),labels=[False,False,False,True])
		map.readshapefile('map_shapes/Estados_Venezuela','map_shapes',drawbounds=1, color='black', default_encoding='iso-8859-15')
	elif isoCty=='BO':
		strCty = "Bolivia"
		plt.figure(figsize=(4.8,3.6), dpi=300)#Width, height in inches. 480px, 461px
		plt.suptitle('Reportes de precipitación diaria de Volunclima Bolivia\n('+"{:02d}".format(datDate.day)+"/"+acc.obtenerAcronimoMes(int(datDate.month))+"/"+str(datDate.year)+')')
		lon_leftup=-69.625
		lat_leftup=-9.625
		lon_rightdown=-57.375
		lat_rightdown=-22.875
		map = Basemap(anchor='W', projection='merc',llcrnrlat=lat_rightdown,urcrnrlat=lat_leftup,llcrnrlon=lon_leftup,urcrnrlon=lon_rightdown,resolution='i')#lat_ts=7,resolution='i'
		map.drawparallels(np.arange(-23, -9, 2),linewidth=0,dashes=(None,None),labels=[True,False,False,False])
		map.drawmeridians(np.arange(-70,-56, 2),linewidth=0,dashes=(None,None),labels=[False,False,False,True])
		map.drawcoastlines(linewidth=0.5)
		map.drawstates(linewidth=0.5)
		map.drawcountries(linewidth=1.2)
	elif isoCty=='CO':
		strCty = "Colombia"
		plt.figure(figsize=(5.1, 6.4), dpi=300)#Width, height in inches. 480px, 461px
		lon_leftup=-78 
		lat_leftup=12 
		lon_rightdown=-72
		lat_rightdown=2 
		map = Basemap(anchor='W', projection='merc',llcrnrlat=lat_rightdown,urcrnrlat=lat_leftup,llcrnrlon=lon_leftup,urcrnrlon=lon_rightdown, resolution='i')#lat_ts=7,resolution='i'
		map.drawparallels(np.arange(1 , 13 , 2),linewidth=0,dashes=(None,None),labels=[True,False,False,False])
		map.drawmeridians(np.arange(-79 ,-71, 2),linewidth=0,dashes=(None,None),labels=[False,False,False,True])
		map.drawcoastlines(linewidth=0.5)
		map.drawstates(linewidth=0.5)
		map.drawcountries(linewidth=1.2)
		plt.suptitle('Reportes de precipitación diaria de Volunclima Colombia\n('+"{:02d}".format(datDate.day)+"/"+acc.obtenerAcronimoMes(int(datDate.month))+"/"+str(datDate.year)+')')

	else:
		strCty = "XXX"
		plt.figure(figsize=(4.8, 4.8), dpi=300)#Width, height in inches. 480px, 461px
		lon_leftup=-81.125
		lat_leftup=1.375
		lon_rightdown=-75.125
		lat_rightdown=-5.125
		map = Basemap(anchor='W', projection='merc',llcrnrlat=lat_rightdown,urcrnrlat=lat_leftup,llcrnrlon=lon_leftup,urcrnrlon=lon_rightdown,resolution='i')#lat_ts=7,resolution='i'
		map.drawparallels(np.arange(-5, 2, 1),linewidth=0,dashes=(None,None),labels=[True,False,False,False])
		map.drawmeridians(np.arange(-81,-74, 1),linewidth=0,dashes=(None,None),labels=[False,False,False,True])

	map.drawmapboundary(fill_color='#cce6ff')
	map.fillcontinents(color='#ffffff',lake_color='#cce6ff')

	lsLngNoData = dfStations.long.to_list()
	lsLatNoData = dfStations.lat.to_list()
	noDataX, noDataY = map(lsLngNoData, lsLatNoData)
	map.scatter(noDataX, noDataY, marker='.',color='#cccccc', s=10, zorder=3)#https://basemaptutorial.readthedocs.io/en/latest/plotting_data.html

	lstIntervals = [0, 1,5,20,50,70,fltTrhld]
	lstColors = ['#000000','#8fbef9','#1d7df2','#124a6d','#1b6a60','#c5be7a','#da8559']
	cCmap = (mpl.colors.ListedColormap(lstColors).with_extremes(under='#000000', over='#9b0121'))		#https://matplotlib.org/stable/tutorials/colors/colorbar_only.html
	cNorm = mpl.colors.BoundaryNorm(lstIntervals, cCmap.N)
	
	dfValuesExtremes = dfValues.loc[dfValues.valor>=fltTrhld]
	if len(dfValuesExtremes.index)>0:
		lsLngExtremes = dfValuesExtremes.long.to_list()
		lsLatExtremes = dfValuesExtremes.lat.to_list()
		lsPrecExtremes = dfValuesExtremes.valor.to_list()
		ExtremesX, ExtremesY = map(lsLngExtremes, lsLatExtremes)
		map.scatter(ExtremesX, ExtremesY, c=lsPrecExtremes, marker='^', s=30, cmap=cCmap, norm=cNorm, zorder=10)#https://matplotlib.org/stable/api/markers_api.html

	for index, row in dfValuesExtremes.iterrows():
		x, y = map(row['long']+0.01, row['lat']+0.01)
		plt.text(x, y, row['valor'],fontsize=6,fontweight='bold',ha='left',va='bottom',color='#9b0121')

	dfValuesGood = dfValues.loc[dfValues.valor<fltTrhld]
	if len(dfValuesGood.index)>0:
		lsLngGood = dfValuesGood.long.to_list()
		lsLatGood = dfValuesGood.lat.to_list()
		lsPrecGood = dfValuesGood.valor.to_list()
		GoodX, GoodY = map(lsLngGood, lsLatGood)
		map.scatter(GoodX, GoodY, c=lsPrecGood, marker='s', s=15, cmap=cCmap, norm=cNorm, zorder=9)

	lstIntervalsLbls = [
		'Mayor a ' + str(lstIntervals[6]), 
		str(lstIntervals[5]) + ' - ' + str(lstIntervals[6]),
		str(lstIntervals[4]) + ' - ' + str(lstIntervals[5]),
		str(lstIntervals[3]) + ' - ' + str(lstIntervals[4]),
		str(lstIntervals[2]) + ' - ' + str(lstIntervals[3]),
		str(lstIntervals[1]) + ' - ' + str(lstIntervals[2]),
		str(lstIntervals[0]) + ' - ' + str(lstIntervals[1]),
		str(lstIntervals[0]),
		'Sin datos'
		]

	custom_lines = [mpl.lines.Line2D([0], [0], color='#9b0121', lw=4),
			mpl.lines.Line2D([0], [0], color=lstColors[6], lw=4),
			mpl.lines.Line2D([0], [0], color=lstColors[5], lw=4),
			mpl.lines.Line2D([0], [0], color=lstColors[4], lw=4),
			mpl.lines.Line2D([0], [0], color=lstColors[3], lw=4),
			mpl.lines.Line2D([0], [0], color=lstColors[2], lw=4),
			mpl.lines.Line2D([0], [0], color=lstColors[1], lw=4),
			mpl.lines.Line2D([0], [0], color=lstColors[0], lw=4),
			mpl.lines.Line2D([0], [0], color='#cccccc', lw=4)]

	plt.legend(bbox_to_anchor=(1,1), loc="upper left",handles=custom_lines, labels=lstIntervalsLbls,title="Precipitación (mm/día)",title_fontsize='small',fontsize='x-small')#https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.legend.html#matplotlib.axes.Axes.legend

	dirName="/var/py/volunclima/salidas/prec/mapas/"+isoCty
	if not os.path.exists(dirName):
		os.makedirs(dirName)

	plt.savefig(dirName+"/Volunclima-"+isoCty+'-PrecDD-'+str(datDate.year)+'_'+str(datDate.month)+'_'+"{:02d}".format(datDate.day)+'.png')
	plt.show()
