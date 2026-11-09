#!/usr/bin/env python3

# ==========================================
#          MNEMOSYNE v0.1.0 Alpha
#          - Persistence Engine -
#                 E-0.1.0-1
# ==========================================

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


# ==========================================
# VERSION INFORMATION
# ==========================================

PROJECT_NAME = "MNEMOSYNE"
PROJECT_VERSION = "0.1.0"
PROJECT_STAGE = "Alpha"

ENGINE_VERSION = "0.1.0"
MANIFEST_VERSION = 1

VERSION_STRING = (
    f"{PROJECT_NAME} v{PROJECT_VERSION} {PROJECT_STAGE} "
    f"E-{ENGINE_VERSION}-{MANIFEST_VERSION}"
)

ENGINE_DIR = Path(__file__).resolve().parent
MANIFEST = ENGINE_DIR / "manifest.json"
KDE_CONFIG = Path.home() / ".config"

# MNEMOSYNE unterstützt grundsätzlich jede KDE-KConfig-Datei
# innerhalb von ~/.config. Der Pfad wird in resolve_config_file()
# sicher auf dieses Verzeichnis begrenzt.

ALLOWED_TYPES = {
    "string",
    "int",
    "double",
    "bool"
}


def load_manifest():
    if not MANIFEST.is_file():
        raise FileNotFoundError(f"Manifest nicht gefunden: {MANIFEST}")

    with MANIFEST.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if data.get("version") != 1:
        raise ValueError("Unbekannte Manifest-Version.")

    if not isinstance(data.get("settings"), list):
        raise ValueError("'settings' muss eine Liste sein.")

    return data


def resolve_config_file(filename, require_exists=False):
    """
    Löst einen relativen KDE-Konfigurationspfad sicher innerhalb
    von ~/.config auf. Absolute Pfade, Pfad-Ausbrüche und Symlinks,
    die aus ~/.config herausführen, werden abgewiesen.
    """

    if not isinstance(filename, str) or not filename.strip():
        raise ValueError("Ungültiger oder fehlender Dateiname.")

    relative_path = Path(filename)

    if relative_path.is_absolute():
        raise ValueError("Absolute Pfade sind nicht erlaubt.")

    if ".." in relative_path.parts or "\\" in filename or "\0" in filename:
        raise ValueError("Unsicherer Konfigurationspfad.")

    config_root = KDE_CONFIG.resolve()
    config_path = (config_root / relative_path).resolve()

    try:
        config_path.relative_to(config_root)
    except ValueError:
        raise ValueError(
            f"Konfigurationsdatei liegt außerhalb von {config_root}: {filename}"
        )

    if require_exists and not config_path.is_file():
        raise FileNotFoundError(
            f"Konfigurationsdatei nicht gefunden: {config_path}"
        )

    return config_path


def validate_setting(setting):
    if not isinstance(setting, dict):
        raise ValueError("Ungültiger Manifest-Eintrag.")

    filename = setting.get("file")

    for field in ("group", "key", "type"):
        if not isinstance(setting.get(field), str) or not setting[field]:
            raise ValueError(f"Ungültiges oder fehlendes Feld: {field}")

    if setting["type"] not in ALLOWED_TYPES:
        raise ValueError(f"Nicht unterstützter Typ: {setting['type']}")

    return resolve_config_file(filename)


def read_current_value(path, group, key):
    result = subprocess.run(
        [
            "kreadconfig6",
            "--file", str(path),
            "--group", group,
            "--key", key
        ],
        capture_output=True,
        text=True,
        check=True
    )

    return result.stdout.rstrip("\n")


