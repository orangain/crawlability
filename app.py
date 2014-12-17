import os
import sys
import asyncio

from aiohttp import web
from jinja2 import Environment, FileSystemLoader

from check import check


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
env = Environment(loader=FileSystemLoader(os.path.join(BASE_DIR, 'templates')))


@asyncio.coroutine
def handle_index(request):
    template = env.get_template('index.html')
    return web.Response(body=template.render().encode('utf-8'))


@asyncio.coroutine
def handle_result(request):
    url = request.GET.get('url')
    c = yield from check(url)

    template = env.get_template('result.html')
    return web.Response(body=template.render(c=c).encode('utf-8'))

    text = 'Status: {0}'.format(c.page.status)
    return web.Response(body=text.encode('utf-8'))


@asyncio.coroutine
def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', '/result', handle_result)
    app.router.add_route('GET', '/', handle_index)

    host = '0.0.0.0'
    port = os.environ.get('PORT', 8000)
    srv = yield from loop.create_server(app.make_handler(), host, port)
    print("Server started at http://{0}:{1}".format(host, port))
    return srv

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
try:
    loop.run_forever()
except KeyboardInterrupt:
    print('Interrupted', file=sys.stderr)
