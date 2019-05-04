# Plugin documentation
This guide expects you to know Python well.

## Getting started
First of all you need to create any file that ends with **.py** in plugins/ directory. It should not be called httprealm.py, because this will lead to name conflicts.

Every single plugin starts with the following import:
```python
from httprealm import BasePlugin
```
You must also provide a class name `Plugin` in your code. It must not be nested and must be inherited from `BasePlugin`.
```python
class Plugin(BasePlugin):
    url = ['char/list']
    name = 'Example'
    version = '1.0'
```
As you can see, there are some parameters i did not said about. These are `name` `name`, and `version`.

|Parameter|Type|Description|
|-|-|-|
|url|List|URLs which plugin will listen to or `*` for all. You can find them [here](https://github.com/Zeroeh/RotMG-Appspot)|
|name|String|Plugin name used for logging|
|version|String|Plugin version used for logging|

There are some predefined functions in `BasePlugin` class. You must redefine them all except _italicized_:

### _on\_load_
Called when plugin is loaded.

```python
def on_load(self, arguments):
        print('Hello from example plugin! You started HTTPRealm with these arguments:', arguments)
```
|Parameter|Type|Description|
|-|-|-|
|arguments|List|Arguments that were passed to HTTPRealm|
#
### on_call
Called when plugin is loaded.

```python
def on_call(self, url, params, response):
        response = response.replace('<Servers>', '<Servers><Server><Name>Proxy</Name><DNS>127.0.0.1</DNS><Lat>0.00</Lat><Long>0.00</Long><Usage>0.00</Usage></Server>')
        return response  # This will be returned to client
```
|Parameter|Type|Description|
|-|-|-|
|url|String|URL that has been called from client|
|params|Dict|Request parameters|
|response|String|RotMG server response on request|

## Full example plugin
```python
from httprealm import BasePlugin


class Plugin(BasePlugin):
    url = ['char/list']
    name = 'Example'
    version = '1.0'

    def on_load(self, arguments):
        print('Hello from example plugin! You started HTTPRealm with these arguments:', arguments)

    def on_call(self, url, params, response):
        response = response.replace('<Servers>', '<Servers><Server><Name>Proxy</Name><DNS>127.0.0.1</DNS><Lat>0.00</Lat><Long>0.00</Long><Usage>0.00</Usage></Server>')
        return response
```

Happy coding!
