import json
import base64
import time
import os
import paho.mqtt.client as mqtt

TOPIC = "application/#"
LORASERVER_MQTTHOST = "127.0.0.1"
LORASERVER_MQTTPORT = 1883

mqttClient = mqtt.Client()

def print_hex(bytes):
    l = [hex(int(i)) for i in bytes]
    print(" ".join(l))

max_temperature = 20
min_temperature = 10

max_humidity = 30
min_humidity = 20

# 连接MQTT服务器
def on_mqtt_connect():
    mqttClient.connect(LORASERVER_MQTTHOST, LORASERVER_MQTTPORT, 60)
    mqttClient.loop_start()

# publish 消息
def on_publish(topic, payload, qos):
    mqttClient.publish(topic, payload, qos)

def ada_send_humidity(app_name, dev_eui, humidity):
    #print('humidity:%f, max:%d, min:%d' % (humidity, max_humidity, min_humidity))
    if (humidity > max_humidity) or (humidity < min_humidity):
        os.system('curl -X POST -H "Content-Type: application/json" -d \'{"value1":"%s","value2":"humidity:%.2f","value3":"1"}\' https://maker.ifttt.com/trigger/raktest/with/key/cs9iQUHh-w1nz5_MYBRMkZ' % (dev_eui, humidity))
        print('send humidity:%.2f to ifttt' % humidity)

def ada_send_ras_resistance(app_name, dev_eui, res):
    pass

def ada_send_pressure(app_name, dev_eui, pres):
    pass

def ada_send_temperature(app_name, dev_eui, temp):
    #print('temperature:%f, max:%d, min:%d' % (temp, max_temperature, min_temperature))
    if (temp > max_temperature) or (temp < min_temperature):
        os.system('curl -X POST -H "Content-Type: application/json" -d \'{"value1":"%s","value2":"temperature:%.2f","value3":"2"}\' https://maker.ifttt.com/trigger/raktest/with/key/cs9iQUHh-w1nz5_MYBRMkZ' % (dev_eui, temp))
        print('send temperature:%.2f to ifttt' % temp)

def ada_send_battery(app_name, dev_eui, batte):
    pass


# 消息处理函数
def on_message_come(lient, userdata, msg):
#    print('[on_message_come] in')
#    print(str(msg.payload))
    str_lora_rx = str(msg.payload, 'utf-8')
#    print(str_lora_rx)
#    print("************************************88")
    str_lora_rx = str_lora_rx.lstrip('b')
    str_lora_rx = str_lora_rx.lstrip('\'')
    str_lora_rx = str_lora_rx.rstrip('\'')
#    print(msg.topic + " " + ":" + str_lora_rx)
#    print('[on_message_come] in 001')
    try:
        json_rx = json.loads(str_lora_rx)
    except Exception as e:
        print('[on_message_come] in json.loads error')
        print(str_lora_rx) 
        print(e)
    finally:
        pass

    app_name = json_rx['applicationName']
    dev_eui = json_rx['devEUI']
    rx_data = base64.b64decode(json_rx['data'])
    print('dev_eui:%s lora data.' % dev_eui)
#    print('base64_decode_data***********************:')
#    print_hex(rx_data)
#    print('***********************base64_decode_data:')

    # gps,加头共11byte，不关注，去除抛弃
    if ((0x01 == rx_data[0]) and (0x88 == rx_data[1])):
        print('[on_message_come] gps')
        rx_data = rx_data[11:]

    # battery，加头共4byte
    if ((0x08 == rx_data[0]) and (0x02 == rx_data[1])):
        print('[on_message_come] battery')
        int_voltage = int.from_bytes(rx_data[2:4], byteorder='big', signed=True) ##signed标志是否为有符号数
        float_voltage = int_voltage * 0.01
        rx_data = rx_data[4:]
#        print('battery:%f' % float_voltage)
#    print('after battery***********************:')
#    print_hex(rx_data)
#    print('***********************after battery:')

    # Acceleration，加头共8byte，不关注，抛弃
    if ((0x03 == rx_data[0]) and (0x71 == rx_data[1])):
        print('[on_message_come] Acceleration')
        rx_data = rx_data[8:]
#    print('[on_message_come] 001')
    # humidity,湿度，加头共3byte
    if ((0x07 == rx_data[0]) and (0x68 == rx_data[1])):
        print('[on_message_come] humidity')
        try:
            int_humidity = int.from_bytes(rx_data[2:3], byteorder='big', signed=True)
        except Exception as e:
            print('humidity error')
            print(e)
        finally:
            pass
        float_humidity = int_humidity * 0.5
        print('humidity:%.2f' % float_humidity)
        ada_send_humidity(app_name, dev_eui, float_humidity)
        rx_data = rx_data[3:]

    # pressure,加头共4byte
    if ((0x06 == rx_data[0]) and (0x73 == rx_data[1])):
#        print('[on_message_come] pressure')
        int_pressure = int.from_bytes(rx_data[2:4], byteorder='big', signed=True)
        float_pressure = int_pressure * 0.1
        rx_data = rx_data[4:]
#    print('[on_message_come] 002')
    # temperature,加头共4byte
    if ((0x02 == rx_data[0]) and (0x67 == rx_data[1])):
        print('[on_message_come] temperature')
        int_temperature = int.from_bytes(rx_data[2:4], byteorder='big', signed=True)
        float_temperature = int_temperature * 0.1
        print('temperature:%.2f' % float_temperature)
        ada_send_temperature(app_name, dev_eui, float_temperature)

# subscribe 消息
def on_subscribe():
    mqttClient.subscribe(TOPIC, 1)
    mqttClient.on_message = on_message_come  # 消息到来处理函数

def main():
    on_mqtt_connect()
    on_subscribe()
    while True:
        pass


if __name__ == '__main__':
    main()

