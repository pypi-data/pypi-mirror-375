import os
import shutil

def create_project():
    """
    This function will create a new project structure where the user will run the command
    """
    base_dir = os.getcwd()

    folders = [
        "features",
        "features/steps",
        "reports"
    ]

    for folder in folders:
        path = os.path.join(base_dir, folder)
        os.makedirs(path, exist_ok=True)

    # sample feature file
    with open(os.path.join(base_dir, "features", "example.feature"), "w") as f:
        f.write("""Feature: Custom steps of Old framework
  To verify selenium cucumber steps via Behave BDD in browser

  Background:
    Given I navigate to "https://www.google.com"

  Scenario: Navigate and refresh the page
    Given I navigate to "https://www.google.com/search?q=python"
    When I navigate back
    Then I navigate forward
    And I refresh page

  Scenario: Check Google homepage title
    Given I should see page title as "Google"

  Scenario: Assert search button presence
    Given element having name "btnK" should be present

  Scenario: Perform Google search
    Given I navigate to "https://www.google.com"
    When element having name "q" should be present
    Then element having name "btnK" should be enabled

  Scenario: Zoom in and out on Google homepage
    Given I zoom in page
    When I zoom out page
    Then I reset page view

  Scenario: Scroll Google search results
    Given I navigate to "https://www.google.com/search?q=python"
    When I scroll to end of page

  Scenario: Close browser
    Given I close browser

# Run: behave features/example.feature -f behave_html_formatter:HTMLFormatter -o reports/test.html
""")

    # sample environment.py
    with open(os.path.join(base_dir, "features", "environment.py"), "w") as f:
        f.write("""from selenium import webdriver

def before_all(context):
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    context.driver = webdriver.Chrome(options=options)

def after_all(context):
    context.driver.quit()
""")

        # sample environment.py
        with open(os.path.join(base_dir, "features", "steps", "steps.py"), "w") as f:
            f.write("""from selenium_behave.steps.common_steps import *
from selenium_behave.steps.agentic_steps import *
from selenium_behave.steps.chatbot_steps import *
from selenium_behave.steps.voicebot_steps import *
from selenium_behave.steps.faq_eval_steps import *
from selenium_behave.steps.Web_And_App_Error import *
    """)

    print("✅ Project created successfully at:", base_dir)