def save_manifest(data):
    """Schreibt das Manifest atomar."""

    fd, temporary_path = tempfile.mkstemp(
        prefix="manifest-",
        suffix=".tmp",
        dir=MANIFEST.parent
    )

    try:
        with os.fdopen(fd, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
            file.write("\n")
            file.flush()
            os.fsync(file.fileno())

        os.replace(temporary_path, MANIFEST)

    except Exception:
        if os.path.exists(temporary_path):
            os.unlink(temporary_path)
        raise


def capture_setting(filename, group, key, value_type):
    """Erfasst einen aktuellen KDE-Wert im Manifest."""

    if value_type not in ALLOWED_TYPES:
        raise ValueError(f"Nicht unterstützter Typ: {value_type}")

    config_path = resolve_config_file(filename, require_exists=True)

    data = load_manifest()

    current_value = read_current_value(config_path, group, key)

    new_entry = {
        "file": filename,
        "group": group,
        "key": key,
        "type": value_type,
        "value": current_value
    }

    existing = next(
        (
            entry for entry in data["settings"]
            if entry.get("file") == filename
            and entry.get("group") == group
            and entry.get("key") == key
        ),
        None
    )

    if existing:
        existing.update(new_entry)
        action = "aktualisiert"
    else:
        data["settings"].append(new_entry)
        action = "neu gespeichert"

    save_manifest(data)

    print("MNEMOSYNE CAPTURE")
    print("=================")
    print(f"Datei:     {filename}")
    print(f"Gruppe:    {group}")
    print(f"Schlüssel: {key}")
    print(f"Wert:      {current_value}")
    print(f"Status:    {action}")
    print("\nManifest erfolgreich gespeichert.")


def apply_setting(filename, group, key):
    """Überträgt einen gespeicherten Wert in die aktuelle Sitzung."""

    data = load_manifest()

    setting = next(
        (
            entry for entry in data["settings"]
            if entry.get("file") == filename
            and entry.get("group") == group
            and entry.get("key") == key
        ),
        None
    )

    if setting is None:
        raise ValueError(
            f"Einstellung nicht im Manifest gefunden: "
            f"{filename} / {group} / {key}"
        )

    config_path = validate_setting(setting)

    if not config_path.is_file():
        raise FileNotFoundError(
            f"Konfigurationsdatei fehlt: {config_path}"
        )

    command = [
        "kwriteconfig6",
        "--file", str(config_path),
        "--group", setting["group"],
        "--key", setting["key"]
    ]

    if setting["type"] == "bool":
        command.extend(["--type", "bool"])

    value = setting.get("value")
    if not isinstance(value, str):
        raise ValueError("Ungültiger oder fehlender Einstellungswert.")

    command.append(value)

    subprocess.run(command, check=True)

    current_value = read_current_value(
        config_path,
        setting["group"],
        setting["key"]
    )

    if current_value != setting["value"]:
        raise RuntimeError(
            f"Apply fehlgeschlagen! Erwartet: "
            f"{setting['value']}, erhalten: {current_value}"
        )

    print("MNEMOSYNE APPLY")
    print("================")
    print(f"Datei:       {filename}")
    print(f"Gruppe:      {group}")
    print(f"Schlüssel:   {key}")
    print(f"Übernommen:  {current_value}")
    print("\nApply erfolgreich!")

def apply_all():
    """Wendet alle permanent gespeicherten Einstellungen an."""

    data = load_manifest()
    settings = data["settings"]

    total = len(settings)
    successful = 0
    failed = 0

    print("MNEMOSYNE PERMANENT APPLY")
    print("=========================")
    print(f"Gespeicherte Einstellungen: {total}\n")

    for index, setting in enumerate(settings, start=1):
        filename = setting["file"]
        group = setting["group"]
        key = setting["key"]

        print(f"[{index}/{total}] {filename} / {group} / {key}")

        try:
            apply_setting(filename, group, key)
            successful += 1
            print("Status: OK\n")

        except (
            OSError,
            ValueError,
            KeyError,
            subprocess.CalledProcessError,
            RuntimeError
        ) as error:
            failed += 1
            print(f"Status: FEHLER – {error}\n")

    print("=========================")
    print(f"{total} Einstellungen verarbeitet.")
    print(f"{successful} erfolgreich.")
    print(f"{failed} fehlgeschlagen.")

def list_settings():
    data = load_manifest()

    print("MNEMOSYNE Persistence Engine")
    print("============================")
    print(f"Manifest: {MANIFEST}")
    print(f"Version:  {data['version']}")
    print(f"Einträge: {len(data['settings'])}\n")

    for index, setting in enumerate(data["settings"], start=1):
        path = validate_setting(setting)

        print(f"--- Einstellung {index} ---")
        print(f"Datei:       {path}")
        print(f"Gruppe:      {setting['group']}")
        print(f"Schlüssel:   {setting['key']}")
        print(f"Typ:         {setting['type']}")
        print(f"Gespeichert: {setting['value']}")

        if path.is_file():
            current = read_current_value(
                path,
                setting["group"],
                setting["key"]
            )
            print(f"Aktuell:     {current}")
        else:
            print("Aktuell:     Datei fehlt!")

        print()

def main():
    parser = argparse.ArgumentParser(
        prog="MNEMOSYNE",
        description=VERSION_STRING
    )

    parser.add_argument(
        "--version",
        action="version",
        version=VERSION_STRING
    )


    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser(
        "list",
        help="Shows all saved settings"
    )

    apply_parser = subparsers.add_parser(
        "apply",
        help="Apply a saved setting"
    )

    apply_parser.add_argument("file")
    apply_parser.add_argument("group")
    apply_parser.add_argument("key")

    subparsers.add_parser(
        "apply-all",
        help="Apply all permanent saved settings"
    )

    capture_parser = subparsers.add_parser(
        "capture",
        help="Capture current settings permanent"
    )

    capture_parser.add_argument("file")
    capture_parser.add_argument("group")
    capture_parser.add_argument("key")
    capture_parser.add_argument(
        "type",
        choices=sorted(ALLOWED_TYPES)
    )

    args = parser.parse_args()

    try:
        if args.command == "capture":
            capture_setting(
                args.file,
                args.group,
                args.key,
                args.type
            )

        elif args.command == "apply":
            apply_setting(
                args.file,
                args.group,
                args.key
            )

        elif args.command == "apply-all":
            apply_all()

        elif args.command == "list":
            list_settings()

        else:
            parser.print_help()

    except (
        OSError,
        ValueError,
        KeyError,
        json.JSONDecodeError,
        subprocess.CalledProcessError
    ) as error:
        print(f"FEHLER: {error}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
