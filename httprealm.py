from urllib3.exceptions import InsecureRequestWarning
import ctypes
import subprocess
import sys
import os
import logging
from flask import Flask
from flask import request
import requests
import atexit

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.disabled = True  # We don't want Flask logs so disabling them.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)  # Disable warnings about SSL.
  
title = r'''
  _     _   _                        _           
 | |   | | | |                      | |          
 | |__ | |_| |_ _ __  _ __ ___  __ _| |_ __ ___  
 | '_ \| __| __| '_ \| '__/ _ \/ _` | | '_ ` _ \ 
 | | | | |_| |_| |_) | | |  __/ (_| | | | | | | |
 |_| |_|\__|\__| .__/|_|  \___|\__,_|_|_| |_| |_|
               | |                               
               |_|                               
'''
hosts_location = r'C:\Windows\System32\drivers\etc\hosts'
plugins = []
args = []


class BasePlugin:
    def on_load(self, arguments):
        pass

    def on_call(self, url, params, response):
        raise NotImplementedError


@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def proxy(path):
    response = None
    form = request.form.to_dict()
    if request.method == 'POST':
        server_response = requests.post(f'http://realmofthemadgodhrd.appspot.com/{path}', data=form, verify=False).text
    else:  # request.method == 'GET'
        server_response = requests.get(f'http://realmofthemadgodhrd.appspot.com/{path}', data=form, verify=False).text
    if 'confidential' in args:  # Don't give GUID and password to any plugin
        form.pop('guid', None)
        form.pop('password', None)
    for plugin in plugins:
        if path in plugin.Plugin.url or '*' in plugin.Plugin.url:  # or path.split('/')[0] + '/*' in plugin.Plugin.url
            # Give an opportunity for plugin to process request.
            response = plugin.Plugin.on_call(plugin.Plugin, path, form, server_response)
    if response is None:  # No plugin was able to process request.
        return server_response
    return response


@app.after_request
def set_response_headers(response):  # Disable caching
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, public, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


def is_admin():
    # Check if administrator permission is granted to program.
    return bool(ctypes.windll.shell32.IsUserAnAdmin())


def get_resource_path(relative_path):
    # Get absolute path to resource, works for dev and for PyInstaller.
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def update_hosts(host, redirect, stdout, add=True):
    if add:
        with open(hosts_location, 'r+') as file:
            content = file.read()
        if f'{redirect} {host}' not in content:
            content = content + os.linesep + f'{redirect} {host}'
            os.remove(hosts_location)
            with open(hosts_location, 'a+') as f:
                f.write(content)
    else:
        with open(hosts_location, 'r+') as file:
            content = file.read()
        if f'{redirect} {host}' in content:
            content = content.replace(f'{redirect} {host}', '')
            os.remove(hosts_location)
            with open(hosts_location, 'a+') as f:
                f.write(content)

    subprocess.call('ipconfig /flushdns', stdout=stdout)  # Flush DNS records so changes will take effect immediately.
    try:
        subprocess.call('nbtstat -R', stdout=stdout)  # Does not work on Windows 8 and lower i guess.
    except FileNotFoundError:
        pass


def cleanup():  # Do some cleanup before killing process.
    with open(os.devnull, 'w') as trash:  # Send all command logs to dev/null and don't litter console with them.
        update_hosts('www.realmofthemadgod.com', '127.0.0.1', trash, False)


def main():
    print(title)
    atexit.register(cleanup)

    for argument in sys.argv[1:]:
        if argument == '--confidential' or argument == '-c':
            args.append('confidential')

    files = os.listdir('plugins')
    sys.path.insert(0, 'plugins')
    for file in files:
        if file.endswith('.py'):
            imported = __import__(file[:-3])
            print(f'Plugin {imported.Plugin.name} v.{imported.Plugin.version} ({file}) loaded')
            imported.Plugin.on_load(imported.Plugin, args)  # Run on_load plugin function so it will prepare to work.
            plugins.append(imported)

    with open(os.devnull, 'w') as trash:  # Send all command logs to dev/null and don't litter console with them.
        update_hosts('www.realmofthemadgod.com', '127.0.0.1', trash, True)
        # Install realmproxy.crt as trusted certificate so the game will think that it is legit.
        subprocess.call('certutil -addstore -enterprise Root realmofthemadgod.crt', stdout=trash)

    context = (get_resource_path('realmofthemadgod.crt'), get_resource_path('realmofthemadgod.key'))
    app.run(port=443, ssl_context=context, threaded=True)  # Run server with self-signed SSL certificate.


if __name__ == '__main__':
    if not is_admin():
        # We really need admin permission so restart with prompt.
        ctypes.windll.shell32.ShellExecuteW(None, 'runas', sys.executable, __file__, None, 1)
        sys.exit()
    main()
