import accesoDatosVolunclima as acc
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import math
from fpdf import FPDF
import os
import matplotlib.lines as mlines
from calendar import monthrange

counterDF=0
requerimientos_hidricos_EC = {
    "Banano": "1200 a 2200 mm por año dependiendo de la humedad.",
    "Cacao": "1500 a 2500 mm distribuidos uniformemente durante el año.",
    "Café": "1700 a 2200 mm por año.",
    "Maíz": "500 a 800 mm por todo el periodo de crecimiento, dividido entre sus etapas fenológicas; es decir, a medida que crece, aumenta la cantidad requerida de agua.",
    "Arroz": "1000 a 1800 mm por 120 a 150 días de cultivo, dependiendo del clima y del periodo de crecimiento.",
    "Trigo": "800 a 1200 mm durante el periodo de crecimiento, incrementando el riego a medida que crece y disminuyendo hacia la cosecha.",
    "Papa": "500 a 800 mm durante el periodo de crecimiento, incrementando la cantidad de riego a medida que crece.",
    "Cebada": "800 a 1200 mm por 120 a 150 días de cultivo, distribuido entre sus fases fenológicas.",
    "Lenteja": "500 a 700 mm por ciclo de cultivo, incrementando la cantidad de agua a medida que crece.",
    "Garbanzo": "600 a 900 mm para un ciclo vegetativo entre 90 a 180 días.",
    "Haba": "600 a 900 mm por 120 a 150 días de cultivo, incrementando la cantidad de agua a medida que crece.",
    "Frijol": "500 a 700 mm por el tiempo de producción (60 a 120 días), dependiendo del clima.",
    "Soya": "800 a 1200 mm distribuidos por temporada de crecimiento (15 a 16 meses).",
    "Cítricos": "800 a 1200 mm por año.",
    "Tomate": "500 a 800 mm por 90 a 120 días, dependiendo del clima, incrementando el riego a medida que crece y disminuyendo al final.",
    "Aguacate": "1500 a 2000 mm por año, distribuidos de forma uniforme.",
    "Plátano": "1200 a 2200 mm por año dependiendo de la humedad.",
    "Uva": "800 a 1200 mm por año, incrementando el riego en etapas de floración y maduración.",
    "Lechuga": "500 a 700 mm para un ciclo de vida de 75 a 85 días, distribuidos de manera uniforme.",
    "Zanahoria": "500 a 800 mm anualmente, distribuidos uniformemente.",
    "Brocoli": "600 a 900 mm por ciclo de cultivo de 90 a 150 días.",
    "Coliflor": "600 a 900 mm por ciclo de cultivo de 90 a 150 días.",
    "Espinaca": "500 a 700 mm por ciclo de cultivo de 45 a 60 días, distribuidos uniformemente.",
    "Brócoli": "600 a 900 mm por ciclo de cultivo de 90 a 150 días.",
    "Coliflor": "600 a 900 mm por ciclo de cultivo de 90 a 150 días.",
    "Espinaca": "500 a 700 mm por ciclo de cultivo de 45 a 60 días, distribuidos uniformemente.",
    "Kiwi": "1500 a 2000 mm por año.",
    "Pimiento": "500 a 800 mm por 90 a 120 días, incrementando el riego a medida que crece y disminuyendo al final.",
    "Fresas": "800 a 1200 mm por año, distribuidos uniformemente.",
    "Manzana": "800 a 1200 mm por año, dependiendo del clima y etapa de crecimiento.",
    "Durazno": "800 a 1200 mm por año, dependiendo del clima y etapa de crecimiento.",
    "Ciruelo": "800 a 1200 mm por año, dependiendo del clima y etapa de crecimiento.",
    "Pera": "800 a 1200 mm por año, dependiendo del clima y etapa de crecimiento."
}

# Requerimientos hídricos para Chile
requerimientos_hidricos_CL = {
    "Avellano": "700 a 800 mm distribuidos para cada etapa del cultivo.",
    "Manzano rojo": "50 mm por semana, tiene un régimen similar al de los cítricos.",
    "Manzano verde": "51 mm por semana, tiene un régimen similar al de los cítricos.",
    "Arándano": "650 a 700 mm al año. Se requiere entre 1.5 a 3 mm por día. Se recomienda aumentar un poco el riego en la época de floración y maduración.",
    "Cranberry": "650 a 700 mm al año. Se requiere entre 1.5 a 3 mm por día. Se recomienda aumentar un poco el riego en la época de floración y maduración.",
    "Trigo": "450 a 650 mm por 100 a 130 días, depende del clima y el periodo de crecimiento. Incrementando el riego a medida que crece y disminuyendo un poco hacia el final.",
    "Triticale": "400 a 900 mm por año, distribuido entre sus fases fenológicas.",
    "Remolacha/ Betarraga": "550 a 750 mm por periodo de crecimiento incrementando a medida que crece y disminuyendo un poco hacia el final.",
    "Garbanzo": "650 a 1000 mm para un ciclo vegetativo entre 90 a 180 días.",
    "Frambuesa": "700 a 900 mm por año.",
    "Castaño": "2 a 4 mm por día o bien de 700 mm por año.",
    "Cerezo": "590 a 650 mm por año. Se recomienda aumentar el riego en las temporadas de floración y producción del fruto.",
    "Arveja verde": "350 a 500 mm por todo el periodo de crecimiento, incrementando la cantidad de agua a medida que crece.",
    "Haba": "350 a 700 mm por 192 a 240 días de cultivo. Se requiere mayor cantidad de agua en la fase de floración y formación de la vaina.",
    "Avena": "400 a 1000 mm por ciclo 110 a 275 días, requiriendo mayor cantidad de agua durante el ciclo de desarrollo.",
    "Lupino": "400 a 1000 mm por año.",
    "Lenteja": "260 a 850 mm por un año. (Cultivo anual)",
    "Nogal": "1000 mm por año.",
    "Eucalipto": "Se requiere un aproximado de 600 a 900 mm por año.",
    "Acelga": "460.72 mm para un ciclo de cultivo de 90 días.",
    "Lechuga": "440.90 mm para un ciclo de vida de 82 días.",
    "Raps": "500 a 1000 mm por año. El periodo de cultivo puede ser de 70 a 120 días."
}

# Requerimientos hídricos para Colombia
requerimientos_hidricos_CO = {
    "Café": "4.31 a 5.14 mm por día.",
    "Palma de aceite": "1700 a 2000 mm por año.",
    "Maíz": "500 a 800 mm por todo el periodo de crecimiento, dividido entre sus etapas fenológicas, es decir, a medida que crece aumenta la cantidad requerida de agua.",
    "Yuca": "800 a 1800 mm de forma bien distribuida durante el año.",
    "Fréjol": "300 a 500 mm por el tiempo de producción (60 a 120 días). Además, depende del clima a más humedad menos agua.",
    "Aguacate": "3.78 y 4.5 mm por día.",
    "Caña de azúcar": "1500 a 2500 mm distribuido igualmente por temporada de crecimiento (15 a 16 meses).",
    "Algodón": "700 a 1300 mm por 150 a 180 días, incrementa el riego a medida que crece, disminuyendo un poco al final.",
    "Cacao": "1500 a 2500 mm de forma bien distribuida durante el año.",
    "Mango": "700 a 1000 mm por año. Dependiendo de la edad se recomienda al primer año (2 a 5 mm por día). Para 2 años (10 a 15 mm por día). Para 3 años (20-25 mm por día). Para 4 años (30 a 35 mm por día). De 4 años en adelante se recomienda (65-80 mm por día).",
    "Plátano": "1200 a 2200 mm por año dependiendo de la humedad.",
    "Arroz": "450 a 700 mm por 90 a 150 días dependiendo del clima y del periodo de crecimiento.",
    "Sorgo": "450 a 650 mm por 110 a 130 días, dependiendo del clima, incrementa la cantidad de riego a medida que crece y disminuye un poco al final.",
    "Soya": "1500 a 2500 mm distribuido igualmente por temporada de crecimiento (15 a 16 meses).",
    "Coco": "1500 mm anuales es lo ideal.",
    "Maní": "500 a 700 mm por periodo de crecimiento, repartido entre sus etapas de crecimiento incrementando la cantidad de agua requerida a medida que crece.",
    "Fique": "1000 a 1600 mm bien distribuidas a lo largo del año.",
    "Cítricos": "900 a 1200 mm por año.",
    "Caña brava": "800 a 1500 mm bien distribuidas por año."
}

requerimientos_hidricos_VE = {
    "arroz": "450 a 700 mm por 90 a 150 días dependiendo del clima y del periodo de crecimiento.",
    "caraotas (fréjol negro)": "300 a 500 mm por el tiempo de producción (60 a 120 días). Además, depende del clima; a más humedad, menos agua.",
    "fréjol": "300 a 500 mm por el tiempo de producción (60 a 120 días).",
    "maíz": "500 a 800 mm por todo el periodo de crecimiento, dividido entre sus etapas fenológicas, es decir, a medida que crece aumenta la cantidad de agua requerida.",
    "mango": "700 a 1000 mm por año. Dependiendo de la edad se recomienda al primer año (2 a 5 mm por día). Para 2 años (10 a 15 mm por día). Para 3 años (20-25 mm por día). Para 4 años (30 a 35 mm por día). De 4 años en adelante se recomienda (65-80 mm por día).",
    "tabaco": "400 a 600 mm por todo el periodo de crecimiento. Durante la primera semana donde emerge la semilla a plántulas se requiere 3 a 5 mm. Luego aumenta la cantidad de riego a medida que crece y disminuye un poco hacia el final.",
    "algodón": "700 a 1300 mm por 150 a 180 días, incrementa el riego a medida que crece, disminuyendo un poco al final.",
    "tomate": "400 a 600 mm por 90 a 120 días, depende del clima, incrementa el riego a medida que va creciendo y disminuye un poco al final.",
    "sorgo": "450 a 650 mm por 110 a 130 días, dependiendo del clima, incrementa la cantidad de riego a medida que crece y disminuye un poco al final.",
    "yuca": "800 a 1800 mm de forma bien distribuida durante el año.",
    "ñame": "3000 a 3500 mm distribuidas uniformemente por todo el año.",
    "girasol": "600 a 1000 mm dependiendo del clima y el periodo de crecimiento (130 a 200 días). Incrementando la cantidad de riego a medida que crece y disminuyendo un poco al final.",
    "plátano": "1200 a 2200 mm por año dependiendo de la humedad, a menos humedad más agua.",
    "caña de azúcar": "1500 a 2500 mm distribuido igualmente por temporada de crecimiento (15 a 16 meses).",
    "café": "4.31 a 5.14 mm por día.",
    "cacao": "1500 a 2500 mm de forma bien distribuida durante el año.",
    "ajonjolí": "300 a 600 mm bien distribuidos durante el ciclo, sobre todo durante la floración y producción de las semillas (ciclo de 90 a 95 días).",
    "papa": "500 a 700 mm por 120 a 150 días, incrementando la cantidad de riego a medida que crece.",
    "albahaca": "300 a 400 mm bien distribuidas durante un año. (Planta caduca anual).",
    "pepino": "678.18 mm para un ciclo de vida de 95 días.",
    "lechuga": "440.90 mm para un ciclo de vida de 82 días.",
    "guayabas": "Precipitación anual de 1000 a 3800 mm para una producción óptima todo el año.",
    "melón": "314.2 mm para un ciclo de vida de 80 días. Se recomienda que el riego incremente un poco en su fase de floración y maduración del fruto, disminuyendo un poco hacia la cosecha.",
    "zanahoria": "400 a 800 mm anualmente, cultivo bianual.",
    "maní": "500 a 700 mm por periodo de crecimiento, repartido entre sus etapas de crecimiento incrementando la cantidad de agua requerida a medida que crece.",
    "carambolo": "1800 a 2000 mm por año. Incrementando un poco la cantidad de agua en las fechas de floración y producción de frutos.",
    "acelga": "460.72 mm para un ciclo de cultivo de 90 días."
}

