import accesoDatosVolunclima as acc
import boletinVolunclima as bv
import plottingVolunclima as pv
import openpyxl
import psycopg2
import pandas as pd
from dateutil.relativedelta import relativedelta
import smtplib
import mimetypes
from email.message import EmailMessage
from email.utils import make_msgid
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders
from calendar import monthrange
import datetime as dt
import matplotlib.pyplot as plt
import math
from fpdf import FPDF
import os
import warnings
import traceback
import base64
from pathlib import Path
from PIL import Image
import io
'''
source /var/py/volunclima/env-volunclima/bin/activate
cd /var/py/volunclima/scripts/boletines/
python3.9

import VolunclimaBoletines as vb
genera boletines pero no envia correo:
vb.GenerarBoletinGeneralMensual("CO",2023,9,True,False)
no genera boletines (usa el ya generado) y envia correo:
vb.GenerarBoletinGeneralMensual("EC",2023,10,True,False)
no genera boletines (usa el ya generado), envia correo y se agrega un nombre y correo para enviar ese boletin :
vb.GenerarBoletinGeneralMensual("CL",2023,5,False,True,[("nombre","correo@hotmail.com"), ("nombre2","correo2@hotmail.com"),etc..])
vb.GenerarBoletinGeneralMensual("VE",2023,5,False,True,[("nombre","correo@hotmail.com") ("nombre2","correo2@hotmail.com"),,etc..])
quit()

import VolunclimaBoletines as vb

genera boletines pero no envia correo:
vb.EnviarBoletinesEstacionesMensual ("VE",2023,5,True,False)
genera boletin de una estacion en concreto (por codigo de estacion) y no envia correo:
vb.EnviarBoletinesEstacionesMensual ("EC",2023,9,True,False,["EC00001"])
no genera boletines (usa el ya generado) y envia correos:
vb.EnviarBoletinesEstacionesMensual ("CL",2023,5,False,True)
no genera boletin (usa el ya generado) y envia correo de una estacion en concreto (por codigo de estacion):
vb.EnviarBoletinesEstacionesMensual ("EC",2023,9,True,False,["EC00001"[)

quit()

import VolunclimaBoletines as vb
import datetime as dt
#datDate = dt.date.today()
datDate = dt.date(2023, 10, 28)
fltTrhld=90
vb.GenerarMapaPrecipitacionDiaria("EC",datDate,fltTrhld)

'''
#datos de la cuenta de envio
MAIL_USER = "correo@gmail.com"
MAIL_PASSWORD = "*********"

#datos del servidor de email
MAIL_SERVER = "gmail"
MAIL_PORT = 465


#observadores externos (usuarios que no estan en el sistema de volunclima pero han solicitado boletines)
observadoresExternosEcuador= [("Observadorexterno1","Observadorexterno1@gmail.com"), ("Observadorexterno2","Observadorexterno2@gmail.com")]
observadoresExternosVenezuela= []
observadoresExternosColombia= []
observadoresExternosBolivia= []
observadoresExternosChile= []
#mails con excepciones los cuales pueden llegar a rebotar.
excepciones= ["mail1@gmail.com","mail2@gmail.com"]

#generarBoletin y enviarCorreo boolean para generar o enviar por correo los boletines. observadoresExternos es un argumento opcional
#que debe ser una lista de tuplas [(nombre,correo),etc..], para poner personas a las que enviar boletin que no son voluntarios
def GeneraryEnviarBoletinGeneralMensual (isoCty,yIni,mIni,generarBoletin, enviarCorreo):
	"""
	Genera y envía un boletín general mensual para un país dado.
	
	Args:
		isoCty (str): Códigos de los países (EC=Ecuador, VE=Venezuela, CO=Colombia, CH=Chile, BO=Bolivia).
		yIni (int): Año de la información contenida en el boletín.
		mIni (int): Mes de la información contenida en el boletín.
		generarBoletin (bool): Indica si se debe generar el boletín (True o False).
		enviarCorreo (bool): Indica si se debe enviar el boletín por correo electrónico (True o False).
	
	Returns:
		None
	
	Nota:
		Esta función genera un boletín general mensual para un país específico. 
		El boletín incluye información sobre precipitación, percepción de sequía y eventos extremos.
		Si 'generarBoletin' es True, se generará el boletín. Si 'enviarCorreo' es True, 
		se enviará el boletín por correo electrónico a los observadores correspondientes. Esto es para generar
		primero y poder revisar posibles errores en los boletines.
		observadoresExternos y excepciones son listas definidas previamente que se usan en esta funcion
	
	Raises:
		None
	"""
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
	if(isoCty=="EC"):
		observadoresExternos=observadoresExternosEcuador
	elif(isoCty=="VE"):
		observadoresExternos=observadoresExternosVenezuela
	elif(isoCty=="CO"):
		observadoresExternos=observadoresExternosColombia
	elif(isoCty=="BO"):
		observadoresExternos=observadoresExternosBolivia
	elif(isoCty=="CL"):
		observadoresExternos=observadoresExternosChile
	#generación de coreos
	if(generarBoletin == True):
		#GENERANDO MAPA DE PRECIPITACION MENSUAL
		#Obteniendo estaciones con datos de precipitacion en el periodo consultado.
		dfStationsWPrec = acc.ObtenerEstacionesConDatosPrecipitacionMes(conn,isoCty,yIni,mIni,dIni,yEnd,mEnd,dEnd)
		if len(dfStationsWPrec.index)<1:
			print("No hay estaciones que hayan reportado precipitación en el periodo indicado.")
			return
		#Obteniendo las estaciones activas con pluviometro del pais y graficar si aún no estan generadas
		
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

		#Obteniendo las estaciones activas del pais (ya que todos pueden reportar sequias) y graficar percepción de sequias si aún no estan generadas
		dfAllStations = acc.ObtenerEstacionesDePais(conn,isoCty,' ','A')#dfAllStations = acc.ObtenerEstacionesActivasPluvioDePais(conn,isoCty)
		pv.graficarPercepcionSequiaMensual(yIni,mIni,isoCty,dfAllStations,dfStationsWDrought)
		print("Se generó el mapa de percepción de sequia del mes.")
		dfObs = acc.ObtenerObservadoresDeListaEstaciones(conn,dfStationsWPrec)
		if len(dfObs.index)<1:
			print("No hay observadores.")
			return
		#Obteniendo reportes de eventos extremos. 
		dfRepExtremos = acc.ObtenerReportesExtremosMes(conn,isoCty,yIni,mIni,dIni,yEnd,mEnd,dEnd)
		ruta_archivo=bv.generarBoletinGeneral(isoCty,dfObs,dfStationsWPrec,dfStationsWDrought,dfRepExtremos,yIni,mIni)
	#envío de correos
	if(enviarCorreo == True):
		print("Se empleará el boletín generado para enviar el correo.")
		dfAllStations = acc.ObtenerEstacionesDePais(conn,isoCty,' ','A')#dfAllStations = acc.ObtenerEstacionesActivasPluvioDePais(conn,isoCty)
		dfObs = acc.ObtenerObservadoresDeListaEstaciones(conn,dfAllStations)
		if len(dfObs.index)<1:
			print("No hay observadores a los que enviar correo.")
			conn.close()
			return
		strCountry=acc.obtenerNombrePais(isoCty)
		strMonth = acc.obtenerNombreMes(int(mIni))+" "+str(int(yIni))
		dirName = "/var/py/volunclima/salidas/boletines/"+isoCty+"/"+str(yIni)
		nombre_pdf = dirName + "/Volunclima-" + strCountry + "_" + str(strMonth) + ".pdf"
		if os.path.exists(nombre_pdf):
			server=email_login()
			observadoresUnicos=[]
			for idxObs in range(len(dfObs.index)):
				nombre= dfObs.iloc[idxObs,1]+ " " + dfObs.iloc[idxObs,2]
				correo = dfObs.iloc[idxObs,3]	
				observador = (nombre, correo)
				if observador not in observadoresUnicos and correo not in excepciones:
					observadoresUnicos.append(observador)
					#AQUI SE DEBEN ENVIAR LOS CORREOS A TODOS LOS OBSERVADORES
					enviar_boletines(correo, nombre, nombre_pdf, mIni, yIni, strCountry, dfObs, server)	

			for i in range(len(observadoresExternos)):
				nombre= observadoresExternos[i][0]
				correo = observadoresExternos[i][1]
				#AQUI SE ENVIAN LOS CORREOS A LOS VOLUNTARIOS QUE NO SON OBSERVADORES PERO IGUAL USAN EL BOLETIN, ES UNA LISTA DE TUPLAS [(nombre,correo)]
				#lo estoy usando como prueba introduciendo nombres y correos
				enviar_boletines(correo, nombre, nombre_pdf, mIni, yIni, strCountry, dfObs, server)
			
			server.quit()

		else:
			print("Boletín no encontrado, no se envía correo")

	conn.close()

