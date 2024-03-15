import pandas as pd
from calendar import monthrange
import datetime as dt
import matplotlib.pyplot as plt
import math

###################################################################################################################################################
"""
Las siguienes funciones son queries a la base de datos de Volunclima para obtener los datos que se indican en el mismo nombre de la función.
Returns:
	pandas.DataFrame: DataFrame que contiene la información sobre las estaciones meteorológicas y sus datos de precipitación.
"""
###################################################################################################################################################
def ObtenerReportesPrecipitacionDiaria(conn,isoCty,datDate):
	strDat = str(datDate.year)+"/"+"{:02d}".format(datDate.month)+"/"+"{:02d}".format(datDate.day)
	sqlqry = """SELECT st.id, CASE WHEN dd.valor=-888 THEN 0 WHEN dd.valor=-777 THEN 279.4 ELSE dd.valor END as "valor", dd.comentario, st.codigo, st.nombre, (SELECT div1.nombre FROM bh.division div1 WHERE div1.id=(SELECT div4."idPadre" FROM bh.division div4 WHERE div4.id=div."idPadre")) as "div1",
	(SELECT div2.nombre FROM bh.division div2 WHERE div2.id=div."idPadre") as "div2", div.nombre as "div3" 
 FROM bh.precipitacion dd, bh.observador obs, bh.estacion st, bh.division div
 WHERE dd."idObservador"=obs.id AND obs."idEstacion"=st.id AND dd.fecha::date = to_date(%s,'YYYY/MM/DD') AND
 st."idUbicacion"=div.id AND div."idPais" = (SELECT cty.id FROM bh.pais cty WHERE cty.siglas = %s AND cty.state='A') AND
 dd.state='A' AND obs.state='A' AND st.state='A' AND div.state='A'"""
	dfPrec = pd.read_sql(sqlqry,conn, params=(strDat,isoCty))
	return dfPrec


def ObtenerEstacionesDePais(conn,isoCty,chrGroup, chrStatus):
#chrGroup='P': con pluviometro,'S': sin pluviometro, else: ambos
#chrStatus= 'A': activas, 'I': inactivas, else: ambas 
	sqlqry = """SELECT st.id, st.codigo, st.nombre,
	ST_X(st.posicion) AS long,
	ST_Y(st.posicion) AS lat 
	FROM bh.estacion st, bh.division div 
	WHERE st."idUbicacion"=div.id AND st.state='A' AND div.state='A' AND 
	div."idPais" = (SELECT cty.id FROM bh.pais cty WHERE cty.siglas = %s AND cty.state='A') AND 
	LEFT(st.codigo,2) != 'PP'"""

	if chrGroup=='P':
		sqlqry+=" AND st.tiene_pluv"
	elif chrGroup=='S':
		sqlqry+=" AND NOT st.tiene_pluv"
	
	if chrGroup=='A':
		sqlqry+=" AND st.state='A'"
	elif chrGroup=='I':
		sqlqry+=" AND st.state='I'"

	dfStations = pd.read_sql(sqlqry,conn, params=[isoCty])
	return dfStations

def ObtenerEstacionesConDatosPrecipitacionMes (conn,isoCty,yIni,mIni,dIni,yEnd,mEnd,dEnd):
	strDatIni = str(yIni)+"/"+"{:02d}".format(mIni)+"/"+"{:02d}".format(dIni)
	strDatEnd = str(yEnd)+"/"+"{:02d}".format(mEnd)+"/"+"{:02d}".format(dEnd)
	sqlqry = """SELECT X.id, X.codigo, X.nombre, sum(X.diario) as "diario", sum(X.acum) as "acum", sum(X.total) as "total", sum(X.dias) as "dias", X.div1 || '-' || X.div2 || '-' || X.div3 as "ubicacion" FROM (
SELECT div.nombre as "div3", (SELECT div2.nombre FROM bh.division div2 WHERE div2.id=div."idPadre") as "div2", (SELECT div1.nombre FROM bh.division div1 WHERE div1.id=(SELECT div4."idPadre" FROM bh.division div4 WHERE div4.id=div."idPadre")) as "div1", 
st.id, st.codigo, st.nombre, sum(CASE WHEN dd.valor=-888 THEN 0 WHEN dd.valor=-777 THEN 279.4 ELSE dd.valor END) as "diario", 0 as "acum", sum(CASE WHEN dd.valor=-888 THEN 0 WHEN dd.valor=-777 THEN 279.4 ELSE dd.valor END) as "total", count(dd.id) as "dias"
FROM bh.estacion st, bh.observador obs, bh.precipitacion dd, bh.division div
WHERE st."idUbicacion"=div.id AND st.state='A' AND div.state='A' AND dd.state='A' AND obs.state='A' AND obs.id = dd."idObservador" AND obs."idEstacion" = st.id AND
div."idPais" = (SELECT cty.id FROM bh.pais cty WHERE cty.siglas = %s AND cty.state='A') AND
dd.fecha::date BETWEEN to_date(%s,'YYYY/MM/DD') AND to_date(%s,'YYYY/MM/DD') AND
LEFT(st.codigo,2) != 'PP' GROUP BY st.id, st.codigo, div3, div2, div1
UNION
SELECT div.nombre as "div3", (SELECT div2.nombre FROM bh.division div2 WHERE div2.id=div."idPadre") as "div2", (SELECT div1.nombre FROM bh.division div1 WHERE div1.id=(SELECT div4."idPadre" FROM bh.division div4 WHERE div4.id=div."idPadre")) as "div1", 
st.id, st.codigo, st.nombre, 0 as "diario", sum(CASE WHEN dd.valor=-888 THEN 0 WHEN dd.valor=-777 THEN 279.4 ELSE dd.valor END) as "acum", sum(CASE WHEN dd.valor=-888 THEN 0 WHEN dd.valor=-777 THEN 279.4 ELSE dd.valor END) as "total", 
sum(DATE_PART('day', 
                LEAST(dd.fecha_fin, to_date(%s, 'YYYY/MM/DD')) -
                GREATEST(dd.fecha_inicio, to_date(%s, 'YYYY/MM/DD')) 
            )+ 1
) as "dias"
FROM bh.estacion st, bh.observador obs, bh.prec_acum dd, bh.division div
WHERE st."idUbicacion"=div.id AND st.state='A' AND div.state='A' AND dd.state='A' AND obs.state='A' AND obs.id = dd."idObservador" AND obs."idEstacion" = st.id AND
div."idPais" = (SELECT cty.id FROM bh.pais cty WHERE cty.siglas = %s AND cty.state='A') AND
(
        (dd.fecha_inicio::date >= to_date(%s,'YYYY/MM/DD') AND dd.fecha_inicio::date <= to_date(%s,'YYYY/MM/DD')) OR
        (dd.fecha_fin::date >= to_date(%s,'YYYY/MM/DD') AND dd.fecha_fin::date <= to_date(%s,'YYYY/MM/DD')) OR
        (dd.fecha_inicio::date < to_date(%s,'YYYY/MM/DD') AND dd.fecha_fin::date > to_date(%s,'YYYY/MM/DD'))
    ) AND
LEFT(st.codigo,2) != 'PP' GROUP BY st.id, st.codigo, div3, div2, div1) as X
GROUP BY X.id, X.codigo, X.nombre, X.div3, X.div2, X.div1"""
	dfStations = pd.read_sql(sqlqry,conn, params=(isoCty,strDatIni,strDatEnd,strDatEnd,strDatIni,isoCty,strDatIni,strDatEnd,strDatIni,strDatEnd,strDatIni,strDatEnd))
	return dfStations


