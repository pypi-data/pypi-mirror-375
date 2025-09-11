import json
from pathlib import Path


def nerf_death_count(world_dir: Path):
    stats_dir = world_dir / "stats"
    for stat_file in stats_dir.glob("*.json"):
        with open(stat_file, "r") as f:
            data = json.load(f)

            data["stats"]["minecraft:custom"]["minecraft:deaths"] = 0
            data["stats"]["minecraft:custom"]["minecraft:time_since_death"] = 0

        with open(stat_file, "w") as f:
            json.dump(data, f)
