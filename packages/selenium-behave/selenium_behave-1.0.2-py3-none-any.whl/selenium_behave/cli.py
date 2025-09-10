# src/selenium_behave/cli.py
import os

def create_project():
    """
    Create a default Selenium + Behave project structure.
    """
    base_dirs = [
        "features",
        "features/steps",
        "reports",
        "config"
    ]

    for d in base_dirs:
        os.makedirs(d, exist_ok=True)

    # Default feature file
    feature_file = os.path.join("features", "example.feature")
    if not os.path.exists(feature_file):
        with open(feature_file, "w") as f:
            f.write(
                "Feature: Example test\n\n"
                "  Scenario: Open Google\n"
                "    Given I navigate to \"https://www.google.com\"\n"
            )

    # Default step file
    step_file = os.path.join("features", "steps", "example_steps.py")
    if not os.path.exists(step_file):
        with open(step_file, "w") as f:
            f.write(
                "from behave import given\n"
                "from selenium import webdriver\n\n"
                "@given('I navigate to \"{url}\"')\n"
                "def step_impl(context, url):\n"
                "    context.driver = webdriver.Chrome()\n"
                "    context.driver.get(url)\n"
            )

    print("✅ Project structure created successfully!")
    print("👉 Now run: behave")