def ObtenerEstacionesConDatosPrecipitacionMes2(conn, isoCty, yIni, mIni, dIni, yEnd, mEnd, dEnd):
	#Putualizar que esta función se diferencia en la de arriba en como se cuantifican los dias reportados, y es usada para poder
	#obtener los dias que han reportado las estaciones en un rango especifico.
	strDatIni = str(yIni) + "/" + "{:02d}".format(mIni) + "/" + "{:02d}".format(dIni)
	strDatEnd = str(yEnd) + "/" + "{:02d}".format(mEnd) + "/" + "{:02d}".format(dEnd)
	sqlqry = """
	SELECT X.id, X.codigo, X.nombre, sum(X.diario) as "diario", sum(X.acum) as "acum", sum(X.total) as "total", sum(X.dias) as "dias", X.div1 || '-' || X.div2 || '-' || X.div3 as "ubicacion" FROM (
		SELECT div.nombre as "div3", (SELECT div2.nombre FROM bh.division div2 WHERE div2.id=div."idPadre") as "div2", (SELECT div1.nombre FROM bh.division div1 WHERE div1.id=(SELECT div4."idPadre" FROM bh.division div4 WHERE div4.id=div."idPadre")) as "div1", 
		st.id, st.codigo, st.nombre, 
		sum(CASE WHEN dd.valor=-888 THEN 0 WHEN dd.valor=-777 THEN 279.4 ELSE dd.valor END) as "diario", 
		0 as "acum", 
		sum(CASE WHEN dd.valor=-888 THEN 0 WHEN dd.valor=-777 THEN 279.4 ELSE dd.valor END) as "total", 
		count(dd.id) as "dias"
		FROM bh.estacion st
		LEFT JOIN bh.observador obs ON obs."idEstacion" = st.id AND obs.state = 'A'
		LEFT JOIN bh.precipitacion dd ON obs.id = dd."idObservador" AND dd.state = 'A' AND dd.fecha::date BETWEEN to_date(%s,'YYYY/MM/DD') AND to_date(%s,'YYYY/MM/DD')
		JOIN bh.division div ON st."idUbicacion" = div.id AND div.state = 'A'
		WHERE st.state = 'A' AND div."idPais" = (SELECT cty.id FROM bh.pais cty WHERE cty.siglas = %s AND cty.state='A') AND LEFT(st.codigo,2) != 'PP' 
		GROUP BY st.id, st.codigo, div3, div2, div1
		
		UNION
		
		SELECT div.nombre as "div3", (SELECT div2.nombre FROM bh.division div2 WHERE div2.id=div."idPadre") as "div2", (SELECT div1.nombre FROM bh.division div1 WHERE div1.id=(SELECT div4."idPadre" FROM bh.division div4 WHERE div4.id=div."idPadre")) as "div1", 
		st.id, st.codigo, st.nombre, 
		0 as "diario", 
		sum(CASE WHEN dd.valor=-888 THEN 0 WHEN dd.valor=-777 THEN 279.4 ELSE dd.valor END) as "acum", 
		sum(CASE WHEN dd.valor=-888 THEN 0 WHEN dd.valor=-777 THEN 279.4 ELSE dd.valor END) as "total", 
		sum(DATE_PART('day', LEAST(dd.fecha_fin, to_date(%s, 'YYYY/MM/DD')) - GREATEST(dd.fecha_inicio, to_date(%s, 'YYYY/MM/DD'))) + 1) as "dias"
		FROM bh.estacion st
		LEFT JOIN bh.observador obs ON obs."idEstacion" = st.id AND obs.state = 'A'
		LEFT JOIN bh.prec_acum dd ON obs.id = dd."idObservador" AND dd.state = 'A' 
		JOIN bh.division div ON st."idUbicacion" = div.id AND div.state = 'A'
		WHERE st.state = 'A' AND div."idPais" = (SELECT cty.id FROM bh.pais cty WHERE cty.siglas = %s AND cty.state = 'A') AND (
			(dd.fecha_inicio::date >= to_date(%s,'YYYY/MM/DD') AND dd.fecha_inicio::date <= to_date(%s,'YYYY/MM/DD')) OR
			(dd.fecha_fin::date >= to_date(%s,'YYYY/MM/DD') AND dd.fecha_fin::date <= to_date(%s,'YYYY/MM/DD')) OR
			(dd.fecha_inicio::date < to_date(%s,'YYYY/MM/DD') AND dd.fecha_fin::date > to_date(%s,'YYYY/MM/DD'))
		) AND LEFT(st.codigo,2) != 'PP' 
		GROUP BY st.id, st.codigo, div3, div2, div1
	) as X
	GROUP BY X.id, X.codigo, X.nombre, X.div3, X.div2, X.div1"""

	dfStations = pd.read_sql(sqlqry, conn, params=(strDatIni, strDatEnd, isoCty, strDatEnd, strDatIni, isoCty, strDatIni, strDatEnd, strDatIni, strDatEnd, strDatIni, strDatEnd))
	return dfStations

