#!/usr/bin/env python
# coding: utf-8
#
# Copyright (c) 2016 Mirantis, Inc.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
import sys
import fcntl
import json
import urllib2
import time
import logging

from oslo_config import cfg
import oslo_messaging
import pika

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


def init_logging():
    formatter = logging.Formatter(
        fmt='%(levelname)-8s %(asctime)s '\
            '[%(name)s; %(filename)s:%(lineno)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    for handler in (logging.FileHandler(CONF.DEFAULT.log_file),
                    logging.StreamHandler()):
        handler.setFormatter(formatter)
        handler.setLevel(logging.DEBUG)
        root_logger.addHandler(handler)


def init_config(conf_files):
    # ----------------------------------------------------------------------    
    
    CONF.register_opts([
        cfg.StrOpt('lock_file', required=True, help='local path to lock file')
    ], 'DEFAULT')

    CONF.register_opts([
        cfg.StrOpt('log_file', required=True, help='local path to log file')
    ], 'DEFAULT')

    # ----------------------------------------------------------------------    

    CONF.register_opts([
        cfg.StrOpt('url', required=True, help='http listner server url')
    ], 'http_server')
    
    # ----------------------------------------------------------------------    

    CONF.register_opts([
        cfg.StrOpt('topic', required=True, help='Topic name')
    ], 'target')    
    CONF.register_opts([
        cfg.StrOpt('ip', required=True, help='RabbitMQ VIP')
    ], 'target')
    CONF.register_opts([
        cfg.StrOpt('password', required=True, help='RabbitMQ password')
    ], 'target')
    CONF.register_opts([
        cfg.StrOpt('user', required=True, help='RabbitMQ username')
    ], 'target')
    CONF.register_opts([
        cfg.IntOpt('port', required=True, help='RabbitMQ port')
    ], 'target')
    CONF.register_opts([
        cfg.StrOpt('queue_name', required=True, help='RabbitMQ queue name')
    ], 'target')
    CONF.register_opts([
        cfg.StrOpt('vhost', required=True, help='RabbitMQ vhost name')
    ], 'target')

    # ----------------------------------------------------------------------    


    conf_file = [conf_files[0] if conf_files else 'cadf_dispatcher.conf']
    
    CONF(default_config_files=conf_file, args='')
    
    CONF.log_opt_values(LOG, logging.DEBUG)


def is_cadf_dispatcher_locked():
    LOG.info('Checking cadf dispatcher locking...')
    
    global lockfile
    lockfile = open(CONF.DEFAULT.lock_file, 'w')
    
    try:
        fcntl.lockf(lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        LOG.error(
            'Cadf dispatcher is locked. There is another running instance.'
        )
        sys.exit(1)

    LOG.info('Cadf dispatcher is not locked.')
    return 0


def is_http_server_available():
    LOG.info('Checking http server %s availability...', CONF.http_server.url)
    res = False
    try:
        res = urllib2.urlopen(CONF.http_server.url, timeout=10).code < 400
        return res
    except (urllib2.URLError, urllib2.HTTPError) as e:
        LOG.error(e, exc_info=True)
    finally:
        if res:
            LOG.info('Http server %s is available.', CONF.http_server.url)
        else:
            LOG.info('Http server %s is unavailable.', CONF.http_server.url)


# left as is
def get_messages_count():
    # TODO (msenin) replace target.topic
    LOG.info('Asking RabbitMQ about %s.info queue messages count...', CONF.target.topic)
    try:
        creds = pika.credentials.PlainCredentials(CONF.target.user, CONF.target.password)
        # connect to pica and get cound of messsages
        connection = pika.BlockingConnection(pika.ConnectionParameters(
                CONF.target.ip,
                CONF.target.port,
                CONF.target.vhost,
                credentials=creds,
            )
        )
        
        channel = connection.channel()
        channel_info = channel.queue_declare(
            queue=CONF.target.queue_name,
            durable=False, 
            exclusive=False,
            auto_delete=False
        )
        messages_count = channel_info.method.message_count
        return messages_count
    except Exception as e:
        LOG.error(e)
        return 0


# left as is
def process_queue_messages():
    messages_count = get_messages_count()

    if messages_count > 0:
        LOG.info('Messages count in %s.info queue = %s.', CONF.target.topic, messages_count)
        handler = NotificationHandler(messages_count)
        server = oslo_messaging.get_notification_listener(oslo_messaging.get_transport(CONF),
                                                          [oslo_messaging.Target(topic=CONF.target.topic)],
                                                          [handler],
                                                          allow_requeue=True,
                                                          executor='threading')             
        LOG.info('Starting RabbitMQ listener to %s.info queue...', CONF.target.topic)
        server.start()
        while handler.messages_count > 0:
            time.sleep(5)
        time.sleep(5)
        LOG.info('Shutting listener down...')
        server.stop()
        LOG.info('Waiting until the listener stops properly...')
        server.wait()
    else:
        LOG.info('There are no messages in %s.info queue.', CONF.target.topic)


# left as is
class NotificationHandler(object):
    def __init__(self, messages_count):
        super(NotificationHandler, self).__init__()
        self.messages_count = messages_count

    def info(self, ctxt, publisher_id, event_type, payload, metadata):
        LOG.info('Processing message count is %s...', self.messages_count)
        LOG.debug(payload)
        self.messages_count -= 1
        data = json.dumps(payload)
        try:
            urllib2.urlopen(urllib2.Request(CONF.http_server.url, data, {
                'Content-Type': 'application/json',
                'Accept': '*/*',
                'User-Agent': 'keystone middleware',
                'Content-Length': len(data)}))
            LOG.info('Message has been removed from %s.info queue.', CONF.target.topic)
            return oslo_messaging.NotificationResult.HANDLED
        except (urllib2.URLError, urllib2.HTTPError) as e:
            LOG.error(e, exc_info=True)
            return oslo_messaging.NotificationResult.REQUEUE

    def warn(self, ctxt, publisher_id, event_type, payload, metadata):
        LOG.debug(payload)
        return oslo_messaging.NotificationResult.HANDLED

    def error(self, ctxt, publisher_id, event_type, payload, metadata):
        LOG.debug(payload)
        return oslo_messaging.NotificationResult.HANDLED


def main(argv):
    init_config(argv[1:])

    init_logging()

    is_cadf_dispatcher_locked()

    if not is_http_server_available():
        return 1

    process_queue_messages()
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))

