import os
import shutil
import subprocess

# --- Configuration ---
THEMES_DIR = "themes"
THEME_NAME = "ananke"
THEME_URL = "https://github.com/theNewDynamic/gohugo-theme-ananke.git"
THEME_PATH = os.path.join(THEMES_DIR, THEME_NAME)

# --- Functions ---

def run_command(command):
    """Runs a command and prints its output."""
    try:
        print(f"Running command: {' '.join(command)}")
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {' '.join(command)}")
        print(e.stderr)
        exit(1)

def clean_theme():
    """Removes the theme directory if it exists."""
    if os.path.exists(THEME_PATH):
        print(f"Removing existing theme directory: {THEME_PATH}")
        shutil.rmtree(THEME_PATH)
        print("Theme directory removed.")

def reinstall_theme():
    """Clones the theme from its Git repository."""
    if not os.path.exists(THEMES_DIR):
        os.makedirs(THEMES_DIR)
    print(f"Cloning theme from {THEME_URL} into {THEMES_DIR}")
    run_command(["git", "clone", THEME_URL, THEME_PATH])
    print("Theme reinstalled successfully.")

def update_git_repository():
    """Adds, commits, and pushes changes to the remote repository."""
    print("Updating Git repository...")
    run_command(["git", "add", "."])
    run_command(["git", "commit", "-m", "Reinstalled ananke theme and updated project structure"])
    run_command(["git", "push"])
    print("Git repository updated.")

# --- Main Execution ---

if __name__ == "__main__":
    clean_theme()
    reinstall_theme()
    update_git_repository()
    print("\nAll tasks completed successfully!")