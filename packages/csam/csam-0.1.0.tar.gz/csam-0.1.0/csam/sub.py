import paho.mqtt.client as mqtt
import time

broker = "148.247.201.226"
# broker = "localhost"
port = 1883
topic = "files/"
hash = "ejemplo"
file_state = None
waiting = True

def on_connect(client, userdata, flags, rc, properties = None):
	if rc == 0:
		client.subscribe(f"{topic}{hash}", qos = 1)
	else:
		# print(f"Fallo al conectar, código: {rc}")
		pass

def on_message(client, userdata, msg):
    # print(f"Mensaje recibido: {msg.payload.decode()} en el tema: {msg.topic}")
    if (msg.payload.decode() == "ready"):
        # print("ENTRANDO A CANCELAR")
        global waiting
        waiting = False
        # client.loop_stop()

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

def subToTopic(topic_hash):
	global hash
	hash = topic_hash

	client.on_connect = on_connect
	client.on_message = on_message

	try:
		client.connect(broker, port)
		# client.loop_forever()
		client.loop_start()
		while waiting:
			time.sleep(0.3)
	except Exception as e:
		# print(f"Error al conectar: {e}")
		exit()
	finally:
		client.loop_stop()
		client.disconnect()


def setBrokerUrl(url):
	global broker
	broker = url

def setBrokerPort(p):
	global port
	port = p