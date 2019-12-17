from typing import List, Dict, Callable

class Endpoint:
    def __init__(self, function: callable, path: str, http_method: str):
        self.function = function
        self.path = path
        self.http_method = http_method


class Controller:
    def __init__(self, base_path, endpoints: List[Endpoint]=[]):
        self.base_path = base_path
        self.endpoint_mapping = {
            endpoint.path: endpoint
            for endpoint in endpoints
        }
        

class Dispatcher:
    def __init__(self, controllers=[]):
        self.controller_mapping = {
            controller.base_path: controllers
            for controller in controllers
        }

    def __setitem_(self, base_path: str, controller: Controller):
        if base_path in controller:
            # TODO raise error
            pass
        self.controller_mapping[base_path] = Controller
    
    def __getitem__(self, path: str):
        base_path = next(path.split('/'))
        if base_path not in self.controller_mapping:
            # TODO raise error
            pass
        return self.controller_mapping[base_path]

    def dispatch(self, environ: Dict[str, str]) -> callable:
        path = environ['PATH_INFO']
        pass


class Application:
    def __init__(self, environ, start_response):
        self.environ = environ
        self.start_response = start_response

    def __iter__(self):
        # TODO iterable response will be returned
        status = '200 OK'
        headers = [('Content-Type', 'text/plain')]
        self.start_response(status, headers)
        yield 'Hello World!'
