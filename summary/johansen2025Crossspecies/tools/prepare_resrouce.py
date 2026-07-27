import os
import yaml
from pathlib import Path
from typing import Any

repo_dir = "/gpfs/commons/groups/iossifov_lab/SC_Summaries_GRR"


def prepapre_resrouce(resource_id: str, files: list[str],
                      config: dict[str, Any]):
    resource_dir = repo_dir + "/" + resource_id
    os.makedirs(resource_dir, exist_ok=True)

    for rf in files:
        remote_file = Path(rf)
        target_dir = Path(resource_dir)

        symlink_path = target_dir / remote_file.name
        if os.path.isfile(symlink_path):
            continue
        symlink_path.symlink_to(remote_file)

    with open(resource_dir + "/genomic_resource.yaml", 'w') as file:
        yaml.dump(config, file, default_flow_style=False, sort_keys=False)