def ObtenerReportesSequiaMes (conn,isoCty,yyyy,mm):#Aqui deberia usarse el mes en curso porque corresponderia a las condiciones del mes previo
	strDatIni = str(yyyy)+"/"+"{:02d}".format(mm)+"/01"
	strDatEnd = str(yyyy)+"/"+"{:02d}".format(mm)+"/15"#Los reportes de sequia solo se pueden enviar hasta el dia #10 
	sqlqry = """SELECT st.id, st.codigo, st.nombre, ST_Y(st.posicion) AS "lat", ST_X(st.posicion) AS "long",
	(SELECT div1.nombre FROM bh.division div1 WHERE div1.id=(SELECT div4."idPadre" FROM bh.division div4 WHERE div4.id=div."idPadre")) as "div1", 
	(SELECT div2.nombre FROM bh.division div2 WHERE div2.id=div."idPadre") as "div2", div.nombre as "div3", 
 dm.fecha::date, (CASE WHEN dm.resp_suelo = 1 THEN 'Saturado'
      WHEN dm.resp_suelo = 2 THEN 'Húmedo'
      WHEN dm.resp_suelo = 3 THEN 'Subhúmedo'
      WHEN dm.resp_suelo = 4  THEN 'Normal'
      WHEN dm.resp_suelo = 5  THEN 'Seco'
      WHEN dm.resp_suelo = 6  THEN 'Muy seco'
      WHEN dm.resp_suelo = 7 THEN 'Erosionable'
END ) as "resp_suelo",
(CASE WHEN dm.resp_veg = 1 THEN 'Clorótica/Aguachinada'
      WHEN dm.resp_veg = 2 THEN 'Verde pálido'
      WHEN dm.resp_veg = 3 THEN 'Normal (verde intenso)'
      WHEN dm.resp_veg = 4  THEN 'Verde azulado (estrés hídrico)'
      WHEN dm.resp_veg = 5  THEN 'Marchitez sin pérdida de hojas'
      WHEN dm.resp_veg = 6  THEN 'Marchitez con pérdida de hojas'
      WHEN dm.resp_veg = 7 THEN 'Marchitez permanente'
END ) as "resp_veg",
(CASE WHEN dm.resp_prec = 1 THEN 'Mucho más de lo normal'
      WHEN dm.resp_prec = 2 THEN 'Más de lo normal'
      WHEN dm.resp_prec = 3 THEN 'Poco más de lo normal'
      WHEN dm.resp_prec = 4  THEN 'Normal'
      WHEN dm.resp_prec = 5  THEN 'Poco menos que lo normal'
      WHEN dm.resp_prec = 6  THEN 'Menos que lo normal'
      WHEN dm.resp_prec = 7 THEN 'Mucho menos que lo normal'
END ) as "resp_prec",
(CASE WHEN dm.resp_temp_prec = 1 THEN 'Muy adelantadas'
      WHEN dm.resp_temp_prec = 2 THEN 'Más adelantadas de lo normal'
      WHEN dm.resp_temp_prec = 3 THEN 'Poco más adelantadas de lo normal'
      WHEN dm.resp_temp_prec = 4  THEN 'Normal'
      WHEN dm.resp_temp_prec = 5  THEN 'Ligeramente retrasadas de lo normal'
      WHEN dm.resp_temp_prec = 6  THEN 'Más retrasadas de lo normal'
      WHEN dm.resp_temp_prec = 7 THEN 'Muy retrasadas'
END ) as "resp_temp_prec",
(CASE WHEN dm.resp_temps = 1 THEN 'Mucho más frío de lo normal'
      WHEN dm.resp_temps = 2 THEN 'Más frío de lo normal'
      WHEN dm.resp_temps = 3 THEN 'Poco más frío de lo normal'
      WHEN dm.resp_temps = 4  THEN 'Normal'
      WHEN dm.resp_temps = 5  THEN 'Poco más cálido que lo normal'
      WHEN dm.resp_temps = 6  THEN 'Más cálido que lo normal'
      WHEN dm.resp_temps = 7 THEN 'Mucho más cálido que lo normal'
END ) as "resp_temps",
(CASE WHEN dm.resp_gana = 1 THEN 'Mucho más que suficiente'
      WHEN dm.resp_gana = 2 THEN 'Más que suficiente'
      WHEN dm.resp_gana = 3 THEN 'Poco más que suficiente'
      WHEN dm.resp_gana = 4  THEN 'Suficiente'
      WHEN dm.resp_gana = 5  THEN 'Poco menos que suficiente'
      WHEN dm.resp_gana = 6  THEN 'Menos que suficiente (escasa)'
      WHEN dm.resp_gana = 7 THEN 'Mucho menos que suficiente'
END ) as "resp_gana",
(CASE WHEN dm.total <=-4 THEN 'Humedad muy alta'
      WHEN dm.total >-4 AND dm.total <=-3  THEN 'Humedad alta'
      WHEN dm.total >-3 AND dm.total <=-2  THEN 'Humedad moderada'
      WHEN dm.total >-2 AND dm.total <=-1  THEN 'Humedad baja'
      WHEN dm.total >-1 AND dm.total < 1  THEN 'Neutro o normal'
      WHEN dm.total >=1 AND dm.total <2  THEN 'Anormalmente seco'
      WHEN dm.total >=2 AND dm.total <3  THEN 'Sequía severa'
      WHEN dm.total >=3 AND dm.total <4  THEN 'Sequía extrema'
      WHEN dm.total >=4  THEN 'Sequía excepcional' 
END ) as "total_txt", dm.total, dm.comentario
FROM bh.estacion st, bh.observador obs, bh.cuestionario dm, bh.division div
WHERE st."idUbicacion"=div.id AND st.state='A' AND div.state='A' AND dm.state='A' AND obs.state='A' AND obs.id = dm."idObservador" AND obs."idEstacion" = st.id AND
div."idPais" = (SELECT cty.id FROM bh.pais cty WHERE cty.siglas = %s AND cty.state='A') AND
dm.fecha::date BETWEEN to_date(%s,'YYYY/MM/DD') AND to_date(%s,'YYYY/MM/DD') AND
LEFT(st.codigo,2) != 'PP'"""
	dfReports = pd.read_sql(sqlqry,conn, params=(isoCty,strDatIni,strDatEnd))
	return dfReports


def ObtenerReportesExtremosMes (conn,isoCty,yIni,mIni,dIni,yEnd,mEnd,dEnd):
	strDatIni = str(yIni)+"/"+"{:02d}".format(mIni)+"/"+"{:02d}".format(dIni)
	strDatEnd = str(yEnd)+"/"+"{:02d}".format(mEnd)+"/"+"{:02d}".format(dEnd)

	sqlqry = """SELECT st.codigo, st.nombre, 
	(SELECT div1.nombre FROM bh.division div1 WHERE div1.id=(SELECT div4."idPadre" FROM bh.division div4 WHERE div4.id=div."idPadre")) as "div1", 
	(SELECT div2.nombre FROM bh.division div2 WHERE div2.id=div."idPadre") as "div2", div.nombre as "div3", 
 ex.fecha, (CASE WHEN ex.prec_extrema=1 THEN 'X' ELSE ' ' END) as "precipitacion", (CASE WHEN ex.inundacion=1 THEN 'X' ELSE ' ' END) as "inundacion",
 (CASE WHEN ex.granizo=1 THEN 'X' ELSE ' ' END) as "granizo", (CASE WHEN ex.rayos=1 THEN 'X' ELSE ' ' END) as "rayos",
 (CASE WHEN ex.deslizamiento=1 THEN 'X' ELSE ' ' END) as "deslizamiento", (CASE WHEN ex.vientos=1 THEN 'X' ELSE ' ' END) as "vientos", 
 (CASE WHEN ex.heladas=1 THEN 'X' ELSE ' ' END) as "heladas", (CASE WHEN ex.calor_extremo=1 THEN 'X' ELSE ' ' END) as "calor_extremo", 
 (CASE WHEN ex.aluvion=1 THEN 'X' ELSE ' ' END) as "aluvion", (CASE WHEN ex.nevadas_extremas=1 THEN 'X' ELSE ' ' END) as "nevadas_extremas", 
 (CASE WHEN ex.ola_calor=1 THEN 'X' ELSE ' ' END) as "ola_calor", (CASE WHEN ex.temp_extrema=1 THEN 'X' ELSE ' ' END) as "temp_extrema", ex.comentario
FROM bh.estacion st, bh.observador obs, bh.evento_ex ex, bh.division div
WHERE st."idUbicacion"=div.id AND st.state='A' AND div.state='A' AND ex.state='A' AND obs.state='A' AND obs.id = ex."idObservador" AND obs."idEstacion" = st.id AND
div."idPais" = (SELECT cty.id FROM bh.pais cty WHERE cty.siglas = %s AND cty.state='A') AND
ex.fecha::date BETWEEN to_date(%s,'YYYY/MM/DD') AND to_date(%s,'YYYY/MM/DD') AND
LEFT(st.codigo,2) != 'PP'"""
	dfReports = pd.read_sql(sqlqry,conn, params=(isoCty,strDatIni,strDatEnd))
	return dfReports