requerimientos_hidricos_BO = {
    "Arroz": "450 a 700 mm por 90 a 150 días dependiendo del clima y del periodo de crecimiento.",
    "Caraotas (fréjol negro)": "300 a 500 mm por el tiempo de producción (60 a 120 días). Además, depende del clima; a más humedad, menos agua.",
    "Fréjol": "300 a 500 mm por el tiempo de producción (60 a 120 días).",
    "Maíz": "500 a 800 mm por todo el periodo de crecimiento, dividido entre sus etapas fenológicas, es decir, a medida que crece aumenta la cantidad de agua requerida.",
    "Mango": "700 a 1000 mm por año. Dependiendo de la edad se recomienda al primer año (2 a 5 mm por día). Para 2 años (10 a 15 mm por día). Para 3 años (20-25 mm por día). Para 4 años (30 a 35 mm por día). De 4 años en adelante se recomienda (65-80 mm por día).",
    "Tabaco": "400 a 600 mm por todo el periodo de crecimiento. Durante la primera semana donde emerge la semilla a plántulas se requiere 3 a 5 mm. Luego aumenta la cantidad de riego a medida que crece y disminuye un poco hacia el final.",
    "Algodón": "700 a 1300 mm por 150 a 180 días, incrementa el riego a medida que crece, disminuyendo un poco al final.",
    "Tomate": "400 a 600 mm por 90 a 120 días, depende del clima, incrementa el riego a medida que va creciendo y disminuye un poco al final.",
    "Sorgo": "450 a 650 mm por 110 a 130 días, dependiendo del clima, incrementa la cantidad de riego a medida que crece y disminuye un poco al final.",
    "Yuca": "800 a 1800 mm de forma bien distribuida durante el año.",
    "Ñame": "3000 a 3500 mm distribuidas uniformemente por todo el año.",
    "Girasol": "600 a 1000 mm dependiendo del clima y el periodo de crecimiento (130 a 200 días). Incrementando la cantidad de riego a medida que crece y disminuyendo un poco al final.",
    "Plátano": "1200 a 2200 mm por año dependiendo de la humedad, a menos humedad más agua.",
    "Caña de azúcar": "1500 a 2500 mm distribuido igualmente por temporada de crecimiento (15 a 16 meses).",
    "Café": "4.31 a 5.14 mm por día.",
    "Cacao": "1500 a 2500 mm de forma bien distribuida durante el año.",
    "Ajonjolí": "300 a 600 mm bien distribuidos durante el ciclo, sobre todo durante la floración y producción de las semillas (ciclo de 90 a 95 días).",
    "Papa": "500 a 700 mm por 120 a 150 días, incrementando la cantidad de riego a medida que crece.",
    "Albahaca": "300 a 400 mm bien distribuidas durante un año. (Planta caduca anual).",
    "Pepino": "678.18 mm para un ciclo de vida de 95 días.",
    "Lechuga": "440.90 mm para un ciclo de vida de 82 días.",
    "Guayabas": "Precipitación anual de 1000 a 3800 mm para una producción óptima todo el año.",
    "Melón": "314.2 mm para un ciclo de vida de 80 días. Se recomienda que el riego incremente un poco en su fase de floración y maduración del fruto, disminuyendo un poco hacia la cosecha.",
    "Zanahoria": "400 a 800 mm anualmente, cultivo bianual.",
    "Maní": "500 a 700 mm por periodo de crecimiento, repartido entre sus etapas de crecimiento incrementando la cantidad de agua requerida a medida que crece.",
    "Carambolo": "1800 a 2000 mm por año. Incrementando un poco la cantidad de agua en las fechas de floración y producción de frutos.",
    "Acelga": "460.72 mm para un ciclo de cultivo de 90 días."
}

colPrec = ['#000000', '#8fbef9', '#1d7df2', '#124a6d', '#1b6a60', '#569975', '#8ec385', '#c5be7a', '#efb96e', '#da8559', '#cb5b4b', '#9b0121']
colSeq = ['#315481','#408ebf','#72c0da','#acddec','#5bbe9d','#fcce4f','#fd8c1c','#f1430e','#97221c']

def graficarDatos(matriz,nombre):
    nombre=str(nombre)+".png"
    fig,ax=plt.subplots()

    barras=matriz.replace(-999,0)
    puntos=matriz.loc[matriz['valor']<0].replace(-999,0)

    number = barras["valor"].astype("float64").max()+5
    rounded = int(round(number/10)*10)
    if rounded==0:
        rounded=5
    ax.bar(barras["fecha"], barras["valor"].astype('float64'), color="royalblue")
    plt.plot(puntos["fecha"], puntos["valor"].astype('float64'), 'X',c="red")
    plt.ylim(0, rounded)

    plt.xticks([pandas_datetime.strftime("%Y-%m-%d") for pandas_datetime in barras["fecha"]],rotation=90, ha="right")
    plt.legend(labels=["Días sin datos","Precipitación"])
    ax.set(title = "Reportes de precipitación diaria",
       xlabel = "Fecha",
       ylabel = "Precipitación (mm)")
    plt.savefig(nombre)
    return nombre


