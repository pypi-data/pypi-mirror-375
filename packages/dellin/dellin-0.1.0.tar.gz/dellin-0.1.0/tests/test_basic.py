def test_import_and_version():
    import dellin

    assert hasattr(dellin, "__version__")
    assert isinstance(dellin.__version__, str)


def test_client_class_available():
    from dellin.api import DellinOrdersClient

    # Класс доступен и можно создать экземпляр с тестовым ключом
    assert callable(DellinOrdersClient)
    c = DellinOrdersClient(appkey="test-key")
    assert c.base_url.startswith("http")
