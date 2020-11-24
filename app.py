import sys
import urllib.request, re
import requests, json
import redis
from flask import Flask, render_template, redirect, request, url_for, session, flash

app = Flask(__name__)

r = redis.Redis(host='localhost', charset="utf-8", port=6379, db=0, decode_responses=True)
global sesionus
global mediassolicitadasTS
global mediassolicitadasRDS
global iusuario

@app.route('/')
def inicio():
	Valor=EscrituraThingSpeak()
	ValorRE=EscrituraRedis()
	global mediassolicitadasTS
	mediassolicitadasTS=0
	global mediassolicitadasRDS
	mediassolicitadasRDS=0
	return render_template("inicio.html", numeroaleatorio=str(Valor))

@app.route('/registro')
def registro():
	return render_template('registro.html')

@app.route('/acceso', methods = ["POST","GET"])
def acceso():
	if (request.method == "POST"):
		rcorreo=request.form.get('correo')
		rnombre=request.form.get('nombre')
		rclave1=request.form.get('Password1')
		rclave2=request.form.get('Password2')
		if(rclave1==rclave2):
			check = busquedaRedis(rcorreo,rnombre)
			if (check==1):
				mensaje='<font color="red">Este correo ya esta registrado</font>'
				return render_template('registro.html', rerror=str(mensaje))
			elif (check==2):
				mensaje='<font color="red">El nombre de usuario ya existe, escoga otro nombre de usuario</font>'
				return render_template('registro.html', rerror=str(mensaje))
			elif (check==0):
				r.lpush("mails",rcorreo)
				r.lpush("users",rnombre)
				r.lpush("claves",str(rclave1))
				r.lpush("conteomediaTS",str(0))
				r.lpush("conteomediaRD",str(0))
				mensaje='<font color="green">El usuario se registro correctamente</font>'
				return render_template("acceso.html", aerror=str(mensaje))
		else:
			mensaje='<font color="red">Las claves no coinciden, introducta de nuevo los datos</font>'
			return render_template('registro.html', rerror=str(mensaje))
	else:
		return render_template("acceso.html")
		
@app.route('/accesousuario', methods=['POST'])
def accesousuario():
	if (request.method == "POST"):
		anombre=request.form.get('nombre')
		aclave=request.form.get('password')
		check=accesoRedis(anombre,aclave)
		if (check==0):
			mensaje='<font color="red">El usuario no existe, por favor registrese primero</font>'
			return render_template("acceso.html", aerror=str(mensaje))
		elif (check==1):
			mensaje='<font color="red">La clave no coincide con la registrada para ese usuario</font>'
			return render_template("acceso.html", aerror=str(mensaje))
		elif (check==2):
			Valor=EscrituraThingSpeak()
			global sesionus
			sesionus=anombre
			global mediassolicitadasRDS
			global mediassolicitadasTS
			global iusuario
			conteomediaRD=r.lrange("conteomediaRD",0,-1)
			mediassolicitadasRDS=int(conteomediaRD[iusuario])
			conteomediaTS=r.lrange("conteomediaTS",0,-1)
			mediassolicitadasTS=int(conteomediaTS[iusuario])
			bbddmedia='ThingSpeak/Redis'
			return render_template("accesousuario.html", mediabbdd=str(bbddmedia), numeroaleatorio=str(Valor), ussesion=sesionus, mediasTS=str(mediassolicitadasTS), mediasRD=str(mediassolicitadasRDS));

@app.route('/accesousuariomedia')
def accesousuariomedia():
	Valor=LecturaThingSpeak(1)
	Media=MediaThingSpeak()
	bbddmedia='ThingSpeak'
	global mediassolicitadasTS
	global iusuario
	mediassolicitadasTS += 1
	r.lset("conteomediaTS",iusuario,mediassolicitadasTS)
	return render_template("accesousuariomedia.html", mediabbdd=str(bbddmedia), numeroaleatorio=str(Valor), mediaTS=str(Media), ussesion=sesionus, mediasTS=str(mediassolicitadasTS), mediasRD=str(mediassolicitadasRDS));
	