def dibujarTablaDeMatriz(self, table_data, title='', data_size=10, title_size=12, align_data='L', align_header='L',
				 cell_width='even', x_start='x_default', emphasize_data=[], emphasize_style=None,
				 emphasize_color=(0, 0, 0), line_height=8, parametro='', dfValues=None, yyyy=0, mm=0):
	global counterDF
	"""
	table_data:
				list of lists with first element being list of headers
	title:
				(Optional) title of table (optional)
	data_size:
				the font size of table data
	title_size:
				the font size fo the title of the table
	align_data:
				align table data
				L = left align
				C = center align
				R = right align
	align_header:
				align table data
				L = left align
				C = center align
				R = right align
	cell_width:
				even: evenly distribute cell/column width
				uneven: base cell size on lenght of cell/column items
				int: int value for width of each cell/column
				list of ints: list equal to number of columns with the widht of each cell / column
	x_start:
				where the left edge of table should start
	emphasize_data:
				which data elements are to be emphasized - pass as list
				emphasize_style: the font style you want emphaized data to take
				emphasize_color: emphasize color (if other than black)
	line_height: para dfinir el amaño de las lineas, por un error en la programacion que se evidenciaba cuando se intentaba poner varias tablas en la misma pagina. La primera tabla se imprimia bien, pero las subsiguientes no. 
	"""

	self.add_font("dejavusans", "", "/usr/share/fonts/dejavu/DejaVuSans.ttf", uni=True)
	default_style = self.font_style
	if emphasize_style == None:
		emphasize_style = default_style

	# default_font = self.font_family
	# default_size = self.font_size_pt
	# default_style = self.font_style
	# default_color = self.color # This does not work

	# Get Width of Columns
	def get_col_widths():
		col_width = cell_width
		if col_width == 'even':
			col_width = self.epw / len(data[0]) - 1  # distribute content evenly   # epw = effective page width (width of page not including margins)
		elif col_width == 'uneven':
			col_widths = []

			# searching through columns for largest sized cell (not rows but cols)
			counter=0
			for col in range(len(table_data[0])):  # for every row
				longest = 0
				for row in range(len(table_data)):
					cell_value = str(table_data[row][col])
					value_length = self.get_string_width(cell_value)
					if value_length > longest:
						longest = value_length
				col_widths.append(longest + 4)  # add 4 for padding
			col_width = col_widths

			### compare columns

		elif isinstance(cell_width, list):
			col_width = cell_width  # TODO: convert all items in list to int
		else:
			# TODO: Add try catch
			col_width = int(col_width)
		return col_width

	# Convert dict to lol
	# Why? because i built it with lol first and added dict func after
	# Is there performance differences?
	if isinstance(table_data, dict):
		header = [key for key in table_data]
		data = []
		for key in table_data:
			value = table_data[key]
			data.append(value)
		# need to zip so data is in correct format (first, second, third --> not first, first, first)
		data = [list(a) for a in zip(*data)]

	else:
		header = table_data[0]
		data = table_data[1:]

	#line_height = self.font_size * 1.5

	col_width = get_col_widths()
	self.set_font(family="Times", size=title_size)
	# Get starting position of x
	# Determin width of table to get x starting point for centred table
	if x_start == 'C':
		table_width = 0
		if isinstance(col_width, list):
			for width in col_width:
				table_width += width
		else:  # need to multiply cell width by number of cells to get table width
			table_width = col_width * len(table_data[0])
		# Get x start by subtracting table width from pdf width and divide by 2 (margins)
		margin_width = self.w - table_width
		# TODO: Check if table_width is larger than pdf width

		center_table = margin_width / 2  # only want width of left margin not both
		x_start = center_table
		self.set_x(x_start)
	elif isinstance(x_start, int):
		self.set_x(x_start)
	elif x_start == 'x_default':
		x_start = self.set_x(self.l_margin)

	# TABLE CREATION #

	# add title
	if title != '':
		self.multi_cell(0, line_height, title, border=0, align='j', ln=3, max_line_height=self.font_size)
		self.ln(line_height)  # move cursor back to the left margin

	self.set_font(size=data_size)
	# add header
	y1 = self.get_y()
	if x_start:
		x_left = x_start
	else:
		x_left = self.get_x()
	x_right = self.epw + x_left
	if not isinstance(col_width, list):
		if x_start:
			self.set_x(x_start)
		counter=0
		for datum in header:
			if(counter==0):
				self.multi_cell(col_width, line_height, datum, border=0, align=align_header, ln=3,
								max_line_height=self.font_size)
			else:
				self.multi_cell(col_width, line_height, datum, border=0, align=align_header, ln=3,
								max_line_height=self.font_size)
			x_right = self.get_x()
			counter+=1
		self.ln(line_height)  # move cursor back to the left margin
		y2 = self.get_y()
		self.line(x_left, y1, x_right, y1)
		self.line(x_left, y2, x_right, y2)
		for row in data:
			if x_start:  # not sure if I need this
				self.set_x(x_start)
			counter=0
			for datum in row:
				if datum in emphasize_data:
					self.set_text_color(*emphasize_color)
					self.set_font(style=emphasize_style)
					try:
						if(counter==0):
							self.multi_cell(col_width, line_height, datum, border=0, align=align_data, ln=3,
											max_line_height=self.font_size)
						else:
							self.multi_cell(col_width, line_height, datum, border=0, align=align_data, ln=3,
											max_line_height=self.font_size)
					except:
						self.set_font("Emojis", "", 12)
						if(counter==0):
							self.multi_cell(col_width, line_height, datum, border=0, align=align_data, ln=3,
											max_line_height=self.font_size)
						else:
							self.multi_cell(col_width, line_height, datum, border=0, align=align_data, ln=3,
											max_line_height=self.font_size)
						self.set_font(family="Times", size=data_size)
					self.set_text_color(0, 0, 0)
					self.set_font(style=default_style)
				else:
					if(parametro=='precipitacion' and counter==0):
						# Crea instancias de los objetos de marcadores
						numMonthDays = monthrange(yyyy, mm)[1]
						indexMinMaxQC = numMonthDays - int(round(numMonthDays*0.20,0))#usaré circulos para calidad excelente (mayor o igual a 24 días tomados, equivale al 20% de datos faltantes, que es considerado como buena calidad), 
						indexMinMidQC = numMonthDays - int(round(numMonthDays*0.50,0))#cuadraditos para calidad media (entre 15 y 24 dias monitoreados, o sea hasta 50% faltantes) 
						dias = dfValues.loc[dfValues.index[counterDF], 'dias']
						total= dfValues.loc[dfValues.index[counterDF], 'total']

						if(dias>=indexMinMaxQC):
							marker = '\u2605'  # Estrella
						elif((dias>=indexMinMidQC) & (dias<indexMinMaxQC)):
							marker = '\u25A0'  # Cuadrado
						elif(dias<indexMinMidQC):
							marker = '\u25CF'  # Círculo
						
						hex_color = asignar_color_hex_prec(total)
						simbolo =' ' + marker # Añadir formato de color ANSI
					elif(parametro=='sequia' and counter==0 ):
						# Configurar opciones para mostrar todas las filas y columnas
						
						total= dfValues.loc[dfValues.index[counterDF], 'total']
						hex_color = asignar_color_hex_seq(total)
						marker = '\u25B2'  # Triángulo apuntando hacia arriba
						simbolo =' ' + marker # Añadir formato de color ANSI					
					else:
						simbolo=''
						
					try:
						self.set_font("dejavusans","",8)
						if(i==0):
							
							# Asignar color al símbolo antes de agregarlo al texto
							self.set_text_color(hex_to_rgb(hex_color))
							self.multi_cell(5, line_height, simbolo, border=0, align=align_data, ln=3,
							max_line_height=self.font_size)
							self.set_text_color(0, 0, 0)  # Restaurar a color negro después de agregar el
							self.multi_cell(col_width-5, line_height, datum, border=0, align=align_data, ln=3,
							max_line_height=self.font_size)
						else:
							self.multi_cell(col_width, line_height, datum, border=0, align=align_data, ln=3,
							max_line_height=self.font_size)
							
					except:
						self.multi_cell(col_width, line_height, datum+simbolo, border=0, align=align_data, ln=3,
						max_line_height=self.font_size)
				counter+=1
			counterDF+=1
			self.ln(line_height)  # move cursor back to the left margin
			counterFila=+1
			
	else:
		if x_start:
			self.set_x(x_start)
		for i in range(len(header)):
			datum = header[i]
			self.multi_cell(col_width[i], line_height, datum, border=0, align=align_header, ln=3,
							max_line_height=self.font_size)
			x_right = self.get_x()
		self.ln(line_height)  # move cursor back to the left margin
		y2 = self.get_y()
		self.line(x_left, y1, x_right, y1)
		self.line(x_left, y2, x_right, y2)
		for j in range(len(data)):
			if x_start:
				self.set_x(x_start)
			row = data[j]
			counter=0
			for i in range(len(row)):
				datum = row[i]
				if not isinstance(datum, str):
					datum = str(datum)
				adjusted_col_width = col_width[i]
				if datum in emphasize_data:
					self.set_text_color(*emphasize_color)
					self.set_font(style=emphasize_style)
					try:
						if(counter==0):
							self.multi_cell(col_width, line_height, datum, border=0, align=align_data, ln=3,
											max_line_height=self.font_size)
						else:
							self.multi_cell(col_width, line_height, datum, border=0, align=align_data, ln=3,
											max_line_height=self.font_size)
					except:
						self.set_font("Emojis", "", 12)
						if(counter==0):
							self.multi_cell(col_width, line_height, datum, border=0, align=align_data, ln=3,
											max_line_height=self.font_size)
						else:
							self.multi_cell(col_width, line_height, datum, border=0, align=align_data, ln=3,
											max_line_height=self.font_size)
						self.set_font(family="Times", size=data_size)
					self.set_text_color(0, 0, 0)
					self.set_font(style=default_style)
				else:
					
					hex_color = '#000000'
					if(parametro=='precipitacion' and counter==0):
						# Crea instancias de los objetos de marcadores
						numMonthDays = monthrange(yyyy, mm)[1]
						indexMinMaxQC = numMonthDays - int(round(numMonthDays*0.20,0))#usaré circulos para calidad excelente (mayor o igual a 24 días tomados, equivale al 20% de datos faltantes, que es considerado como buena calidad), 
						indexMinMidQC = numMonthDays - int(round(numMonthDays*0.50,0))#cuadraditos para calidad media (entre 15 y 24 dias monitoreados, o sea hasta 50% faltantes) 
						dias = dfValues.loc[dfValues.index[counterDF], 'dias']
						total= dfValues.loc[dfValues.index[counterDF], 'total']
						pd.set_option('display.max_rows', None)
						pd.set_option('display.max_columns', None)
						
						if(dias>=indexMinMaxQC):
							marker = '\u2605'  # Estrella
						elif((dias>=indexMinMidQC) & (dias<indexMinMaxQC)):
							marker = '\u25A0'  # Cuadrado
						elif(dias<indexMinMidQC):
							marker = '\u25CF'  # Círculo
						hex_color = asignar_color_hex_prec(total)
						simbolo =' ' + marker # Añadir formato de color ANSI	
							
					elif(parametro=='sequia' and counter==0 ):
						# Configurar opciones para mostrar todas las filas y columnas
						
						total= dfValues.loc[dfValues.index[counterDF], 'total']
						hex_color = asignar_color_hex_seq(total)
						marker = '\u25B2'  # Triángulo apuntando hacia arriba
						simbolo =' ' + marker # Añadir formato de color ANSI
						
					else:
						simbolo=''
					
						
					try:
						
						self.set_font("dejavusans","",8)
						if(i==0):
							
							# Asignar color al símbolo antes de agregarlo al texto
							self.set_text_color(hex_to_rgb(hex_color))
							self.multi_cell(5, line_height, simbolo, border=0, align=align_data, ln=3,
							max_line_height=self.font_size)
							self.set_text_color(0, 0, 0)  # Restaurar a color negro después de agregar el
							self.multi_cell(adjusted_col_width-5, line_height, datum, border=0, align=align_data, ln=3,
							max_line_height=self.font_size)

						else:
							self.multi_cell(adjusted_col_width, line_height, datum, border=0, align=align_data, ln=3,
							max_line_height=self.font_size)
 
							
					except:
						self.multi_cell(adjusted_col_width, line_height, datum+simbolo, border=0, align=align_data, ln=3,
						max_line_height=self.font_size)

				counter+=1
			counterDF+=1	
			self.ln(line_height)  # move cursor back to the left margin

	y3 = self.get_y()
	self.line(x_left, y3, x_right, y3)


def insertarPaginaPortada(pdf,texto,mes):
    pdf.add_page()
    pdf.portada(texto,mes)


def insertarPaginaReportesEstacion(pdf,yIni,mIni,dIni,yEnd,mEnd,dEnd,dfDiarios, dfAcums, dfObs):
	pdf.add_page(orientation="P")
	numMiss = acc.obtenerDiasFaltantesDatos(yIni,mIni,dIni,yIni,mIni,dEnd,dfDiarios,dfAcums)
	pdf.dibujarTablasReportes(dfDiarios, dfAcums, dfObs, numMiss)

def insertarPaginaIndices(pdf,conceptos,imagen,acu5dias,acu10dias,acu15dias,valores):
    pdf.add_page(orientation="P")
    pdf.conceptos(conceptos)
    pdf.diagrama_barras(imagen)
    pdf.dibujarTablasAgregados(acu5dias,acu10dias,acu15dias)
    pdf.cuadro_indices(valores)
    os.remove(imagen)

