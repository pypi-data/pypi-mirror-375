import os
from pathlib import Path
import platform


def get_default_minecraft_home(edition: str = "java") -> Path:
    """
    Returns the default Minecraft directory based on OS and edition.

    edition: "java" (default) or "bedrock"
    """
    home = Path.home()
    system = platform.system()

    if edition.lower() == "java":
        if system == "Windows":
            return Path(os.getenv("APPDATA", home / "AppData/Roaming")) / ".minecraft"
        elif system == "Darwin":  # macOS
            return home / "Library" / "Application Support" / "minecraft"
        else:  # Linux, BSD, etc.
            return home / ".minecraft"

    elif edition.lower() == "bedrock":
        if system == "Windows":
            local_appdata = Path(os.getenv("LOCALAPPDATA", home / "AppData/Local"))
            return (
                local_appdata
                / "Packages"
                / "Microsoft.MinecraftUWP_8wekyb3d8bbwe"
                / "LocalState"
                / "games"
                / "com.mojang"
            )
        elif system == "Darwin":  # macOS (iOS not supported here)
            return (
                home
                / "Library"
                / "Containers"
                / "com.mojang.minecraftpe"
                / "Data"
                / "Documents"
                / "games"
                / "com.mojang"
            )
        else:  # Linux/Android → not standardized
            return Path("/sdcard/games/com.mojang")

    else:
        raise ValueError(f"Unknown edition: {edition!r}")


def check_if_valid_home(home: Path) -> bool:
    required_subdirs = ["versions", "assets", "saves"]

    for subdir in required_subdirs:
        dir = home / subdir
        if not dir.is_dir():
            return False

    return True


def check_if_valid_save(home: Path) -> bool:
    required_subdirs = ["playerdata", "region"]
    required_files = ["level.dat"]

    for subdir in required_subdirs:
        dir = home / subdir
        if not dir.is_dir():
            return False

    for file_name in required_files:
        dir = home / file_name
        if not dir.is_file():
            return False

    return True
