# coding=utf-8

import logging
import telegram
import MySQLdb
import geopy.distance
import datetime
import os

from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes, InlineQueryHandler, CallbackContext
from telethon import TelegramClient, events

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

#Variables globales
now = datetime.datetime.now().strftime('%H:%M:%S')

horaIni1 = "Hora inicio 1"
horaFin1 = "Hora fin 1"

horaIni2 = "Hora inicio 2"
horaFin2 = "Hora fin 2"

checkCodigoTrabajador = False
codigoTrabajador = 0
idTrabajador = 0
current_pos = ""



#HOMESTEAD
""" db = MySQLdb.connect(host="192.168.10.10",    # localhost
                 user="homestead",         #  username
                 passwd="secret",  #  password
                 db="uati")        # name of the data base """
try:
    db = MySQLdb.connect(host="82.223.75.143",    # localhost
                 user="root",         #  username
                 passwd="0tran234del",  #  password
                 db="transfermane")        # name of the data base
    # If connection is not successful
except:
    print("No se ha podido conectar a la BBDD, por favor, contacte con el administrador de la aplicación")

#Función para conectar por MySQLdb
def mysqlconnect():
    #Trying to connect
    try:
        db = MySQLdb.connect(host="82.223.75.143",    # localhost
                 user="root",         #  username
                 passwd="0tran234del",  #  password
                 db="transfermane")        # name of the data base
    # If connection is not successful
    except:
        print("No se ha podido conectar a la BBDD, por favor, contacte con el administrador de la aplicación")
        return 0
    # If Connection Is Successful
    print("Conectado a la BBDD")
 
    # Making Cursor Object For Query Execution
    cursor=db.cursor()
 
    # Executing Query
    cursor.execute("SELECT CURDATE();")
 
    # Above Query Gives Us The Current Date
    # Fetching Data
    m = cursor.fetchone()
 
    # Printing Result Of Above
    print("La fecha de hoy es: ",m[0])
 
    # Closing Database Connection
    db.close()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global idTrabajador
    global checkCodigoTrabajador
    global codigoTrabajador
    global current_pos

    checkCodigoTrabajador = False
    idTrabajador = 0
    codigoTrabajador = 0
    current_pos = ""


    #Nos debe enviar su identificador, hasta que no lo haga no puede continuar
    location_keyboard = telegram.KeyboardButton(text="send_location", request_location=True)
    #location_keyboard = telegram.Location()
    #contact_keyboard = telegram.KeyboardButton(text="send_contact", request_contact=True)
    custom_keyboard = [[location_keyboard]]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)

    #INICIO - LOG
    cursor=db.cursor()
    sql = """INSERT INTO log_bot(comando, usuario, mensaje, posicion, sucursal) VALUES ('start', 'Sin usuario', 'Se inicia la conexión', 'Sin posición', 'Sin sucursal')"""
    cursor.execute(sql)
    db.commit()
    cursor.close()
    #FIN - LOG

    await context.bot.send_message(
        chat_id=update.effective_chat.id
        , text="Por favor, introduce tu identificador personal"
        #, reply_markup=reply_markup
    )

async def fichajeEntrada(update: Update, context: ContextTypes.DEFAULT_TYPE):

    #Nos debe enviar su identificador, hasta que no lo haga no puede continuar
    location_keyboard = telegram.KeyboardButton("Pulsa para fichar entrada", request_location=True)
    #location_keyboard = telegram.Location()
    #contact_keyboard = telegram.KeyboardButton(text="send_contact", request_contact=True)
    custom_keyboard = [[location_keyboard]]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)

    await context.bot.send_message(
        chat_id=update.effective_chat.id
        , text="Vas a fichar la HORA DE ENTRADA, si es así pulsa sobre el botón fichar, si no elije otro comando"
        , reply_markup=reply_markup
    )

