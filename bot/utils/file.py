# /project/helpers/io/file.py
# File editors for the bot

import asyncio
import json
import tomllib
import os
import tempfile

from colorama import Fore, Style, init

from bot.utils.lock import LockManager

init(autoreset=True)

lock_manager = LockManager()


def coerce(current_value, new_value):
    target_type = type(current_value)

    if target_type is bool:
        if isinstance(new_value, str):
            return new_value.lower() in (
                "true", "1", "yes", "on", "enable",
                "false", "0", "no", "off", "disable"
            )
        return bool(new_value)

    if target_type in (int, str):
        try:
            return target_type(new_value)
        except (ValueError, TypeError):
            return new_value

    if target_type in (list, dict):
        return new_value if isinstance(new_value, target_type) else current_value

    return new_value


class JsonFile:
    def __init__(self, file_path, CREATE_MISSING_FILE=True):
        self.file_path = "data/" + file_path
        self.CREATE_MISSING_FILE = CREATE_MISSING_FILE

    async def _lock(self) -> asyncio.Lock:
        return await lock_manager.get_lock(self.file_path)

    # ===================== LOGGING =====================

    def _log(self, level: str, message: str):
        color = {
            "ERROR": Fore.RED,
            "WARNING": Fore.YELLOW
        }.get(level, Fore.WHITE)

        print(
            f"{Fore.GREEN}[FILE EDITORS]"
            f"{color}[{level}]:{Style.RESET_ALL} "
            f"{message} File path: {Fore.BLUE}{self.file_path}"
        )

    # ===================== ATOMIC WRITE =====================

    def _atomic_write(self, data: dict):
        directory = os.path.dirname(self.file_path)

        with tempfile.NamedTemporaryFile(
            mode="w",
            dir=directory,
            delete=False,
            encoding="utf-8"
        ) as tmp:
            json.dump(data, tmp, indent=4)
            tmp.flush()
            os.fsync(tmp.fileno())
            temp_name = tmp.name

        os.replace(temp_name, self.file_path)

    # ===================== LOAD =====================

    def _load_json(self):
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)

        except json.JSONDecodeError:
            self._log("ERROR", "⚠️ JSON is corrupt or empty. Writing is not allowed.")
            return {}

        except FileNotFoundError:
            self._log("ERROR", "⚠️ File not found.")

            if self.CREATE_MISSING_FILE:
                self._log("WARNING", "⚠️ Creating new file.")
                self._atomic_write({})
            return {}

    # ===================== READ =====================

    def read_sync(self, key=None, default=None):
        json_load = self._load_json()
        if key is None:
            return json_load
        return json_load.get(key, default)

    async def read(self, key=None, default=None):
        async with await self._lock():
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(None, self._sync_read, key, default)

    # ===================== WRITE (DEPRECATED) =====================

    async def write(self, data, merge=True, prioritize=0):
        print(
            f"{Fore.GREEN}[FILE EDITORS]"
            f"{Fore.YELLOW}[WARNING]:{Style.RESET_ALL} "
            f"⚠️ The write function is deprecated. Use update instead. "
            f"File path: {Fore.BLUE}{self.file_path}"
        )
        return

    # ===================== UPDATE =====================

    async def update(
        self,
        data: dict,
        strict_types: bool = True,
        strict_keys: bool = False,
        coerce_types: bool = False
    ):
        async with await self._lock():
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(
                None,
                self._sync_update,
                data,
                strict_types,
                coerce_types,
                strict_keys
            )

    async def set_key(self, key, value):
        await self.update({key: value})

    async def delete_key(self, key):
        async with await self._lock():
            data = self._load_json()
            if key in data:
                del data[key]
                self._atomic_write(data)
                return True
            return False

    # ===================== SYNC UPDATE =====================

    def _sync_update(self, data, strict_types, coerce_types, strict_keys):
        current_data = self._load_json()
        errors = []

        for key, value in data.items():
            key = str(key)
            key_exists = key in current_data

            if not key_exists and strict_keys:
                errors.append(f"Missing key: {key}")
                continue

            if not key_exists and not strict_keys:
                current_data[key] = value
                continue

            if coerce_types:
                value = coerce(current_data[key], value)

            if strict_types and not isinstance(value, type(current_data[key])):
                errors.append(
                    f"Type mismatch for '{key}': "
                    f"{type(current_data[key]).__name__} != {type(value).__name__}"
                )
                continue

            if isinstance(current_data[key], dict) and isinstance(value, dict):
                current_data[key].update(value)
            else:
                current_data[key] = value

        if errors:
            raise ValueError("; ".join(errors))

        self._atomic_write(current_data)

    # ===================== SYNC READ =====================

    def _sync_read(self, key, default):
        json_load = self._load_json()
        if key is None:
            return json_load
        return json_load.get(key, default)

    # ===================== SYNC WRITE (DEPRECATED INTERNAL) =====================

    def _sync_write(self, data, merge, prioritize):
        if merge:
            current_data = self._load_json()
            current_data.update(data)
            data = current_data

        self._atomic_write(data)


class TomlFile:
    def __init__(self, file_path, CREATE_MISSING_FILE=True):
         self.file_path = "data/" + file_path
         self.CREATE_MISSING_FILE = CREATE_MISSING_FILE

    def _load_toml(self):
        """Loads TOML from disk."""
        toml_data = None
        try:
            with open(self.file_path, "rb") as f:
                toml_data =  tomllib.load(f)

        except tomllib.TOMLDecodeError:
            toml_data = {}

            print(f"{Fore.GREEN}[FILE EDITORS]{Fore.RED}[ERROR]:{Style.RESET_ALL}⚠️ TOML is corrupt or empty. File path: {Fore.BLUE}{self.file_path}")

        except FileNotFoundError:
            toml_data = {}

            print(f"{Fore.GREEN}[FILE EDITORS]{Fore.RED}[ERROR]:{Style.RESET_ALL}⚠️ File not found. File path: {Fore.BLUE}{self.file_path}")

            if self.CREATE_MISSING_FILE:
                 print(f"{Fore.GREEN}[FILE EDITORS]{Fore.YELLOW}[WARNING]:{Style.RESET_ALL}⚠️ Creating new file. File path: {Fore.BLUE}{self.file_path}")
                 with open(self.file_path, "w", encoding="utf-8") as f:
                    f.write("")

        return toml_data

    def read_sync(self, key=None, default=None):
        toml_load = self._load_toml()
        if key is None:
            return toml_load
        return toml_load.get(key, default)

    async def read(self, key=None, default=None):
        toml_load = self._load_toml()
        if key is None:
            return toml_load
        return toml_load.get(key, default)