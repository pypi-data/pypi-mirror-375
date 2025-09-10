import os
from dynaconf import Dynaconf
from pathlib import Path

config_dir = Path.home() / ".config" / "ying"
if not config_dir.exists():
    os.makedirs(config_dir, exist_ok=True)

settings = Dynaconf(
    root_path=config_dir,
    settings_files=["settings.toml"],
    environments=True,
    envvar_prefix="YING",
    load_dotenv=True,
)
