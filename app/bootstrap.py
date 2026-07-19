import ssl

try:
    import truststore

    truststore.inject_into_ssl()
    print("Windows Trust Store enabled")
except Exception:
    print("Default SSL certificates")