def ObtenerObservadoresPais(conn,isoCty):
	sqlqry = """select obs."idEstacion", u.nombre, u.apellido, u.email, 
	st.nombre || ' (' || st.codigo || ')' as estacion 
	FROM bh.estacion st, bh.observador obs, bh.user u, bh.division div
	WHERE st."idUbicacion"=div.id AND st.state='A' AND div.state='A' 
	AND div."idPais" = (SELECT cty.id FROM bh.pais cty WHERE cty.siglas = %s AND cty.state='A') 
	AND obs.state='A' AND u.state='A' AND obs."idUser"=u.id AND obs."idEstacion" = st.id 
	AND LEFT(st.codigo,2) != 'PP'"""
	dfObs = pd.read_sql(sqlqry,conn, params=[isoCty])
	return dfObs

def ObtenerObservadoresDeListaEstaciones(conn,dfStations):
	lstStIds = dfStations.id.array.tolist()
	lstStIds = list(map(int, lstStIds))
	placeholders = ", ".join(["%s" for _ in lstStIds])
	sqlqry = """select obs."idEstacion", u.nombre, u.apellido, u.email, 
	(SELECT  st.nombre || ' (' || st.codigo || ')' FROM bh.estacion st WHERE obs."idEstacion"=st.id) as estacion
	FROM bh.observador obs, bh.user u 
	WHERE obs.state='A' AND u.state='A' AND obs."idUser"=u.id AND obs."idEstacion" IN ({})""".format(placeholders)
	dfObs = pd.read_sql(sqlqry,conn, params=[*lstStIds])
	return dfObs

def ObtenerPrecipitacionDiariaDeEstacion(conn, idSt, yIni=2010, mIni=1, dIni=1, yEnd=3000, mEnd=12, dEnd=31):
	strDatIni = str(yIni)+"/"+"{:02d}".format(mIni)+"/"+"{:02d}".format(dIni)
	strDatEnd = str(yEnd)+"/"+"{:02d}".format(mEnd)+"/"+"{:02d}".format(dEnd)
	sqlqry = """SELECT dd.fecha::date, dd.valor, CASE WHEN position(' ' in usr.nombre) > 0 THEN LEFT(nombre,position(' ' in usr.nombre)-1) ELSE usr.nombre END || ' ' || CASE WHEN position(' ' in usr.apellido) > 0 THEN LEFT(apellido,position(' ' in usr.apellido)-1) ELSE usr.apellido END as "observador", dd.comentario 
	FROM bh.observador obs, bh.precipitacion dd, bh."user" usr 
	WHERE usr.state='A' AND dd.state='A' AND obs.state='A' AND obs.id = dd."idObservador" AND obs."idEstacion" = %s AND 
	obs."idUser" = usr.id AND dd.fecha::date BETWEEN to_date(%s,'YYYY/MM/DD') AND to_date(%s,'YYYY/MM/DD') ORDER BY 1"""
	dfVals = pd.read_sql(sqlqry,conn, params=(idSt,strDatIni,strDatEnd))
	#ELIMINANDO REPETIDOS
	dfVals = dfVals.drop_duplicates(subset=['fecha'])
	return dfVals

def ObtenerPrecipitacionAcumuladaDeEstacion(conn, idSt, yIni=2010, mIni=1, dIni=1, yEnd=3000, mEnd=12, dEnd=31):
	strDatIni = str(yIni)+"/"+"{:02d}".format(mIni)+"/"+"{:02d}".format(dIni)
	strDatEnd = str(yEnd)+"/"+"{:02d}".format(mEnd)+"/"+"{:02d}".format(dEnd)
	sqlqry = """SELECT dd.fecha_inicio, dd.fecha_fin::date, EXTRACT(DAY FROM dd.fecha_fin-dd.fecha_inicio)+1 AS numdias, dd.valor, CASE WHEN position(' ' in usr.nombre) > 0 THEN LEFT(nombre,position(' ' in usr.nombre)-1) ELSE usr.nombre END || ' ' || CASE WHEN position(' ' in usr.apellido) > 0 THEN LEFT(apellido,position(' ' in usr.apellido)-1) ELSE usr.apellido END as "observador", dd.comentario 
	FROM bh.observador obs, bh.prec_acum dd, bh."user" usr 
	WHERE usr.state='A' AND dd.state='A' AND obs.state='A' AND obs.id = dd."idObservador" AND obs."idEstacion" = %s AND 
	obs."idUser" = usr.id AND dd.fecha_inicio::date >= to_date(%s,'YYYY/MM/DD') AND dd.fecha_fin <= to_date(%s,'YYYY/MM/DD') ORDER BY 1"""
	dfValAcums = pd.read_sql(sqlqry,conn, params=(idSt,strDatIni,strDatEnd))
	dfValAcums = dfValAcums.drop_duplicates(subset=['fecha_inicio','fecha_fin'])
	return dfValAcums

###################################################################################################################################################
"""
Fin de los queries
"""
###################################################################################################################################################

def obtenerDiasFaltantesDatos(yIni,mIni,dIni,yEnd,mEnd,dEnd,dfVals,dfValAcums):
	"""
	Calcula el número de días faltantes entre dos fechas específicas, teniendo en cuenta los datos proporcionados en dos DataFrames.

	Args:
		yIni (int): Año inicial.
		mIni (int): Mes inicial.
		dIni (int): Día inicial.
		yEnd (int): Año final.
		mEnd (int): Mes final.
		dEnd (int): Día final.
		dfVals (pandas.DataFrame): DataFrame que contiene los datos diarios.
		dfValAcums (pandas.DataFrame): DataFrame que contiene los datos acumulados.

	Returns:
		int: Número de días faltantes entre las fechas especificadas.

	"""
	datIni = dt.date(yIni,mIni,dIni)
	datEnd = dt.date(yEnd,mEnd,dEnd)
	delta = datEnd - datIni
	numDays = delta.days+1
	intDaysAcum = 0
	if len(dfValAcums.index)>0:
		intDaysAcum = int(dfValAcums['numdias'].sum())
	intMissDays = numDays - len(dfVals.index) - intDaysAcum
	return intMissDays

#PLML: Función para obtener los límites de una serie de tiempo de precipitación
def obtenerUmbrales(dfSeriePrec):
	"""
	Calcula los límites inferior y superior de una serie de tiempo de precipitación utilizando el método de los cuartiles y el rango intercuartílico.

	Args:
		dfSeriePrec (pandas.DataFrame): DataFrame que contiene la serie de tiempo de precipitación. Debe tener al menos una columna de datos de precipitación.

	Returns:
		list: Una lista que contiene el límite inferior (BI_Calculado) y el límite superior (BS_Calculado).

	"""
	Q1 = dfSeriePrec.iloc[:,[1]].quantile(.25)
	Q3 = dfSeriePrec.iloc[:,[1]].quantile(0.75)
	IQR = Q3 - Q1
	BI_Calculado = (Q1 - 1.5 * IQR)
	BS_Calculado = (Q3 + 1.5 * IQR)
	return [BI_Calculado,BS_Calculado]

