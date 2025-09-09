import os, sys, shutil, platform
from pathlib import Path
import importlib.resources as res

APP_NAME = "Gel Annotate"

def _icon_file(ext: str) -> str:
    name = f"icon.{ext}"
    with res.as_file(res.files("annotation.assets") / name) as p:
        return str(p)

def _is_windows() -> bool: return platform.system().lower().startswith("win")
def _is_macos() -> bool:   return platform.system().lower().startswith("darwin")
def _is_linux() -> bool:   return platform.system().lower().startswith("linux")

def create_windows_shortcuts():
    try:
        import win32com.client  # from pywin32
    except Exception as e:
        print("pywin32 is required on Windows: pip install aer-gel-annotate[windows]")
        raise

    shell = win32com.client.Dispatch("WScript.Shell")

    # Where to place shortcuts
    desktop = Path(os.path.join(os.path.expanduser("~"), "Desktop"))
    start_menu = Path(os.path.join(os.environ.get("APPDATA", ""), "Microsoft", "Windows", "Start Menu", "Programs"))

    target = sys.executable
    args = "-m annotation.gui.gel_gui_wrapper"   # use module execution so venv is respected
    icon = _icon_file("ico")
    workdir = str(Path.home())

    for dest_dir in [desktop, start_menu]:
        dest_dir.mkdir(parents=True, exist_ok=True)
        lnk = str(dest_dir / f"{APP_NAME}.lnk")
        sc = shell.CreateShortCut(lnk)
        sc.Targetpath = target
        sc.Arguments = args
        sc.IconLocation = icon
        sc.WorkingDirectory = workdir
        sc.Description = APP_NAME
        sc.save()
        print(f"Created: {lnk}")

def create_linux_shortcut():
    applications_dir = Path("~/.local/share/applications").expanduser()
    desktop_dir = Path("~/Desktop").expanduser()
    applications_dir.mkdir(parents=True, exist_ok=True)

    icon_src = _icon_file("png")
    # Copy icon into a stable place in ~/.local/share/icons
    icon_target_dir = Path("~/.local/share/icons").expanduser()
    icon_target_dir.mkdir(parents=True, exist_ok=True)
    icon_target = icon_target_dir / "aer-gel-annotate.png"
    shutil.copyfile(icon_src, icon_target)

    desktop_entry = f"""[Desktop Entry]
Type=Application
Name={APP_NAME}
Comment=Gel well detection and annotation
Exec=gel-annotate
Icon={icon_target}
Terminal=false
Categories=Education;Science;
"""
    appfile = applications_dir / "aer-gel-annotate.desktop"
    appfile.write_text(desktop_entry)
    print(f"Created: {appfile}")

    # Also drop a desktop shortcut if Desktop exists
    if desktop_dir.exists():
        desktop_file = desktop_dir / f"{APP_NAME}.desktop"
        desktop_file.write_text(desktop_entry)
        desktop_file.chmod(0o755)
        print(f"Created: {desktop_file}")

def create_macos_shortcut():
    # Simple .command launcher on Desktop (double-clickable)
    desktop = Path("~/Desktop").expanduser()
    desktop.mkdir(parents=True, exist_ok=True)
    cmd = desktop / f"{APP_NAME}.command"
    cmd.write_text("#!/bin/bash\nexec gel-annotate\n")
    cmd.chmod(0o755)
    print(f"Created: {cmd}")
    print("Tip: drag the shortcut into the Dock if you want quick access.")
    # (Attaching a custom icon to a .command file is manual via Finder → Get Info.)

def main():
    if _is_windows():
        create_windows_shortcuts()
    elif _is_linux():
        create_linux_shortcut()
    elif _is_macos():
        create_macos_shortcut()
    else:
        print("Unsupported OS?")
        sys.exit(1)

if __name__ == "__main__":
    main()
