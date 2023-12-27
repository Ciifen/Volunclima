import accesoDatosVolunclima as acc
import boletinVolunclima as bv
import plottingVolunclima as pv

import psycopg2
import pandas as pd
from dateutil.relativedelta import relativedelta
import smtplib
import mimetypes
from email.message import EmailMessage
from email.utils import make_msgid
from email.mime.text import MIMEText
from calendar import monthrange
import datetime as dt
import matplotlib.pyplot as plt
import math
from fpdf import FPDF
import os
import warnings
import traceback

'''
source /var/py/volunclima/env-volunclima/bin/activate
cd /var/py/volunclima/scripts/boletines/
python3.9

import VolunclimaBoletines as vb
vb.GenerarBoletinGeneralMensual("CO",2023,6)
vb.GenerarBoletinGeneralMensual("EC",2023,5)
vb.GenerarBoletinGeneralMensual("CL",2023,5)
vb.GenerarBoletinGeneralMensual("VE",2023,5)
quit()

import VolunclimaBoletines as vb
vb.EnviarBoletinesEstacionesMensual ("EC",2023,9)
vb.EnviarBoletinesEstacionesMensual ("VE",2023,5)
vb.EnviarBoletinesEstacionesMensual ("CL",2023,5)
quit()

import VolunclimaBoletines as vb
import datetime as dt
#datDate = dt.date.today()
datDate = dt.date(2023, 10, 28)
fltTrhld=90
vb.GenerarMapaPrecipitacionDiaria("EC",datDate,fltTrhld)

'''

def GenerarBoletinGeneralMensual (isoCty,yIni,mIni):
	warnings.filterwarnings('ignore')
	yEnd=yIni
	mEnd=mIni
	dIni=1
	dEnd = monthrange(int(yIni), int(mIni))[1]

	try:
		conn = psycopg2.connect(database="precdb", user="****", password="*************", host="*********", port="****")
	except Exception as err:
		print("Ocurrió un error intentando conectarse a la base de datos. Error: ", err)
		return
	
	#GENERANDO MAPA DE PRECIPITACION MENSUAL
	#Obteniendo estaciones con datos de precipitacion en el periodo consultado.
	dfStationsWPrec = acc.ObtenerEstacionesConDatosPrecipitacionMes(conn,isoCty,yIni,mIni,dIni,yEnd,mEnd,dEnd)
	if len(dfStationsWPrec.index)<1:
		print("No hay estaciones que hayan reportado precipitación en el periodo indicado.")

	#Obteniendo las estaciones activas con pluviometro del pais
	dfAllStations = acc.ObtenerEstacionesDePais(conn,isoCty,'P','A')
	pv.graficarPrecipitacionMensual(yIni,mIni,isoCty,dfAllStations,dfStationsWPrec)
	print("Se generó el mapa de precipitación del mes.")

	#GENERANDO MAPA DE PERCEPCION DE SEQUIA MENSUAL
	#Obteniendo estaciones con datos de precipitacion en el periodo consultado.
	dRepSequia = dt.date(yIni, mIni, 15) + relativedelta(months=1)#Se le suma un mes a la fecha de consulta porque cada mes se hace el reporte de sequia del mes anterior
	dfStationsWDrought = acc.ObtenerReportesSequiaMes(conn,isoCty,dRepSequia.year,dRepSequia.month)
	if len(dfStationsWDrought.index)<1:
		print("No hay estaciones que hayan enviado su encuesta de sequias para el mes indicado.")
	#se quitan los reportes provenientes de la misma estacion. Se mantiene el que fue enviado primero.
	dfStationsWDrought.sort_values(by=['id','fecha'], ascending=True, inplace=True)
	dfStationsWDrought.drop_duplicates(subset=['id'], inplace=True)
	#Obteniendo las estaciones activas del pais ya que todos pueden reportar sequias.
	dfAllStations = acc.ObtenerEstacionesDePais(conn,isoCty,' ','A')#dfAllStations = acc.ObtenerEstacionesActivasPluvioDePais(conn,isoCty)
	pv.graficarPercepcionSequiaMensual(yIni,mIni,isoCty,dfAllStations,dfStationsWDrought)
	print("Se generó el mapa de percepción de sequia del mes.")

	dfObs = acc.ObtenerObservadoresDeListaEstaciones(conn,dfStationsWPrec)
	if len(dfObs.index)<1:
		print("No hay observadores.")
	#Obteniendo reportes de eventos extremos
	dfRepExtremos = acc.ObtenerReportesExtremosMes(conn,isoCty,yIni,mIni,dIni,yEnd,mEnd,dEnd)
	conn.close()
	bv.generarBoletinGeneral(isoCty,dfObs,dfStationsWPrec,dfStationsWDrought,dfRepExtremos,yIni,mIni)