def insertarPaginaMapaPrecipitacionMensual(pdf,isoCty,yIni,mIni,dfValStMon):
	global counterDF
	counterDF=0
	dfValStMon1 = dfValStMon[['codigo','nombre','total','ubicacion']]
	if len(dfValStMon1.index)>0:
		if isoCty == "EC":
			""" numTbls=3
			numRegPerPage=38#9,9,9
			lstTblRegs=[10,14,14] """
			numTbls=2
			numRegPerPage=18#9,9
			lstTblRegs=[9,9]
		elif isoCty == "BO":
			numTbls=3
			numRegPerPage=38#9,9,9
			lstTblRegs=[10,14,14]
		elif isoCty== "CL":
			numTbls=3
			numRegPerPage=37#debe coincidir con la suma de los elements de lstTblRegs
			lstTblRegs=[15,11,11]
		elif isoCty== "VE":
			numTbls=2
			numRegPerPage=18#9,9
			lstTblRegs=[9,9]
		elif isoCty== "CO":
			numTbls=3
			numRegPerPage=27#9,9,9
			lstTblRegs=[9,9,9]
		arrMtxRegs = acc.dfPrecEstacionesMensualAMatriz(dfValStMon1,numRegPerPage,lstTblRegs)
		intNumPags=math.ceil(len(dfValStMon1.index)/numRegPerPage)
		idxMtx=0
		for idx in range(1,intNumPags+1):
			pdf.add_page(orientation="P")
			imagen = "/var/py/volunclima/salidas/prec/mapas/"+isoCty+"/Volunclima-"+isoCty+'-PrecMensual-'+str(yIni)+'_'+str(mIni)+'.png'
			if isoCty == "EC":
				"pdf.mapaPrecipitacion(imagen,9, 35, 110)"
				pdf.mapaPrecipitacion(imagen,50, 35, 110)
			elif isoCty== "BO":
				pdf.mapaPrecipitacion(imagen,9, 35, 110)
			elif isoCty== "CL":
				pdf.mapaPrecipitacion(imagen, 9, 35, 110)
			elif isoCty== "VE":
				pdf.mapaPrecipitacion(imagen, 20, 35, 160)
			elif isoCty== "CO":
				pdf.mapaPrecipitacion(imagen, 9, 35, 110)
			idxEnd=idx*numTbls
			if idxEnd>len(arrMtxRegs):
				idxEnd=len(arrMtxRegs)
			pdf.insertarTablaMensualesEstaciones(isoCty,arrMtxRegs[idxMtx:idxEnd],dfValStMon,yIni,mIni)
			idxMtx=idxEnd#idxMtx=idxEnd+1
		counterDF=0
	else:
		pdf.add_page(orientation="P")
		imagen = "/var/py/volunclima/salidas/prec/mapas/"+isoCty+"/Volunclima-"+isoCty+'-PrecMensual-'+str(yIni)+'_'+str(mIni)+'.png'
		strQuote = "No se recibieron reportes de precipitación."
		if isoCty == "EC":
			""" pdf.mapaPrecipitacion(imagen,9, 35, 110)
			pdf.insertLabel(115,38,85,strQuote,"QTE")#x,y,w,msg,format """
			pdf.mapaPrecipitacion(imagen, 50, 35, 110)
			#quizas hay que cambiar el 15 en caso de que no haya reportes de precipitacion (no creo que pase nunca)
			pdf.insertLabel(15,125,277,strQuote,"QTE")
		elif isoCty == "BO":
			pdf.mapaPrecipitacion(imagen,9, 35, 110)
			pdf.insertLabel(115,38,85,strQuote,"QTE")
		elif isoCty== "CL":
			pdf.mapaPrecipitacion(imagen, 9, 35, 110)
			pdf.insertLabel(115,35,85,strQuote,"QTE")
		elif isoCty== "VE":
			pdf.mapaPrecipitacion(imagen, 20, 35, 160)
			pdf.insertLabel(9,125,277,strQuote,"QTE")
		elif isoCty== "CO":
			pdf.mapaPrecipitacion(imagen, 9, 35, 110)
			pdf.insertLabel(115,35,85,strQuote,"QTE")


def insertarPaginaMapaPercepcionSequia(pdf,isoCty,yIni,mIni,dfReps):
	global counterDF
	counterDF=0
	imagen = "/var/py/volunclima/salidas/seq/"+isoCty+"/Volunclima-"+isoCty+'-SequiaMensual-'+str(yIni)+'_'+str(mIni)+'.png'
	strLayout = "L"
	if len(dfReps.index)>0:
		if isoCty == "EC":
			numRegPerPage=10
			strLayout = "P"
		elif isoCty== "BO":
			numRegPerPage=10
		elif isoCty== "CL":
			numRegPerPage=10
		elif isoCty== "VE":
			numRegPerPage=10
			strLayout = "P"
		elif isoCty== "CO":
			numRegPerPage=10
		arrMtxRegs = acc.dfReportesSequiaAMatriz(dfReps,isoCty,numRegPerPage)
		intNumPags=math.ceil(len(dfReps.index)/numRegPerPage)

		for idx in range(intNumPags):
			pdf.add_page(orientation=strLayout)
			if isoCty == "EC":
				""" pdf.mapaSequias(isoCty,imagen,9, 35, 110) """
				pdf.mapaSequias(isoCty,imagen, 50, 35, 110)
			elif isoCty== "CL":
				pdf.mapaSequias(isoCty,imagen, 9, 35, 110)
			elif isoCty== "VE":
				pdf.mapaSequias(isoCty,imagen, 20, 35, 160)
			elif isoCty== "CO":
				pdf.mapaSequias(isoCty,imagen, 9, 35, 110)
			pdf.insertarTablaReportesSequias(isoCty,arrMtxRegs[idx],dfReps,yIni,mIni)
		counterDF=0
	else:
		strQuote = "No se recibieron encuestas de percepción de sequías."
		if (isoCty == "VE" or isoCty == "EC"):
			pdf.add_page(orientation="P")
		else:
			pdf.add_page(orientation="L")
		if isoCty == "EC":
			""" pdf.mapaSequias(isoCty,imagen,9, 35, 110)
			pdf.insertLabel(125,38,160,strQuote,"QTE") """
			pdf.mapaSequias(isoCty,imagen, 50, 35, 110)
			pdf.insertLabel(26,125,160,strQuote,"QTE")
		elif isoCty == "BO":
			pdf.mapaSequias(isoCty,imagen,9, 35, 110)
			pdf.insertLabel(125,38,160,strQuote,"QTE")
		elif isoCty== "CL":
			pdf.mapaSequias(isoCty,imagen, 9, 35, 110)
			pdf.insertLabel(125,35,160,strQuote,"QTE")
		elif isoCty== "VE":
			pdf.mapaSequias(isoCty,imagen, 20, 35, 160)
			pdf.insertLabel(20,125,160,strQuote,"QTE")
		elif isoCty== "CO":
			pdf.mapaSequias(isoCty,imagen, 9, 35, 110)
			pdf.insertLabel(125,35,160,strQuote,"QTE")


def insertarPaginaExtremos(pdf,isoCty,yIni,mIni,dfExtreme):
	if len(dfExtreme.index)>0:
		numRegPerPage=10
		arrMtxRegs = acc.dfExtremosAMatriz(dfExtreme,numRegPerPage)
		intNumPags=math.ceil(len(dfExtreme.index)/numRegPerPage)
		for idx in range(intNumPags):
			pdf.add_page(orientation="L")
			pdf.insertarTablaExtremos(isoCty,arrMtxRegs[idx])
	else:
			pdf.add_page(orientation="L")
			pdf.insertarTablaExtremos(isoCty,None)

def insertarPaginaAgradecimientos(pdf,dfObs):
	if len(dfObs.index)>0:
		numTbls=2
		numRegPerPage=40#40
		lstTblRegs=[20,20]#20,20
		arrMtxObs = acc.dfAgradecimientosAMatriz(dfObs,numRegPerPage,lstTblRegs)
		intNumPags=math.ceil(len(dfObs.index)/numRegPerPage)
		idxMtx=0
		for idx in range(1,intNumPags+1):
			pdf.add_page(orientation="P")
			pdf.insertarAgradecimiento(True)
			idxEnd=idx*numTbls
			if idxEnd>len(arrMtxObs):
				idxEnd=len(arrMtxObs)
			pdf.insertarTablasObservadores(arrMtxObs[idxMtx:idxEnd])
			idxMtx=idxEnd#-1
	else:
		pdf.add_page(orientation="P")
		pdf.insertarAgradecimiento(False)

def insertarPaginaPronosticos(pdf,isoCty):
    # Agregar la página de pronósticos con los 4 PNG y el texto deseado
    pdf.add_page(orientation="P")
    pdf.insertarPredicciones(isoCty)

def insertarPaginaReqHidricosyConsejos(pdf,isoCty):
    # Agregar la página de pronósticos con los 4 PNG y el texto deseado
    pdf.add_page(orientation="P")
    pdf.insertarTablaRequerimientosHidricosyConsejos(isoCty)

def generarBoletinGeneral(isoCty,dfAllObs,dfValStMon,dfRepSeqs,dfExtreme,yIni,mIni):
	#generarBoletinDeEstacion
	strTitulo="Centro Internacional para la Investigación del Fenómeno de El Niño"
	#Texto en las pagians
	strCountry=acc.obtenerNombrePais(isoCty)
	portada_texto="Boletín de Volunclima\n"+strCountry
	strMonth = acc.obtenerNombreMes(int(mIni))+" "+str(int(yIni))

	#crear pdf
	pdf=PDFVolunclimaJournal("P","mm","A4")
	pdf.alias_nb_pages()
	pdf.set_auto_page_break(auto=True,margin=15)
	pdf.add_font("Emojis", fname="/var/py/volunclima/scripts/boletines/unifont/NotoSansSymbols2-Regular.ttf", uni=True)#https://fonts.google.com/noto/specimen/Noto+Sans+Symbols+2/tester?noto.query=noto+sans+symbols... 

	insertarPaginaPortada(pdf,portada_texto,strMonth)
	insertarPaginaMapaPrecipitacionMensual(pdf,isoCty,yIni,mIni,dfValStMon)
	insertarPaginaMapaPercepcionSequia(pdf,isoCty,yIni,mIni,dfRepSeqs)
	insertarPaginaExtremos(pdf,isoCty,yIni,mIni,dfExtreme)
	insertarPaginaPronosticos(pdf,isoCty)
	if(isoCty=="EC"):
		insertarPaginaPronosticos(pdf,"GA")
	insertarPaginaReqHidricosyConsejos(pdf,isoCty)
	insertarPaginaAgradecimientos(pdf,dfAllObs)
	dirName = "/var/py/volunclima/salidas/boletines/"+isoCty+"/"+str(yIni)
	nombre_pdf = dirName + "/Volunclima-" + strCountry + "_" + str(strMonth) + ".pdf"
	if not os.path.exists(dirName):
		os.makedirs(dirName)
		pdf.output(nombre_pdf)
	else:
		pdf.output(nombre_pdf)
	return nombre_pdf


