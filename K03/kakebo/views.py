from kakebo import app
from flask import jsonify, render_template, request, redirect, url_for, flash
from kakebo.forms import MovimientosForm
import sqlite3

def consultaSQL(query):
    # Abrimos la conexión
    conexion = sqlite3.connect('movimientos.db')
    cur = conexion.cursor()

    # Ejecutamos la consulta
    cur.execute(query)

    # Obtenemos los datos de la consulta
    claves = cur.description
    filas = cur.fetchall()

    # Procesar los datos para devolver una lista de dicionarios. Um diccionario por fila
    resultado = []  # creamos una lista vacía. Despúes será una lista de diccionarios
    for fila in filas:
        d ={}  # creamos un diccionario vacío
        for tuplaClave, valor in zip(claves, fila):
            d[tuplaClave[0]] = valor
        
        resultado.append(d)

    conexion.close()
    return resultado



def modificaTablaSQL(query, parametros=[]):
    conexion = sqlite3.connect('movimientos.db')
    cur = conexion.cursor()

    cur.execute(query, parametros)

    conexion.commit()
    conexion.close()
    


@app.route('/')
def index():
    movimientos = consultaSQL("SELECT * FROM movimientos order by fecha")

    saldo = 0
    for d in movimientos:
        if d['esGasto'] == 0:
            saldo = saldo + d['cantidad']
        else:
            saldo = saldo - d['cantidad']
        d['saldo'] = saldo 

    # return jsonify(movimientos)
    return render_template('movimientos.html', datos = movimientos)


@app.route('/nuevo', methods=['GET', 'POST'])
def nuevo():
    formulario = MovimientosForm()
    if request.method == 'GET':
        return render_template('alta.html', form = formulario)
    else:  # será un POST
        if formulario.validate():  # insertar el movimiento en la base de datos

            query = """ INSERT INTO movimientos (fecha, concepto, categoria, esGasto, cantidad)
                        VALUES (?, ?, ?, ?, ?) """
            try:
                modificaTablaSQL(query, [formulario.fecha.data, formulario.concepto.data, formulario.categoria.data,
                                    formulario.esGasto.data, formulario.cantidad.data])
            except sqlite3.Error as el_error:
                print("ERROR EN SQL", el_error)
                flash('Se ha producido un error en la base de datos. Pruebe en unos minutos')
                return render_template('alta.html', form = formulario)

            return redirect(url_for('index'))  # redirect a la ruta / a través de la función index
        else:
            return render_template('alta.html', form = formulario)


@app.route('/borrar/<int:id>', methods=['GET', 'POST'])
def borrar(id):
    return render_template('borrar.html', identificador = id)