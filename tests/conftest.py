
def pytest_addoption(parser):
    parser.addoption("--external", action="store_true",
                     help="Run external tests")