#PLML: ME PARECE QUE ESTOS VALORES ATIPICOS, AL MENOS LOS Q1 O Q3, DEBEN DE CONSIDERARSE TODOS LOS DATOS DE LA SERIE DE TIEMPO 
def obtenerAtipicos(dfVals,BI_Calculado,BS_Calculado):
	"""
	determinar los valores atipicos y sacar una matriz sin los outliers
	Args:
		dfVals (pandas.DataFrame): DataFrame que contiene la serie de datos.
		BI_Calculado (float): Límite inferior calculado para identificar valores atípicos.
		BS_Calculado (float): Límite superior calculado para identificar valores atípicos.

	Returns:
		list: Una lista que contiene dos DataFrames. El primer DataFrame contiene los datos que no son atípicos (dentro de los límites), 
		mientras que el segundo DataFrame contiene los datos atípicos (fuera de los límites).

	"""
	dfValsOutliers = dfVals.loc[((dfVals.valor < BI_Calculado.valor) | (dfVals.valor > BS_Calculado.valor))]
	if len(dfValsOutliers.index)>0:
		dfValsNoOutliers = dfVals.loc[((dfVals.valor >= BI_Calculado.valor) & (dfVals.valor <= BS_Calculado.valor))]
	else:
		dfValsNoOutliers = dfVals.copy()
	return [dfValsNoOutliers,dfValsOutliers]

def obtenerSDII(dfPrec, dfAcums, limite=0):
	"""
	Calcula el Índice de Intensidad de Precipitación Diaria Simple (SDII) dado un DataFrame de datos de precipitación diaria y otro de datos de precipitación acumulada.

	Args:
		dfPrec (pandas.DataFrame): DataFrame que contiene los datos de precipitación diaria.
		dfAcums (pandas.DataFrame): DataFrame que contiene los datos de precipitación acumulada.
		limite (float, opcional): Umbral opcional para considerar solo los valores de precipitación superiores a este límite. Por defecto, es 0.

	Returns:
		float: Valor del SDII calculado.

	"""
	sumPrecDiario=dfPrec.loc[dfPrec['valor']>= limite]['valor'].sum()
	sumPrecAcum=dfAcums.loc[dfAcums['valor']>= limite]['valor'].sum()
	totalPrec = sumPrecDiario + sumPrecAcum
	intDaysAcum = int(dfAcums['numdias'].sum())
	totalDays = len(dfPrec.index) + intDaysAcum#Estoy considerando los días de lluvia acumulada, puede que no sea lo más exacto, pero ahí va
	sdii = totalPrec / totalDays
	return sdii

def obtenerPrecipitacionTotal(dfPrec, dfAcums, limite=0):
	"""
	Calcula los límites inferior y superior de una serie de tiempo de precipitación utilizando el método de los cuartiles y el rango intercuartílico.

	Args:
		dfSeriePrec (pandas.DataFrame): DataFrame que contiene la serie de tiempo de precipitación. Debe tener al menos una columna de datos de precipitación.

	Returns:
		list: Una lista que contiene el límite inferior (BI_Calculado) y el límite superior (BS_Calculado).

	"""
	sumPrecDiario=dfPrec.loc[dfPrec['valor']>= limite]['valor'].sum()
	sumPrecAcum=dfAcums.loc[dfAcums['valor']>= limite]['valor'].sum()
	totalPrec = sumPrecDiario + sumPrecAcum
	return totalPrec

def obtenerCDDCWD(dfPrec,yIni,mIni,dIni,yEnd,mEnd,dEnd,limit=1):
	"""
	Calcula la duración máxima de períodos consecutivos secos (CDD) y húmedos (CWD) en una serie de tiempo de precipitación.

	Args:
		dfPrec (pandas.DataFrame): DataFrame que contiene los datos de precipitación.
		yIni (int): Año inicial.
		mIni (int): Mes inicial.
		dIni (int): Día inicial.
		yEnd (int): Año final.
		mEnd (int): Mes final.
		dEnd (int): Día final.
		limit (float, opcional): Umbral para considerar un día como húmedo. Por defecto es 1.

	Returns:
		list: Una lista que contiene dos valores: la duración máxima de períodos consecutivos secos (CDD) y 
		la duración máxima de períodos consecutivos húmedos (CWD) en la serie de tiempo.

	"""
	#Recorro las fechas del mes-año
	cdd=0
	cwd=0
	cntCdd=0
	cntCwd=0
	
	datIni = dt.date(yIni,mIni,dIni)
	datEnd = dt.date(yEnd,mEnd,dEnd)
	delta = dt.timedelta(days=1)
	while (datIni <= datEnd):
		dfVal = dfPrec.loc[dfPrec['fecha'] == str(datIni.year)+"/"+"{:02d}".format(datIni.month)+"/""{:02d}".format(datIni.day)]
		if len(dfVal.index)>0:
			#Evaluo el dato
			if dfVal.valor.values[0] >= limit:#Es dia humedo, se usa el values[0] porque dfVal.valor es una serie
				cntCwd=cntCwd+1
				if cntCdd > cdd:
					cdd = cntCdd
				cntCdd=0
			else: #Es dia seco
				cntCdd=cntCdd+1
				if cntCwd > cwd:
					cwd = cntCwd
				cntCwd=0
		else:#Dato faltante, se considera un cero.
			cntCdd=cntCdd+1
			if cntCwd > cwd:
				cwd = cntCwd
			cntCwd=0
		datIni += delta
	return [cdd,cwd]

def rellenarRegistros(dfPrec,yIni,mIni,dIni,yEnd,mEnd,dEnd):
	"""
	Rellena los registros faltantes en un DataFrame de precipitación con el valor -999.

	Args:
		dfPrec (pandas.DataFrame): DataFrame que contiene los datos de precipitación.
		yIni (int): Año inicial.
		mIni (int): Mes inicial.
		dIni (int): Día inicial.
		yEnd (int): Año final.
		mEnd (int): Mes final.
		dEnd (int): Día final.

	Returns:
		pandas.DataFrame: DataFrame de precipitación con las fechas faltantes rellenadas con el valor -999.

	"""
	datIni = dt.date(yIni,mIni,dIni)
	datEnd = dt.date(yEnd,mEnd,dEnd)
	lstDates =[]
	lstVals =[]
	delta = dt.timedelta(days=1)
	while (datIni <= datEnd):
		dfVal = dfPrec.loc[dfPrec['fecha'] == str(datIni.year)+"/"+"{:02d}".format(datIni.month)+"/""{:02d}".format(datIni.day)]
		if len(dfVal.index)==0:#Fecha faltante, relleno con -999
			lstDates.append(datIni)
			lstVals.append(-999)
		datIni += delta

	dfAux = pd.DataFrame({"fecha":lstDates, "valor":lstVals}, columns=dfPrec.columns)
	dfPrec = pd.concat([dfPrec, dfAux], ignore_index=True)
	dfPrec['fecha'] = pd.to_datetime(dfPrec['fecha'], format='%Y-%m-%d')
	dfPrec.sort_values(by=['fecha'], inplace=True, ignore_index=True)
	return dfPrec