def EnviarBoletinesEstacionesMensual (isoCty,yIni,mIni):
	warnings.filterwarnings('ignore')
	yEnd=yIni
	mEnd=mIni
	dIni=1
	dEnd = monthrange(int(yIni), int(mIni))[1]

	try:
		conn = psycopg2.connect(database="precdb", user="****", password="*************", host="*********", port="****")
	except Exception as err:
		print("Ocurrió un error intentando conectarse a la base de datos. Error: ", err)
		return
	
	#GENERANDO MAPA DE PRECIPITACION MENSUAL
	#Obteniendo estaciones con datos de precipitacion en el periodo consultado.
	dfStationsWPrec = acc.ObtenerEstacionesConDatosPrecipitacionMes(conn,isoCty,yIni,mIni,dIni,yEnd,mEnd,dEnd)
	if len(dfStationsWPrec.index)<1:
		print("No hay estaciones que hayan reportado precipitación en el periodo indicado.")

	#Obteniendo las estaciones activas con pluviometro del pais
	dfAllStations = acc.ObtenerEstacionesDePais(conn,isoCty,'P','A')
	pv.graficarPrecipitacionMensual(yIni,mIni,isoCty,dfAllStations,dfStationsWPrec)
	print("Se generó el mapa de precipitación del mes.")

	#GENERANDO MAPA DE PERCEPCION DE SEQUIA MENSUAL
	#Obteniendo estaciones con datos de precipitacion en el periodo consultado.
	dRepSequia = dt.date(yIni, mIni, 15) + relativedelta(months=1)#Se le suma un mes a la fecha de consulta porque cada mes se hace el reporte de sequia del mes anterior
	dfStationsWDrought = acc.ObtenerReportesSequiaMes(conn,isoCty,dRepSequia.year,dRepSequia.month)
	if len(dfStationsWPrec.index)<1:
		print("No hay estaciones que hayan enviado su encuesta de sequias para el mes indicado.")
	#se quitan los reportes provenientes de la misma estacion. Se mantiene el que fue enviado primero.
	dfStationsWDrought.sort_values(by=['id','fecha'], ascending=True, inplace=True)
	dfStationsWDrought.drop_duplicates(subset=['id'], inplace=True)
	#Obteniendo las estaciones activas del pais ya que todos pueden reportar sequias.
	dfAllStations = acc.ObtenerEstacionesDePais(conn,isoCty,' ','A')
	pv.graficarPercepcionSequiaMensual(yIni,mIni,isoCty,dfAllStations,dfStationsWDrought)
	print("Se generó el mapa de percepción de sequia del mes.")

	#Obteniendo reportes de eventos extremos
	dfRepExtremos = acc.ObtenerReportesExtremosMes(conn,isoCty,yIni,mIni,dIni,yEnd,mEnd,dEnd)

	dfObs = acc.ObtenerObservadoresDeListaEstaciones(conn,dfStationsWPrec)
	if len(dfObs.index)<1:
		print("No hay observadores.")
		return
		
	strDatIni = str(yIni)+"/"+"{:02d}".format(mIni)+"/"+"{:02d}".format(dIni)
	strDatEnd = str(yEnd)+"/"+"{:02d}".format(mEnd)+"/"+"{:02d}".format(dEnd)
	for idxSt in range(len(dfStationsWPrec.index)):
		try:
			idSt = int(dfStationsWPrec.iloc[idxSt,0])
			strStName = dfStationsWPrec.iloc[idxSt,1]+"_" +dfStationsWPrec.iloc[idxSt,2]
			print("********* "+strStName+" ********")
			dfStObs = dfObs.loc[dfObs['idEstacion'] == idSt]
			if len(dfStObs.index)<1:
				print("No hay observador para la estación ")
				continue
			
			print(">OBSERVADORES")
			for idxObs in range(len(dfStObs.index)):
				strObservador = dfStObs.iloc[idxObs,1]+" "+dfStObs.iloc[idxObs,2]+" ("+dfStObs.iloc[idxObs,3]+")"
				print (strObservador)
			
			dfTotalVals = acc.ObtenerPrecipitacionDiariaDeEstacion(conn, idSt)#Se consultan todos los datos
			dfTotalVals['fecha'] = pd.to_datetime(dfTotalVals['fecha'], format='%Y-%m-%d')
			dfVals = dfTotalVals[(dfTotalVals['fecha'] >= strDatIni) & (dfTotalVals['fecha'] <= strDatEnd)]
			dfValAcums = acc.ObtenerPrecipitacionAcumuladaDeEstacion(conn, idSt, yIni, mIni, dIni, yEnd, mEnd, dEnd)
			bv.generarBoletinEstaciones(isoCty,dfObs,strStName,dfStationsWPrec,dfStationsWDrought,dfRepExtremos,dfStObs,dfTotalVals,dfVals,dfValAcums,yIni,mIni,dIni,yEnd,mEnd,dEnd)
		except:
			print(traceback.format_exc())
	conn.close()


