from pathlib import Path
from typing import Tuple
import nbtlib as nbt
from nbtlib.tag import Short, Float, Int, Double


def restore(world_dir: Path, move: Tuple[float, float, float]):
    with nbt.load(world_dir / "level.dat") as level:

        level["Data"]["Player"]["foodLevel"] = Int(20)
        level["Data"]["Player"]["Health"] = Float(10)
        if level["Data"]["Player"].get("LastDeathLocation") is not None:
            del level["Data"]["Player"]["LastDeathLocation"]
        level["Data"]["Player"]["DeathTime"] = Short(0)

        level["Data"]["Player"]["playerGameType"] = Int(0)

        for cord_index in range(3):
            level["Data"]["Player"]["Pos"][cord_index] += Double(move[cord_index])

    playerdata_dir = world_dir / "playerdata"
    for file in playerdata_dir.glob("*.dat"):
        with nbt.load(file) as f:

            f["foodLevel"] = Int(20)
            f["Health"] = Float(10)
            if f.get("LastDeathLocation") is not None:
                del f["LastDeathLocation"]
            f["DeathTime"] = Short(0)

            f["playerGameType"] = Int(0)

            for cord_index in range(3):
                f["Pos"][cord_index] += Double(move[cord_index])
