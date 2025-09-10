import json
from urllib.parse import parse_qs

class Request:
    def __init__(self, scope, receive):
        self.scope = scope
        self._query_params = None
        self.receive = receive
        self._headers = None

    async def json(self):
        body = b''
        more_body = True
        while more_body:
            message = await self.receive()
            body += message.get('body', b'')
            more_body = message.get('more_body', False)

        if not body:
            return None
        return json.loads(body)

    @property
    def path(self):
        return self.scope['path']


    @property
    def method(self):
        return self.scope['method']


    @property
    def headers(self):
        if self._headers is None:
            self._headers = {
                key.decode('utf-8'): value.decode('utf-8')
                for key, value in self.scope['headers']
            }
        return self._headers


    @property
    def query(self):
        if self._query_params is None:
            query_string = self.scope['query_string'].decode("utf-8")
            self._query_params = QueryParams(query_string)
        return self._query_params



class QueryParams:
    def __init__(self, query_string):
        self._params = parse_qs(query_string)

    def get(self, key, default=None):
        values = self._params.get(key, [])
        return values[0] if values else default

    def getall(self, key, default=None):
        return self._params.get(key, default or [])



class Response:
    def __init__(self, content, status_code=200):
        self.content = content
        self.status_code = status_code
        self.headers = {}

    async def send_to_asgi(self, send):
        body = json.dumps(self.content).encode("utf-8")
        
        headers_list = [[b"content-type", b"application/json"]]
        for key, value in self.headers.items():
            headers_list.append([key.encode("utf-8"), value.encode("utf-8")])

        await send({
            "type": "http.response.start",
            "status": self.status_code,
            "headers": headers_list,
        })
        await send({"type": "http.response.body", "body": body})



class Router:
    def __init__(self):
        self.routes = {}

    def route(self, path, methods=None):
        if methods is None: methods = ["GET"]
        def wrapper(handler):
            for method in methods:
                self.routes[(method.upper(), path)] = handler
            return handler
        return wrapper



class MiddlewareWrapper:
    def __init__(self, app, middleware_func):
        self.app = app
        self.middleware_func = middleware_func

    async def __call__(self, scope, receive):
        async def call_next(request):
            response = await self.app(scope, receive)
            return response

        request = Request(scope, receive)
        response = await self.middleware_func(request, call_next)
        return response



class SerPy:
    def __init__(self):
        self.routes = {}
        self.app = self._dispatch_request

    def add_middleware(self, middleware_func):
        self.app = MiddlewareWrapper(self.app, middleware_func)

    def include_router(self, router: Router, prefix=""):
        for (method, path), handler in router.routes.items():
            self.routes[(method, prefix + path)] = handler

    def route(self, path, methods=None, middleware=None):
        if methods is None: methods = ["GET"]
        if middleware is None: middleware = []
        
        def wrapper(handler):
            for method in methods:
                self.routes[(method.upper(), path)] = (handler, middleware)
            return handler
        return wrapper

    def find_route(self, method, path):
        for (route_method, route_path), (handler, middleware) in self.routes.items():

            if route_method != method: continue
            
            route_parts = route_path.split("/")
            path_parts = path.split("/")
            
            if len(route_parts) != len(path_parts): continue
            
            params = {}
            match = True
            
            for route_part, path_part in zip(route_parts, path_parts):
                if route_part.startswith('{') and route_part.endswith('}'):
                    param_name = route_part[1:-1]
                    params[param_name] = path_part
                elif route_part != path_part:
                    match = False
                    break
            if match:
                return handler, params, middleware
        return None, None, []

    async def _dispatch_request(self, scope, receive):
        
        request = Request(scope, receive)
        handler, params, route_middleware = self.find_route(request.method, request.path)

        if not handler:
            return Response(content={"error": "Route Not Found"}, status_code=404)

        async def handler_call(req):
            return await handler(req, **params)

        chain = handler_call
        for mw in reversed(route_middleware):
            chain = self._wrap_middleware_for_dispatch(mw, chain)

        response = await chain(request)
        return response
    
    def _wrap_middleware_for_dispatch(self, middleware_func, next_in_chain):
        async def new_chain_link(request):
            return await middleware_func(request, next_in_chain)
        return new_chain_link
    
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http": return
        response = await self.app(scope, receive)
        await response.send_to_asgi(send)