def test_import():
    import subpackage
    assert subpackage.__version__ == "0.1.0"