def generarBoletinEstaciones(isoCty,dfAllObs,strStName,dfValStMon,dfRepSeqs,dfExtreme,dfObs,dfTotalVals,dfValsDD,dfValAcums,yIni,mIni,dIni,yEnd,mEnd,dEnd):
	#generarBoletinDeEstacion
	strTitulo="Centro Internacional para la Investigación del Fenómeno de El Niño"
	#Texto en las pagians
	portada_texto="Boletín de Volunclima\nEstación\n"+strStName
	strMonth = acc.obtenerNombreMes(int(mIni))+" "+str(int(yIni))

	#crear pdf
	pdf=PDFVolunclimaJournal("P","mm","A4")
	pdf.alias_nb_pages()
	pdf.set_auto_page_break(auto=True,margin=15)
	pdf.add_font("Emojis", fname="/var/py/volunclima/scripts/boletines/unifont/NotoSansSymbols2-Regular.ttf", uni=True)#https://fonts.google.com/noto/specimen/Noto+Sans+Symbols+2/tester?noto.query=noto+sans+symbols... 

	#primera pagina
	insertarPaginaPortada(pdf,portada_texto,strMonth)
	insertarPaginaMapaPrecipitacionMensual(pdf,isoCty,yIni,mIni,dfValStMon)
	insertarPaginaMapaPercepcionSequia(pdf,isoCty,yIni,mIni,dfRepSeqs)
	insertarPaginaExtremos(pdf,isoCty,yIni,mIni,dfExtreme)
	insertarPaginaPronosticos(pdf,isoCty)
	if(isoCty=="EC"):
		insertarPaginaPronosticos(pdf,"GA")
	insertarPaginaReqHidricosyConsejos(pdf,isoCty)
	insertarPaginaReportesEstacion(pdf,yIni,mIni,dIni,yEnd,mEnd,dEnd,dfValsDD, dfValAcums, dfObs)
	
	#boletin_pdf.boletin_pdf
	#DECODIFICANDO LAS TRAZAS
	dfValsDD.loc[dfValsDD['valor']==-888,'valor']=0#dfValsDD.replace({'valor': -888},0, inplace=True)#dfVals.loc[dfVals['valor']==-888] = 0#.loc[row_indexer,col_indexer] = value
	dfValAcums.loc[dfValAcums['valor']==-888,'valor']=0#dfValAcums.replace({'valor': -888},0, inplace=True)
	dfTotalVals.loc[dfTotalVals['valor']==-888,'valor']=0#dfTotalVals.replace({'valor': -888},0, inplace=True)
	dfValsDD.loc[dfValsDD['valor']==-777,'valor']=279.4
	dfValAcums.loc[dfValAcums['valor']==-777,'valor']=279.4
	dfTotalVals.loc[dfTotalVals['valor']==-777,'valor']=279.4
	
	if len(dfValsDD.index)>0:#Hay reportes diarios en el periodo?
		if len(dfTotalVals.index) >= 5*365:
			BI_Calculado,BS_Calculado = acc.obtenerUmbrales(dfTotalVals)
			dfVals,dfValsOutliers = acc.obtenerAtipicos(dfValsDD,BI_Calculado,BS_Calculado)
		else:
			dfVals = dfValsDD.copy()#POR QUÉ NO SE USAN LOS OUTLIERS?
	else:
		dfVals = dfValsDD.copy()

	if len(dfVals.index)>0:
		#Dias lluvia
		diasSecos = len(dfVals.loc[dfVals['valor']<1].index)
		diasHumedos = len(dfVals.loc[dfVals['valor']>= 1].index)
		#secos_humedos=obtenerDiasSecosHumedos(dfPrec,limite)
		R10 = len(dfVals.loc[dfVals['valor']>= 10].index)#obtenerDiasSecosHumedos(dfPrec,10)[1]
		R20 = len(dfVals.loc[dfVals['valor']>= 20].index)#obtenerDiasSecosHumedos(dfPrec,20)[1]
		SDII  = acc.obtenerSDII(dfVals, dfValAcums, 0)
		totPrec = acc.obtenerPrecipitacionTotal(dfVals, dfValAcums, 0)
		CDD, CWD = acc.obtenerCDDCWD(dfVals,yIni,mIni,dIni,yEnd,mEnd,dEnd,1)
	else:
		diasSecos = -999
		diasHumedos = -999
		R10 = -999
		R20 = -999
		SDII  = -999
		totPrec = -999
		CDD = -999
		CWD = -999

	dfAcu5=acc.obtenerAgregadosPorPeriodoDias(dfVals,dfValAcums,5,yIni,mIni,dIni,yEnd,mEnd,dEnd)
	dfAcu10=acc.obtenerAgregadosPorPeriodoDias(dfVals,dfValAcums,10,yIni,mIni,dIni,yEnd,mEnd,dEnd)
	dfAcu15=acc.obtenerAgregadosPorPeriodoDias(dfVals,dfValAcums,15,yIni,mIni,dIni,yEnd,mEnd,dEnd)
	indices_concepto= ['Índice Simple de Intensidad Diaria ' + "(SDII): la precipitación total divida para el número de dias con precipitación",
		'R10: ' + "número de días con precipitación sobre los 10 mm",
		'R20: ' + "número de días con precipitación sobre los 20 mm",
		'CWD: ' + "número de días consecutivos con precipitación mayor a 1 mm",
		"CDD: " + "número de días consecutivos con precipitación menor a 1 mm",
		"Días de lluvia: " + "número de días con precipitación mayor a 1 mm",
		"Agregados: " + "total de precipitación en un período de tiempo (cada: 5 días, 10 días, 15 días)",
		"Precipitación total (PRCTOT): total de precipitación durante todo el mes"]
	valores_indices = [
	'SDII= ' + str(round(SDII, 2)),
	'R10= ' + str(R10),
	'R20= ' + str(R20),
	'CWD= ' + str(CWD),
	"CDD= " + str(CDD),
	"Días secos= " + str(diasSecos),
	"Días de lluvia= " + str(diasHumedos),
	"PRCTOT= " + str(round(totPrec,1))]
	
	dfValsFilled = acc.rellenarRegistros(dfVals,yIni,mIni,dIni,yEnd,mEnd,dEnd)
	barras=graficarDatos(dfValsFilled,"barras en "+strStName)
	insertarPaginaIndices(pdf,indices_concepto,barras,dfAcu5,dfAcu10,dfAcu15,valores_indices)
	insertarPaginaAgradecimientos(pdf,dfAllObs)													 
	dirName = "/var/py/volunclima/salidas/boletines/"+isoCty+"/"+str(yIni)
	nombre_pdf = dirName + "/" + strStName + "_" + str(strMonth) + ".pdf"
	if not os.path.exists(dirName):
		os.makedirs(dirName)
		pdf.output(nombre_pdf)
	else:
		pdf.output(nombre_pdf)
	return nombre_pdf
#nombre_boletin=boletin_pdf(df,tipo="DF",datos_estacion=nombre_del_archivo)


