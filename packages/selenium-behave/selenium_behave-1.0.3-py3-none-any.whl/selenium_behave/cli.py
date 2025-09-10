import os
import shutil

def create_project():
    """
    Ye function ek naya project structure bana dega
    jaha user command run karega
    """
    base_dir = os.getcwd()

    folders = [
        "features",
        "features/steps",
        "features/environment",
        "reports"
    ]

    for folder in folders:
        path = os.path.join(base_dir, folder)
        os.makedirs(path, exist_ok=True)

    # sample feature file
    with open(os.path.join(base_dir, "features", "example.feature"), "w") as f:
        f.write("""Feature: Example Feature
  Scenario: Open Google
    Given I navigate to "https://www.google.com"
""")

    print("✅ Project created successfully at:", base_dir)
