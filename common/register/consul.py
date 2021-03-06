import random
import consul
import requests
from common.register.base import Register


class ConsulRegister(Register):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.c = consul.Consul(host=host, port=port)

    # 注册服务
    def register(self, name, service_id, address, port, tags, check):
        if check is None:
            check = {
                "GRPC": f"{address}:{port}",
                "GRPCUseTLS": False,
                "Timeout": "10s",
                "Interval": "5s",
                "DeregisterCriticalServiceAfter": "30s",
            }
        return self.c.agent.service.register(name=name, service_id=service_id, address=address, port=port, tags=tags,
                                             check=check)

    # 注销服务
    def deregister(self, service_id):
        return self.c.agent.service.deregister(service_id=service_id)

    # 获取全部服务
    def get_all_services(self):
        return self.c.agent.services()

    # 获取过滤后的服务
    def filter_services(self, name):
        url = f"http://{self.host}:{self.port}/v1/agent/services"
        params = {
            "filter": f'Service == "{name}"'
        }
        return requests.get(url, params=params).json()

    # 获取服务端口和域名
    def get_host_port(self, name):
        data = self.filter_services(name)
        if data:
            service = random.choice(list(data.values()))
            return service["Address"], service["Port"]
        return None, None