#generarBoletin y enviarCorreo boolean para generar o enviar por correo los boletines. 
#codigoEstacion es un argumento opcional para poder generar el boletin o enviar correos a una estación específica
def GeneraryEnviarBoletinesEstacionesMensual (isoCty,yIni,mIni,generarBoletin, enviarCorreo, codigoEstacion=[]):
	"""
	Genera y envía boletines mensuales para las estaciones meteorológicas de un país.
	
	Args:
		isoCty (str): Códigos de los países (EC=Ecuador, VE=Venezuela, CO=Colombia, CH=Chile, BO=Bolivia).
		yIni (int): Año de la información contenida en el boletín.
		mIni (int): Mes de la información contenida en el boletín.
		generarBoletin (bool): Indica si se debe generar el boletín (True o False).
		enviarCorreo (bool): Indica si se debe enviar el boletín por correo electrónico (True o False).
		codigoEstacion (list, opcional): Lista de códigos de estación para generar boletines específicos (por defecto es una lista vacía).
		excepciones es una lista previamente definida que se usa en esta función
	Returns:
		None
	
	Nota:
		Esta función genera y envía boletines mensuales para las estaciones meteorológicas de un país específico.
		Si 'generarBoletin' es True, se generará el boletín para todas las estaciones.
		Si 'enviarCorreo' es True, se enviará el boletín por correo electrónico a los observadores correspondientes.
		
	Raises:
		None
	"""
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
	if(generarBoletin == True):
		#GENERANDO MAPA DE PRECIPITACION MENSUAL
		#Obteniendo estaciones con datos de precipitacion en el periodo consultado.
		dfStationsWPrec = acc.ObtenerEstacionesConDatosPrecipitacionMes(conn,isoCty,yIni,mIni,dIni,yEnd,mEnd,dEnd)
		if len(dfStationsWPrec.index)<1:
			print("No hay estaciones que hayan reportado precipitación en el periodo indicado.")
			return
		#Obteniendo las estaciones activas con pluviometro del pais.
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
		if len(codigoEstacion) != 0:
			generarEspecifico = True
		else:
			generarEspecifico = False
		for idxSt in range(len(dfStationsWPrec.index)):
			try:			
				if (generarEspecifico == True and dfStationsWPrec.iloc[idxSt,1] not in codigoEstacion):
					continue
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
				ruta_archivo=bv.generarBoletinEstaciones(isoCty,dfObs,strStName,dfStationsWPrec,dfStationsWDrought,dfRepExtremos,dfStObs,dfTotalVals,dfVals,dfValAcums,yIni,mIni,dIni,yEnd,mEnd,dEnd)
				if(generarEspecifico == True and dfStationsWPrec.iloc[idxSt,1] in codigoEstacion):
					if(len(codigoEstacion)==0):
						break
					else:
						codigoEstacion.remove(dfStationsWPrec.iloc[idxSt,1])
			except:
				print(traceback.format_exc())

	if (enviarCorreo == True):
		dfStationsWPrec = acc.ObtenerEstacionesConDatosPrecipitacionMes(conn,isoCty,yIni,mIni,dIni,yEnd,mEnd,dEnd)
		if len(dfStationsWPrec.index)<1:
			print("No hay estaciones que hayan reportado precipitación en el periodo indicado.")
			return
		dfObs = acc.ObtenerObservadoresDeListaEstaciones(conn,dfStationsWPrec) 
		if len(dfObs.index)<1:
			print("No hay observadores.")
			return
			
		strDatIni = str(yIni)+"/"+"{:02d}".format(mIni)+"/"+"{:02d}".format(dIni)
		strDatEnd = str(yEnd)+"/"+"{:02d}".format(mEnd)+"/"+"{:02d}".format(dEnd)
		if len(codigoEstacion) != 0:
			generarEspecifico = True
		else:
			generarEspecifico = False
		server = email_login()
		for idxSt in range(len(dfStationsWPrec.index)):
			try:			
				if (generarEspecifico == True and dfStationsWPrec.iloc[idxSt,1] not in codigoEstacion):
					continue
				idSt = int(dfStationsWPrec.iloc[idxSt,0])
				strStName = dfStationsWPrec.iloc[idxSt,1]+"_" +dfStationsWPrec.iloc[idxSt,2]
				print("********* "+strStName+" ********")
				dfStObs = dfObs.loc[dfObs['idEstacion'] == idSt]
				strMonth = acc.obtenerNombreMes(int(mIni))+" "+str(int(yIni))
				dirName = "/var/py/volunclima/salidas/boletines/"+isoCty+"/"+str(yIni)
				ruta_archivo = dirName + "/" + strStName + "_" + str(strMonth) + ".pdf"

				if len(dfStObs.index)<1:
					print("No hay observador para la estación ")
					continue	
				if os.path.exists(ruta_archivo):
					for idxObs in range(len(dfStObs.index)):
						strObservador = dfStObs.iloc[idxObs,1]+" "+dfStObs.iloc[idxObs,2]+" ("+dfStObs.iloc[idxObs,3]+")"
						nombre = dfStObs.iloc[idxObs,1]+" "+dfStObs.iloc[idxObs,2]
						correo = dfStObs.iloc[idxObs,3]
						print (strObservador)
						#AQUI SE ENVIA EL CORREO A LAS ESTACIONES, DE MOMENTO SOLO SE EJECUTA CON LA OPCION DE ENVIAR CORREO UNA ESTACION EN CONCRETO COMO PRUEBA
						#hay que sustituir correo y nombre por los datos de strObservador
						if correo not in excepciones:
							enviar_boletines_por_estacion(correo,nombre,dfStationsWPrec.iloc[idxSt,1],dfStationsWPrec.iloc[idxSt,2],ruta_archivo,mIni,yIni,isoCty, server)
				else:
					print("Boletín no encontrado, no se envía correo")
	
				if(generarEspecifico == True and dfStationsWPrec.iloc[idxSt,1] in codigoEstacion):
					if(len(codigoEstacion)==0):
						break
					else:
						codigoEstacion.remove(dfStationsWPrec.iloc[idxSt,1])
			except:
				print(traceback.format_exc())
		server.quit()	
	conn.close()


def GenerarMapaPrecipitacionDiaria (isoCty,datDate,fltTrhld=90):
	"""
	Genera un mapa de precipitación diaria para un país en una fecha específica.
	
	Args:
		isoCty (str): Códigos de los países (EC=Ecuador, VE=Venezuela, CO=Colombia, CH=Chile, BO=Bolivia).
		datDate (datetime.date): Fecha para la que se generará el mapa de precipitación diaria.
		fltTrhld (float, opcional): Umbral de precipitación (por defecto es 90).
	
	Returns:
		None
	
	Nota:
		Esta función genera un mapa de precipitación diaria para un país en una fecha específica.
		Utiliza los datos de precipitación diaria de la base de datos para generar el mapa y lo guarda en un archivo.
		Además, genera una tabla de datos de precipitación diaria y la guarda en un archivo CSV.
	
	Raises:
		None
	"""
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

