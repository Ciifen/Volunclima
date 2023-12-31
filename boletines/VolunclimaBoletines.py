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

#mails con excepciones
excepciones= ["mail1@gmail.com","mail2@gmail.com"]

#generarBoletin y enviarCorreo boolean para generar o enviar por correo los boletines. observadoresExternos es un argumento opcional
#que debe ser una lista de tuplas [(nombre,correo),etc..], para poner personas a las que enviar boletin que no son voluntarios
def GenerarBoletinGeneralMensual (isoCty,yIni,mIni,generarBoletin, enviarCorreo, observadoresExternos=[]):
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
def EnviarBoletinesEstacionesMensual (isoCty,yIni,mIni,generarBoletin, enviarCorreo, codigoEstacion=[]):
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
	<p class="MsoNormal" style="font-size: 12pt; margin: 0cm 0cm 0.0001pt; font-family: 'times new roman' , serif; color: #222222;"><i><span style="font-size: 9pt; font-family: 'calibri' , sans-serif; color: black;"><img width="103" height="117" src="data:image/png;base64, {}" /></span></i></p>
	""".format(base64.b64encode(image_data).decode('utf-8'))

	# Cuerpo del mensaje, sustituir nombre con el nombre de cada observador, todo lo que queda de codigo va dentro del for
	msg["To"]=MAIL_RECIEVER.strip()
	cuerpo_mensaje = ("Estimado/a " + nombre_observador.strip() + "," + 
	"<br><br>Esperamos que se encuentre bien. Adjunto encontrará el boletín mensual con la información climática del mes de "+ mes + " de " + str(yIni) +
	" en la estación "+ estacion + " (" + codigo + ")"
	""". Agradecemos su continua participación y esperamos que encuentre útil esta recopilación para sus actividades y análisis personales.

	<br><br>Saludos cordiales,<br><br>

	""")
	# Agregar el cuerpo del mensaje y el HTML al objeto mensaje
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
	<p class="MsoNormal" style="font-size: 12pt; margin: 0cm 0cm 0.0001pt; font-family: 'times new roman' , serif; color: #222222;"><i><span style="font-size: 9pt; font-family: 'calibri' , sans-serif; color: black;"><img width="103" height="117" src="data:image/png;base64, {}" /></span></i></p>
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
	# Agregar el cuerpo del mensaje y el HTML al objeto mensaje
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

""" GenerarBoletinGeneralMensual("EC",2023,11,True,False)
GenerarBoletinGeneralMensual("CO",2023,11,True,False)
GenerarBoletinGeneralMensual("VE",2023,11,True,False)
GenerarBoletinGeneralMensual("CL",2023,11,True,False) """

""" EnviarBoletinesEstacionesMensual ("EC",2023,11,True,False)
EnviarBoletinesEstacionesMensual ("CO",2023,11,True,False)
EnviarBoletinesEstacionesMensual ("VE",2023,11,True,False)
EnviarBoletinesEstacionesMensual ("CL",2023,11,True,False) """