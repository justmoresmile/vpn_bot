import truststore
import ssl


def init_ssl():
    ctx = truststore.SSLContext(
        ssl.PROTOCOL_TLS_CLIENT
    )

    ssl._create_default_https_context = (
        lambda: ctx
    )