#función de enviar correos para una estacion
def enviar_boletines_por_estacion(MAIL_RECIEVER, nombre_observador, codigo, estacion, archivo, mIni, yIni, isoCty, server ):
	"""
	Envía un boletín mensual por correo electrónico a un observador de una estación meteorológica.
	
	Args:
		MAIL_RECIEVER (str): Dirección de correo electrónico del receptor.
		nombre_observador (str): Nombre del observador.
		codigo (str): Código de la estación.
		estacion (str): Nombre de la estación.
		archivo (str): Ruta del archivo del boletín.
		mIni (int): Mes inicial del período.
		yIni (int): Año inicial del período.
		isoCty (str): Códigos de los países (EC=Ecuador, VE=Venezuela, CO=Colombia, CH=Chile, BO=Bolivia).
		server (smtplib.SMTP): Objeto de conexión SMTP.
	
	Returns:
		None
	
	Nota:
		Esta función envía un boletín mensual por correo electrónico a un observador de una estación meteorológica.
		El boletín incluye información climática del mes para la estación específica.
	
	Raises:
	None
	"""
	mes = formato_mes(mIni).lower()
	strCountry=acc.obtenerNombrePais(isoCty)
	#mensaje del email
	msg=MIMEMultipart('mixed')
	msg["Subject"]=" Boletín mensual de la estación " + codigo +" de la red volunclima "+ strCountry + " - " + mes + " " + str(yIni) 
	msg["From"]=MAIL_USER
	files=[archivo]

	with open("/var/py/volunclima/scripts/boletines/logo_CIIFEN.png", "rb") as img:
		image_data = img.read()

	# HTML
	html_content = """
	<p class="MsoNormal" style="font-size: 12pt; margin: 0cm 0cm 0.0001pt; font-family: 'times new roman' , serif; color: #222222;"><b><span style="font-family: 'calibri' , sans-serif; color: #17365d;">Volunclima</span></b><b><i><span style="font-size: 9pt; font-family: 'calibri' , sans-serif; color: #1f497d;"><br /></span></i></b></p>
	<p class="MsoNormal" style="font-size: 12pt; margin: 0cm 0cm 0.0001pt; font-family: 'times new roman' , serif; color: #222222;"><i><span style="font-size: 9pt; font-family: 'calibri' , sans-serif; color: black;">Centro Internacional para la Investigaci&oacute;n</span></i><span style="font-size: 11pt; font-family: 'calibri' , sans-serif; color: black;"><u></u><u></u></span></p>
	<p class="MsoNormal" style="font-size: 12pt; margin: 0cm 0cm 0.0001pt; font-family: 'times new roman' , serif; color: #222222;"><i><span style="font-size: 9pt; font-family: 'calibri' , sans-serif; color: black;">del Fen&oacute;meno de El Ni&ntilde;o- CIIFEN</span></i><span style="font-size: 11pt; font-family: 'calibri' , sans-serif; color: black;"><u></u><u></u></span></p>
	<p class="MsoNormal" style="font-size: 12pt; margin: 0cm 0cm 0.0001pt; font-family: 'times new roman' , serif; color: #222222;"><i><span style="font-size: 9pt; font-family: 'calibri' , sans-serif; color: black;">Direcci&oacute;n: Puerto Santa Ana, Ciudad del r&iacute;o. Edificio The Point, Of. 1904.</span></i></p>
	<p class="MsoNormal" style="font-size: 12pt; margin: 0cm 0cm 0.0001pt; font-family: 'times new roman' , serif; color: #222222;"><i><span lang="PT" style="font-size: 9pt; font-family: 'calibri' , sans-serif; color: black;">Guayaquil - Ecuador</span></i><span style="font-size: 11pt; font-family: 'calibri' , sans-serif; color: black;"><u></u><u></u></span><span style="font-size: 10pt; font-family: 'calibri' , sans-serif; color: #000000;"><strong></strong></span></p>
	<div><em><span style="font-size: 10pt; font-family: 'calibri' , sans-serif;">Web site:&nbsp;<span class="Object" id="OBJ_PREFIX_DWT629_com_zimbra_url" style="color: #005a95;"><span class="Object" id="OBJ_PREFIX_DWT592_com_zimbra_url"><a href="https://ciifen.org/" rel="noopener nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer" style="color: #000000;" target="_blank">ciifen.org</a></span></span>&nbsp;&nbsp;<span class="Object" id="OBJ_PREFIX_DWT630_com_zimbra_url" style="color: #005a95;"><span class="Object" id="OBJ_PREFIX_DWT593_com_zimbra_url"><a href="https://crc-osa.ciifen.org/" rel="noopener nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer" style="color: #000000;" target="_blank">crc-osa.ciifen.org</a></span></span>&nbsp;&nbsp;</span></em></div>
	<div><span style="font-size: 10pt; font-family: 'calibri' , sans-serif;"><strong><span style="color: #333399;"><span style="color: #0000ff;"><span class="Object" id="OBJ_PREFIX_DWT631_com_zimbra_url" style="color: #005a95;"><span class="Object" id="OBJ_PREFIX_DWT594_com_zimbra_url"><a href="https://www.facebook.com/CIIFEN/" rel="noopener nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer" style="color: #0000ff;" target="_blank">Facebook</a></span></span></span>&nbsp;|&nbsp;<span style="color: #0000ff;"><span class="Object" id="OBJ_PREFIX_DWT632_com_zimbra_url" style="color: #005a95;"><span class="Object" id="OBJ_PREFIX_DWT595_com_zimbra_url"><a href="https://x.com/ciifen" rel="noopener nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer" style="color: #0000ff;" target="_blank">X</a></span></span></span>&nbsp;|&nbsp;<span style="color: #0000ff;"><span class="Object" id="OBJ_PREFIX_DWT633_com_zimbra_url" style="color: #005a95;"><span class="Object" id="OBJ_PREFIX_DWT596_com_zimbra_url"><a href="https://www.youtube.com/user/CIIFEN" rel="noopener nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer" style="color: #0000ff;" target="_blank">YouTube</a></span></span></span>&nbsp;|&nbsp;<span style="color: #0000ff;"><span class="Object" id="OBJ_PREFIX_DWT634_com_zimbra_url" style="color: #005a95;"><span class="Object" id="OBJ_PREFIX_DWT597_com_zimbra_url"><a href="https://www.instagram.com/ciifenorg/" rel="noopener nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer" style="color: #0000ff;" target="_blank">Instagram</a></span></span></span>&nbsp;|&nbsp;<span style="color: #0000ff;"><span class="Object" id="OBJ_PREFIX_DWT635_com_zimbra_url" style="color: #005a95;"><span class="Object" id="OBJ_PREFIX_DWT598_com_zimbra_url"><a href="https://www.linkedin.com/company/ciifen/" rel="noopener nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer" style="color: #0000ff;" target="_blank">Linkedin</a></span></span></span></span></strong></span></div>
	<p class="MsoNormal" style="font-size: 12pt; margin: 0cm 0cm 0.0001pt; font-family: 'times new roman' , serif; color: #222222;"><i><span style="font-size: 9pt; font-family: 'calibri' , sans-serif; color: black;"><img width="103" height="117" src="cid:ciifen_logo" /></span></i></p>
	""".format(base64.b64encode(image_data).decode('utf-8'))

	# Cuerpo del mensaje, sustituir nombre con el nombre de cada observador, todo lo que queda de codigo va dentro del for
	msg["To"]=MAIL_RECIEVER.strip()
	cuerpo_mensaje = ("Estimado/a " + nombre_observador.strip() + "," + 
	"<br><br>Esperamos que se encuentre bien. Adjunto encontrará el boletín mensual con la información climática del mes de "+ mes + " de " + str(yIni) +
	" en la estación "+ estacion + " (" + codigo + ")"
	""". Agradecemos su continua participación y esperamos que encuentre útil esta recopilación para sus actividades y análisis personales.

	<br><br>Saludos cordiales,<br><br>

	""")
	img_attachment = MIMEImage(image_data, name="ciifen_logo.png")
	img_attachment.add_header('Content-ID', '<ciifen_logo>')
	img_attachment.add_header('Content-Disposition', 'inline')  # Esto oculta el adjunto
	# Agregar el cuerpo del mensaje y el HTML al objeto mensaje
	msg.attach(img_attachment)
	msg.attach(MIMEText(cuerpo_mensaje+html_content, 'html'))
	#adjuntar boletin en formato pdf
	for path in files:
		part = MIMEBase('application', "octet-stream")
		with open(path, 'rb') as file:
			part.set_payload(file.read())
		encoders.encode_base64(part)
		original_file_name = Path(path).name
		part.add_header('Content-Disposition', f'attachment; filename="{original_file_name}"')
		msg.attach(part)
	#enviar el email
	try:
		server.send_message(msg)
		print("boletín enviado al observador "+ nombre_observador + "(" + MAIL_RECIEVER + ")" )
	except:
		print(f"An error occurred: {e}")


