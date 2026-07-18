from urllib.parse import urlparse, parse_qs, unquote


def wireguard_link_to_config(link: str) -> str:
    url = urlparse(link)

    private_key = unquote(url.username or "")
    endpoint = f"{url.hostname}:{url.port}"

    params = parse_qs(url.query)

    address = unquote(params["address"][0])
    public_key = unquote(params["publickey"][0])

    dns = params.get("dns", ["1.1.1.1"])
    mtu = params.get("mtu")

    lines = [
        "[Interface]",
        f"PrivateKey = {private_key}",
        f"Address = {address}",
        f"DNS = {', '.join(dns)}",
    ]

    if mtu:
        lines.append(f"MTU = {mtu[0]}")

    lines.extend([
        "",
        "[Peer]",
        f"PublicKey = {public_key}",
        "AllowedIPs = 0.0.0.0/0, ::/0",
        f"Endpoint = {endpoint}",
    ])

    return "\n".join(lines)