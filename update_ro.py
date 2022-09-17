import pandas as pd
from tools import *
import yaml


def update(yaml_path: str, out_yaml: str, ro_path: str, task_dict: Dict[str, Task]):
    with open(yaml_path, "r") as f:
        yaml_recruits = yaml.safe_load(f)
    recruits = yaml_recruits["recruits"]
    ro_df = pd.read_csv(ro_path, index_col="4D")
    for index, row in ro_df.iterrows():
        recruit = recruits[index]
        for task in task_dict.values():
            recruit["toilet_merit"] += row[task.name] * task.toilet_merit
            recruit["general_merit"] += row[task.name] * task.general_merit
        recruit["toilet_merit"] = round(recruit["toilet_merit"], 3)
        recruit["general_merit"] = round(recruit["general_merit"], 3)
        recruit["history"].append(row["role"])

    with open(out_yaml, "w") as f:
        yaml.dump(yaml_recruits, f)


def main():
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    task_dict = {task.name: task for task in map((lambda item: Task(**item)), config["tasks"].values())}

    update("save.yaml", "save.yaml", "assigned_ro.csv", task_dict)


if __name__ == "__main__":
    main()