class PDFVolunclimaJournal(FPDF):
	def header(self):
		titulo="Centro Internacional para la Investigación del Fenómeno de El Niño"
		self.set_font("times","B",12)
		title_w=self.get_string_width(titulo)+6
		doc_w=self.w
		self.set_x((doc_w-title_w-35)/2)
		#self.set_x(0)
		self.set_y(0)

		self.set_fill_color(4,57, 103)
		self.set_text_color(255,255,255)
		self.cell(0,20,titulo, border=0,ln=1,fill=1)
		self.image("logos.png", 155, 3, 45)
		self.ln(20)
	#pie de pagina
	def footer(self):
		self.set_y(-15)
		self.set_font("times","I",10)
		self.set_text_color(169,169,169)
		self.cell(0,10,f'{self.page_no()}/{{nb}}',align='C')
	
	def insertLabel(self,x,y,w,msg,format):
		self.set_y(y)
		self.set_x(x)
		if format=="QTE":
			self.set_text_color(0, 0, 0)
			self.set_font("times", "", 16)
			self.cell(w, 12, msg, align='C')
		else:
			self.cell(w, 12, msg)#Cell(float w [, float h [, string txt [, mixed border [, int ln [, string align [, boolean fill [, mixed link]]]]]]])

	#portada
	def portada(self,portada,fecha):
		self.set_y(110)
		self.set_x(110)
		self.set_font("times", "B", 24)
		self.multi_cell(90, 20, portada, align='C')
		self.set_x(130)
		self.set_font("times", "I", 16)
		self.set_text_color(51,63,80)
		self.cell(50,12,fecha,align="C")
		self.image("logo_CIIFEN.png", 20, 100, 80)
		self.ln()
	#segunda pagina
	def conceptos(self,conceptos):
		# titulo de indices:conceptos
		self.set_y(25)
		self.set_font("times", "B", 16)
		self.set_fill_color(29, 46, 51)
		self.set_text_color(255, 255, 255)
		self.cell(190, 10, "Índices", align='C', fill=1)
		#Nota
		self.set_y(38)#self.set_y(205)
		self.set_text_color(0, 0, 0)
		self.set_font("times", "", 10)
		self.cell(190, 10, "NOTA: Los índices presentados son calculados exclusivamente con los reportes de precipitación diaria. En el caso de los agregados,")
		self.set_y(42)
		self.cell(190, 10, "se consideran los reportes acumulados enviados siempre y cuando el intervalo de fechas del reporte estén contenidas totalmente en ")
		self.set_y(46)
		self.cell(190, 10, "el periodo de tiempo analizado.")
		#texto
		self.set_font("times", "", 12)
		self.set_y(55)
		for i in conceptos:
			self.cell(8, 9, i, ln=1)

	#diagrama de datos
	def diagrama_barras(self,imagen):
		# titulo de graficos
		# self.set_y(120)
		# self.set_font("times", "B", 16)
		# self.set_fill_color(29, 46, 51)
		# self.set_text_color(255, 255, 255)
		# self.cell(190, 9, "Gráficos", align='C', fill=1)
		# imagen
		self.image(imagen, 2, 125, 130)
		# texto de los indices
		self.set_y(130)
		self.set_text_color(0, 0, 0)
		#valores de los indices

	def cuadro_indices(self,valores):
		self.set_y(230)
		self.set_x(15)
		self.cell(104, 52, border=1)#95, 50, border=1)
		self.set_y(233)
		self.set_x(20)
		self.set_font("times", "", 11)
		self.cell(8, 5, "Indices de precipitación")
		self.set_y(240)
		for i in valores:
			self.set_x(20)
			self.cell(15, 5, i, ln=1)


	#tablas de agregados
	def dibujarTablasAgregados(self,acu5dias,acu10dias,acu15dias):
		self.set_y(130)
		self.set_text_color(0, 0, 0)
		#dibujarTablaDeMatriz(self,acu5dias, "Acumulados cada 5 días", 9.5, 12, "C", "L", cell_width=23, x_start=130)
		mtxAcum = acc.dfAgregadosAMatriz(acu5dias)
		dibujarTablaDeMatriz(self,mtxAcum, "Acumulados cada 5 días", 9.5, 12, "L", "C", cell_width=23, x_start=130)
		self.set_y(198)
		#dibujarTablaDeMatriz(self,acu10dias, "Acumulados cada 10 días", 9.5, 12, "C", "L", cell_width=23, x_start=130)#cell_width="uneven", x_start=130)
		mtxAcum = acc.dfAgregadosAMatriz(acu10dias)
		dibujarTablaDeMatriz(self,mtxAcum, "Acumulados cada 10 días", 9.5, 12, "L", "C", cell_width=23, x_start=130)#cell_width="uneven", x_start=130)
		self.set_y(243)
		#dibujarTablaDeMatriz(self,acu15dias, "Acumulados cada 15 días", 9.5, 12, "C", "L", cell_width=23, x_start=130)#cell_width="uneven", x_start=130)
		mtxAcum = acc.dfAgregadosAMatriz(acu15dias)
		dibujarTablaDeMatriz(self,mtxAcum, "Acumulados cada 15 días", 9.5, 12, "L", "C", cell_width=23, x_start=130)#cell_width="uneven", x_start=130)

	def dibujarTablasReportes(self, dfDiarios, dfAcums, dfObs, numMiss):
		# titulo
		self.set_y(25)
		self.set_font("times", "B", 16)
		self.set_fill_color(29, 46, 51)
		self.set_text_color(255, 255, 255)
		self.cell(190, 10, "Reportes recibidos de la estación", align='C', fill=1)
		self.set_text_color(0, 0, 0)
		self.set_font("times", "", 12)
		numAccum = int(dfAcums.numdias.sum())
		self.set_y(38)#self.set_y(205)
		self.set_x(110)
		self.cell(8, 5, "Días reportados (Reportes diarios): " + str(len(dfDiarios.index)))
		self.set_y(42)#self.set_y(209)
		self.set_x(110)
		self.cell(8, 5, "Días cubiertos por reportes acumulados: " + str(numAccum))
		self.set_y(46)#self.set_y(213)
		self.set_x(110)
		self.cell(8, 5, "Días del mes no monitoreados: " + str(numMiss))
		self.set_y(52)#self.set_y(38)
		mtxRegs = acc.dfPrecAcumAMatriz(dfAcums, dfObs)
		if len(dfObs.index)>1:
			dibujarTablaDeMatriz(self,mtxRegs, "Reportes Acumulados de Precipitación", 9.5, 12, "L", "C", cell_width=[20,23,10,37], x_start=110, line_height=10)#130
		else:
			dibujarTablaDeMatriz(self,mtxRegs, "Reportes Acumulados de Precipitación", 9.5, 12, "L", "C", cell_width=[23,10,57], x_start=110, line_height=10)#130

		self.set_x(15)
		self.set_y(38)
		# tabla diaria
		mtxRegs = acc.dfPrecDiarioAMatriz(dfDiarios, dfObs)
		if len(dfObs.index)>1:
			dibujarTablaDeMatriz(self,mtxRegs, "Reportes de Precipitación diaria", 9.5, 12, "L", "C", cell_width=[20,18,10,45], x_start=10, line_height=8)#130
		else:
			dibujarTablaDeMatriz(self,mtxRegs, "Reportes de Precipitación diaria", 9.5, 12, "L", "C", cell_width=[18,10,65], x_start=10, line_height=8)#130

	def dibujarTablaReportesAcumulados(self,dfAcums, dfObs):
		# titulo
		self.set_y(25)
		self.set_font("times", "B", 16)
		self.set_fill_color(29, 46, 51)
		self.set_text_color(255, 255, 255)
		self.cell(190, 10, "Reportes de precipitación acumulada", align='C', fill=1)
		self.set_text_color(0, 0, 0)
		self.set_font("times", "", 12)
		self.set_y(38)
		self.set_x(50)
		mtxRegs = acc.dfPrecAcumAMatriz(dfAcums, dfObs)
		dibujarTablaDeMatriz(self,mtxRegs, "", 9.5, 12, "L", "C", cell_width="uneven", x_start=50)#130

	def dibujarTablaReportesDiarios(self,dfDiarios, dfObs):
		# titulo
		self.set_y(25)
		self.set_font("times", "B", 16)
		self.set_fill_color(29, 46, 51)
		self.set_text_color(255, 255, 255)
		self.cell(190, 10, "Reportes de precipitación diaria", align='C', fill=1)
		
		if len(dfDiarios.index)>10:
			#Primeros quince registros
			self.set_text_color(0, 0, 0)
			self.set_font("times", "", 12)
			self.set_y(38)
			self.set_x(15)
			mtxRegs = acc.dfPrecDiarioAMatriz(dfDiarios.head(10), dfObs)
			dibujarTablaDeMatriz(self,mtxRegs, "", 9.5, 12, "L", "C", cell_width="uneven", x_start=15)#130
			self.set_y(38)
			self.set_x(130)
			mtxRegs = acc.dfPrecDiarioAMatriz(dfDiarios.tail(len(dfDiarios.index)-10), dfObs)
			dibujarTablaDeMatriz(self,mtxRegs, "", 9.5, 12, "L", "C", cell_width="uneven", x_start=130)#130
		else:
			self.set_text_color(0, 0, 0)
			self.set_font("times", "", 12)
			self.set_y(38)
			self.set_x(50)
			mtxRegs = acc.dfPrecDiarioAMatriz(dfDiarios, dfObs)
			dibujarTablaDeMatriz(self,mtxRegs, "", 9.5, 12, "L", "C", cell_width="uneven", x_start=50)#130

	def insertarAgradecimiento(self, blnObs):
		self.set_y(25)# titulo
		self.set_font("times", "B", 16)
		self.set_fill_color(29, 46, 51)
		self.set_text_color(255, 255, 255)
		self.cell(190, 10, "Agradecimientos", align='C', fill=1)
		self.set_text_color(0, 0, 0)
		self.set_font("times", "", 12)
		self.set_x(15)
		self.set_y(38)#1 linea
		self.cell(190, 10, "La red de observadores voluntarios del clima (Volunclima) ha sido implementada en el marco del proyecto")
		self.set_y(43)#2 linea
		self.cell(190, 10, "\"Euroclima+: Sequías e Inundaciones - Andes\", el cual ha sido financiado con recursos de la Unión Europea")
		self.set_y(49)#3 linea
		self.cell(190, 10, "y gestionado con el apoyo de la Agencia Española de Cooperación Internacional para el Desarrollo (AECID)")
		self.set_y(55)#4 linea
		self.cell(190, 10, " y la Agencia Francesa para el Desarrollo (AFD) del componente Gestión de Riesgo.")
		self.set_y(60)#5 linea
		self.cell(190, 10, "La red Volunclima está conformada por ciudadanos de Venezuela, Colombia, Ecuador, Perú, Bolivia y Chile")
		self.set_y(66)#6 linea
		self.cell(190, 10, "quienes colaboran en el monitoreo de las precipitaciones diarias, las condiciones de sequía y la ocurrencia")
		self.set_y(72)#7 linea
		self.cell(190, 10, "de eventos extremos.")
		self.set_y(78)#8 linea
		self.cell(190, 10, "Para mayor información y acceder a los datos reportados por los voluntarios puede acceder al sitio web")
		self.set_y(84)#9 linea
		self.cell(190, 10, "https://volunclima.ciifen.org.")
		if blnObs:
			self.set_y(96)#9 linea
			self.cell(190, 10, "Agradecemos a los voluntarios que han enviado los reportes que han permitido elaborar este boletín:")


	def insertarTablasObservadores(self, arrMtxRegs):
		for idx in range(len(arrMtxRegs)):
			self.set_y(102)#altura de acuerdo a la ubicación de la última linea en pdf.insertarAgradecimiento
			if idx==0:
				dibujarTablaDeMatriz(self,arrMtxRegs[0], " ", 9.5, 11, "L", "C", cell_width=[44,44], x_start=9)#130
			else:
				dibujarTablaDeMatriz(self,arrMtxRegs[1], "   ", 9.5, 11, "L", "C", cell_width=[44,44], x_start=115)#130


	#colocar mapas
	def mapaPrecipitacion(self,imagen,x,y,width):
		# titulo de graficos
		self.set_y(25)
		self.set_font("times", "B", 16)
		self.set_fill_color(29, 46, 51)
		self.set_text_color(255, 255, 255)
		self.cell(190, 9, "Precipitación Total del Mes", align='C', fill=1)
		# imagen
		self.image(imagen, x,y,width)
		# texto de los indices
		self.set_y(130)
		self.set_text_color(0, 0, 0)

	#colocar mapas
	def mapaSequias(self,isoCty,imagen,x,y,width):
		# titulo de graficos
		self.set_y(25)
		self.set_font("times", "B", 16)
		self.set_fill_color(29, 46, 51)
		self.set_text_color(255, 255, 255)
		if isoCty=="VE" or isoCty=="EC":
			self.cell(190, 9, "Percepción de la Sequía", align='C', fill=1)
		else:
			self.cell(277, 9, "Percepción de la Sequía", align='C', fill=1)
		# imagen
		self.image(imagen, x,y,width)
		# texto de los indices
		self.set_y(130)
		self.set_text_color(0, 0, 0)

	def insertarTablaReportesSequias(self,isoCty,mtxRegs,dfReps,yIni,mIni):
		if isoCty == "CL":
			self.set_y(35)
			dibujarTablaDeMatriz(self,mtxRegs, " ", 9, 11, "L", "C", cell_width=[28,32,18,99], x_start=110,parametro='sequia',dfValues=dfReps,
			yyyy=yIni,mm=mIni)#130
		elif isoCty== "VE":
			self.set_y(125)
			dibujarTablaDeMatriz(self,mtxRegs, " ", 9.5, 11, "L", "C", cell_width=[36,39,18,109], x_start=9,parametro='sequia',dfValues=dfReps,
			yyyy=yIni,mm=mIni,line_height=11)#130
		elif isoCty== "EC":
			""" self.set_y(35)
			dibujarTablaDeMatriz(self,mtxRegs, " ", 9, 11, "L", "C", cell_width=[33,39,18,77], x_start=120,parametro='sequia',dfValues=dfReps,
			yyyy=yIni,mm=mIni)#130 """
			self.set_y(125)
			dibujarTablaDeMatriz(self,mtxRegs, " ", 9.5, 11, "L", "C", cell_width=[36,39,18,106], x_start=9,parametro='sequia',dfValues=dfReps,
			yyyy=yIni,mm=mIni)#130
		else:
			self.set_y(35)
			dibujarTablaDeMatriz(self,mtxRegs, " ", 9, 11, "L", "C", cell_width=[28,39,18,82], x_start=120,parametro='sequia',dfValues=dfReps,
			yyyy=yIni,mm=mIni)#130
