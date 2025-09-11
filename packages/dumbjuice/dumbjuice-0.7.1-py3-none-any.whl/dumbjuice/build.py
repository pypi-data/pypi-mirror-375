import os
import shutil
import requests
import importlib
import json
import sys
import subprocess
import stat
import zipfile
#import dumbjuice.addins as addins

ICON_NAME = "djicon.ico"
HARDCODED_IGNORES = {"dumbjuice_build","dumbjuice_dist",".gitignore",".git",".git/","*.git"}
default_config = {"gui":False,"ignore":None,"use_gitignore":False,"include":None,"addins":None,"mainfile":"main.py"}
ADDINS_LIBRARY = {"ffmpeg":{"relpath":"addins/ffmpeg/bin","installer_source":"https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"}}

def create_dist_zip(build_folder, dist_folder, zip_filename):
    os.makedirs(dist_folder, exist_ok=True)
    zip_path = os.path.join(dist_folder, zip_filename + ".zip")

    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(build_folder):
            for file in files:
                if file == "install.nsi":
                    continue  # optionally skip the nsis script
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, build_folder)
                zipf.write(abs_path, rel_path)

    print(f"Created zip archive at: {zip_path}")

def handle_remove_readonly(func, path, exc_info):
    # Clear the read-only flag and try again
    os.chmod(path, stat.S_IWRITE)
    func(path)

def find_makensis():
    local_path = os.path.join(os.path.dirname(__file__), "bin", "nsis", "makensis.exe") 
    if os.path.isfile(local_path):
        return local_path
    raise RuntimeError("NSIS not found")

def generate_nsis_script(conf, active_addins=None,python_exe="python.exe"):
    python_version = conf['python_version']
    app_name = conf['program_name']
    binpath = str(importlib.resources.files('dumbjuice.bin').joinpath('').resolve())
    mainfile = conf['mainfile']
    addin_blocks = []
    for addin_name in active_addins:
        meta = ADDINS_LIBRARY[addin_name]
        zip_name = addin_name + ".zip"
        install_path = os.path.join("$INSTDIR", meta["relpath"].replace("/", "\\"))
        install_check_path = os.path.join(install_path, "*.*")

        skip_label = f"skip_addin_{addin_name}"
        
        block = f"""
        ; --- {addin_name} add-in installation ---
        IfFileExists "{install_check_path}" {skip_label}
        
        DetailPrint "Installing add-in: {addin_name}"
        inetc::get "{meta['installer_source']}" "$TEMP\\{zip_name}" /END
        Pop $0
        StrCmp $0 "OK" 0 +3
            DetailPrint "Extracting {addin_name}..."
            nsisunz::Unzip "$TEMP\\{zip_name}" "{install_path}"
            Delete "$TEMP\\{zip_name}"
        
        {skip_label}:
        """
        addin_blocks.append(block)
    addins_scripts = "\n".join(addin_blocks)

    script = f"""
!addplugindir "{binpath}"
!include "FileFunc.nsh"
!include "LogicLib.nsh"
!define APP_NAME "{app_name}"
!define PYTHON_VERSION "{python_version}"
!define PYTHON_INSTALLER "python-{python_version}-amd64.exe"
!define PYTHON_URL "https://www.python.org/ftp/python/{python_version}/python-{python_version}-amd64.exe"

Var PYTHON_DL_RESULT
var PYTHON_DIR
var APP_DIR

OutFile "install.exe"
InstallDir "$PROGRAMFILES\\Dumbjuice"
RequestExecutionLevel admin

Page directory
Page instfiles

Section "Install ${{APP_NAME}}"

  ; Define paths
  StrCpy $PYTHON_DIR "$INSTDIR\\python\\{python_version}"
  StrCpy $APP_DIR "$INSTDIR\\programs\\{app_name}"

  ; Create folders
  CreateDirectory $PYTHON_DIR
  CreateDirectory $APP_DIR

  ; Set output to app folder
  SetOutPath $APP_DIR

  ; Copy all app files
  File /r "appfolder\\*.*"

  ; Check if Python version already exists
  IfFileExists "$PYTHON_DIR\\python.exe" skip_python_install

  ; Download Python installer
  DetailPrint "Downloading Python from: ${{PYTHON_URL}}"
  inetc::get /CAPTION "Downloading Python..." /RESUME "" "${{PYTHON_URL}}" "$TEMP\${{PYTHON_INSTALLER}}" /END
  Pop $PYTHON_DL_RESULT
  DetailPrint "Download result: $PYTHON_DL_RESULT"
  StrCmp $PYTHON_DL_RESULT "OK" download_ok cancel_download
  MessageBox MB_OK "Download failed: $PYTHON_DL_RESULT"
  Abort

  download_ok:
  DetailPrint "Download succeeded."

  ; Install Python
  DetailPrint "Installing Python ${{PYTHON_VERSION}}..."
  DetailPrint "$PROGRAMFILES\\Dumbjuice\\python\\{python_version}"
  ExecWait '"$TEMP\\${{PYTHON_INSTALLER}}" /quiet InstallAllUsers=0 PrependPath=0 Include_test=0 TargetDir="$PROGRAMFILES\\Dumbjuice\\python\\{python_version}"'

skip_python_install:

  ; Create virtual environment in app folder
  DetailPrint "Creating virtual environment..."
  ExecWait '"$PYTHON_DIR\\python.exe" -m venv "$APP_DIR\\venv"'

  ; Install requirements into venv
  DetailPrint "Installing dependencies..."
  ExecWait '"$APP_DIR\\venv\\Scripts\\pip.exe" install -r "$APP_DIR\\requirements.txt"'

  ; Install addins
  {addins_scripts}

  ; Create shortcut on desktop
  DetailPrint "Creating desktop shortcut..."
  CreateShortCut "$DESKTOP\\${{APP_NAME}}.lnk" "$APP_DIR\\venv\\Scripts\\{python_exe}" '"$APP_DIR\\{mainfile}"' "$INSTDIR\\programs\\{app_name}\\djicon.ico"
  CreateShortCut "$APP_DIR\\${{APP_NAME}}_debug.lnk" "$APP_DIR\\venv\\Scripts\\python.exe" '"$APP_DIR\\{mainfile}"' "$APP_DIR\\djicon.ico"
  Goto done

cancel_download:
  MessageBox MB_OK "Python download failed or cancelled."

done:

SectionEnd
"""
    return script

