import os
import yaml
from pathlib import Path
from typing import Any

repo_dir = "/gpfs/commons/groups/iossifov_lab/SC_Summaries_GRR"


def get_resource_dir(resource_id: str) -> str:
    return repo_dir + "/" + resource_id


def prepapre_resrouce(resource_id: str, files: list[str|tuple[str,str]],
                      config: dict[str, Any]):
    resource_dir = get_resource_dir(resource_id)
    os.makedirs(resource_dir, exist_ok=True)

    for rf in files:
        if isinstance(rf, str):
            remote_file = Path(rf)
            link_name = remote_file.name
        else:
            assert len(rf) == 2
            remote_file = Path(rf[0])
            link_name = rf[1]
        target_dir = Path(resource_dir)

        symlink_path = target_dir / link_name
        if os.path.isfile(symlink_path):
            continue
        symlink_path.symlink_to(remote_file)

    with open(resource_dir + "/genomic_resource.yaml", 'w') as file:
        yaml.dump(config, file, default_flow_style=False, sort_keys=False)