@app.route('/accesousuariomediaRE')
def accesousuariomediaRE():
	Valor=LecturaThingSpeak(1)
	Media=MediaRedis()
	bbddmedia='Redis'
	global mediassolicitadasRDS
	global iusuario
	mediassolicitadasRDS += 1
	r.lset("conteomediaRD",iusuario,mediassolicitadasRDS)
	return render_template("accesousuariomedia.html", mediabbdd=str(bbddmedia), numeroaleatorio=str(Valor), mediaTS=str(Media), ussesion=sesionus, mediasTS=str(mediassolicitadasTS), mediasRD=str(mediassolicitadasRDS));
	
@app.route('/accesousuarioumbral', methods=['POST'])
def accesousuarioumbral():
	Valor=LecturaThingSpeak(1)
	bbddmedia='ThingSpeak/Redis'
	if (request.method == "POST"):
		umbral=request.form.get("wumbral")
		a=umbral.isdigit()
		if (a==True):
			(numumbral1,numumbral2,numumbral3,numumbral4,numumbral5)=numUmbral(umbral)
			if (numumbral1==0):
				message="Ningun valor de la base de datos supera el umbral definido"
				return render_template("accesousuarioumbral.html", mediabbdd=str(bbddmedia), numeroaleatorio=str(Valor),umbS=str(umbral), valoressobreumbral1=message, ussesion=sesionus, mediasTS=str(mediassolicitadasTS), mediasRD=str(mediassolicitadasRDS));
			elif (numumbral2==0):
				return render_template("accesousuarioumbral.html", mediabbdd=str(bbddmedia), numeroaleatorio=str(Valor),umbS=str(umbral),valoressobreumbral1=str(numumbral1), ussesion=sesionus, mediasTS=str(mediassolicitadasTS), mediasRD=str(mediassolicitadasRDS));
			elif (numumbral3==0):
				return render_template("accesousuarioumbral.html", mediabbdd=str(bbddmedia), numeroaleatorio=str(Valor),umbS=str(umbral),valoressobreumbral1=str(numumbral1),valoressobreumbral2=str('- '+str(numumbral2)), ussesion=sesionus, mediasTS=str(mediassolicitadasTS), mediasRD=str(mediassolicitadasRDS));
			elif (numumbral4==0):
				return render_template("accesousuarioumbral.html", mediabbdd=str(bbddmedia), numeroaleatorio=str(Valor),umbS=str(umbral),valoressobreumbral1=str(numumbral1),valoressobreumbral2=str('- '+str(numumbral2)),valoressobreumbral3=str('- '+str(numumbral3)), ussesion=sesionus, mediasTS=str(mediassolicitadasTS), mediasRD=str(mediassolicitadasRDS));
			elif (numumbral5==0):
				return render_template("accesousuarioumbral.html", mediabbdd=str(bbddmedia), numeroaleatorio=str(Valor),umbS=str(umbral),valoressobreumbral1=str(numumbral1),valoressobreumbral2=str('- '+str(numumbral2)),valoressobreumbral3=str('- '+str(numumbral3)),valoressobreumbral4=str('- '+str(numumbral4)), ussesion=sesionus, mediasTS=str(mediassolicitadasTS), mediasRD=str(mediassolicitadasRDS));
			else:
				return render_template("accesousuarioumbral.html", mediabbdd=str(bbddmedia), numeroaleatorio=str(Valor),umbS=str(umbral),valoressobreumbral1=str(numumbral1),valoressobreumbral2=str('- '+str(numumbral2)),valoressobreumbral3=str('- '+str(numumbral3)),valoressobreumbral4=str('- '+str(numumbral4)),valoressobreumbral5=str('- '+str(numumbral5)), ussesion=sesionus, mediasTS=str(mediassolicitadasTS), mediasRD=str(mediassolicitadasRDS));
		else:
			error = '<font color="red">El umbral debe ser un numero entero entre 1 y 99</font>'
			return render_template("accesousuarioumbral.html", mediabbdd=str(bbddmedia), numeroaleatorio=str(Valor),umbS=str(umbral), valoressobreumbral1=str(error), ussesion=sesionus, mediasTS=str(mediassolicitadasTS), mediasRD=str(mediassolicitadasRDS));

@app.route('/accesousuariografica')
def accesousuariografica():
	Valor=LecturaThingSpeak(1)
	bbddmedia='ThingSpeak/Redis'
	return render_template("accesousuariografica.html", mediabbdd=str(bbddmedia), numeroaleatorio=str(Valor), ussesion=sesionus, mediasTS=str(mediassolicitadasTS), mediasRD=str(mediassolicitadasRDS));
    