def load_gitignore(source_folder):
    """Load ignore patterns from .gitignore if it exists."""
    gitignore_path = os.path.join(source_folder, ".gitignore")
    ignore_patterns = set()

    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):  # Ignore empty lines and comments
                    ignore_patterns.add(line)

    return ignore_patterns

def inject_addins_to_main(main_py_path, addin_relpaths):
    """
    Injects add-in PATH patching code into the top of the main.py file.
    Uses namespaced variables to prevent naming conflicts.
    
    Args:
        main_py_path (str): Full path to main.py (or other entrypoint).
        addin_relpaths (List[str]): List of relative paths to prepend to PATH.
    """
    start_marker = "# >>> dumbjuice addins injection >>>"
    end_marker = "# <<< dumbjuice addins injection <<<"

    # Generate the code block with namespaced variables (Clumsy attempt at such)
    lines = [start_marker]
    lines.append("import os")
    lines.append("import sys")
    lines.append("")
    lines.append(f"_dj_addin_relpaths = {repr(addin_relpaths)}")
    lines.append("_dj_base_path = os.path.dirname(sys.argv[0])")
    lines.append("for _dj_rel in _dj_addin_relpaths:")
    lines.append("    _dj_abs_path = os.path.abspath(os.path.join(_dj_base_path, _dj_rel))")
    lines.append("    if _dj_abs_path not in os.environ['PATH']:")
    lines.append("        os.environ['PATH'] = _dj_abs_path + os.pathsep + os.environ['PATH']")
    lines.append(end_marker)
    injected_block = "\n".join(lines) + "\n\n"

    # Read the original content
    with open(main_py_path, "r", encoding="utf-8") as f:
        original = f.read()

    # Remove any previous injected block
    if start_marker in original and end_marker in original:
        pre = original.split(start_marker)[0]
        post = original.split(end_marker)[-1]
        cleaned = pre.strip() + "\n\n" + post.lstrip()
    else:
        cleaned = original

    # Write the new file with injection at the top
    with open(main_py_path, "w", encoding="utf-8") as f:
        f.write(injected_block + cleaned)

    print(f"[dumbjuice] Injected addin paths into {main_py_path}")

def get_default_icon():
    f"""Returns the path to the default {ICON_NAME} file."""
    return str(importlib.resources.files('dumbjuice.assets') / ICON_NAME) # / joins the paths

def is_python_version_available(python_version):
    url = f"https://www.python.org/ftp/python/{python_version}/"
    response = requests.get(url)
    # If the version page exists, the status code will be 200
    if response.status_code == 200:
        return True
    else:
        return False

