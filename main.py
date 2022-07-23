import os
import json
import requests
import subprocess

from dotenv import load_dotenv
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt

load_dotenv()

# GPIO
led_pin = 4

# Beebotte
host = 'mqtt.beebotte.com'
username = os.getenv('IoT_BEEBOTTE_TOKEN')
password = ''
clientID = 'Raspberry456'
name = 'raspberry'
port = 1883
topic = os.getenv('IoT_BEEBOTTE_TOPIC')

# LINE
url = 'https://api.line.me/v2/bot/message/reply'
access_token = os.getenv('IoT_LINE_ACCESS_TOKEN')

def on_connect(client, userdata, flags, respons_code):
    print('status {0},{1}'.format(respons_code,userdata))
    client.subscribe(topic)

def on_message(client, userdata, msg):
    print(msg.topic + ' ' + str(msg.qos) + ' ' + str(msg.payload))

    lineData = json.loads(msg.payload.decode())
    token  = lineData['data'][0]['TOKEN']
    message = lineData['data'][0]['MESG']

    print(f'{token} - {message}')

    reply_message = {
        'type': 'sticker',
        'stickerId': '52114129',
        'packageId': '11539'
    }

    if message == 'ON':
        reply_message = {
            'type': 'sticker',
            'stickerId': '52002740',
            'packageId': '11537'
        }
        GPIO.output(led_pin, 1)
        subprocess.run(['/usr/bin/python3', '/home/pi/IoT/irrp.py', '-p', '-g22', '-f', '/home/pi/IoT/codes', '--gap', '1', 'power:on:1', 'power:on:2', 'power:on:3'])
    elif message == 'OFF':
        reply_message = {
            'type': 'sticker',
            'stickerId': '52114128',
            'packageId': '11539'
        }
        GPIO.output(led_pin, 0)
        subprocess.run(['/usr/bin/python3', '/home/pi/IoT/irrp.py', '-p', '-g22', '-f', '/home/pi/IoT/codes', '--gap', '1', 'power:off:1', 'power:off:2', 'power:off:3'])

    headers ={
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': 'Bearer ' + access_token,
    }
    obj = {
        'replyToken': token,
        'messages': [reply_message]
    }
    json_data = json.dumps(obj).encode('utf-8')
    response = requests.post(url, headers=headers, data = json_data)
    print(response)

if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(led_pin, GPIO.OUT)

    client = mqtt.Client(client_id=clientID, clean_session=True, protocol=mqtt.MQTTv311, transport='tcp')
    client.username_pw_set(username, password=password)

    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(host, port=port, keepalive=60)
    client.loop_forever()