async def fichajeSalida(update: Update, context: ContextTypes.DEFAULT_TYPE):

    #Nos debe enviar su identificador, hasta que no lo haga no puede continuar
    location_keyboard = telegram.KeyboardButton("Pulsa para fichar salida", request_location=True)
    #location_keyboard = telegram.Location()
    #contact_keyboard = telegram.KeyboardButton(text="send_contact", request_contact=True)
    custom_keyboard = [[location_keyboard]]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)

    await context.bot.send_message(
        chat_id=update.effective_chat.id
        , text="Vas a fichar la HORA DE SALIDA, si es así pulsa sobre el botón fichar, si no elije otro comando"
        , reply_markup=reply_markup
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    resTxt = ""
    global checkCodigoTrabajador
    global codigoTrabajador
    global idTrabajador

    if not checkCodigoTrabajador:
        validateNumeric = update.message.text.isnumeric()
        if not validateNumeric:
            #INICIO - LOG
            cursor=db.cursor()
            sql = """INSERT INTO log_bot(comando, usuario, mensaje, posicion, sucursal) VALUES ('echo', %s, 'Se inserta incorrectamente el código del trabajador', 'Sin posición', 'Sin sucursal')"""
            cursor.execute(sql, (update.message.text))
            db.commit()
            cursor.close()
            #FIN - LOG
            resTxt = "No es un codigo válido, por favor, introduce un código válido"

        if validateNumeric:
            cursor=db.cursor()

            sql = """SELECT apellidos, idPersonal FROM Personal WHERE codigotrabajador = %s;"""
            valor = update.message.text
            

            cursor.execute(sql, (valor,))

            m = cursor.fetchone()

            codigoTrabajador = valor
            idTrabajador = m[1]

            resTxt = "Hola " + m[0] + ". Ahora puedes registrar tu jornada. Debes seleccionar el comando correspondiente del menú"

            checkCodigoTrabajador = True

            #INICIO - LOG
            cursor=db.cursor()
            sql = """INSERT INTO log_bot(comando, usuario, mensaje, posicion, sucursal) VALUES ('echo', %s, 'Se inserta correctamente el código del trabajador', 'Sin posición', 'Sin sucursal')"""
            cursor.execute(sql, (valor,))
            db.commit()
            cursor.close()
            #FIN - LOG

    else :
        resTxt ="Ya se ha registrado tu código, continúa con tu fichaje"

    await context.bot.send_message(
        chat_id=update.effective_chat.id
        , text=resTxt
    )

async def caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text_caps = ' '.join(context.args).upper()
    await context.bot.send_message(
        chat_id=update.effective_chat.id
        , text=text_caps
    )

async def inline_caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    if not query:
        return
    results = []
    results.append(
        InlineQueryResultArticle(
            id=query.upper(),
            title='Caps',
            input_message_content=InputTextMessageContent(query.upper())
        )
    )
    await context.bot.answer_inline_query(
        update.inline_query.id
        , results
    )

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id
        , text="Lo siento, No entiendo este comando."
    )