def GenerarMapaPrecipitacionDiaria (isoCty,datDate,fltTrhld=90):
	warnings.filterwarnings('ignore')
	try:
		conn = psycopg2.connect(database="precdb", user="****", password="*************", host="*********", port="****")
	except Exception as err:
		print("Ocurrió un error intentando conectarse a la base de datos. Error: ", err)
		return

	dfPrecs = acc.ObtenerReportesPrecipitacionDiaria(conn,isoCty,datDate)
	dfAllStations = acc.ObtenerEstacionesDePais(conn,isoCty,'P','A')
	if len(dfPrecs.index)>0:
		dfPrecs['lat'] = dfPrecs.apply (lambda row: float(dfAllStations.loc[dfAllStations['id']==row.id]['lat'].values[0]), axis=1)
		dfPrecs['long'] = dfPrecs.apply (lambda row: float(dfAllStations.loc[dfAllStations['id']==row.id]['long'].values[0]), axis=1)

	pv.graficarPrecipitacionDiariaRed(datDate,isoCty,dfAllStations,dfPrecs,fltTrhld)
	print("Se generó el mapa de precipitación diaria.")

	dfPrecs['Ubicacion'] = dfPrecs["div1"]+"-"+dfPrecs["div2"]+"-"+dfPrecs["div3"]
	dfPrecs['Estacion'] = dfPrecs["nombre"]+" ("+dfPrecs["codigo"]+")"
	dfPrecs = dfPrecs[['Estacion', 'Ubicacion', 'lat', 'long', 'valor', 'comentario']]
	dfPrecs.to_csv("/var/py/volunclima/salidas/prec/tablas/"+isoCty+"/Volunclima-"+isoCty+'-PrecDD-'+str(datDate.year)+'_'+str(datDate.month)+'_'+"{:02d}".format(datDate.day)+'.csv', header=['Estación', 'Ubicación', 'Latitud', 'Longitud', 'Valor', 'Comentario'], index=False)
	print("Se generó la tabla de precipitación diaria.")