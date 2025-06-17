import subprocess
import sys
import os
from pathlib import Path


def run_command(command, shell=False, cwd=None):
    """Run a shell command and return the output or None if it fails."""
    try:
        result = subprocess.run(
            command,
            shell=shell,
            capture_output=True,
            text=True,
            check=True,
            cwd=cwd
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e.stderr}")
        return None
    except FileNotFoundError:
        print(f"Command not found: {command}")
        return None


def get_python_versions():
    """Detect installed Python versions."""
    python_executables = ["python", "python3"]
    installed_versions = []
    for exe in python_executables:
        version = run_command([exe, "--version"])
        if version:
            installed_versions.append((exe, version))
    return installed_versions


def find_python_files(root_dir):
    """Find all .py files in the repository, grouped by subfolder."""
    root_path = Path(root_dir)
    folder_scripts = {}
    exclude_dirs = {"venv", ".venv", "env", "myenv", "__pycache__", "site-packages", "Lib", "Scripts"}
    for py_file in root_path.rglob("*.py"):
        if any(part.startswith(".") or part in exclude_dirs for part in py_file.parts):
            continue
        folder = py_file.parent.relative_to(root_path)
        folder_scripts.setdefault(folder, []).append(py_file)
    return folder_scripts


def get_pipreqs_path():
    """Get the path to pipreqs executable."""
    scripts_dir = Path(sys.executable).parent
    if os.name == "nt":
        pipreqs_exe = scripts_dir / "pipreqs.exe"
    else:
        pipreqs_exe = scripts_dir / "pipreqs"
    return str(pipreqs_exe)


def generate_folder_requirements(folder_path, output_file="requirements.txt"):
    try:
        pipreqs_path = get_pipreqs_path()
        folder_path = Path(folder_path).resolve()
        output_file = folder_path / output_file
        if not folder_path.exists():
            print(f"SKIPPED: {folder_path} does not exist.")
            return None
        command = [
            str(pipreqs_path), str(folder_path),
            "--savepath", str(output_file),
            "--force", "--encoding", "utf-8", "--use-local"
        ]
        print(f"Running: {' '.join(command)}")
        result = run_command(command)
        if result is not None:
            print(f"Generated {output_file}")
            return output_file
        else:
            print(f"Failed to generate {output_file}")
            return None
    except Exception as e:
        print(f"Failed to generate requirements for {folder_path}: {e}")
        return None


def consolidate_requirements(folder_scripts, output_file="requirements.txt"):
    """Consolidate requirements.txt files from all folders."""
    consolidated_reqs = []
    temp_files = []

    for folder, scripts in folder_scripts.items():
        if not scripts:
            print(f"Skipping {folder} (no Python files).")
            continue
        folder_path = Path(folder).resolve()
        print(f"Running pipreqs for {folder_path} with scripts: {scripts}")
        req_file = generate_folder_requirements(folder_path)
        if req_file and req_file.exists():
            temp_files.append(req_file)
            with open(req_file, "r", encoding="utf-8") as f:
                reqs = f.read().strip()
                if reqs:
                    consolidated_reqs.append(f"# Dependencies for folder: {folder}")
                    consolidated_reqs.append(reqs)
                    consolidated_reqs.append("")
                else:
                    print(f"Note: No requirements found in {req_file} (no imports detected).")

    if consolidated_reqs:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(consolidated_reqs))
        print(f"Generated consolidated {output_file}")

    for temp_file in temp_files:
        if temp_file.name != output_file:
            temp_file.unlink(missing_ok=True)

    return bool(consolidated_reqs)


def setup_environment(python_exe, requirements_file="requirements.txt"):
    """Install dependencies from requirements.txt."""
    if not Path(requirements_file).exists():
        print(f"Error: {requirements_file} not found.")
        return False
    print(f"Installing dependencies using {python_exe}...")
    pip_install_cmd = [
        python_exe, "-m", "pip", "install", "-r", requirements_file
    ]
    result = run_command(pip_install_cmd)
    if result is not None:
        print("Dependencies installed successfully.")
        return True
    else:
        print(f"Failed to install dependencies. Ensure pip is installed for {python_exe}.")
        return False


def main():
    root_dir = Path.cwd()
    print("Checking installed Python versions...")
    python_versions = get_python_versions()
    if not python_versions:
        print("No Python installations found. Please install Python.")
        sys.exit(1)
    print("Found the following Python versions:")
    for exe, version in python_versions:
        print(f"- {exe}: {version}")
    selected_python = sys.executable
    print(f"Using {selected_python} for environment setup.")
    print("Scanning for Python scripts...")
    folder_scripts = find_python_files(root_dir)
    if not folder_scripts:
        print("No Python scripts found in the repository.")
        sys.exit(1)
    print("Found Python scripts in the following folders:")
    for folder, scripts in folder_scripts.items():
        print(f"- {folder}: {len(scripts)} script(s)")
    requirements_success = consolidate_requirements(folder_scripts)
    if requirements_success:
        if setup_environment(selected_python):
            print("\nSetup complete! To activate your environment:")
            print(f"1. Ensure {selected_python} is used (e.g., `alias python={selected_python}`).")
            print(f"2. Install dependencies: `{selected_python} -m pip install -r requirements.txt`")
            print("3. Run your scripts with the same Python version.")
        else:
            print("Failed to install dependencies. Check pip and requirements.txt.")
    else:
        print("Failed to generate requirements. Ensure pipreqs is installed and scripts have valid imports.")
        sys.exit(1)


if __name__ == "__main__":
    main()