#funciona de enviar correos para todas las estaciones
def enviar_boletines(MAIL_RECIEVER, nombre_observador, archivo, mIni, yIni, strCountry, dfObs, server):
	"""
	Envía un boletín mensual por correo electrónico a un observador de la red Volunclima.
	
	Args:
		MAIL_RECIEVER (str): Dirección de correo electrónico del receptor.
		nombre_observador (str): Nombre del observador.
		archivo (str): Ruta del archivo del boletín.
		mIni (int): Mes inicial del período.
		yIni (int): Año inicial del período.
		strCountry (str): Nombre del país.
		dfObs (DataFrame): DataFrame de observaciones.
		server (smtplib.SMTP): Objeto de conexión SMTP.
	
	Returns:
		None
	
	Nota:
		Esta función envía un boletín mensual por correo electrónico a un observador de la red Volunclima.
		El boletín incluye información climática del mes para la red Volunclima en un país específico.
		Adjunta un archivo de boletín en formato PDF al correo electrónico.

	Raises:
	None
	"""
	mes = formato_mes(mIni).lower()

	#mensaje del email
	msg=MIMEMultipart('mixed')
	msg["Subject"]=" Boletín mensual de la red volunclima "+ strCountry + " - " + mes + " " + str(yIni) 
	msg["From"]=MAIL_USER.strip()
	files=[archivo]

	with open("/var/py/volunclima/scripts/boletines/logo_CIIFEN.png", "rb") as img:
		image_data = img.read()

	# HTML
	html_content = """
	<p class="MsoNormal" style="font-size: 12pt; margin: 0cm 0cm 0.0001pt; font-family: 'times new roman' , serif; color: #222222;"><b><span style="font-family: 'calibri' , sans-serif; color: #17365d;">Volunclima</span></b><b><i><span style="font-size: 9pt; font-family: 'calibri' , sans-serif; color: #1f497d;"><br /></span></i></b></p>
	<p class="MsoNormal" style="font-size: 12pt; margin: 0cm 0cm 0.0001pt; font-family: 'times new roman' , serif; color: #222222;"><i><span style="font-size: 9pt; font-family: 'calibri' , sans-serif; color: black;">Centro Internacional para la Investigaci&oacute;n</span></i><span style="font-size: 11pt; font-family: 'calibri' , sans-serif; color: black;"><u></u><u></u></span></p>
	<p class="MsoNormal" style="font-size: 12pt; margin: 0cm 0cm 0.0001pt; font-family: 'times new roman' , serif; color: #222222;"><i><span style="font-size: 9pt; font-family: 'calibri' , sans-serif; color: black;">del Fen&oacute;meno de El Ni&ntilde;o- CIIFEN</span></i><span style="font-size: 11pt; font-family: 'calibri' , sans-serif; color: black;"><u></u><u></u></span></p>
	<p class="MsoNormal" style="font-size: 12pt; margin: 0cm 0cm 0.0001pt; font-family: 'times new roman' , serif; color: #222222;"><i><span style="font-size: 9pt; font-family: 'calibri' , sans-serif; color: black;">Direcci&oacute;n: Puerto Santa Ana, Ciudad del r&iacute;o. Edificio The Point, Of. 1904.</span></i></p>
	<p class="MsoNormal" style="font-size: 12pt; margin: 0cm 0cm 0.0001pt; font-family: 'times new roman' , serif; color: #222222;"><i><span lang="PT" style="font-size: 9pt; font-family: 'calibri' , sans-serif; color: black;">Guayaquil - Ecuador</span></i><span style="font-size: 11pt; font-family: 'calibri' , sans-serif; color: black;"><u></u><u></u></span><span style="font-size: 10pt; font-family: 'calibri' , sans-serif; color: #000000;"><strong></strong></span></p>
	<div><em><span style="font-size: 10pt; font-family: 'calibri' , sans-serif;">Web site:&nbsp;<span class="Object" id="OBJ_PREFIX_DWT629_com_zimbra_url" style="color: #005a95;"><span class="Object" id="OBJ_PREFIX_DWT592_com_zimbra_url"><a href="https://ciifen.org/" rel="noopener nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer" style="color: #000000;" target="_blank">ciifen.org</a></span></span>&nbsp;&nbsp;<span class="Object" id="OBJ_PREFIX_DWT630_com_zimbra_url" style="color: #005a95;"><span class="Object" id="OBJ_PREFIX_DWT593_com_zimbra_url"><a href="https://crc-osa.ciifen.org/" rel="noopener nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer" style="color: #000000;" target="_blank">crc-osa.ciifen.org</a></span></span>&nbsp;&nbsp;</span></em></div>
	<div><span style="font-size: 10pt; font-family: 'calibri' , sans-serif;"><strong><span style="color: #333399;"><span style="color: #0000ff;"><span class="Object" id="OBJ_PREFIX_DWT631_com_zimbra_url" style="color: #005a95;"><span class="Object" id="OBJ_PREFIX_DWT594_com_zimbra_url"><a href="https://www.facebook.com/CIIFEN/" rel="noopener nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer" style="color: #0000ff;" target="_blank">Facebook</a></span></span></span>&nbsp;|&nbsp;<span style="color: #0000ff;"><span class="Object" id="OBJ_PREFIX_DWT632_com_zimbra_url" style="color: #005a95;"><span class="Object" id="OBJ_PREFIX_DWT595_com_zimbra_url"><a href="https://x.com/ciifen" rel="noopener nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer" style="color: #0000ff;" target="_blank">X</a></span></span></span>&nbsp;|&nbsp;<span style="color: #0000ff;"><span class="Object" id="OBJ_PREFIX_DWT633_com_zimbra_url" style="color: #005a95;"><span class="Object" id="OBJ_PREFIX_DWT596_com_zimbra_url"><a href="https://www.youtube.com/user/CIIFEN" rel="noopener nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer" style="color: #0000ff;" target="_blank">YouTube</a></span></span></span>&nbsp;|&nbsp;<span style="color: #0000ff;"><span class="Object" id="OBJ_PREFIX_DWT634_com_zimbra_url" style="color: #005a95;"><span class="Object" id="OBJ_PREFIX_DWT597_com_zimbra_url"><a href="https://www.instagram.com/ciifenorg/" rel="noopener nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer" style="color: #0000ff;" target="_blank">Instagram</a></span></span></span>&nbsp;|&nbsp;<span style="color: #0000ff;"><span class="Object" id="OBJ_PREFIX_DWT635_com_zimbra_url" style="color: #005a95;"><span class="Object" id="OBJ_PREFIX_DWT598_com_zimbra_url"><a href="https://www.linkedin.com/company/ciifen/" rel="noopener nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer" style="color: #0000ff;" target="_blank">Linkedin</a></span></span></span></span></strong></span></div>
	<p class="MsoNormal" style="font-size: 12pt; margin: 0cm 0cm 0.0001pt; font-family: 'times new roman' , serif; color: #222222;"><i><span style="font-size: 9pt; font-family: 'calibri' , sans-serif; color: black;"><img width="103" height="117" src="cid:ciifen_logo" /></span></i></p>
	""".format(base64.b64encode(image_data).decode('utf-8'))


	# Cuerpo del mensaje, sustituir nombre con el nombre de cada observador, todo lo que queda de codigo va dentro del for
	msg["To"]=MAIL_RECIEVER.strip() #correo dentro del for
	cuerpo_mensaje = ("""
	Estimado/a """ + 
	nombre_observador.strip() + "," + """
	<br><br>Esperamos que se encuentre bien. Adjunto encontrará el boletín mensual con la información climática del mes de """+ mes + " de " + str(yIni) + " en " +
	strCountry+
	""". Agradecemos su continua participación y esperamos que encuentre útil esta recopilación para sus actividades y análisis personales.
	
	<br><br>Saludos cordiales,<br><br>

	""")

	img_attachment = MIMEImage(image_data, name="ciifen_logo.png")
	img_attachment.add_header('Content-ID', '<ciifen_logo>')
	img_attachment.add_header('Content-Disposition', 'inline')  # Esto oculta el adjunto
	# Agregar el cuerpo del mensaje y el HTML al objeto mensaje
	msg.attach(img_attachment)
	msg.attach(MIMEText(cuerpo_mensaje+html_content, 'html'))
	#adjuntar boletin en formato pdf
	for path in files:
		part = MIMEBase('application', "octet-stream")
		with open(path, 'rb') as file:
			part.set_payload(file.read())
		encoders.encode_base64(part)
		original_file_name = Path(path).name
		part.add_header('Content-Disposition', f'attachment; filename="{original_file_name}"')
		msg.attach(part)
	#enviar el email
	try:
		server.send_message(msg)
		print("boletín enviado al observador "+ nombre_observador + "(" + MAIL_RECIEVER + ")" )
	except:
		print(f"An error occurred: {e}")

def email_login():
	try:
		server = smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT)
		server.login(MAIL_USER,MAIL_PASSWORD)
		return server
	except Exception as e:
		print(f"An error occurred: {e}")

def formato_mes(nombre_mes):

    months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre',
              'Noviembre', 'Diciembre']
    if str(nombre_mes).isnumeric(): #es num:
        return months[int(nombre_mes) - 1]
    else:#es str
        return months.index(nombre_mes.title())+1

#que debe ser una lista de tuplas [(nombre,correo),etc..], para poner personas a las que enviar boletin que no son voluntarios
def envio (isoCty,observadoresExternos=[]):
	"""
	Envía boletines mensuales por correo electrónico a observadores de la red Volunclima y a observadores externos.

	Args:
		isoCty (str): Códigos de los países (EC=Ecuador, VE=Venezuela, CO=Colombia, CH=Chile, BO=Bolivia).
		observadoresExternos (list, optional): Lista de tuplas con nombres y correos de observadores externos. 
			Defaults to [].

	Returns:
		None

	Nota:
		Esta función envía boletines mensuales por correo electrónico a observadores de la red Volunclima y a observadores externos.
		Utiliza la función `enviar_flyers` para enviar los boletines.

	Raises:
		None
	"""
	warnings.filterwarnings('ignore')

	try:
		conn = psycopg2.connect(database="precdb", user="****", password="*************", host="*********", port="****")
	except Exception as err:
		print("Ocurrió un error intentando conectarse a la base de datos. Error: ", err)
		return

	dfAllStations = acc.ObtenerEstacionesDePais(conn,isoCty,' ','A')#dfAllStations = acc.ObtenerEstacionesActivasPluvioDePais(conn,isoCty)
	dfObs = acc.ObtenerObservadoresDeListaEstaciones(conn,dfAllStations)
	if len(dfObs.index)<1:
		print("No hay observadores a los que enviar correo.")
		conn.close()
		return

	server=email_login()
	observadoresUnicos=[]
	for idxObs in range(len(dfObs.index)):
		nombre= dfObs.iloc[idxObs,1]+ " " + dfObs.iloc[idxObs,2]
		correo = dfObs.iloc[idxObs,3]	
		observador = (nombre, correo)
		if observador not in observadoresUnicos and correo not in excepciones:
			observadoresUnicos.append(observador)
			#AQUI SE DEBEN ENVIAR LOS CORREOS A TODOS LOS OBSERVADORES
			enviar_flyers(correo, nombre,server)	

	for i in range(len(observadoresExternos)):
		nombre= observadoresExternos[i][0]
		correo = observadoresExternos[i][1]
		#AQUI SE ENVIAN LOS CORREOS A LOS VOLUNTARIOS QUE NO SON OBSERVADORES PERO IGUAL USAN EL BOLETIN, ES UNA LISTA DE TUPLAS [(nombre,correo)]
		#lo estoy usando como prueba introduciendo nombres y correos
		enviar_flyers(correo, nombre,server)
	
	server.quit()
	conn.close()

def obtenerEstacionesSinReportarQuincena (isoCty,yIni,mIni):
	"""
	Obtiene las estaciones que no han reportado precipitaciones en la primera quincena del mes y envía un correo con el detalle.

	Args:
		isoCty (str): Códigos de los países (EC=Ecuador, VE=Venezuela, CO=Colombia, CH=Chile, BO=Bolivia).
		yIni (int): Año inicial del período.
		mIni (int): Mes inicial del período.

	Returns:
		None

	Nota:
		Esta función obtiene las estaciones que no han reportado precipitaciones en la primera quincena del mes especificado
		y envía un correo electrónico con el detalle a la dirección "observadores@ciifen.org".

	Raises:
		None
	"""
	warnings.filterwarnings('ignore')
	yEnd=yIni
	mEnd=mIni
	dIni=1
	dEnd = 15

	try:
		conn = psycopg2.connect(database="precdb", user="****", password="*************", host="*********", port="****")
	except Exception as err:
		print("Ocurrió un error intentando conectarse a la base de datos. Error: ", err)
		return
	#GENERANDO MAPA DE PRECIPITACION MENSUAL
	#Obteniendo estaciones con datos de precipitacion en el periodo consultado.
	#dfAllStations = acc.ObtenerEstacionesDePais(conn,isoCty,'P','A')
	dfStationsWPrec = acc.ObtenerEstacionesConDatosPrecipitacionMes2(conn,isoCty,yIni,mIni,dIni,yEnd,mEnd,dEnd)
	""" dfStationsWPrec['lat'] = dfStationsWPrec.apply (lambda row: float(dfAllStations.loc[dfAllStations['id']==row.id]['lat'].values[0]), axis=1)
	dfStationsWPrec['long'] = dfStationsWPrec.apply (lambda row: float(dfAllStations.loc[dfAllStations['id']==row.id]['long'].values[0]), axis=1) """
	pd.set_option('display.max_rows', None)
	pd.set_option('display.max_columns', None)
	df=dfStationsWPrec[dfStationsWPrec['dias'] < 11][['id', 'codigo', 'nombre', 'dias']]
	""" print(acc.ObtenerPrecipitacionDiariaDeEstacion(conn, "1", yIni, mIni, 1, yEnd, mEnd, 30))
	print(acc.ObtenerPrecipitacionAcumuladaDeEstacion(conn, "1", yIni, mIni, 1, yEnd, mEnd, 30)) """
	filas_como_string = df.apply(lambda row: f"ID: {row['id']}, Código: {row['codigo']}, Nombre: {row['nombre']}, Días: {row['dias']}", axis=1)
	# Supongamos que filas_como_string es tu Serie con las filas convertidas en cadenas
	filas_como_string = filas_como_string.astype(str)  # Asegurémonos de que todas las entradas sean de tipo str

	# Combina las cadenas con saltos de línea
	cadena_final = '<br>'.join(filas_como_string)
	print(cadena_final)
	strCountry=acc.obtenerNombrePais(isoCty)
	server=email_login()
	enviar_no_reportados("observadores@ciifen.org", strCountry, mIni, yIni, " hasta el día 15 ", cadena_final,  server)
	server.quit()
	conn.close()

