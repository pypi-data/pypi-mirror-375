def test_import():
    import os
    import sys

    print("CWD:", os.getcwd())
    print("PATH0:", sys.path[0])

    import arched_emailer

    assert hasattr(arched_emailer, "ArchedEmailer")
