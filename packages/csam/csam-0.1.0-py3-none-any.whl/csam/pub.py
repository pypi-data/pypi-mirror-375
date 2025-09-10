import paho.mqtt.client as mqtt
import time
import random

broker = "148.247.201.226"  
# broker = "localhost"
port = 1883
topic = "files/"
pub_confirmed = False
def on_connect(client, userdata, flags, rc, properties = None):
	if rc == 0:
		# print("Conectado al broker MQTT!")
		pass
	else:
		# print(f"Fallo al conectar, código de retorno: {rc}")
		pass

def on_publish(client, userdata, mid, rc, properties=None):
    global pub_confirmed
    if rc == 0:
        # print(f"Mensaje con ID {mid} publicado y confirmado.")
        pub_confirmed = True
    else:
        # print(f"Fallo al publicar el mensaje con ID {mid}.")
        pub_confirmed = False

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

def pubTopic(hash = "test-hash", value = "test value"):
	client.on_connect = on_connect
	client.on_publish = on_publish
	try:
		client.connect(broker, port, 60)
	except Exception as e:
		# print(f"Error al conectar: {e}")
		exit()

	client.loop_start()

	try:	
		result = client.publish(f"{topic}{hash}", value, retain=True, qos = 1)
		timeout = time.time() + 10
		while not pub_confirmed and time.time() < timeout:
			time.sleep(0.1)
		if (pub_confirmed):
			# print(f"Publicado exitosamente '{value}' en el tema '{topic}{hash}'")
			client.loop_stop()
			client.disconnect()
			# print("Publicador detenido.")
			return {"pub": True}
		else:
			# print(f"Fallo al publicar mensaje al tema {topic}")
			client.loop_stop()
			client.disconnect()
			# print("Publicador detenido.")
			return {"pub": False}
		# if result[0] == 0:
		# 	print(f"Publicado exitosamente '{value}' en el tema '{topic}{hash}'")
		# 	return {"pub": True}
		# else:
		# 	# print(f"Fallo al publicar mensaje al tema {topic}")
		# 	return {"pub": False}
		# client.loop_stop()
		# client.disconnect()
		# print("Publicador detenido.")

	except KeyboardInterrupt:
		# print("Fallo inesperado.")
		pass

def setBrokerUrl(url):
	global broker
	broker = url

def setBrokerPort(p):
	global port
	port = p