def obtenerEstacionesSinReportarFinDeMes (isoCty,yIni,mIni):
	"""
	Obtiene las estaciones que no han reportado precipitaciones en la segunda quincena del mes y envía un correo con el detalle.

	Args:
		isoCty (str): Códigos de los países (EC=Ecuador, VE=Venezuela, CO=Colombia, CH=Chile, BO=Bolivia).
		yIni (int): Año inicial del período.
		mIni (int): Mes inicial del período.

	Returns:
		None

	Nota:
		Esta función obtiene las estaciones que no han reportado precipitaciones en la segunda quincena del mes especificado
		y envía un correo electrónico con el detalle a la dirección "observadores@ciifen.org".

	Raises:
		None
	"""
	warnings.filterwarnings('ignore')
	yEnd=yIni
	mEnd=mIni
	dIni=16
	dEnd = monthrange(int(yIni), int(mIni))[1]

	try:
		conn = psycopg2.connect(database="precdb", user="****", password="*************", host="*********", port="****")
	except Exception as err:
		print("Ocurrió un error intentando conectarse a la base de datos. Error: ", err)
		return
	#GENERANDO MAPA DE PRECIPITACION MENSUAL
	#Obteniendo estaciones con datos de precipitacion en el periodo consultado.
	dfStationsWPrec = acc.ObtenerEstacionesConDatosPrecipitacionMes2(conn,isoCty,yIni,mIni,dIni,yEnd,mEnd,dEnd)
	pd.set_option('display.max_rows', None)
	pd.set_option('display.max_columns', None)
	df=dfStationsWPrec[dfStationsWPrec['dias'] < 11][['id', 'codigo', 'nombre', 'dias']]
	filas_como_string = df.apply(lambda row: f"ID: {row['id']}, Código: {row['codigo']}, Nombre: {row['nombre']}, Días: {row['dias']}", axis=1)
	filas_como_string = filas_como_string.astype(str)  # Asegurémonos de que todas las entradas sean de tipo str

	# Combina las cadenas con saltos de línea
	cadena_final = '<br>'.join(filas_como_string)
	print(cadena_final)
	strCountry=acc.obtenerNombrePais(isoCty)
	server=email_login()
	enviar_no_reportados("observadores@ciifen.org", strCountry, mIni, yIni, " desde el día 16 en adelante ", cadena_final,  server)
	server.quit()
	conn.close()

def obtenerEstacionesSinReportarAnual (isoCty,yIni,mIni):
	"""
	Obtiene las estaciones que no han reportado precipitaciones en un año y envía un correo con el detalle.

	Args:
		isoCty (str): Códigos de los países (EC=Ecuador, VE=Venezuela, CO=Colombia, CH=Chile, BO=Bolivia).
		yIni (int): Año inicial del período.
		mIni (int): Mes inicial del período.

	Returns:
		None

	Nota:
		Esta función obtiene las estaciones que no han reportado precipitaciones en un año especificado
		y envía un correo electrónico con el detalle a la dirección "observadores@ciifen.org", aunque ahora 
		esta modificada para introducir periodos en vez de un año en la misma funcion y no enviar correo.

	Raises:
		None
	"""
	warnings.filterwarnings('ignore')
	#yEnd=yIni
	yIni=2023
	yEnd=2023
	mIni=1
	mEnd=12
	dIni=1
	dEnd = monthrange(int(yIni), int(mEnd))[1]

	try:
		conn = psycopg2.connect(database="precdb", user="****", password="*************", host="*********", port="****")
	except Exception as err:
		print("Ocurrió un error intentando conectarse a la base de datos. Error: ", err)
		return
	#GENERANDO MAPA DE PRECIPITACION MENSUAL
	#Obteniendo estaciones con datos de precipitacion en el periodo consultado.
	dfStationsWPrec = acc.ObtenerEstacionesConDatosPrecipitacionMes2(conn,isoCty,yIni,mIni,dIni,yEnd,mEnd,dEnd)
	
	pd.set_option('display.max_rows', None)
	pd.set_option('display.max_columns', None)
	#print(dfStationsWPrec)
	df=dfStationsWPrec[dfStationsWPrec['dias'] > 350][['id', 'codigo', 'nombre', 'dias']]
	print(df)
	filas_como_string = df.apply(lambda row: f"ID: {row['id']}, Código: {row['codigo']}, Nombre: {row['nombre']}, Días: {row['dias']}", axis=1)
	filas_como_string = filas_como_string.astype(str)  # Asegurémonos de que todas las entradas sean de tipo str

	# Combina las cadenas con saltos de línea
	cadena_final = '<br>'.join(filas_como_string)
	
	""" strCountry=acc.obtenerNombrePais(isoCty)
	server=email_login()
	enviar_no_reportados("observadores@ciifen.org", strCountry, mIni, yIni, "", cadena_final,  server, anual=False)
	server.quit() """
	conn.close()


def envio_correos_seguimiento(nombre_archivo):
	"""
	Envía correos electrónicos de seguimiento basados en los datos proporcionados en un archivo Excel.

	Args:
		nombre_archivo (str): Nombre del archivo Excel que contiene los datos de seguimiento.

	Returns:
		None

	Nota:
		Esta función carga los datos de un archivo Excel y envía correos electrónicos de seguimiento a los observadores
		de la red Volunclima basados en esos datos. Utiliza la función `enviar_correo_analisis` para enviar los correos.

	Raises:
		None
	"""
	# Lista para almacenar las tuplas de datos
	datos = []

	# Cargando el archivo xlsx
	wb = openpyxl.load_workbook(nombre_archivo)
	# Seleccionando la primera hoja del libro
	sheet = wb.active
	server=email_login()
	# Iterando sobre las filas del archivo xlsx
	for fila in sheet.iter_rows(min_row=3, max_col=12):
		# Comprobando si la primera columna no est� vac�a
		if fila[0].value:
			# Obteniendo los valores de la cuarta, sexta y onceava columna
			valor1 = fila[4].value if fila[4].value else ''
			valor2 = fila[6].value if fila[6].value else ''
			valor3 = fila[11].value if fila[11].value else ''
			# Creando la tupla y agreg�ndola a la lista de datos
			datos.append((valor1, valor2, valor3))

	for dato in datos:
		if dato[0]=="-SIN OBSERVADOR-":
			pass
		else:
			enviar_correo_analisis(dato[1], dato[0],dato[2], server)
			#enviar_correo_analisis("r.zevallos@ciifen.org", dato[0],dato[2], server)
			
	server.quit()