def build(target_folder=None):
    if target_folder is None:
        target_folder = os.getcwd()

    config_path = os.path.join(target_folder,"dumbjuice.conf")

    print("DumbJuice in:",target_folder)
    try:
        with open(config_path, "r") as f:
            loaded_config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print("Error: Invalid or missing dumbjuice.conf file.")
        sys.exit(1)
    required_keys = ["program_name", "python_version"]
    missing_keys = [key for key in required_keys if key not in loaded_config or not loaded_config[key]]
    if missing_keys:
        print(f"Error: Missing or empty required config values: {', '.join(missing_keys)}")
        sys.exit(1)  # Exit the script if critical settings are missing

    config = default_config.copy()
    config.update(loaded_config)
    python_version = config["python_version"]
    print("Using combined config with defaults:")
    print(config)
    if "gui" in config:
        gui = config["gui"]
    else:
        gui = False

    if gui:
        python_executable = "pythonw.exe"
    else:
        python_executable = "python.exe"

    # Check if the specified Python version is available
    if not is_python_version_available(python_version):
        print(f"Error: Python version {python_version} is not available for download.")
        return  # Exit the function to stop further processing
    
    build_folder = os.path.join(os.getcwd(), "dumbjuice_build")
    dist_folder = os.path.join(os.getcwd(), "dumbjuice_dist")
    zip_filename = config["program_name"]
    source_folder = target_folder
    # Ensure build folder exists

    if os.path.exists(build_folder):
        try:
            shutil.rmtree(build_folder, onerror=handle_remove_readonly)
        except Exception as e:
            print(f"Could not delete existing build folder: {e}")
            print("Make sure the files (especially install.exe) are not open or locked.")
            sys.exit(1)

    os.makedirs(build_folder)

    # Copy appfolder contents to the build folder
    appfolder = os.path.join(build_folder, 'appfolder')
    #print(appfolder)
    if not os.path.exists(appfolder):
        os.makedirs(appfolder)

    # Copy contents of the user's appfolder into the new appfolder
    excluded_files = set()
    if config["use_gitignore"]:
        excluded_files = excluded_files | load_gitignore(target_folder)
    # add custom files to ignore set
    if config["ignore"] is not None:
        excluded_files = excluded_files | set(config["ignore"])

    excluded_files = excluded_files | HARDCODED_IGNORES # some hardcoded ones to ensure the build folders aren't added recursively 
    if config["include"] is not None:
        excluded_files.difference_update(set(config["include"]))
    excluded_files = {item.rstrip('/') for item in excluded_files} # not sure why, but the .gitignore items with a trailing / is not identified by ignore_patterns, maybe not, dunno, but this way works so meh
    shutil.copytree(source_folder, appfolder, dirs_exist_ok=True, ignore=shutil.ignore_patterns(*excluded_files))

    # get the defult icon if there isn't one available
    if not os.path.isfile(os.path.join(appfolder,ICON_NAME)):
        shutil.copyfile(get_default_icon(),os.path.join(appfolder,ICON_NAME))

    active_addins = {}
    if "addins" in config:
        active_addin_relpaths = []
        for addin_name in config["addins"]:
            if addin_name in ADDINS_LIBRARY:
                active_addins[addin_name] = ADDINS_LIBRARY[addin_name]["relpath"]
                active_addin_relpaths.append(ADDINS_LIBRARY[addin_name]["relpath"])
            else:
                print(f"addin '{addin_name}' is not supported. Available are {list(ADDINS_LIBRARY.keys())}")

    if len(active_addin_relpaths) > 0:
        inject_addins_to_main(os.path.join(appfolder,config["mainfile"]), active_addin_relpaths)
    else:
        active_addin_relpaths = None

    script = generate_nsis_script(config, active_addins,python_executable)     
    nsis_file = os.path.join(build_folder,"installer.nsi")
    makensis_path = importlib.resources.files('dumbjuice.bin') / 'nsis' / 'makensis.exe'
    with open(nsis_file ,"w") as outfile:
        outfile.write(script)

    try:
        result = subprocess.run(
            [makensis_path, nsis_file],
            check=True,
            capture_output=True,
            text=True
        )
        print("NSIS build output:\n", result.stdout)
    except subprocess.CalledProcessError as e:
        print("NSIS build failed:\n", e.stderr)

    
    create_dist_zip(build_folder, dist_folder, zip_filename)

    

    