#Si el día de la fecha inicial es diferente de 1 o de un multiplo del número de días a acumular 
def obtenerAgregadosPorPeriodoDias(dfVals,dfAcums,intSize,yIni,mIni,dIni,yEnd,mEnd,dEnd):
	"""
	Calcula los agregados por un período de tiempo determinado en días.

	Args:
		dfVals (pandas.DataFrame): DataFrame que contiene los datos diarios.
		dfAcums (pandas.DataFrame): DataFrame que contiene los datos acumulados.
		intSize (int): Tamaño del período de tiempo en días para calcular los agregados.
		yIni (int): Año inicial.
		mIni (int): Mes inicial.
		dIni (int): Día inicial.
		yEnd (int): Año final.
		mEnd (int): Mes final.
		dEnd (int): Día final.

	Returns:
		pandas.DataFrame: DataFrame que contiene los agregados por el período de tiempo especificado.

	Raises:
		ValueError: Si el tamaño del período es menor o igual a 1.
	"""
	if intSize<=1:
		print("Por favor escoja un lapso de acumulación mayor a 1")
	dfDataD=dfVals.loc[dfVals["valor"]>=0]
	dfDataD['fecha'] = pd.to_datetime(dfDataD['fecha'], format='%Y-%m-%d').dt.date#datetime to date
	dfDataA=dfAcums.loc[dfAcums["valor"]>=0]
	dfDataA['fecha_inicio'] = pd.to_datetime(dfDataA['fecha_inicio'], format='%Y-%m-%d').dt.date#datetime to date
	dfDataA['fecha_fin'] = pd.to_datetime(dfDataA['fecha_fin'], format='%Y-%m-%d').dt.date#datetime to date
	lstDatesIni = []
	lstDatesEnd = []
	lstValDiarios = []
	lstRecDiarios = []
	lstValAcums = []
	lstRecAcums = []
	lstAggs = []
	lstDayTots = []
	lstMiss = []
	datIni = dt.date(yIni,mIni,dIni)
	datEnd = dt.date(yEnd,mEnd,dEnd)
	delta = dt.timedelta(days=intSize)
	blnFixed = False
	blnFirstDayIsMultiple = False
	#Manejando inicios irregulares (por si se ponen fechas que no corresponden a los días convencionales: 1, 10, 15, etc)
	#Es el día inicial un múltiplo del lapso?
	if (dIni!=1) and (dIni%intSize!=0):
		intDaysAux=abs((intSize*int(math.ceil(dIni/intSize)))-dIni)
		datAux=datIni+dt.timedelta(days=intDaysAux+1)
		blnFixed = True
	else:
		if dIni%intSize==0:#en el caso de que el dia Inicial sea igual a un múltiplo del lapso, se debe sumarle 1 día a datIni para la siguiente iteración
			datAux=datIni+dt.timedelta(days=1)
			blnFirstDayIsMultiple = True
		else:
			datAux=datIni+delta

	while (datIni < datEnd):
		lstDatesIni.append(datIni)
		fltAggDiario = round(dfDataD.loc[(dfDataD['fecha']>=datIni) & (dfDataD['fecha']<datAux)]['valor'].sum(),1)
		intRecDiarios = len(dfDataD.loc[(dfDataD['fecha']>=datIni) & (dfDataD['fecha']<datAux)].index)
		fltAggAcum = round(dfDataA.loc[(dfDataA['fecha_inicio']>=datIni) & (dfDataA['fecha_fin']<datAux)]['valor'].sum(),1)
		intDayAcums = dfDataA.loc[(dfDataA['fecha_inicio']>=datIni) & (dfDataA['fecha_fin']<datAux)]['numdias'].sum()
		intMiss = abs((datIni - datAux).days) - intRecDiarios - intDayAcums
		lstDatesEnd.append(datAux-dt.timedelta(days=1))
		lstRecDiarios.append(int(intRecDiarios))
		lstValDiarios.append(fltAggDiario)
		lstValAcums.append(fltAggAcum)
		lstRecAcums.append(int(intDayAcums))
		lstAggs.append(round(fltAggDiario+fltAggAcum,1))
		lstDayTots.append(int(intRecDiarios+intDayAcums))
		lstMiss.append(int(intMiss))
		if blnFixed:#datIni no es 1, sino un número entre 1 y un múltiplo del lapso
			datIni += dt.timedelta(days=intDaysAux+1)
			blnFixed = False
		else:
			if blnFirstDayIsMultiple:
				datIni += dt.timedelta(days=1)
				blnFirstDayIsMultiple=False
			else:
				datIni += delta
		datAux=datIni+delta
		if datAux >= datEnd:
			datAux = datEnd+dt.timedelta(days=1)
	dfAgg = pd.DataFrame({"fecha_inicial":lstDatesIni, "fecha_final":lstDatesEnd, "reportes_diarios":lstRecDiarios, "total_diarios":lstValDiarios, "reportes_acum":lstRecAcums, "total_acum":lstValAcums, "agregado_total":lstAggs, "dias_monitoreados": lstDayTots,"faltantes": lstMiss})
	return dfAgg

def dfAgregadosAMatriz(dfAgg):
	"""
	Convierte un DataFrame de agregados en una lista de listas para representar una tabla.

	Args:
		dfAgg (pandas.DataFrame): DataFrame que contiene los datos agregados.

	Returns:
		list: Lista de listas que representa los datos en formato de tabla.
	"""
	table_data=[["Periodo", "Valor [mm]", "Días faltantes"]]
	for idx in range(len(dfAgg.index)):
		strInterval = dfAgg.iloc[idx,0].strftime('%d/%m/%Y')+ " - "+dfAgg.iloc[idx,1].strftime('%d/%m/%Y')
		strAgg = str(dfAgg.iloc[idx,6])
		strMiss = str(dfAgg.iloc[idx,8])
		table_data.append([strInterval, strAgg, strMiss])
	return table_data