#funciona de enviar correos para todas las estaciones MAIL_RECIEVER, nombre_observador, archivo, mIni, yIni, strCountry, dfObs, server
def enviar_correo_analisis(MAIL_RECIEVER, nombre,codigo, server):
	"""
	Envía correos electrónicos de análisis basados en los datos proporcionados.

	Args:
		MAIL_RECIEVER (str): Dirección de correo electrónico del destinatario.
		nombre (str): Nombre del destinatario.
		codigo (int): Código que determina el tipo de mensaje a enviar.
		server (smtplib.SMTP): Objeto del servidor SMTP para enviar el correo.

	Returns:
		None

	Nota:
		Esta función envía correos electrónicos de análisis a los destinatarios basados en el código proporcionado.
		El código determina el tipo de mensaje a enviar.

	Raises:
		Exception: Se produce si hay algún error al enviar el correo electrónico.
	"""
	#mensaje del email
	msg=MIMEMultipart('mixed')
	msg["Subject"]="Seguimiento de datos climáticos en las estaciones de la red Voluncima"

	msg["From"]=MAIL_USER.strip()
	with open("/var/py/volunclima/scripts/boletines/logo_CIIFEN.png", "rb") as img:
		image_data = img.read()

	# HTML
	html_content = """
	<p class="MsoNormal" style="font-size: 12pt; margin: 0cm 0cm 0.0001pt; font-family: 'times new roman' , serif; color: #222222;"><b><span style="font-family: 'calibri' , sans-serif; color: #17365d;">Volunclima</span></b><b><i><span style="font-size: 9pt; font-family: 'calibri' , sans-serif; color: #1f497d;"><br /></span></i></b></p>
	<p class="MsoNormal" style="font-size: 12pt; margin: 0cm 0cm 0.0001pt; font-family: 'times new roman' , serif; color: #222222;"><i><span style="font-size: 9pt; font-family: 'calibri' , sans-serif; color: black;">Centro Internacional para la Investigaci&oacute;n</span></i><span style="font-size: 11pt; font-family: 'calibri' , sans-serif; color: black;"><u></u><u></u></span></p>
	<p class="MsoNormal" style="font-size: 12pt; margin: 0cm 0cm 0.0001pt; font-family: 'times new roman' , serif; color: #222222;"><i><span style="font-size: 9pt; font-family: 'calibri' , sans-serif; color: black;">del Fen&oacute;meno de El Ni&ntilde;o- CIIFEN</span></i><span style="font-size: 11pt; font-family: 'calibri' , sans-serif; color: black;"><u></u><u></u></span></p>
	<p class="MsoNormal" style="font-size: 12pt; margin: 0cm 0cm 0.0001pt; font-family: 'times new roman' , serif; color: #222222;"><i><span style="font-size: 9pt; font-family: 'calibri' , sans-serif; color: black;">Direcci&oacute;n: Puerto Santa Ana, Ciudad del r&iacute;o. Edificio The Point, Of. 1904.</span></i></p>
	<p class="MsoNormal" style="font-size: 12pt; margin: 0cm 0cm 0.0001pt; font-family: 'times new roman' , serif; color: #222222;"><i><span lang="PT" style="font-size: 9pt; font-family: 'calibri' , sans-serif; color: black;">Guayaquil - Ecuador</span></i><span style="font-size: 11pt; font-family: 'calibri' , sans-serif; color: black;"><u></u><u></u></span><span style="font-size: 10pt; font-family: 'calibri' , sans-serif; color: #000000;"><strong></strong></span></p>
	<div><em><span style="font-size: 10pt; font-family: 'calibri' , sans-serif;">Web site:&nbsp;<span class="Object" id="OBJ_PREFIX_DWT629_com_zimbra_url" style="color: #005a95;"><span class="Object" id="OBJ_PREFIX_DWT592_com_zimbra_url"><a href="https://ciifen.org/" rel="noopener nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer" style="color: #000000;" target="_blank">ciifen.org</a></span></span>&nbsp;&nbsp;<span class="Object" id="OBJ_PREFIX_DWT630_com_zimbra_url" style="color: #005a95;"><span class="Object" id="OBJ_PREFIX_DWT593_com_zimbra_url"><a href="https://crc-osa.ciifen.org/" rel="noopener nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer" style="color: #000000;" target="_blank">crc-osa.ciifen.org</a></span></span>&nbsp;&nbsp;</span></em></div>
	<div><span style="font-size: 10pt; font-family: 'calibri' , sans-serif;"><strong><span style="color: #333399;"><span style="color: #0000ff;"><span class="Object" id="OBJ_PREFIX_DWT631_com_zimbra_url" style="color: #005a95;"><span class="Object" id="OBJ_PREFIX_DWT594_com_zimbra_url"><a href="https://www.facebook.com/CIIFEN/" rel="noopener nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer" style="color: #0000ff;" target="_blank">Facebook</a></span></span></span>&nbsp;|&nbsp;<span style="color: #0000ff;"><span class="Object" id="OBJ_PREFIX_DWT632_com_zimbra_url" style="color: #005a95;"><span class="Object" id="OBJ_PREFIX_DWT595_com_zimbra_url"><a href="https://x.com/ciifen" rel="noopener nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer" style="color: #0000ff;" target="_blank">X</a></span></span></span>&nbsp;|&nbsp;<span style="color: #0000ff;"><span class="Object" id="OBJ_PREFIX_DWT633_com_zimbra_url" style="color: #005a95;"><span class="Object" id="OBJ_PREFIX_DWT596_com_zimbra_url"><a href="https://www.youtube.com/user/CIIFEN" rel="noopener nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer" style="color: #0000ff;" target="_blank">YouTube</a></span></span></span>&nbsp;|&nbsp;<span style="color: #0000ff;"><span class="Object" id="OBJ_PREFIX_DWT634_com_zimbra_url" style="color: #005a95;"><span class="Object" id="OBJ_PREFIX_DWT597_com_zimbra_url"><a href="https://www.instagram.com/ciifenorg/" rel="noopener nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer" style="color: #0000ff;" target="_blank">Instagram</a></span></span></span>&nbsp;|&nbsp;<span style="color: #0000ff;"><span class="Object" id="OBJ_PREFIX_DWT635_com_zimbra_url" style="color: #005a95;"><span class="Object" id="OBJ_PREFIX_DWT598_com_zimbra_url"><a href="https://www.linkedin.com/company/ciifen/" rel="noopener nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer" style="color: #0000ff;" target="_blank">Linkedin</a></span></span></span></span></strong></span></div>
	<p class="MsoNormal" style="font-size: 12pt; margin: 0cm 0cm 0.0001pt; font-family: 'times new roman' , serif; color: #222222;"><i><span style="font-size: 9pt; font-family: 'calibri' , sans-serif; color: black;"><img width="103" height="117" src="cid:ciifen_logo" /></span></i></p>
	""".format(base64.b64encode(image_data).decode('utf-8'))

	img_attachment = MIMEImage(image_data, name="ciifen_logo.png")
	img_attachment.add_header('Content-ID', '<ciifen_logo>')
	img_attachment.add_header('Content-Disposition', 'inline')  # Esto oculta el adjunto
	# Adjunta la imagen redimensionada al mensaje

	# Cuerpo del mensaje, sustituir nombre con el nombre de cada observador, todo lo que queda de codigo va dentro del for
	msg["To"]=MAIL_RECIEVER.strip() #correo dentro del for
	cuerpo_mensaje=""
	if codigo==1:
		cuerpo_mensaje = ("<br><br>Estimado/a "+nombre+",<br><br><br>Esperamos se encuentre bien, desde el CIIFEN le extendemos un caluroso saludo, le escribimos por un tema relacionado con la red de observadores climáticos “Volunclima”, según nuestros registros, usted pertenece como voluntario con una estación y pluviómetro asignado. <br>Nos encontramos en una mejora continua y por lo tanto, hemos realizado un análisis de la información de los registros climáticos y no logramos encontrar datos de su estación. Sin afán de asumir alguna posición al respecto, le escribimos para poder obtener información sobre este tema, ya que puede darse el caso de que usted no ha recibido la adecuada capacitación para poder participar activamente en el programa. También existe la posibilidad de que, si ha tomado lecturas del equipo y los ha anotado en la hoja de registro, si este es el caso le invitamos a que nos los comparta por este medio sus planillas para poder subirlas a nuestra base de datos y usar los datos de la mejor manera, entregándole a usted productos climáticos que le sirvan en sus actividades productivas y en su diario vivir. <br>Esas son algunas de las razones que se nos ocurre por las cuales sus registros no aparecen en el sistema, es por ello que le escribimos para poder obtener una respuesta sobre lo que ha sucedido y de esta forma brindarle nuestro apoyo en lo que se requiera para fortalecer su participación en el programa. <br>Cabe resaltar que cuenta con nuestro respaldo para poder solventar todas sus inquietudes y comentarios. Quedamos muy agradecidos de antemano por su respuesta y responsabilidad con la red.<br>Su compromiso como voluntario climático es vital para nosotros.<br>Saludos Cordiales.<br><br>" )
	elif codigo==2:
		cuerpo_mensaje = ("<br><br>Estimado/a "+nombre+",<br><br><br>Esperamos se encuentre bien, desde el CIIFEN le extendemos un caluroso saludo, le escribimos por un tema relacionado con la red de observadores climáticos “Volunclima”.<br>Nos encontramos en una mejora continua y se ha realizado un análisis de datos de los registros climáticos que ustedes nos proporcionan. Sin embargo, nos arroja que, al día de hoy, no se encuentra información registrada por parte de usted. Es por ello que le invitamos a que nos comente, si ha tenido dificultades para realizar la lectura del pluviómetro a las horas indicadas, si requiere capacitación de nuestra parte o alguna otra cosa que esté a nuestro alcance para brindarle soporte y apoyo técnico. <br>Deseamos poder afirmar y consolidar su participación en el programa, para ello requerimos su respuesta y confirmación contando con usted y su compromiso como voluntario climático.<br>Saludos Cordiales.<br><br>")
	elif codigo==3:
		cuerpo_mensaje = ("<br><br>Estimado/a "+nombre+",<br><br><br>Esperamos se encuentre bien, desde el CIIFEN le extendemos un caluroso saludo, le escribimos por un tema relacionado con la red de observadores climáticos “Volunclima”.<br>Nos encontramos en una mejora continua, por lo tanto, estamos haciendo el seguimiento a la red y para brindarle el apoyo necesario a nuestros voluntarios hemos realizado un análisis de identificación para conocer quienes necesitan mayor soporte en el programa. <br>Entendemos que los primeros meses de integración a la red pueden ser un poco complicado, es por ello que le enviamos este correo para animarle a que continue con la labor de ser un voluntario/a climático/a. Además, a fin de conocer en lo que podemos ayudar para que su participación en el programa transcurra de la forma más amena y fácil posible, le invitamos a que nos comente si requiere capacitación tanto para el uso de las plataformas digitales de Volunclima como para la lectura del equipo.<br>Estaremos muy agradecidos con su respuesta y estamos atentos a despejar todas sus inquietudes para poderle brindar el apoyo necesario y continuar con su proceso como observador climático. <br> Saludos Cordiales.<br><br>")
	elif codigo==4:
		cuerpo_mensaje = ("<br><br>Estimado/a "+nombre+",<br><br><br>Esperamos que se encuentre bien, desde CIIFEN le extendemos nuestros saludos escribiéndole por temas relacionados con la red Volunclima, específicamente por la estación ubicada en el Cuerpo de Bomberos de Pimocha. La estación lleva poco tiempo de ser creada, sin embargo, aún no se ha logrado asignar un observador que pueda reportarnos datos a la plataforma. Por lo cual, requerimos su atención en el tema para la identificación de una persona que voluntariamente reporte los datos registrados por los pluviómetros y demás datos climáticos que se pueden emitir por la app móvil. <br>Quedamos atentos a su respuesta y les agradecemos por su gestión. <br>Saludos Cordiales.<br><br>")
	else:
		return

	# Agregar el cuerpo del mensaje y el HTML al objeto mensaje
	msg.attach(img_attachment)
	msg.attach(MIMEText(cuerpo_mensaje+html_content, 'html'))
	#adjuntar boletin en formato pdf
	#enviar el email
	try:
		server.send_message(msg)
	except:
		print(f"An error occurred: {e}")

