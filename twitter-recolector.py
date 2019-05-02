#!/usr/bin/python

#-*- coding: utf-8 -*-

"""
* @author Luis Diago de Aguilar
*
* Codigo pensado para sacar informacion de twitter y poder hacer OSINT de manera automatizada y facil
* El documento tiene notas repartidas para poder saber lo que estamos haciendo, mejoras que se pueden implementar, etc.
*
* Este codigo es open source y puede modificarse al completo por cualquier persona interesada en implementar cualquier mejora.
*
"""

# Imports que vamos a necesitar

import re
import sys
import smtplib
from tweepy import OAuthHandler
from tweepy import API
from tweepy import Cursor
from tweepy.streaming import StreamListener
from datetime import datetime, date, time, timedelta
from collections import Counter
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Necesitamos esto para que el archivo se guarde como utf-8 en caso de contener caracteres especiales

reload(sys)
sys.setdefaultencoding('utf8')

# Las credenciales de conexion con la api de twitter

consumer_key=""
consumer_secret=""
access_token=""
access_token_secret=""

# Aqui se realiza la autenticacion con nuestras claves

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
auth_api = API(auth)


""" 
* Aqui va el main del programa, donde llamaremos a todas las funciones para su futura ejecucion
*
* @author Luis Diago de Aguilar 
*
"""

def __main__():

# Queremos que nos lea un fichero para hacer el seguimiento de usuarios

  f = open ('usuarios_monitorizar','r')
  account_list = f.readlines() 
  print("Se van a gestionar los siguientes usuarios de twitter para su monitorizacion:")
  print(account_list)
  print("-----------------------------------------------------------------------------\n")

  if (len(account_list) > 1):
    account_list = account_list[0:]
    informacion_cuentas_individuales(account_list)
  else:
    print("Por favor, provee una lista de usuarios en el doc.")
    sys.exit(0)


"""
* Vamos a escribir en el fichero los datos de twitter para compararlos con los que ya tenemos y asi 
* saber si la hemos recibido esos datos o no antes de enviar el correo.
*
* @author Luis Diago de Aguilar
*
"""

def escribe_fichero(texto, target):
  target = target.replace("\n","")
  #texo = texto.encode('ascii', 'ignore').decode('ascii')
  #try:
  print("###################################")
  print(" SE ESTA ESCRIBIENDO EN EL FICHERO ")
  print("###################################")
  print
  print("Item = " + target)
  print
  try:
    print("###################################")
    #EL wb+ lo que hace es crear un fichero nuevo en caso de no existir el mismo
    file = open(target,'wb+')
    contenido_fich = file.read()
    if contenido_fich != texto:
      # Si va bien y no coinciden los tuits nos enviara el correo electronico y ademas guardara los datos en el fichero
      f = open(target, 'w')
      f.write(texto)
    else:
      print("--- No hemos escrito nada porque el contenido era igual ---")
      print("--- No hemos enviado nada porque el contenido era igual ---")
  except:
    print("\nError en la apertura del fichero\n")	



"""
* Vamos a hacer un try except para capturar el problema del servidor de correo durante las pruebas 
* o para saber si no funciona en el servidor
*
* @author Luis Diago de Aguilar
*
"""

def mailer_class(target, message):
  target = target.replace("\n","")
#  
  msg = MIMEMultipart()
# ponemos los parametros de informacuon del mensaje
  password = ""
  msg['From'] = ""
  msg['To'] = ""
  msg['Subject'] = "[Monitorizacion Twitter][OSINT][Usuario: " + target + "]"

  print "EL OBJETIVO --------------------------------------------------------"
  print target
  print "EL MENSAJE ---------------------------------------------------------"
  print message
#  
  try:   
#
# anadimos el cuerpo del mensaje
    msg.attach(MIMEText(message, 'plain'))
#
# create server
    server = smtplib.SMTP('smtp.gmail.com')
#   
    server.starttls()
#
# Login Credentials para enviar el correo
    server.login(msg['From'], password)
#   
#   
# Envia el mensaje a traves del servidor
    server.sendmail(msg['From'], msg['To'], msg.as_string())
#   
    server.quit()
    print ("Envio correcto del correo a: " + msg['To'])
#
  except:
#
    print("\nNo se pudo conectar con el servidor de correo\n")


""" 
* Aqui va la funcion cuentas individuales del programa.
*
* En esta funcion llamaremos a diferentes funciones para sacar el contenido de las cuentas de tweeter que introducimos en el fichero
* Como posible actualizacion y mejora del programa estaria bien poder incluir diferentes funciones para subdividir los procesoso que se generan
* en esta funcion, reducinedo asi el espacio de la misma al minimo y haciendo que esta se a mas clara para sus posibles actualizaciones.
*
* @author Luis Diago de Aguilar 
*
"""

def informacion_cuentas_individuales(account_list):
#
  
  if len(account_list) > 0:
    for target in account_list:
      # Metemos aqui un try catch por si el usuario no se encuentra o se da algun problema
      try:
        try:
          print("\n\nObteniendo datos de " + target)
          item = auth_api.get_user(target)

