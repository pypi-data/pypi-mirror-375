def test_imports():
    import joepie_tools
    from joepie_tools.hackerprank import fake_hack_screen, fake_matrix, fake_terminal, fake_file_dump, fake_warning_popup
    assert hasattr(joepie_tools, '__version__')