#funciona de enviar correos para todas las estaciones
def enviar_flyers(MAIL_RECIEVER, nombre_observador,  server):
	"""
	Envía correos electrónicos de flyers para un evento de socialización de Volunclima.

	Args:
		MAIL_RECIEVER (str): Dirección de correo electrónico del destinatario.
		nombre_observador (str): Nombre del destinatario.
		server (smtplib.SMTP): Objeto del servidor SMTP para enviar el correo.

	Returns:
		None

	Nota:
		Esta función envía correos electrónicos de flyers para un evento de socialización de Volunclima a los destinatarios especificados.

	Raises:
		Exception: Se produce si hay algún error al enviar el correo electrónico.
	"""
	#mensaje del email
	msg=MIMEMultipart('mixed')
	msg["Subject"]=" Evento de socialización de Volunclima"
	msg["From"]=MAIL_USER.strip()


	with open("/var/py/volunclima/scripts/boletines/logo_CIIFEN.png", "rb") as img:
		image_data = img.read()

	with open("/var/py/volunclima/scripts/boletines/zoom.png", "rb") as img:
		image_data2 = img.read()

	# HTML
	html_content = """
	<p class="MsoNormal" style="font-size: 12pt; margin: 0cm 0cm 0.0001pt; font-family: 'times new roman' , serif; color: #222222;"><b><span style="font-family: 'calibri' , sans-serif; color: #17365d;">Volunclima</span></b><b><i><span style="font-size: 9pt; font-family: 'calibri' , sans-serif; color: #1f497d;"><br /></span></i></b></p>
	<p class="MsoNormal" style="font-size: 12pt; margin: 0cm 0cm 0.0001pt; font-family: 'times new roman' , serif; color: #222222;"><i><span style="font-size: 9pt; font-family: 'calibri' , sans-serif; color: black;">Centro Internacional para la Investigaci&oacute;n</span></i><span style="font-size: 11pt; font-family: 'calibri' , sans-serif; color: black;"><u></u><u></u></span></p>
	<p class="MsoNormal" style="font-size: 12pt; margin: 0cm 0cm 0.0001pt; font-family: 'times new roman' , serif; color: #222222;"><i><span style="font-size: 9pt; font-family: 'calibri' , sans-serif; color: black;">del Fen&oacute;meno de El Ni&ntilde;o- CIIFEN</span></i><span style="font-size: 11pt; font-family: 'calibri' , sans-serif; color: black;"><u></u><u></u></span></p>
	<p class="MsoNormal" style="font-size: 12pt; margin: 0cm 0cm 0.0001pt; font-family: 'times new roman' , serif; color: #222222;"><i><span style="font-size: 9pt; font-family: 'calibri' , sans-serif; color: black;">Direcci&oacute;n: Puerto Santa Ana, Ciudad del r&iacute;o. Edificio The Point, Of. 1904.</span></i></p>
	<p class="MsoNormal" style="font-size: 12pt; margin: 0cm 0cm 0.0001pt; font-family: 'times new roman' , serif; color: #222222;"><i><span lang="PT" style="font-size: 9pt; font-family: 'calibri' , sans-serif; color: black;">Guayaquil - Ecuador</span></i><span style="font-size: 11pt; font-family: 'calibri' , sans-serif; color: black;"><u></u><u></u></span><span style="font-size: 10pt; font-family: 'calibri' , sans-serif; color: #000000;"><strong></strong></span></p>
	<div><em><span style="font-size: 10pt; font-family: 'calibri' , sans-serif;">Web site:&nbsp;<span class="Object" id="OBJ_PREFIX_DWT629_com_zimbra_url" style="color: #005a95;"><span class="Object" id="OBJ_PREFIX_DWT592_com_zimbra_url"><a href="https://ciifen.org/" rel="noopener nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer" style="color: #000000;" target="_blank">ciifen.org</a></span></span>&nbsp;&nbsp;<span class="Object" id="OBJ_PREFIX_DWT630_com_zimbra_url" style="color: #005a95;"><span class="Object" id="OBJ_PREFIX_DWT593_com_zimbra_url"><a href="https://crc-osa.ciifen.org/" rel="noopener nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer" style="color: #000000;" target="_blank">crc-osa.ciifen.org</a></span></span>&nbsp;&nbsp;</span></em></div>
	<div><span style="font-size: 10pt; font-family: 'calibri' , sans-serif;"><strong><span style="color: #333399;"><span style="color: #0000ff;"><span class="Object" id="OBJ_PREFIX_DWT631_com_zimbra_url" style="color: #005a95;"><span class="Object" id="OBJ_PREFIX_DWT594_com_zimbra_url"><a href="https://www.facebook.com/CIIFEN/" rel="noopener nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer" style="color: #0000ff;" target="_blank">Facebook</a></span></span></span>&nbsp;|&nbsp;<span style="color: #0000ff;"><span class="Object" id="OBJ_PREFIX_DWT632_com_zimbra_url" style="color: #005a95;"><span class="Object" id="OBJ_PREFIX_DWT595_com_zimbra_url"><a href="https://x.com/ciifen" rel="noopener nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer" style="color: #0000ff;" target="_blank">X</a></span></span></span>&nbsp;|&nbsp;<span style="color: #0000ff;"><span class="Object" id="OBJ_PREFIX_DWT633_com_zimbra_url" style="color: #005a95;"><span class="Object" id="OBJ_PREFIX_DWT596_com_zimbra_url"><a href="https://www.youtube.com/user/CIIFEN" rel="noopener nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer" style="color: #0000ff;" target="_blank">YouTube</a></span></span></span>&nbsp;|&nbsp;<span style="color: #0000ff;"><span class="Object" id="OBJ_PREFIX_DWT634_com_zimbra_url" style="color: #005a95;"><span class="Object" id="OBJ_PREFIX_DWT597_com_zimbra_url"><a href="https://www.instagram.com/ciifenorg/" rel="noopener nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer" style="color: #0000ff;" target="_blank">Instagram</a></span></span></span>&nbsp;|&nbsp;<span style="color: #0000ff;"><span class="Object" id="OBJ_PREFIX_DWT635_com_zimbra_url" style="color: #005a95;"><span class="Object" id="OBJ_PREFIX_DWT598_com_zimbra_url"><a href="https://www.linkedin.com/company/ciifen/" rel="noopener nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer" style="color: #0000ff;" target="_blank">Linkedin</a></span></span></span></span></strong></span></div>
	<p class="MsoNormal" style="font-size: 12pt; margin: 0cm 0cm 0.0001pt; font-family: 'times new roman' , serif; color: #222222;"><i><span style="font-size: 9pt; font-family: 'calibri' , sans-serif; color: black;"><img width="103" height="117" src="cid:ciifen_logo" /></span></i></p>
	""".format(base64.b64encode(image_data).decode('utf-8'))

	original_image = Image.open(io.BytesIO(image_data2))

	# Define el nuevo tamaño deseado (ancho, alto)
	new_size = (600, 600)  # Puedes ajustar 'width' y 'height' según tus necesidades

	# Redimensiona la imagen
	resized_image = original_image.resize(new_size)

	# Convierte la imagen redimensionada de nuevo a bytes
	resized_image_data = io.BytesIO()
	resized_image.save(resized_image_data, format="PNG")
	resized_image_data.seek(0)
	resized_image_bytes = resized_image_data.read()

	# Adjunta la imagen redimensionada al mensaje
	img_attachment = MIMEImage(resized_image_bytes, name="zoom.png")
	img_attachment.add_header('Content-ID', '<zoom_image>')
	img_attachment.add_header('Content-Disposition', 'inline')  # Esto oculta el adjunto
	img_attachment2 = MIMEImage(image_data, name="ciifen_logo.png")
	img_attachment2.add_header('Content-ID', '<ciifen_logo>')
	img_attachment2.add_header('Content-Disposition', 'inline')  # Esto oculta el adjunto
	html_content2 ="""
	<div style="text-align: center;">  <!-- Este div centra el contenido -->
    	<img src="cid:zoom_image" alt="zoom">
    </div>
	""".format(base64.b64encode(resized_image_bytes).decode('utf-8'))

	# Cuerpo del mensaje, sustituir nombre con el nombre de cada observador, todo lo que queda de codigo va dentro del for
	msg["To"]=MAIL_RECIEVER.strip() #correo dentro del for
	cuerpo_mensaje = ("""
		<br><br>Estimados voluntarios, voluntarias y colaboradores de la red Volunclima,<br><br><br>Esperamos que se encuentren bien, los invitamos a la reunión de
		<p style="font-weight: bold; display: inline;"> Encuentro y Recapitulación Volunclima 2023</p>.
		 Presentaremos el nuevo video institucional, los manuales de observadores y<br>compartiremos con ustedes los avances que hemos tenido en la red en el año 2023.
		 <br><br>
		El link de la reunión  es el siguiente:    
		<br><br>
		<a href="https://us02web.zoom.us/j/86003264863?pwd=QkxRZ3p6aEVTNTl2cGE3WHhseWh0dz09" target="_blank">
				https://us02web.zoom.us/j/86003264863?pwd=QkxRZ3p6aEVTNTl2cGE3WHhseWh0dz09 </a>
		<br><br><br>
		Rectificamos la fecha de la reunión para el día miercoles 17 de enero 2024 a las 17:00 hora de Ecuador. Lamentamos la confusión con las fechas y 
		los esperamos ese día.<br><br><br>
		Saludos cordiales,<br><br>
	""" )
	# Agregar el cuerpo del mensaje y el HTML al objeto mensaje
	msg.attach(img_attachment)
	msg.attach(img_attachment2)
	msg.attach(MIMEText(html_content2+cuerpo_mensaje+html_content, 'html'))
	#adjuntar boletin en formato pdf
	#enviar el email
	try:
		server.send_message(msg)
		print("boletín enviado al observador "+ nombre_observador + "(" + MAIL_RECIEVER + ")" )
	except Exception as e:
		print(f"An error occurred: {e}")