async def location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Cuando se pulsa cualquier botón ya entra aquí ya que coge la ubicación:
    global codigoTrabajador
    global idTrabajador
    global now
    global current_pos
    tipoFichaje = update.message.reply_to_message.text
    fin = 0
    
    fechaHoy = update.message.date

    if update.edited_message:
        message = update.edited_message
    else:
        message = update.message

    current_pos = (message.location.latitude, message.location.longitude)

    cursor=db.cursor()
    sql = """SELECT idContrato FROM Contrato WHERE idPersonal = %s AND ultimovigente = 1;"""
    cursor.execute(sql, (idTrabajador,))
    m = cursor.fetchone()

    idContrato = m[0]

    cursor=db.cursor()
    sql = """SELECT id_sucursal FROM personal_sucursal WHERE id_personal = %s;"""
    cursor.execute(sql, (idTrabajador,))
    m = cursor.fetchall()

    if cursor.rowcount > 0:
        ultimadistancia = ""
        idUltimaSucrusal = 0
        ultimaCoordenadaCentro = ""
        ultimoNombreSucursal = ""
        entraDis = False
        for suc in m:
            idSucursal = suc

            #Cogemos las coordenadas de todas las sucursales en las que está inscrito este trabajador
            sql = """SELECT latitud, longitud, nombre, idCliente FROM Sucursal WHERE idSucursal = %s;"""
            cursor.execute(sql, (idSucursal,))
            m = cursor.fetchone() 

            coords_1 = (m[0], m[1])

            nombreSucursal = m[2]
            idCliente = m[3]
            

            distancia = geopy.distance.geodesic(current_pos, coords_1).km

            if not entraDis:
                ultimadistancia = distancia
                entraDis = True
            
            if ultimadistancia >= distancia:
                ultimadistancia = distancia
                ultimaCoordenadaCentro = coords_1
                ultimoNombreSucursal = nombreSucursal
                idUltimaSucrusal = idSucursal

            #INICIO - LOG
            cursor=db.cursor()
            sql = """INSERT INTO log_bot(comando, usuario, mensaje, posicion, sucursal) VALUES ('location', 'fichaje', 'Se coge las coordenadas de cada uno', %s, %s)"""
            cursor.execute(sql, (distancia, idSucursal,))
            db.commit()
            #FIN - LOG

            #Si la distancia es menor que 11 entonces sí está en el sitio y procedemos a registrar el fichaje
            if distancia < 0.020:
                #Podemos preguntar por el fichaje
                sql = """SELECT id, horaini1, horafin1, horaini2, horafin2 FROM MotivoHoraBot WHERE idPersonal = %s AND fecha = CAST(%s as DATE)"""
                cursor.execute(sql, (idTrabajador,fechaHoy,))

                m = cursor.fetchone()

                if m is None:
                    now = datetime.datetime.now().strftime('%H:%M:%S')
                    sql = """INSERT INTO MotivoHoraBot(usuario, idPersonal, idTipoMotivo, idTipoMotivo2, comentarios, idCliente, idSucursal, idContrato, fecha, horas, horaIni1, horaFin1, horaIni2, horaFin2) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CAST(%s as DATE), %s, CAST(%s as TIME), %s, %s, %s)"""
                    if "ENTRADA" in tipoFichaje:
                        cursor.execute(sql, ('bot', idTrabajador, None, None, 'Telegram BOT', idCliente, idSucursal, idContrato, fechaHoy, 0, now, None, None, None))
                    if "SALIDA" in tipoFichaje:
                        cursor.execute(sql, ('bot', idTrabajador, None, None, 'Telegram BOT', idCliente, idSucursal, idContrato, fechaHoy, 0, None, now, None, None))
                    db.commit()
                if m:
                    if "ENTRADA" in tipoFichaje:
                        #Si no tiene horaIni1 y no tiene horaIni2, miramos si tiene horaFin1
                        if m[1] is None and m[3] is None:
                            #Si no tiene horaFin1 ni horaFin2
                            if m[2] is None and m[4] is None and m[1] is None:
                                sql = """UPDATE MotivoHoraBot SET horaini1 = CAST(%s as TIME) WHERE id = %s"""
                            #Si no tiene horaFin2 y sí tiene horaFin2
                            elif m[2] is None and m[4] and m[3] is None:
                                sql = """UPDATE MotivoHoraBot SET horaini2 = CAST(%s as TIME) WHERE id = %s"""
                            #Si tiene horaFin1 y no tiene horaFin2
                            elif m[2] and m[4] is None and m[1] is None:
                                sql = """UPDATE MotivoHoraBot SET horaini1 = CAST(%s as TIME) WHERE id = %s"""
                        #Si tiene horaIni1 y no tiene horaIni2
                        if m[1] and m[3] is None:
                            sql = """UPDATE MotivoHoraBot SET horaini2 = CAST(%s as TIME) WHERE id = %s"""

                    if "SALIDA" in tipoFichaje:
                        print("Entra")
                        #Si no tiene horaFin1 y no tiene horaFin2
                        if m[2] is None and m[4] is None:
                            #Si no tiene horaIni1 y no tiene horaIni2
                            if m[1] is None and m[3] is None:
                                sql = """UPDATE MotivoHoraBot SET horafin1 = CAST(%s as TIME) WHERE id = %s"""
                            #Si no tiene horaIni1 y sí tiene horaIni2
                            elif m[1] is None and m[3]:
                                sql = """UPDATE MotivoHoraBot SET horafin2 = CAST(%s as TIME) WHERE id = %s"""
                            #Si tiene horaIni1 y no tiene horaIni2
                            elif m[1] and m[3] is None:
                                sql = """UPDATE MotivoHoraBot SET horafin1 = CAST(%s as TIME) WHERE id = %s"""
                        #Si tiene horaFin1 y no tiene horaFin2
                        if m[2]:
                            sql = """UPDATE MotivoHoraBot SET horafin2 = CAST(%s as TIME) WHERE id = %s"""
                    idMotivoHoraBot = m[0]
                    now = datetime.datetime.now().strftime('%H:%M:%S')
                    cursor.execute(sql, (now, idMotivoHoraBot,))
                    db.commit()
                    

                await context.bot.send_message(
                    chat_id=update.effective_chat.id
                    , text="Se ha registrado correctamente tu fichaje en el centro: " + str(nombreSucursal) + ". Distancia total: " + str(distancia) + ". Tus coordenadas:" + str(current_pos) + " Coordenadas del centro: " + str(coords_1)
                )

                #INICIO - LOG
                cursor=db.cursor()
                sql = """INSERT INTO log_bot(comando, usuario, mensaje, posicion, sucursal) VALUES ('location', 'fichaje', 'Se inserta el fichaje correctamente', %s, %s)"""
                cursor.execute(sql, (distancia, idSucursal,))
                db.commit()
                #FIN - LOG

                fin = 1

                break

        if not fin:
            #Recorremos las sucursales nuevamente y vemos en cuál está más cerca


            #INICIO - LOG
            cursor=db.cursor()
            sql = """INSERT INTO log_bot(comando, usuario, mensaje, posicion, sucursal) VALUES ('location', 'fichaje', 'No se ha podido vertificar el fichaje. No está en ningún centro cerca', %s, 'Sin sucursal')"""
            cursor.execute(sql, (idTrabajador,))
            db.commit()
            cursor.close()
            #FIN - LOG

            await context.bot.send_message(
                chat_id=update.effective_chat.id
                , text="No se ha podido realizar el fichaje. Verifica que estás en el centro asignado. Habla con tu supervisor. Gracias. Nombre del centro: " + ultimoNombreSucursal +  ". Distancia total: " + str(ultimadistancia) + ". Tus coordenadas:" + str(current_pos) + " Coordenadas del centro: " + str(ultimaCoordenadaCentro)
            )           
       
    else:
        #INICIO - LOG
        cursor=db.cursor()
        sql = """INSERT INTO log_bot(comando, usuario, mensaje, posicion, sucursal) VALUES ('location', 'fichaje', 'No se han registrado sucursales', %s, 'Sin sucursal')"""
        cursor.execute(sql, (idTrabajador,))
        db.commit()
        cursor.close()
        #FIN - LOG

        await context.bot.send_message(
            chat_id=update.effective_chat.id
            , text="No se han registrado sucursales para tu usuario. Habla con tu supervisor. Gracias"
        )

