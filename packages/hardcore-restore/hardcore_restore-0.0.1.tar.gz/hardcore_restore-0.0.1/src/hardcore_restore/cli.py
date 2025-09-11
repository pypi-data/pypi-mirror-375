from pathlib import Path
from typing import Annotated
import typer

from hardcore_restore.backup import make_backup
from hardcore_restore.restore import restore
from hardcore_restore.utils import (
    check_if_valid_home,
    check_if_valid_save,
    get_default_minecraft_home,
)
from hardcore_restore.statistics import nerf_death_count


default_home: Path = get_default_minecraft_home()


def run(
    world_name: Annotated[str, typer.Argument()],
    minecraft_home: Annotated[
        Path, typer.Option("--minecraft-home", "-m")
    ] = default_home,
    do_backup: bool = True,
    change_stats: bool = False,
    move_x: Annotated[float, typer.Option("--move-x", "-rx")] = 0,
    move_y: Annotated[float, typer.Option("--move-y", "-ry")] = 0,
    move_z: Annotated[float, typer.Option("--move-z", "-rz")] = 0,
):

    if not check_if_valid_home(minecraft_home):
        # typer.echo("Minecraft Home not exists, try to specify with -m")
        while not check_if_valid_home(minecraft_home):
            typer.echo("Minecraft Home dir doesn't seem to be valid!")
            minecraft_home = typer.prompt(
                "Please provide the correct minecraft home! (leave empty for default)",
                default=default_home,
                type=Path,
            )

    world_dir = minecraft_home / "saves" / world_name

    if not world_dir.is_dir():
        typer.echo(
            f"Error, no world exists in {world_dir} (no directory). Check if it is correct",
            err=True,
        )
        raise typer.Exit(1)

    if not check_if_valid_save(world_dir):
        typer.echo(
            f"Error, the given world doesn't seem like a valid minecraft world in {world_dir}. Check if it is correct",
            err=True,
        )
        raise typer.Exit(1)

    if do_backup:
        typer.echo("Making backup..")
        backup_zip = make_backup(minecraft_home / "saves", world_name)
        typer.echo(
            typer.style(f"backup is under {backup_zip}", bold=True)
            + ", simply unzip to recover!"
        )

    typer.echo(f"Changing world in {world_dir}!")
    restore(world_dir, (move_x, move_y, move_z))

    if change_stats:
        typer.echo(f"Changing stats..")
        nerf_death_count(world_dir)


def main():
    typer.run(run)


if __name__ == "__main__":
    main()