# Vamos dando valores a las variables para luego mandarnoslas por correo
      
          message="Nombre: " +item.name+"\n"
          message+="Nombre de usuario: " +item.screen_name+"\n"
          message+="Descripcion: " + item.description+"\n"
          message+="Statuses count: " + str(item.statuses_count)+"\n"
          message+="Usuarios seguidos: " +str(item.friends_count)+"\n"
          message+="Usuarios seguidores: " +str(item.followers_count)+"\n"
		
          tweets = item.statuses_count
          account_created_date = item.created_at
          delta = datetime.utcnow() - account_created_date
          account_age_days = delta.days
        #print("Tiempo que tiene la cuenta (en dias): " + str(account_age_days))
          message+="Cuenta creada hace " + str(account_age_days) + " dias\n"
          if account_age_days > 0:
          #print("Numero de tuits por dia: " + "%.2f"%(float(tweets)/float(account_age_days)))
            message+="Numero de tuits por dia " + str(float(tweets)/float(account_age_days)) + "\n"
            hashtags = []
            mentions = []
            tweet_count = 0
            end_date = datetime.utcnow() - timedelta(days=100)
            for status in Cursor(auth_api.user_timeline, id=target).items():
              tweet_count += 1
              if hasattr(status, "entities"):
                entities = status.entities
                if "hashtags" in entities:
                  for ent in entities["hashtags"]:
                    if ent is not None:
                      if "text" in ent:
                        hashtag = ent["text"]
                        if hashtag is not None:
                          hashtags.append(hashtag)
                if "user_mentions" in entities:
                  for ent in entities["user_mentions"]:
                    if ent is not None:
                      if "screen_name" in ent:
                        name = ent["screen_name"]
                        if name is not None:
                          mentions.append(name)
                if status.created_at < end_date:
                  break
        except:
      	  print "FASE 1 INCOMPLETA"

        try:
#
# Para los usuarios mas mencionados por el usuario en cuestion
#
        #print("\nUsuarios que mas menciona:\n")
          for item, count in Counter(mentions).most_common(10):
          #print(item + " t: " + str(count))
            message+="Usuario: " + item
            message+=" tuits realizados nombrandolo: "
            message+= str(count) +"\n"
        except:
      	  print "FASE 2 INCOMPLETA"
        try:

#
# Para los hastags mas mencionados por el usuario en cuestion
#
        #print("\nHastags que mas menciona:\n")
          for item, count in Counter(hashtags).most_common(10):
          #print(item + " t: " + str(count))
            message+="Hastags: " + item
            message+=" tuits realizados nombrandolo: "
            message+= str(count) +"\n"
#
          print
        #print ("Todo correcto. Procesados " + str(tweet_count) + " tweets.")
          message+="Tuits totales de la cuenta: " + str(tweet_count) + "." + "\n"
          message+="\n\n\n"
          message+="____________________________________________________________"
          message+="\n\n\n"

        except:
      	  print "FASE 3 INCOMPLETA"
      
        try:
          contenido_tweet=""
          el_tuit_en_si = ""

      # Nota: leer la NOTA 1 del final
          stuff = Cursor(auth_api.user_timeline, id=target, include_rts = True)
          end_date = datetime.utcnow() - timedelta(days=100)
          print ("--------------")
          print ("--- TWEETS ---")
          print ("--------------")
          print
          for status in stuff.items(10):
            el_tuit_en_si+=str(status.text + "\n-----\n")
            print ("EL TUIT EN SI")
            print(el_tuit_en_si)
            print()
            print("--------------")
          print
          print "-_-_EL CONTENIDO DEL TUIT DEL MENSAJE_-_-"
          print
          message+=el_tuit_en_si
          print "FASE 4 COMPLETA"
        except:
          print "FASE 4 INCOMPLETA"
        try:

          contador = 0
        
      # Vamos a guardar las urls de cada tweet, debido a que tienen un identificador unico
          for status in Cursor(auth_api.user_timeline, id=target, include_entities=True).items(20): 
            for url in status.entities['urls']:
              ruta=url['expanded_url']+"\n"
              target = target.replace("\n","")
              f = open(target, "a+")
              lines = f.readlines()
              contador=contador+1
          #si coincide, no las guardamos

              if ruta in lines:
                print ('ruta in lines')

              else:
                print("ruta not in lines")
            ###
                contenido_tweet+= ruta
              f.close()

# Necesitamos este if como comprobacion para poder saber si hemos recolectado nuevo contenido o no
# si no hemos recolectado nuevo contenido pasamos, pq no queremos correos repetidos. Hacemos unos prints de comprobacion
          if contenido_tweet != "":
            contenido_tweet=str(contenido_tweet)
            message=str(message)
# Llamamos a las funciones que escriben en el fichero y que escriben el correo
            print("********************MENSAJE*************************")
            print(message)
            print("****************************************************")
            escribe_fichero(contenido_tweet, target)
            mailer_class(target,message)
            print("---------------------------------------")
            print("               FIN USER                ")
          else:
            print("---------------------------------------")
            print("            URL YA CONTENIDAS          ")
        except:
          print("FASE 5 INCOMPLETA")
      except:
        print "El usuario no se encuentra disponible, ha sido bloqueado o se han sobrepasado las peticiones de la API"
	    
""" 
* Aqui va la llamada al main para el inicio del programa.
* Tambien podras ver la instanciacion de algunas variables globales
*
* @author Luis Diago de Aguilar 
*
"""

account_list = []
item=""
#
# Llamamos al main
#
__main__()


# Escribe_fichero(contenido_tweet)
#
# Fin
#


# Notas extras: 

""" 
*
* NOTA 1
*
* Montamos el cursor para poder realizar la monitorizacion de los ultimos tweets del usuario en cuestion
* Posteriormente llamamos a la funcion de imprimir los tweets y le decimos que nos de los 10 ultimos
* Necesitamos guardar los ultimos tweets en un fichero, pero no queremos que se mezclen con el resto de info,
* por ello vamos a crear una variable global en la que guardemos todos.
*

        print("Nombre: " + item.name)
        print("Nombre de usuario: " + item.screen_name)
        print("Descripcion: " + item.description)
        print("statuses_count: " + str(item.statuses_count))
        print("Usuarios seguidos: " + str(item.friends_count))
        print("Usuarios seguidores: " + str(item.followers_count))
		"""