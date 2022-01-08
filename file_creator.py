import re
from typing import TextIO

from gherkin_parser import parse_from_filename


class BddToPytest:
    def __init__(self, feature_file: str):
        self.parsed_file = parse_from_filename(feature_file)
        self.filename = f"test_{self._convert_name_to_snake_case(self.parsed_file['title']['content'])}.py"

    def convert_bdd_to_pytest(self) -> str:
        self.fill_imports()
        self.fill_class_name()
        self.fill_class_description()
        self.fill_tests()
        self.fill_fixtures()
        return self.filename

    def fill_imports(self):
        imports = """import allure
import pytest
from allure_commons._allure import step\n\n
"""
        with open(self.filename, mode='a') as pytest_file:
            pytest_file.write(imports)

    def fill_class_name(self):
        if not self.parsed_file['title']:
            raise ValueError('No features in the file')
        self.fill_class_tags()
        feature_name = self.parsed_file['title']['content']
        class_info = f"""@allure.feature('{feature_name}')
class Test{''.join([word.capitalize() for word in feature_name.split()])}:\n"""
        with open(self.filename, mode='a') as pytest_file:
            pytest_file.write(class_info)

    def fill_class_description(self):
        if self.parsed_file['description']:
            docstring = f'''\t"""{self.parsed_file['description']['content']}"""'''
            with open(self.filename, mode='a') as pytest_file:
                pytest_file.write(docstring)

    def fill_tests(self):
        with open(self.filename, mode='a') as pytest_file:
            pytest_file.write('\n')
            for scenario in self.parsed_file['scenarios']:
                pytest_file.write('\n')
                self.fill_test_tags(scenario, pytest_file)
                pytest_file.write(f'\t@allure.title("{self._replace_single_quote(scenario["title"]["content"])}")\n')
                test_name = f"\tdef test_{self._convert_name_to_snake_case(scenario['title']['content'])}"
                if scenario['examples']:
                    parameters = ', '.join(scenario['examples']['table'][0]['columns'])
                    pytest_file.write(f'\t@pytest.mark.parametrize("{parameters}", '
                                      f'{[par["columns"] for par in scenario["examples"]["table"][1:]]})\n')
                    test_name += f'(self, {parameters}):\n'
                else:
                    test_name += '(self):\n'
                pytest_file.write(test_name)
                if scenario['steps']:
                    for step in scenario['steps']:
                        self.fill_step(step, pytest_file)
                else:
                    pytest_file.write('\tpass')

    def fill_step(self, step: dict, pytest_file: TextIO):
        pytest_file.write(
            f"\t\twith step('{step['title']['clause'].upper()} "
            f"{self._replace_single_quote(step['title']['content'])}'):\n")
        pytest_file.write('\t\t\tpass\n')

    def fill_fixtures(self):
        setup_fixture = self.parsed_file.get('background')
        if setup_fixture:
            with open(self.filename, mode='a') as pytest_file:
                pytest_file.write('\n')
                pytest_file.write('\t@pytest.fixture(autouse=True)\n')
                fixture_name = 'Background' if not setup_fixture['title']['content'] else setup_fixture['title'][
                    'content']
                fixture_name = f"\tdef {self._convert_name_to_snake_case(fixture_name)}(self):\n"
                pytest_file.write(fixture_name)
                if setup_fixture['steps']:
                    for step in setup_fixture['steps']:
                        self.fill_step(step, pytest_file)
                else:
                    pytest_file.write('\tpass')

    def fill_class_tags(self):
        if self.parsed_file['tags']:
            with open(self.filename, mode='a') as pytest_file:
                for tag in self.parsed_file['tags']['content']:
                    pytest_file.write(f'@pytest.mark.{tag}\n')

    @staticmethod
    def fill_test_tags(scenario: dict, pytest_file: TextIO):
        if scenario['tags']:
            for tag in scenario['tags']['content']:
                pytest_file.write(f'\t@pytest.mark.{tag}\n')

    @staticmethod
    def _convert_name_to_snake_case(name: str) -> str:
        name = re.sub(r'[^\w]', ' ', name)
        return "_".join(name.split()).lower()

    @staticmethod
    def _replace_single_quote(text: str) -> str:
        return text.replace(r"'", r"\'")
