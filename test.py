from file_creator import BddToPytest

conv = BddToPytest('test.feature')
pytest_file = conv.convert_bdd_to_pytest()
b = 1
