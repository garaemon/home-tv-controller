#!/usr/bin/env python
import socket
import re
import os
from urllib.parse import urlparse
import logging

import pylgtv
import paho.mqtt.client as mqtt

logger = logging.getLogger()


class App(object):
    LGTV_CLIENT_KEY_ENV = 'LGTV_CLIENT_KEY'
    CLOUD_MQTT_URL_ENV = 'CLOUDMQTT_URL'
    LOGGLY_TOKEN_ENV = 'LOGGLY_TOKEN'

    def __init__(self):
        self.verify_environmental_variables()
        ip = App.find_tvs()[0]
        self.client = pylgtv.WebOsClient(ip)
        self.client.client_key = os.environ[self.LGTV_CLIENT_KEY_ENV]

    def verify_environmental_variables(self):
        envs = [self.LGTV_CLIENT_KEY_ENV, self.CLOUD_MQTT_URL_ENV,
                self.LOGGLY_TOKEN_ENV]
        for env in envs:
            logging.info('Verifying %s' % env)
            if env not in os.environ:
                raise Exception('No %s is defined in environmental variables.'
                                % env)

    def connect_mqtt(self):
        logger.info('Connect to mqtt server')
        self.mqtt_client = mqtt.Client(protocol=mqtt.MQTTv311)
        url = urlparse(os.environ[self.CLOUD_MQTT_URL_ENV])
        self.mqtt_client.username_pw_set(username=url.username,
                                         password=url.password)
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.connect(url.hostname, port=url.port)

    def setup_mqtt_subscribers(self):
        self.mqtt_client.subscribe('tv/turn_on')
        self.mqtt_client.subscribe('tv/turn_off')
        self.mqtt_client.subscribe('tv/volume_up')
        self.mqtt_client.subscribe('tv/volume_down')
        self.mqtt_client.subscribe('tv/channel_up')
        self.mqtt_client.subscribe('tv/channel_down')

    def on_connect(self, client, userdata, flags, rc):
        self.is_connected = True
        logger.info('Connected to MQTT Broker')
        self.setup_mqtt_subscribers()

    def on_message(self, client, userdata, message):
        topic = message.topic
        if topic == 'tv/turn_on':
            self.client.power_on()
        elif topic == 'tv/turn_off':
            self.client.power_off()
        elif topic == 'tv/volume_up':
            self.client.volume_up()
        elif topic == 'tv/volume_down':
            self.client.volume_down()
        elif topic == 'tv/channel_up':
            self.client.channel_up()
        elif topic == 'tv/channel_down':
            self.client.channel_down()
        else:
            raise Exception('Unsupported topic: %s' % topic)

    def run_forever(self):
        self.mqtt_client.loop_forever()

    def power_off(self):
        self.client.power_off()

    def power_on(self):
        self.client.power_on()

    # originally from https://github.com/grieve/python-lgtv/blob/master/lg.py
    @classmethod
    def _find_tvs(cls, attempts=10, first_only=False):
        """
        Create a broadcast socket and listen for LG TVs responding.
        Returns list of IPs unless `first_only` is true, in which case it
        will return the first TV found.
        """

        request = 'M-SEARCH * HTTP/1.1\r\n' \
                  'HOST: 239.255.255.250:1900\r\n' \
                  'MAN: "ssdp:discover"\r\n' \
                  'MX: 2\r\n' \
                  'ST: urn:schemas-upnp-org:device:MediaRenderer:1\r\n\r\n'

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(1)

        addresses = []
        while attempts > 0:
            sock.sendto(request.encode(), ('239.255.255.250', 1900))
            try:
                response, address = sock.recvfrom(512)
            except:
                attempts -= 1
                continue

            if re.search('LG', str(response)):
                if first_only:
                    sock.close()
                    return address[0]
                else:
                    addresses.append(address[0])

            attempts -= 1

        sock.close()
        return addresses

    @classmethod
    def find_tvs(cls, attempts=10, first_only=False):
        return list(set(cls._find_tvs(attempts, first_only)))

    @classmethod
    def get_new_client_key(cls, ip):
        client = pylgtv.WebOsClient(ip)
        client.register()
        return client.client_key


if __name__ == '__main__':
    app = App()
    app.power_off()
