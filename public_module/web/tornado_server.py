#!/usr/bin/env python3
#
# Copyright 2009 Facebook
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

import asyncio
import threading

import tornado.escape
import tornado.ioloop
import tornado.locks
import tornado.web
import os.path
import uuid

from tornado.options import define, options, parse_command_line

from deploy.es import es_install
from deploy.es.es_config import ESInstallConfig, get_yml_value
from deploy.es.es_install import re_construct_config
from public_module import to_text
from public_module.global_vars import addNotifier, removeNotifier
from public_module.ssh_connect.paramiko_ssh import ParamikoConnection
from public_module.utils import none_null_stringNone, path_join
from ui.myThread import NotifyCombine

define("port", default=8888, help="run on the given port", type=int)
define("debug", default=True, help="run in debug mode")


class MessageBuffer(object):
    def __init__(self):
        # cond is notified whenever the message cache is updated
        self.cond = tornado.locks.Condition()
        self.cache = []
        self.cache_size = 200

    def get_messages_since(self, cursor):
        """Returns a list of messages newer than the given cursor.

        ``cursor`` should be the ``id`` of the last message received.
        """
        results = []
        for msg in reversed(self.cache):
            if msg["id"] == cursor:
                break
            results.append(msg)
        results.reverse()
        return results

    # def add_message(self, message):
    #     self.cache.append(message)
    #     if len(self.cache) > self.cache_size:
    #         self.cache = self.cache[-self.cache_size :]
    #     self.cond.notify_all()

    def write(self,msg):
        msg = {"id": str(uuid.uuid4()), "body": msg}
        self.cache.append(msg)
        if len(self.cache) > self.cache_size:
            self.cache = self.cache[-self.cache_size :]
        self.cond.notify_all()



def start_es_wrap(messagebuffer:MessageBuffer,config):
    def _inner():
        _n = NotifyCombine(messagebuffer,None,None)
        addNotifier(_n)
        es_install.install(config)
        es_install.start_es(config)
        with ParamikoConnection(config.ssh_host,config.ssh_user,config.ssh_passwd,config.ssh_port) as pk:
            pk.outputlog(path_join(get_yml_value(config.yml_config,*('path','logs')),get_yml_value(config.yml_config,*('cluster','name'))+'.log'),240)
        removeNotifier()
    threading.Thread(target=_inner).start()

global_message_buffer = {}
global_config = {}

def setConfig(p_config={}):
    global global_config
    global_config = p_config

class LogHandler(tornado.web.RequestHandler):
    def get(self):
        host_id = to_text(self.request.arguments.get('host_id')[0])
        log_file = self.request.arguments.get('log_file')
        ssh_host = self.request.arguments.get('ssh_host')
        ssh_port = self.request.arguments.get('ssh_port')
        ssh_passwd = self.request.arguments.get('ssh_passwd')
        ssh_user = self.request.arguments.get('ssh_user')
        # self.render("index.html", messages=global_message_buffer[host_id].cache)
        msgs = []
        for msg in global_message_buffer[host_id].cache:
            if not msg.get('html',None):
                msg["html"] = tornado.escape.to_unicode(self.render_string("message.html", message=msg))
            msgs.append(msg)
        self.render("index.html", messages=msgs,host_id=host_id)

    # def post(self):
    #     host_id = self.request.arguments.get('host_id')
    #     self.render("index.html", messages=global_message_buffer[host_id].cache)

class ConfigHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("configs.html",config=global_config)




class ConfigSetHandler(tornado.web.RequestHandler):
    def get(self):
        params = self.request.arguments
        self.render("configs.html",config=global_config)

    def post(self):
        params = self.request.arguments
        size = len(params.get('http.host'))
        configs = []
        for i in range(size):
            config = ESInstallConfig()
            config.yml_config = {}
            configs.append(config)
        for k,v in params.items():
            print(k,v)
            if k in ('_xsrf'):
                continue
            for i in range(size):
                if hasattr(configs[i],k):
                    setattr(configs[i],k,to_text(v[i]))
                else:
                    _s = to_text(v[i])
                    if str(_s).find(',') > 0:
                        _s = _s.split(',')
                    if not none_null_stringNone(_s):
                        configs[i].yml_config[k] = _s
        re_construct_config(configs)
        result = es_install.install_check(configs)
        p_urls = []
        global global_message_buffer
        for config in configs:
            url = {}
            url['address'] = '/getlog?host_id=%s&log_file=%s&ssh_host=%s&ssh_port=%s&ssh_user=%s&ssh_passwd=%s'%(get_yml_value(config.yml_config,*('http','host')) + ':' + get_yml_value(config.yml_config,*('http','port')),\
                                                               path_join(get_yml_value(config.yml_config,*('path','logs')),get_yml_value(config.yml_config,*('cluster','name'))+".log"),\
                                                               config.ssh_host,config.ssh_port,config.ssh_user,config.ssh_passwd)
            url['host'] = get_yml_value(config.yml_config,*('http','host')) + ':' + get_yml_value(config.yml_config,*('http','port'))
            p_urls.append(url)
            host_id = get_yml_value(config.yml_config,*('http','host')) + ':' + get_yml_value(config.yml_config,*('http','port'))
            global_message_buffer[host_id] = MessageBuffer()
            start_es_wrap(global_message_buffer[host_id],config)
        self.render("getlogs.html",urls=p_urls)


class MessageUpdatesHandler(tornado.web.RequestHandler):
    """Long-polling request for new messages.

    Waits until new messages are available before returning anything.
    """
    async def post(self):
        cursor = self.get_argument("cursor", None)
        host_id = self.get_argument("host_id", None)
        messages = global_message_buffer[host_id].get_messages_since(cursor)
        while not messages:
            # Save the Future returned here so we can cancel it in
            # on_connection_close.
            self.wait_future = global_message_buffer[host_id].cond.wait()
            try:
                await self.wait_future
            except asyncio.CancelledError:
                return
            messages = global_message_buffer[host_id].get_messages_since(cursor)
        if self.request.connection.stream.closed():
            return
        for msg in messages:
            if not msg.get('html',None):
                msg["html"] = tornado.escape.to_unicode(self.render_string("message.html", message=msg))
        self.write(dict(messages=messages))

    def on_connection_close(self):
        self.wait_future.cancel()

tornado_start = False
def start(*args,**kwargs):
    global tornado_start
    if not tornado_start:
        # parse_command_line()
        asyncio.set_event_loop(asyncio.new_event_loop())
        app = tornado.web.Application(
            [
                (r"/getlog", LogHandler),
                (r"/a/message/updates", MessageUpdatesHandler),
                (r"/g/config", ConfigHandler),
                (r"/s/config", ConfigSetHandler)
            ],
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
            debug=options.debug,
        )
        app.listen(options.port)
        tornado.ioloop.IOLoop.current().start()


def stop():
    global tornado_start
    tornado_start = False