from tools import *


def main():
    from generate_ro import generate
    from update_ro import update
    import os
    import copy
    import yaml
    import datetime

    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)

    yaml_path = "save.yaml"
    num_days = 20
    days = [int((datetime.datetime.today() + datetime.timedelta(days=add_days)).strftime('%Y%m%d'))
            for add_days in range(num_days)]
    for day in days:
        task_dict = {task.name: task for task in map((lambda item: Task(**item)), config["tasks"].values())}
        role_dict = {role.name: role for role in map((lambda item: Role(task_dict, **item)), config["roles"].values())}
        out_csv = os.path.join("ro_sample/ro_hist", f"assigned_ro_{day}.csv")
        out_yaml = os.path.join("ro_sample/save_hist", f"save_{day}.yaml")
        generate(out_csv=out_csv, yaml_path=yaml_path, task_dict=task_dict, role_dict=role_dict, seed=day)
        update(yaml_path=yaml_path, out_yaml=out_yaml, ro_path=out_csv, task_dict=task_dict)
        yaml_path = out_yaml


if __name__ == "__main__":
    main()