def dfReportesSequiaAMatriz(dfReps,isoCty,numRegPerPage):
	"""
	Convierte un DataFrame de reportes de sequía en una lista de matrices para mostrar los datos en páginas.

	Args:
		dfReps (pandas.DataFrame): DataFrame que contiene los reportes de sequía.
		isoCty (str): Código ISO del país para determinar el número máximo de caracteres permitidos en los comentarios.
		numRegPerPage (int): Número máximo de registros por página.

	Returns:
		list: Lista de matrices que representa los datos de los reportes de sequía en páginas.
	"""
	arrMats = []
	numMats = math.ceil(len(dfReps.index)/numRegPerPage)#cuantos juegos de matrices 
	idxAux=0
	if isoCty=="VE":
		intNumChars = 270
	elif isoCty=="EC":
		intNumChars = 207
	elif isoCty=="CL":
		intNumChars = 182
	else: 
		intNumChars = 170
	for idxMat in range(numMats):
		idxEnd=idxAux+numRegPerPage
		if idxEnd > len(dfReps.index):
			idxEnd = len(dfReps.index)
		table_data=[["Estación", "Ubicación", "Nivel de sequía", "Comentarios"]]
		for idx in range(idxAux,idxEnd):#El orden viene del df obtenido de la funcion ObtenerReportesSequiaMes
			strStation = dfReps.iloc[idx,2] + " (" + dfReps.iloc[idx,1]+ ")"
			strLoc = dfReps.iloc[idx,5]+ "-" + dfReps.iloc[idx,6]+ "-"+dfReps.iloc[idx,7]
			strTotal = dfReps.iloc[idx,15]
			strComms = dfReps.iloc[idx,17]
			strComms = ''.join(strComms.splitlines())#quitando saltos de linea
			if len(strComms)>intNumChars:
				strComms=strComms[0:intNumChars]+"..."
			table_data.append([strStation, strLoc, strTotal, strComms])
		arrMats.append(table_data)
		idxAux=idxEnd
		if idxEnd == len(dfReps.index):
			return arrMats


def dfExtremosAMatriz(dfReps,numRegPerPage):
	"""
	Convierte un DataFrame de reportes de eventos extremos en una lista de matrices para mostrar los datos en páginas.

	Args:
		dfReps (pandas.DataFrame): DataFrame que contiene los reportes de eventos extremos.
		numRegPerPage (int): Número máximo de registros por página.

	Returns:
		list: Lista de matrices que representa los datos de los reportes de eventos extremos en páginas.
	"""
	arrMats = []
	numMats = math.ceil(len(dfReps.index)/numRegPerPage)#cuantos juegos de matrices 
	idxAux=0
	for idxMat in range(numMats):
		idxEnd=idxAux+numRegPerPage
		if idxEnd > len(dfReps.index):
			idxEnd = len(dfReps.index)
		#table_data=[["Estación", "Ubicación", "Fecha", "Prec. Extrema","Inundaciones", "Granizo", "Tormenta Electrica", "Deslizamientos", "Vientos Fuertes", "Comentarios"]]
		table_data=[["Estación", "Ubicación", "Fecha", "Eventos Extremos Observados", "Comentarios"]]
		for idx in range(idxAux,idxEnd):#El orden viene del df obtenido de la funcion ObtenerReportesSequiaMes
			strEvent = ""
			strStation = dfReps.iloc[idx,1] + " (" + dfReps.iloc[idx,0]+ ")"
			strLoc = dfReps.iloc[idx,2]+ "-" + dfReps.iloc[idx,3]+ "-"+dfReps.iloc[idx,4]
			strDat = dfReps.iloc[idx,5].strftime('%d/%m/%Y %H:%M')
			if dfReps.iloc[idx,6]=='X':
				strEvent += "Lluvia Extrema, "
			if dfReps.iloc[idx,7]=='X':
				strEvent += "Inundación, "
			if dfReps.iloc[idx,8]=='X':
				strEvent += "Granizo, "
			if dfReps.iloc[idx,9]=='X':
				strEvent += "Rayos y/o tormenta eléctrica, "
			if dfReps.iloc[idx,10]=='X':
				strEvent += "Deslizamiento, "
			if dfReps.iloc[idx,11]=='X':
				strEvent += "Vientos Fuertes, "
			if dfReps.iloc[idx,12]=='X':
				strEvent += "Heladas, "
			# if dfReps.iloc[idx,13]=='X':
				# strEvent += "Calor extremo, "
			if dfReps.iloc[idx,14]=='X':
				strEvent += "Aluvión, "
			if dfReps.iloc[idx,15]=='X':
				strEvent += "Nevada Extrema, "
			if dfReps.iloc[idx,16]=='X':
				strEvent += "Ola de calor, "
			if dfReps.iloc[idx,17]=='X':
				strEvent += "Frío o Calor Extremo, "
			strEvent = strEvent[:-2]
			# strPrec = dfReps.iloc[idx,6]
			# strFlood = dfReps.iloc[idx,7]
			# strHail = dfReps.iloc[idx,8]
			# strLight = dfReps.iloc[idx,9]
			# strLand = dfReps.iloc[idx,10]
			# strWind = dfReps.iloc[idx,11]
			strComms = dfReps.iloc[idx,18]
			strComms = ''.join(strComms.splitlines())#quitando saltos de linea
			#table_data.append([strStation, strLoc, strDat, strPrec, strFlood, strHail, strLight, strLand, strWind, strComms])
			table_data.append([strStation, strLoc, strDat, strEvent, strComms])
		arrMats.append(table_data)
		idxAux=idxEnd
		if idxEnd == len(dfReps.index):
			return arrMats


#Devuelve una matriz de matrices. Cada matriz tiene 9 registros mas el encabezado. Eso porque es la altura disponible en los boletines (media pagina) 
def dfPrecEstacionesMensualAMatriz(dfPrec,numRegPerPage,lstTblRegs):
	"""
	Convierte un DataFrame de datos mensuales de precipitación por estación en una lista de matrices para mostrar los datos en páginas.

	Args:
		dfPrec (pandas.DataFrame): DataFrame que contiene los datos mensuales de precipitación por estación.
		numRegPerPage (int): Número máximo de registros por página.
		lstTblRegs (list): Lista que contiene el número de registros por tabla en cada página.

	Returns:
		list: Lista de matrices que representa los datos de precipitación mensual por estación en páginas.
	"""
	arrMats = []
	numMats = math.ceil(len(dfPrec.index)/numRegPerPage)#cuantos juegos de matrices 
	idxAux=0
	for idxMat in range(numMats):
		for idxRec in range(len(lstTblRegs)):
			idxEnd=idxAux+lstTblRegs[idxRec]
			if idxEnd > len(dfPrec.index):
				idxEnd = len(dfPrec.index)
			table_data=[["Estación", "Ubicación", "Prec. Total [mm/mes]"]]
			for idx in range(idxAux,idxEnd):
				strStation = dfPrec.iloc[idx,1] + " (" + dfPrec.iloc[idx,0]+ ")"
				strVal = str(dfPrec.iloc[idx,2]) if dfPrec.iloc[idx,2]!=-888 else 'TRZ'
				strLoc = dfPrec.iloc[idx,3]
				table_data.append([strStation, strLoc, strVal])
			arrMats.append(table_data)
			idxAux=idxEnd
			if idxEnd == len(dfPrec.index):
				return arrMats