#[["Estación", "Ubicación", "FEcha Repore", "INTENSIDAD SEQUIA", "Comentarios"]]

	#colocar mapas
	def insertarTablaMensualesEstaciones(self,isoCty,arrMtxRegs,dfValStMon,yIni,mIni):
		#mtxRegs = acc.dfPrecEstacionesMensualAMatriz(dfValStMon)
		if isoCty=='EC':
			""" for idx in range(len(arrMtxRegs)):
				if idx==0:
					self.set_y(35)
					dibujarTablaDeMatriz(self,arrMtxRegs[0], " ", 9.5, 11, "L", "C", cell_width=[35,35,17], x_start=115, parametro='precipitacion',dfValues=dfValStMon
					,yyyy=yIni,mm=mIni)#130
				elif idx==1:
					self.set_y(127)
					dibujarTablaDeMatriz(self,arrMtxRegs[1], " ", 9.5, 11, "L", "C", cell_width=[35,35,17], x_start=9, parametro='precipitacion',dfValues=dfValStMon
					,yyyy=yIni,mm=mIni)#130
				else:
					self.set_y(127)
					dibujarTablaDeMatriz(self,arrMtxRegs[2], "   ", 9.5, 11, "L", "C", cell_width=[35,35,17], x_start=115, parametro='precipitacion',dfValues=dfValStMon
					,yyyy=yIni,mm=mIni)#130 """
			for idx in range(len(arrMtxRegs)):
				if idx==0:
					self.set_y(125)
					dibujarTablaDeMatriz(self,arrMtxRegs[0], "   ", 9.5, 11, "L", "C", cell_width=[35,35,17], x_start=9, parametro='precipitacion',dfValues=dfValStMon
					,yyyy=yIni,mm=mIni)#130
				else:
					self.set_y(125)
					dibujarTablaDeMatriz(self,arrMtxRegs[1], "   ", 9.5, 11, "L", "C", cell_width=[35,35,17], x_start=115, parametro='precipitacion',dfValues=dfValStMon
					,yyyy=yIni,mm=mIni)#130
		elif isoCty=='BO':
			for idx in range(len(arrMtxRegs)):
				if idx==0:
					self.set_y(35)
					dibujarTablaDeMatriz(self,arrMtxRegs[0], " ", 9.5, 11, "L", "C", cell_width=[35,35,17], x_start=115, parametro='precipitacion',dfValues=dfValStMon
					,yyyy=yIni,mm=mIni)#130
				elif idx==1:
					self.set_y(127)
					dibujarTablaDeMatriz(self,arrMtxRegs[1], " ", 9.5, 11, "L", "C", cell_width=[35,35,17], x_start=9, parametro='precipitacion',dfValues=dfValStMon
					,yyyy=yIni,mm=mIni)#130
				else:
					self.set_y(127)
					dibujarTablaDeMatriz(self,arrMtxRegs[2], "   ", 9.5, 11, "L", "C", cell_width=[35,35,17], x_start=115, parametro='precipitacion',dfValues=dfValStMon
					,yyyy=yIni,mm=mIni)#130
		elif isoCty=='VE':
			for idx in range(len(arrMtxRegs)):
				if idx==0:
					self.set_y(125)
					dibujarTablaDeMatriz(self,arrMtxRegs[0], "   ", 9.5, 11, "L", "C", cell_width=[35,35,17], x_start=9, parametro='precipitacion',dfValues=dfValStMon
					,yyyy=yIni,mm=mIni)#130
				else:
					self.set_y(125)
					dibujarTablaDeMatriz(self,arrMtxRegs[1], "   ", 9.5, 11, "L", "C", cell_width=[35,35,17], x_start=115, parametro='precipitacion',dfValues=dfValStMon
					,yyyy=yIni,mm=mIni)#130
		elif isoCty== "CL":
			for idx in range(len(arrMtxRegs)):
				if idx==0:
					self.set_y(35)
					dibujarTablaDeMatriz(self,arrMtxRegs[0], "  ", 9.5, 11, "L", "C", cell_width=[35,35,17], x_start=115, parametro='precipitacion',dfValues=dfValStMon
					,yyyy=yIni,mm=mIni)#130
				elif idx==1:
					self.set_y(175)
					dibujarTablaDeMatriz(self,arrMtxRegs[1], "  ", 9.5, 11, "L", "C", cell_width=[35,35,17], x_start=9, parametro='precipitacion',dfValues=dfValStMon
					,yyyy=yIni,mm=mIni)#130
				else:
					self.set_y(175)#155
					dibujarTablaDeMatriz(self,arrMtxRegs[2], "  ", 9.5, 11, "L", "C", cell_width=[35,35,17], x_start=115, parametro='precipitacion',dfValues=dfValStMon
					,yyyy=yIni,mm=mIni)#130
		elif isoCty== "CO":
			# Display all columns and rows
			for idx in range(len(arrMtxRegs)):
				if idx==0:
					self.set_y(35)
					dibujarTablaDeMatriz(self,arrMtxRegs[0], " ", 9.5, 11, "L", "C", cell_width=[35,35,17], x_start=115, parametro='precipitacion',dfValues=dfValStMon
					,yyyy=yIni,mm=mIni)#130
				elif idx==1:
					self.set_y(125)
					dibujarTablaDeMatriz(self,arrMtxRegs[1], " ", 9.5, 11, "L", "C", cell_width=[35,35,17], x_start=9, parametro='precipitacion',dfValues=dfValStMon
					,yyyy=yIni,mm=mIni)#130
				else:
					self.set_y(125)
					dibujarTablaDeMatriz(self,arrMtxRegs[2], "  ", 9.5, 11, "L", "C", cell_width=[35,35,17], x_start=115, parametro='precipitacion',dfValues=dfValStMon
					,yyyy=yIni,mm=mIni)#130


	def insertarTablaExtremos(self,isoCty,mtxRegs):
		# titulo de graficos
		self.set_y(25)
		#self.set_x(15)
		self.set_font("times", "B", 16)
		self.set_fill_color(29, 46, 51)
		self.set_text_color(255, 255, 255)
		self.cell(277, 9, "Reportes de Eventos Extremos", align='C', fill=1)
		self.set_text_color(0, 0, 0)
		self.set_font("times", "", 12)
		self.set_y(38)
		self.cell(8, 5, "Se listan los reportes de eventos extremos reportados por los observadores voluntarios en el mes:")
		self.set_y(45)
		if mtxRegs is None:
			strQuote = "No se recibieron reportes de eventos extremos."
			self.insertLabel(10,45,277,strQuote,"QTE")
		else:
			if(isoCty=='VE'):
				dibujarTablaDeMatriz(self,mtxRegs, " ", 9, 11, "L", "C", cell_width=[36,39,26,90,94], x_start=10)#130
			else:
				dibujarTablaDeMatriz(self,mtxRegs, " ", 9, 11, "L", "C", cell_width=[28,39,26,90,94], x_start=10)#130
			#dibujarTablaDeMatriz(self,mtxRegs, " ", 9, 11, "L", "C", cell_width=[28,39,26,15,15,15,15,15,15,94], x_start=10)#130

	#colocar predicciones
	def insertarPredicciones(self, isoCty):
		try:
			self.set_y(25)
			# Título de la mitad seuprior
			self.set_font("times", "B", 16)
			self.set_fill_color(29, 46, 51)
			self.set_text_color(255, 255, 255)
			self.cell(190, 10, "Pronóstico Mensual", align='C', fill=1, ln=True)
			
			# Colocar las dos imágenes de pronóstico mensual lado a lado
			self.image("/var/py/volunclima/salidas/predicciones/"+isoCty+"/pron_tsaireECMWF_"+isoCty+"_mens.png", x=10, y=self.get_y(), w=90)
			self.image("/var/py/volunclima/salidas/predicciones/"+isoCty+"/pron_prcpECMWF_"+isoCty+"_mens.png", x=110, y=self.get_y(), w=90)
			if(isoCty=="CL"):
				self.set_y(self.get_y()+10)
			self.ln(100)  # Salto de línea para dejar espacio entre las imágenes

			# Título de la mitad inferior
			self.cell(190, 10, "Pronóstico Estacional", align='C', fill=1, ln=True)
			
			# Colocar las dos imágenes de pronóstico estacional lado a lado
			self.image("/var/py/volunclima/salidas/predicciones/"+isoCty+"/pron_tsaireECMWF_"+isoCty+"_estac.png", x=10, y=self.get_y(), w=90)
			self.image("/var/py/volunclima/salidas/predicciones/"+isoCty+"/pron_prcpECMWF_"+isoCty+"_estac.png", x=110, y=self.get_y(), w=90)
			
			# Texto personalizado al final
			self.ln(110)  # Salto de línea para dejar espacio entre las imágenes
			self.set_font("times", "", 10)
			self.set_text_color(0, 0, 0)
			self.multi_cell(0, 4, "El usuario debe considerar esta información como una estimación de los valores más probables de "+
			"precipitación y temperatura en el país para el siguiente mes o los siguientes tres meses, a partir del sistema de pronóstico " + 
			"SEAS5 del Centro Europeo de Previsiones Meteorológicas a Plazo Medio (ECMWF). "+"Adicionalmente se sugiere consultar los pronósticos "+
			"del servicio meteorológico nacional.", align='C')

		except Exception as e:
			print(f"Error al obtener las predicciones: {e}")

	#colocar predicciones
	def insertarTablaRequerimientosHidricosyConsejos(self, isoCty):
		if(isoCty=="EC"):
			requerimientos_hidricos=requerimientos_hidricos_EC
			cultivos_texto="CULTIVOS EN ECUADOR"
		elif(isoCty=="VE"):
			requerimientos_hidricos=requerimientos_hidricos_VE
			cultivos_texto="CULTIVOS EN VENEZUELA"
		elif(isoCty=="CL"):
			requerimientos_hidricos=requerimientos_hidricos_CL
			cultivos_texto="CULTIVOS EN CHILE"
		elif(isoCty=="CO"):
			requerimientos_hidricos=requerimientos_hidricos_CO
			cultivos_texto="CULTIVOS EN COLOMBIA"
		elif(isoCty=="BO"):
			requerimientos_hidricos=requerimientos_hidricos_BO
			cultivos_texto="CULTIVOS EN BOLIVIA"
		else:
			requerimientos_hidricos=requerimientos_hidricos_EC
			cultivos_texto="CULTIVOS EN ECUADOR"
		try:
			self.set_y(25)
			width_inicial= self.get_x()
			# Título de la mitad seuprior
			self.set_font("times", "B", 16)
			self.set_fill_color(29, 46, 51)
			self.set_text_color(255, 255, 255)
			self.cell(190, 10, "REQUERIMIENTOS HÍDRICOS", align='C', fill=1, ln=True)
			# Configuración inicial
			#col_widths = [80, 110]
			col_widths = [35, 55]
			padding = 2
			self.set_y(self.get_y()+4)
			# Título de la tabla
			altura_inicial= self.get_y()
			
			self.set_fill_color(0, 112, 192)  # Color hex: "#0070c0"
			self.set_text_color(255, 255, 255)  # Texto blanco
			self.set_font("times", "B", 12)
			self.cell(col_widths[0] + col_widths[1], 10, "REQUERIMIENTO HÍDRICO", 1, ln=True, align='C',fill=1)

			# Cabecera de la tabla
			self.set_fill_color(0, 176, 240)  # Color hex: "#00b0f0"
			self.set_font("times", "B", 10)
			self.multi_cell(col_widths[0], 6, cultivos_texto, 1,fill=1, align='C')
			x = self.get_x()
			y = self.get_y() - (12)
			self.set_xy(x , y)
			self.set_fill_color(146,208,80)  # Color hex: "#92d050"
			self.multi_cell(col_widths[1], 6, "MILÍMETROS REQUERIDOS POR CULTIVO", 1, ln=True, align='C',fill=1)
			
			# Contenido de la tabla
			self.set_fill_color(220, 230, 241)  # Color hex: "#dce6f1"
			self.set_text_color(0, 0, 0)  # Texto negro
			self.set_font("times", "", 10)
			flag=False
			counter=0
			for cultivo, requerimiento in requerimientos_hidricos.items():
				# Calcula la altura máxima necesaria para esta fila
				if (counter % 2 == 0):
					self.set_fill_color(220, 230, 241)  # Color hex: "#dce6f1"
				else:
					self.set_fill_color(255, 255, 255)  # Color hex: "#ffffff"
				if(col_widths[1]>=self.get_string_width(requerimiento)):
					altura_requerimiento = 1
				else:
					#print(cultivo)
					altura_requerimiento = ( self.get_string_width(requerimiento)//col_widths[1])+1
					altura_requerimiento_float = ( self.get_string_width(requerimiento)/col_widths[1])
					valor_decimal = "{:.3f}".format(altura_requerimiento_float)
					# Convierte el número a cadena y obtén los últimos dos caracteres
					#print(valor_decimal)
					parte_decimal_str = str(valor_decimal).split('.')[1]
					# Convierte la parte decimal a un entero		
					parte_decimal_int = int(parte_decimal_str)
					#print(parte_decimal_int)
					if (997>parte_decimal_int >= 599 or parte_decimal_int ==0):
						altura_requerimiento+=1			
				#print(altura_requerimiento)      
				# Establece la altura de la fila 
				
				self.multi_cell(col_widths[0], 6*altura_requerimiento, cultivo, 1,fill=1)
				x = self.get_x()
				y = self.get_y() - (6*altura_requerimiento)
				self.set_xy(x , y)         
				if flag:
					self.multi_cell(col_widths[1], 6, requerimiento, 1,ln=True,fill=1)      
					#print("altura")
					#print(self.get_y())

					if(self.get_y()+6*altura_requerimiento>275):    
						#print("xddd")                
						flag=False
						self.add_page()
						self.set_y(25)
						continue               
					else:
						self.set_xy(col_widths[0] + col_widths[1] +20 , self.get_y())
				else:
					self.multi_cell(col_widths[1], 6, requerimiento, 1,ln=True,fill=1)
				
				if(isoCty=="VE"):
					#ajustar aqui para otras tablas, en cual es la altura maxima a la que cambiar la columna
					if(self.get_y()+6*altura_requerimiento>280):
						self.set_xy(col_widths[0] + col_widths[1] +20, altura_inicial)
						flag=True  
				elif (isoCty=="BO"):
					#ajustar aqui para otras tablas, en cual es la altura maxima a la que cambiar la columna
					if(self.get_y()+6*altura_requerimiento>270):
						self.set_xy(col_widths[0] + col_widths[1] +20, altura_inicial)
						flag=True  
				else:
					if(self.get_y()>270):
						self.set_xy(col_widths[0] + col_widths[1] +20, altura_inicial)
						flag=True  

				counter+=1
			
			if(isoCty=="CO" or isoCty=="CL"):
				self.add_page()  # Agregar una nueva página
				self.set_y(25)
			else:
				self.ln(4)
			self.set_font("times", "B", 16)
			self.set_fill_color(29, 46, 51)
			self.set_text_color(255, 255, 255)
			self.cell(190, 10, "REQUERIMIENTOS HÍDRICOS", align='C', fill=1, ln=True)
			self.set_x(width_inicial)
			self.ln(4)  # Salto de línea
			# Después de agregar las tablas, introducir el texto adicional
			self.add_font("dejavusans", "", "/usr/share/fonts/dejavu/DejaVuSans.ttf", uni=True)
			
			self.set_text_color(0, 0, 0)
			self.set_font("dejavusans", "", 9)
			self.multi_cell(0, 4, "• Tome en cuenta que los rangos de agua que necesita cada tipo de cultivo son los óptimos para obtener un buen rendimiento de sus siembras sin tener que desperdiciar agua.")
			self.ln(5)  # Salto de línea
			self.multi_cell(0, 4, "• Es importante tener en cuenta el tipo de suelo en el que siembra, si su suelo es más arcilloso que arenoso, tendrá que adicionar menos agua de acuerdo al rango de referencia para su cultivo, porque retendrá mejor la humedad.")
			self.ln(5)  # Salto de línea
			self.multi_cell(0, 4, "• Recuerde que el tipo de suelo influye en el drenaje, es decir que tan rápido escurrirá el agua hasta donde se encuentran las raíces para su absorción.")
			self.ln(5)  # Salto de línea
			self.multi_cell(0, 4, "• Se recomienda que en días soleados con altas temperaturas usted riegue en forma de aspersión para mantener la humedad circundante en su siembra.")
			self.ln(5)  # Salto de línea
			self.multi_cell(0, 4, "• Todos los cultivos tienen una fase de crecimiento inicial, desarrollo, floración, producción de frutos y cosecha. Por lo cual se recomienda que la curva de riego para todas las plantas sea de esta forma.")
			# Insertar imagen (ajusta la ruta y el tamaño según tus necesidades)
			if(isoCty=="VE"):
				self.add_page()  # Agregar una nueva página
				self.set_y(25)
			self.image('consejos.png', x=10, y=None, w=100)
			
			self.ln(4)  # Salto de línea
			self.multi_cell(0, 4, "• Una forma de saber cuanto se debe regar por día su cultivo es dividir la cantidad mínima de milímetros de agua por el mínimo días de cultivo. Ejemplo el maracuyá (900 a 1500 mm por año), se debe dividir 900/365 año = 2.5 mm es lo mínimo que necesitaría al día el cultivo para crecer bien. Sin embargo, se recomienda adicionar unos milímetros más dependiendo de las condiciones climáticas de su zona y también de la etapa de crecimiento en la que se encuentre, hasta un máximo de 4.10 mm por día.")

		except Exception as e:
			print(f"Error al insertar la tabla de requerimientos hídricos: {e}")

def asignar_color_hex_prec(total):
	if total < 1:
		return colPrec[0]
	elif 1 <= total < 50:
		return colPrec[1]
	elif 50 <= total < 100:
		return colPrec[2]
	elif 100 <= total < 150:
		return colPrec[3]
	elif 150 <= total < 200:
		return colPrec[4]
	elif 200 <= total < 250:
		return colPrec[5]
	elif 250 <= total < 300:
		return colPrec[6]
	elif 300 <= total < 350:
		return colPrec[7]
	elif 350 <= total < 400:
		return colPrec[8]
	elif 400 <= total < 450:
		return colPrec[9]
	elif 450 <= total < 500:
		return colPrec[10]
	elif total >= 500:
		return colPrec[11]
	else:
		return colPrec[12]

# Función adaptada
def asignar_color_hex_seq(total):
	lstIntervals = [-4, -3, -2, -1, 1, 2, 3, 4]
	if total < lstIntervals[0]:
		return colSeq[0]
	elif lstIntervals[0] <= total < lstIntervals[1]:
		return colSeq[1]
	elif lstIntervals[1] <= total < lstIntervals[2]:
		return colSeq[2]
	elif lstIntervals[2] <= total < lstIntervals[3]:
		return colSeq[3]
	elif lstIntervals[3] <= total < lstIntervals[4]:
		return colSeq[4]
	elif lstIntervals[4] <= total < lstIntervals[5]:
		return colSeq[5]
	elif lstIntervals[5] <= total < lstIntervals[6]:
		return colSeq[6]
	elif lstIntervals[6] <= total < lstIntervals[7]:
			return colSeq[7]
	else:
		return colSeq[-1]


def hex_to_rgb(hex_color):
    # Asegúrate de que la cadena hexadecimal comience con "0x" o "#", y quita esos caracteres
    hex_color = hex_color.lstrip("0x").lstrip("#")
    
    # Convierte la cadena hexadecimal a un número entero
    hex_value = int(hex_color, 16)
    
    # Extrae los componentes RGB
    red = (hex_value >> 16) & 0xFF
    green = (hex_value >> 8) & 0xFF
    blue = hex_value & 0xFF
    
    return red, green, blue