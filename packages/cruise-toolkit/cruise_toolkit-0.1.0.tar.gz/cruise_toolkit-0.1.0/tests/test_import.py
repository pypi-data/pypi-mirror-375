
def test_import():
    import cruise_toolkit
    assert hasattr(cruise_toolkit, "__all__")