# Escritura en la bbdd de ThingSpeak
def EscrituraThingSpeak():
	fileWeb = urllib.request.urlopen("https://www.numeroalazar.com.ar/")
	web = fileWeb.read().decode("utf-8")
	RandomNumber =re.search('\d\d\.\d\d',str(web)).group(0)
	UrlW = 'https://api.thingspeak.com/update?api_key=ZL3SLW04HRLYSD5Z&field1='
	TSwURL = urllib.request.urlopen(UrlW + str(RandomNumber))
	return(str(RandomNumber))

# Escritura en la bbdd de Redis	
def EscrituraRedis():
	fileWeb = urllib.request.urlopen("https://www.numeroalazar.com.ar/")
	web = fileWeb.read().decode("utf-8")
	RandomNumber =re.search('\d\d\.\d\d',str(web)).group(0)
	r.lpush("RandomNumber",RandomNumber)

# Lectura en la bbdd de ThingSpeak
def LecturaThingSpeak(NumberOfReads = 1):
	UrlR='https://api.thingspeak.com/channels/1204208/fields/1.json?api_key=BMRDYHNGVVB2VNLR&results='
	TSrUrl=UrlR+str(NumberOfReads)
	ReadData=requests.get(TSrUrl).json()
	return (ReadData["feeds"][0]['field1'])

# Calculo de la media de los valores de ThingSpeak
def MediaThingSpeak():
	a=float(0)
	fileTSmedia = urllib.request.urlopen('https://api.thingspeak.com/channels/1204208/last_entry_id.json')
	entries = int(fileTSmedia.read())
	UrlM = 'https://api.thingspeak.com/channels/1204208/fields/1.json?api_key=BMRDYHNGVVB2VNLR&results='
	TSUrlRead = UrlM + str(entries)
	get_data = requests.get(TSUrlRead).json()
	for i in range(entries):
		a += float(get_data["feeds"][int(i)]['field1'])
	media = a / entries
	return ("%.2f" %media)
	
def MediaRedis():
	media=0
	a=float(0)
	RandomNumber=r.lrange("RandomNumber",0,-1)
	for i in range(int(r.llen("RandomNumber"))):
		a+= float(RandomNumber[i])
	media=a/float(r.llen("RandomNumber"))
	return ("%.2f" %media)

def numUmbral(umbral):
	fileTSmedia = urllib.request.urlopen('https://api.thingspeak.com/channels/1204208/last_entry_id.json')
	entries = int(fileTSmedia.read())
	UrlM = 'https://api.thingspeak.com/channels/1204208/fields/1.json?api_key=BMRDYHNGVVB2VNLR&results='
	get_data = requests.get(UrlM+str(entries)).json()
	umbflag=0
	vumbral = [0,0,0,0,0]
	for i in range(entries):
		if (float(get_data["feeds"][int(entries-1-i)]['field1'])>float(umbral)):
			vumbral[umbflag]=float(get_data["feeds"][int(entries-1-i)]['field1'])
			umbflag += 1
		if (umbflag == 5):
			break
	return (vumbral[0],vumbral[1],vumbral[2],vumbral[3],vumbral[4])
	
def numUmbralRedis(umbral):
	RandomNumber=r.lrange("RandomNumber",0,-1)
	vumbral = [0,0,0,0,0]
	umbflag=0
	for i in range(int(r.llen("RandomNumber"))):
		if(float(RandomNumber[i]>float(umbral))):
			vumbral[umbflag]=float(RandomNumber[i])
			umbflag += 1
		if (umbflag == 5):
			break
	return (vumbral[0],vumbral[1],vumbral[2],vumbral[3],vumbral[4])

def busquedaRedis(mail,user):
	mails=r.lrange("mails",0,-1)
	users=r.lrange("users",0,-1)
	a=0
	for i in range(int(r.llen("mails"))):
		if(mails[i]==mail):
			a=1
			break
		if(users[i]==user):
			a=2
	return(a)

def accesoRedis(user,clave):
	users=r.lrange("users",0,-1)
	claves=r.lrange("claves",0,-1)
	a=0
	for i in range(int(r.llen("users"))):
		if(users[i]==user):
			a=1
			if(claves[i]==clave):
				global iusuario
				iusuario=i
				a=2
			break
	return(a)

if __name__ == "__main__":
	#app.run()
	app.run(host='0.0.0.0', port=5000, debug=True)