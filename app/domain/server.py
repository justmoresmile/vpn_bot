from dataclasses import dataclass



@dataclass
class Server:

    id: int

    name: str

    country: str

    host: str

    api_url: str

    api_token: str

    wireguard_inbound_id: int

    enabled: bool

    priority: int