def dfPrecDiarioAMatriz(dfDD, dfObs):
	"""
	Convierte un DataFrame de datos diarios de precipitación en una lista de listas para su presentación tabular.

	Args:
		dfDD (pandas.DataFrame): DataFrame que contiene los datos diarios de precipitación.
		dfObs (pandas.DataFrame): DataFrame que contiene la información del observador.

	Returns:
		list: Lista de listas que representa los datos diarios de precipitación para mostrar en una tabla.
	"""
	if len(dfObs.index)>1:
		table_data=[["Observador", "Fecha", "Valor [mm]", "Comentarios"]]
		for idx in range(len(dfDD.index)):
			strDate = dfDD.iloc[idx,0].strftime('%d/%m/%Y')
			strDate = dfDD.iloc[idx,0].strftime('%d/%m/%Y')# %H:%M')
			if dfDD.iloc[idx,1]!=-888 and dfDD.iloc[idx,1]!=-777:#strVal = str(dfDD.iloc[idx,1]) if dfDD.iloc[idx,1]!=-888 else 'TRZ'
				strVal = str(dfDD.iloc[idx,1])
			elif dfDD.iloc[idx,1]==-888:
				strVal = 'TRZ'
			else:# dfDD.iloc[idx,1]==-777
				strVal = 'DSB'
			strComms = str(dfDD.iloc[idx,3])
			strComms = ''.join(strComms.splitlines())#quitando saltos de linea
			if len(strComms)>135:
				strComms=strComms[0:135]+"..."
			strObs = str(dfDD.iloc[idx,2])
			table_data.append([strObs, strDate, strVal, strComms])
	else:
		table_data=[["Fecha", "Valor [mm]", "Comentarios"]]
		for idx in range(len(dfDD.index)):
			strDate = dfDD.iloc[idx,0].strftime('%d/%m/%Y')
			if dfDD.iloc[idx,1]!=-888 and dfDD.iloc[idx,1]!=-777:#strVal = str(dfDD.iloc[idx,1]) if dfDD.iloc[idx,1]!=-888 else 'TRZ'
				strVal = str(dfDD.iloc[idx,1])
			elif dfDD.iloc[idx,1]==-888:
				strVal = 'TRZ'
			else:# dfDD.iloc[idx,1]==-777:
				strVal = 'DSB'
			strComms = str(dfDD.iloc[idx,3])
			strComms = ''.join(strComms.splitlines())#quitando saltos de linea
			if len(strComms)>135:
				strComms=strComms[0:135]+"..."
			table_data.append([strDate, strVal, strComms])
	return table_data

def dfPrecAcumAMatriz(dfPrec, dfObs):
	"""
	Convierte un DataFrame de datos acumulados de precipitación en una lista de listas para su presentación tabular.

	Args:
		dfPrec (pandas.DataFrame): DataFrame que contiene los datos acumulados de precipitación.
		dfObs (pandas.DataFrame): DataFrame que contiene la información del observador.

	Returns:
		list: Lista de listas que representa los datos acumulados de precipitación para mostrar en una tabla.
	"""
	if len(dfObs.index)>1:
		table_data=[["Observador", "Periodo", "Valor [mm]", "Comentarios"]]
		for idx in range(len(dfPrec.index)):
			strInterval = dfPrec.iloc[idx,0].strftime('%d/%m/%Y')+ " - "+dfPrec.iloc[idx,1].strftime('%d/%m/%Y')
			if dfPrec.iloc[idx,3]!=-888 and dfPrec.iloc[idx,3]!=-777:#strVal = str(dfPrec.iloc[idx,3]) if dfPrec.iloc[idx,3]!=-888 else 'TRZ' 
				strVal = str(dfPrec.iloc[idx,3])
			elif dfPrec.iloc[idx,3]==-888:
				strVal = 'TRZ'
			else:# dfPrec.iloc[idx,3]==-777:
				strVal = 'DSB'
			strComms = str(dfPrec.iloc[idx,5])
			strComms = ''.join(strComms.splitlines())#quitando saltos de linea
			if len(strComms)>135:
				strComms=strComms[0:135]+"..."
			strObs = str(dfPrec.iloc[idx,4])
			table_data.append([strObs, strInterval, strVal, strComms])
	else:
		table_data=[["Periodo", "Valor [mm]", "Comentarios"]]
		for idx in range(len(dfPrec.index)):
			strInterval = dfPrec.iloc[idx,0].strftime('%d/%m/%Y')+ " - "+dfPrec.iloc[idx,1].strftime('%d/%m/%Y')
			if dfPrec.iloc[idx,3]!=-888 and dfPrec.iloc[idx,3]!=-777:#strVal = str(dfPrec.iloc[idx,3]) if dfPrec.iloc[idx,3]!=-888 else 'TRZ' 
				strVal = str(dfPrec.iloc[idx,3])
			elif dfPrec.iloc[idx,3]==-888:
				strVal = 'TRZ'
			else:# dfPrec.iloc[idx,3]==-777:
				strVal = 'DSB'
			strComms = str(dfPrec.iloc[idx,5])
			strComms = ''.join(strComms.splitlines())#quitando saltos de linea
			if len(strComms)>135:
				strComms=strComms[0:135]+"..."
			table_data.append([strInterval, strVal, strComms])
	return table_data

def obtenerAcronimoMes(idxMes):
	return {
		1: "Ene",
		2: "Feb",
		3: "Mar",
		4: "Abr",
		5: "May",
		6: "Jun",
		7: "Jul",
		8: "Ago",
		9: "Sep",
		10: "Oct",
		11: "Nov",
		12: "Dic",
	}.get(idxMes, '%ERR%') 

def obtenerNombreMes(idxMes):
	return {
		1: "Enero",
		2: "Febrero",
		3: "Marzo",
		4: "Abril",
		5: "Mayo",
		6: "Junio",
		7: "Julio",
		8: "Agosto",
		9: "Septiembre",
		10: "Octubre",
		11: "Noviembre",
		12: "Diciembre",
	}.get(idxMes, '%ERR%') 

def obtenerNombrePais(strIso2):
	return {
		"EC": "Ecuador",
		"CL": "Chile",
		"VE": "Venezuela",
		"BO": "Bolivia",
		"CO": "Colombia",
	}.get(strIso2, '%ERR%') 

def dfAgradecimientosAMatriz(dfObs,numRegPerPage,lstTblRegs):
	"""
	Convierte un DataFrame de observadores en una lista de listas para su presentación tabular.

	Esta función se utiliza para generar los agradecimientos en un boletín climático.

	Args:
		dfObs (pandas.DataFrame): DataFrame que contiene la información de los observadores.
		numRegPerPage (int): Número máximo de registros por página.
		lstTblRegs (list): Lista que contiene el número de registros por tabla.

	Returns:
		list: Lista de listas que representa los agradecimientos para mostrar en una tabla.
	"""
	arrMats = []
	numMats = math.ceil(len(dfObs.index)/numRegPerPage)#cuantos juegos de matrices 
	idxAux=0
	for idxMat in range(numMats):
		for idxRec in range(len(lstTblRegs)):
			idxEnd=idxAux+lstTblRegs[idxRec]
			if idxEnd > len(dfObs.index):
				idxEnd = len(dfObs.index)
			table_data=[['Observador','Estacion']]
			for idx in range(idxAux,idxEnd):
				strObs = dfObs.iloc[idx,1] + " " + dfObs.iloc[idx,2]
				strStation = dfObs.iloc[idx,4]
				table_data.append([strObs, strStation])
			arrMats.append(table_data)
			idxAux=idxEnd
			if idxEnd == len(dfObs.index):
				return arrMats