#funciona de enviar correos para todas las estaciones MAIL_RECIEVER, nombre_observador, archivo, mIni, yIni, strCountry, dfObs, server
def enviar_no_reportados(MAIL_RECIEVER,	strCountry, mIni, yIni, dias, texto,  server, anual=True):
	"""
	Envía correos electrónicos con reportes de estaciones no reportadas para un país y un período específicos.

	Args:
		MAIL_RECIEVER (str): Dirección de correo electrónico del destinatario.
		strCountry (str): Nombre del país.
		mIni (int): Mes inicial del período.
		yIni (int): Año inicial del período.
		dias (str): Cadena que indica los días (e.g., "de lluvia") para el mensaje del asunto.
		texto (str): Texto adicional para incluir en el cuerpo del mensaje.
		server (smtplib.SMTP): Objeto del servidor SMTP para enviar el correo.
		anual (bool, optional): Indica si el reporte es anual o mensual. Por defecto, es True.

	Returns:
		None

	Nota:
		Esta función envía correos electrónicos con reportes de estaciones no reportadas para un país y un período específicos,
		ya sea mensual o anualmente.

	Raises:
		Exception: Se produce si hay algún error al enviar el correo electrónico.
	"""
	#mensaje del email
	mes = formato_mes(mIni).lower()
	msg=MIMEMultipart('mixed')
	if (anual==True):
		msg["Subject"]="Reporte de estaciones de " + strCountry + " con menos de 11 reportes "+dias+"en el mes: "+ str(mIni) +"-"+ str(yIni)
	else:
		msg["Subject"]="Reporte de estaciones de " + strCountry + " que han reportado menos de 256 días en "+str(yIni)

	msg["From"]=MAIL_USER.strip()
	with open("/var/py/volunclima/scripts/boletines/logo_CIIFEN.png", "rb") as img:
		image_data = img.read()

	# HTML
	html_content = """
	<p class="MsoNormal" style="font-size: 12pt; margin: 0cm 0cm 0.0001pt; font-family: 'times new roman' , serif; color: #222222;"><b><span style="font-family: 'calibri' , sans-serif; color: #17365d;">Volunclima</span></b><b><i><span style="font-size: 9pt; font-family: 'calibri' , sans-serif; color: #1f497d;"><br /></span></i></b></p>
	<p class="MsoNormal" style="font-size: 12pt; margin: 0cm 0cm 0.0001pt; font-family: 'times new roman' , serif; color: #222222;"><i><span style="font-size: 9pt; font-family: 'calibri' , sans-serif; color: black;">Centro Internacional para la Investigaci&oacute;n</span></i><span style="font-size: 11pt; font-family: 'calibri' , sans-serif; color: black;"><u></u><u></u></span></p>
	<p class="MsoNormal" style="font-size: 12pt; margin: 0cm 0cm 0.0001pt; font-family: 'times new roman' , serif; color: #222222;"><i><span style="font-size: 9pt; font-family: 'calibri' , sans-serif; color: black;">del Fen&oacute;meno de El Ni&ntilde;o- CIIFEN</span></i><span style="font-size: 11pt; font-family: 'calibri' , sans-serif; color: black;"><u></u><u></u></span></p>
	<p class="MsoNormal" style="font-size: 12pt; margin: 0cm 0cm 0.0001pt; font-family: 'times new roman' , serif; color: #222222;"><i><span style="font-size: 9pt; font-family: 'calibri' , sans-serif; color: black;">Direcci&oacute;n: Puerto Santa Ana, Ciudad del r&iacute;o. Edificio The Point, Of. 1904.</span></i></p>
	<p class="MsoNormal" style="font-size: 12pt; margin: 0cm 0cm 0.0001pt; font-family: 'times new roman' , serif; color: #222222;"><i><span lang="PT" style="font-size: 9pt; font-family: 'calibri' , sans-serif; color: black;">Guayaquil - Ecuador</span></i><span style="font-size: 11pt; font-family: 'calibri' , sans-serif; color: black;"><u></u><u></u></span><span style="font-size: 10pt; font-family: 'calibri' , sans-serif; color: #000000;"><strong></strong></span></p>
	<div><em><span style="font-size: 10pt; font-family: 'calibri' , sans-serif;">Web site:&nbsp;<span class="Object" id="OBJ_PREFIX_DWT629_com_zimbra_url" style="color: #005a95;"><span class="Object" id="OBJ_PREFIX_DWT592_com_zimbra_url"><a href="https://ciifen.org/" rel="noopener nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer" style="color: #000000;" target="_blank">ciifen.org</a></span></span>&nbsp;&nbsp;<span class="Object" id="OBJ_PREFIX_DWT630_com_zimbra_url" style="color: #005a95;"><span class="Object" id="OBJ_PREFIX_DWT593_com_zimbra_url"><a href="https://crc-osa.ciifen.org/" rel="noopener nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer" style="color: #000000;" target="_blank">crc-osa.ciifen.org</a></span></span>&nbsp;&nbsp;</span></em></div>
	<div><span style="font-size: 10pt; font-family: 'calibri' , sans-serif;"><strong><span style="color: #333399;"><span style="color: #0000ff;"><span class="Object" id="OBJ_PREFIX_DWT631_com_zimbra_url" style="color: #005a95;"><span class="Object" id="OBJ_PREFIX_DWT594_com_zimbra_url"><a href="https://www.facebook.com/CIIFEN/" rel="noopener nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer" style="color: #0000ff;" target="_blank">Facebook</a></span></span></span>&nbsp;|&nbsp;<span style="color: #0000ff;"><span class="Object" id="OBJ_PREFIX_DWT632_com_zimbra_url" style="color: #005a95;"><span class="Object" id="OBJ_PREFIX_DWT595_com_zimbra_url"><a href="https://x.com/ciifen" rel="noopener nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer" style="color: #0000ff;" target="_blank">X</a></span></span></span>&nbsp;|&nbsp;<span style="color: #0000ff;"><span class="Object" id="OBJ_PREFIX_DWT633_com_zimbra_url" style="color: #005a95;"><span class="Object" id="OBJ_PREFIX_DWT596_com_zimbra_url"><a href="https://www.youtube.com/user/CIIFEN" rel="noopener nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer" style="color: #0000ff;" target="_blank">YouTube</a></span></span></span>&nbsp;|&nbsp;<span style="color: #0000ff;"><span class="Object" id="OBJ_PREFIX_DWT634_com_zimbra_url" style="color: #005a95;"><span class="Object" id="OBJ_PREFIX_DWT597_com_zimbra_url"><a href="https://www.instagram.com/ciifenorg/" rel="noopener nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer" style="color: #0000ff;" target="_blank">Instagram</a></span></span></span>&nbsp;|&nbsp;<span style="color: #0000ff;"><span class="Object" id="OBJ_PREFIX_DWT635_com_zimbra_url" style="color: #005a95;"><span class="Object" id="OBJ_PREFIX_DWT598_com_zimbra_url"><a href="https://www.linkedin.com/company/ciifen/" rel="noopener nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer nofollow noopener noreferrer" style="color: #0000ff;" target="_blank">Linkedin</a></span></span></span></span></strong></span></div>
	<p class="MsoNormal" style="font-size: 12pt; margin: 0cm 0cm 0.0001pt; font-family: 'times new roman' , serif; color: #222222;"><i><span style="font-size: 9pt; font-family: 'calibri' , sans-serif; color: black;"><img width="103" height="117" src="cid:ciifen_logo" /></span></i></p>
	""".format(base64.b64encode(image_data).decode('utf-8'))

	img_attachment = MIMEImage(image_data, name="ciifen_logo.png")
	img_attachment.add_header('Content-ID', '<ciifen_logo>')
	img_attachment.add_header('Content-Disposition', 'inline')  # Esto oculta el adjunto
	# Adjunta la imagen redimensionada al mensaje

	# Cuerpo del mensaje, sustituir nombre con el nombre de cada observador, todo lo que queda de codigo va dentro del for
	msg["To"]=MAIL_RECIEVER.strip() #correo dentro del for

	if (anual==True):
		cuerpo_mensaje = ("Estos son los voluntarios que han reportado menos de 11 días "+dias+"en el mes de "+ mes +" de "+ str(yIni) +" en "+strCountry+"<br><br>"+texto+
		"<br><br>Saludos cordiales,<br><br>" )
	else:
		""" cuerpo_mensaje = ("Estos son los voluntarios que han reportado menos de 256 días en "+ str(yIni) +" en "+strCountry+"<br><br>"+texto+
		"<br><br>Saludos cordiales,<br><br>" ) """
		cuerpo_mensaje = ("Estos son los voluntarios que han reportado menos de 1 día desde el 2020 hasta ahora en "+strCountry+"<br><br>"+texto+
		"<br><br>Saludos cordiales,<br><br>" )
	
	# Agregar el cuerpo del mensaje y el HTML al objeto mensaje
	msg.attach(img_attachment)
	msg.attach(MIMEText(cuerpo_mensaje+html_content, 'html'))
	#adjuntar boletin en formato pdf
	#enviar el email
	try:
		server.send_message(msg)
	except Exception as e:
		print(f"An error occurred: {e}")



