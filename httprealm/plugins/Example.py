from httprealm import BasePlugin


class Plugin(BasePlugin):
    url = ['*']  # URLs which plugin will listen to (* to listen to all of them)
    name = 'Example'
    version = '1.0'

    def on_load(self, arguments):
        print('Hello from example plugin! You started HTTPRealm with these arguments:', arguments)

    def on_call(self, url, params, response):
        return response  # This response will be returned to client
