# Gherkin feature file style to pytest with Allure parser
Simple parser to convert BDD Gherkin feature style files into the pytest with Allure test style files

## Income Feature file 
```
@slow
Feature: Multiple site support
  Only blog owners can post to a blog, except administrators,
  who can post to all blogs.

  Background:
    Given a global administrator named "Greg"
    And a blog named "Greg's anti-tax rants"
    And a customer named "Dr. Bill"
    And a blog named "Expensive Therapy" owned by "Dr. Bill"

  @test_tag
  Scenario: Dr. Bill posts to his own blog
    Given I am logged in as Dr. Bill
    When I try to post to "Expensive Therapy"
    Then I should see "Your article was published."

  Scenario Outline: eating
  Given there are <start> cucumbers
  When I eat <eat> cucumbers
  Then I should have <left> cucumbers

  Examples:
    | start | eat | left |
    |    12 |   5 |    7 |
    |    20 |   5 |   15 |
```

## Outcome Pytest+Allure file
`test_multiple_site_support.py`
```
import allure
import pytest
from allure_commons._allure import step


@pytest.mark.slow
@allure.feature('Multiple site support')
class TestMultipleSiteSupport:
	"""Only blog owners can post to a blog, except administrators,
who can post to all blogs."""

	@pytest.mark.test_tag
	@allure.title("Dr. Bill posts to his own blog")
	def test_dr_bill_posts_to_his_own_blog(self):
		with step('GIVEN I am logged in as Dr. Bill'):
			pass
		with step('WHEN I try to post to "Expensive Therapy"'):
			pass
		with step('THEN I should see "Your article was published."'):
			pass

	@allure.title("eating")
	@pytest.mark.parametrize("start, eat, left", [['12', '5', '7'], ['20', '5', '15']])
	def test_eating(self, start, eat, left):
		with step('GIVEN there are <start> cucumbers'):
			pass
		with step('WHEN I eat <eat> cucumbers'):
			pass
		with step('THEN I should have <left> cucumbers'):
			pass

	@pytest.fixture(autouse=True)
	def background(self):
		with step('GIVEN a global administrator named "Greg"'):
			pass
		with step('GIVEN a blog named "Greg\'s anti-tax rants"'):
			pass
		with step('GIVEN a customer named "Dr. Bill"'):
			pass
		with step('GIVEN a blog named "Expensive Therapy" owned by "Dr. Bill"'):
			pass

```