if __name__ == '__main__':
    token = os.environ['TOKEN']
    # Se ejecuta para el /start
    application = ApplicationBuilder().token(token).build()
    
    start_handler = CommandHandler('start', start)
    entrada_handler = CommandHandler('entrada', fichajeEntrada)
    salida_handler = CommandHandler('salida', fichajeSalida)
    application.add_handler(start_handler)
    application.add_handler(entrada_handler)
    application.add_handler(salida_handler)
    

    #application.run_polling()

    # Se ejecuta para el /echo --> Devuelve todo lo que le escribamos
    echo_handler = MessageHandler((filters.TEXT) & (~filters.COMMAND), echo)
    
    application.add_handler(start_handler)
    application.add_handler(echo_handler)

    #application.run_polling()

    # Se ejecuta para el /caps --> Lo convierte todo a mayúsculas y lo devuelve
    """ caps_handler = CommandHandler('caps', caps)
    
    application.add_handler(start_handler)
    application.add_handler(echo_handler)
    application.add_handler(caps_handler) """

    #application.run_polling()

    # Se utiliza para el /setinline
    """ inline_caps_handler = InlineQueryHandler(inline_caps)
    application.add_handler(inline_caps_handler) """

    #application.run_polling()

    # Se usa cuando no se reconoce el comando
    # Other handlers
    """ unknown_handler = MessageHandler(filters.COMMAND, unknown)
    application.add_handler(unknown_handler) """

    #application.run_polling()

    #start_handler = CommandHandler('location', location)
    #start_handler = MessageHandler(filters._Location, location)
    #application.add_handler(start_handler)

    #application.run_polling()

    #Prueba para la localización
    location_handler = MessageHandler(filters.LOCATION & (~filters.COMMAND), location)
    
    application.add_handler(echo_handler)
    application.add_handler(location_handler)

    application.run_polling()