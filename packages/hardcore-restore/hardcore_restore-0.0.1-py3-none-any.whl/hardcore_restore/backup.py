from pathlib import Path
import shutil


def make_backup(save_dir: Path, world_name: str) -> str:
    output_filename = save_dir / f"{world_name}-before_restore"
    dir_name = save_dir / world_name
    return shutil.make_archive(output_filename, "zip", dir_name)
