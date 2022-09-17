import pandas as pd
import numpy as np
from tools import *
import yaml


def generate(
        out_csv: str,
        yaml_path: str,
        task_dict: Dict[str, Task],
        role_dict: Dict[str, Role],
        details: bool = False,
        seed: int = None):
    with open(yaml_path, "r") as f:
        recruits = yaml.safe_load(f)["recruits"]
    recruits = list(map((lambda item: Recruit(**item)), recruits.values()))

    seed = np.random.RandomState(seed=seed)
    ro_df = pd.DataFrame.from_dict({
        "4D": [recruit.four_d for recruit in recruits],
        "role": [None for _ in recruits],
        "special": [recruit.specialization for recruit in recruits],
        "misc_role": [recruit.misc_role for recruit in recruits],
        "history": [recruit.history[-1] for recruit in recruits],
        "toilet_merit": [recruit.toilet_merit for recruit in recruits],
        "general_merit": [recruit.general_merit for recruit in recruits],
        "toilet_merit_new": [recruit.toilet_merit for recruit in recruits],
        "general_merit_new": [recruit.general_merit for recruit in recruits],
    })
    ro_df = ro_df.set_index("4D")

    for task in task_dict.keys():
        ro_df[task] = 0

    # Fill in misc tasks
    for n, recruit in enumerate(recruits):
        if recruit.misc_role:
            ro_df.at[recruit.four_d, recruit.misc_role] += 1
            task = task_dict[recruit.misc_role]
            try:
                role_dict[task.role].tasks.remove(task)
            except ValueError:
                print([task.name for task in role_dict[task.role].tasks])
                print(task.name)
                raise ValueError

    # Fill in toilet IC
    toilet_ic_num = role_dict["toilet_ic"].strength
    toilet_ic_pool = ro_df[ro_df["history"] != "toilet_ic"]
    toilet_ic_pool_w_role = toilet_ic_pool[toilet_ic_pool['special'].notna()].sort_values(
        by="toilet_merit", ascending=True)
    toilet_ic_pool_w_role = toilet_ic_pool_w_role.drop_duplicates(subset="special")
    toilet_ic_pool = pd.concat(
        [toilet_ic_pool_w_role, toilet_ic_pool[toilet_ic_pool['special'].isna()]]).sample(frac=1.0, random_state=seed)
    toilet_ics = toilet_ic_pool.nsmallest(toilet_ic_num, "toilet_merit")["toilet_main"].index.tolist()
    for toilet_ic in toilet_ics:
        ro_df.at[toilet_ic, "toilet_main"] += 1
        ro_df.at[toilet_ic, "role"] = "toilet_ic"
    role_dict["toilet_ic"].tasks = []

    role_mean_points = {
        name: sum(task.general_merit for task in role.tasks) / role.strength for name, role in role_dict.items()
        if sum(task.general_merit for task in role.tasks) > 0
    }
    role_mean_points = dict(sorted(role_mean_points.items(), key=(lambda item: item[1]), reverse=True))

    for role_name, points in role_mean_points.items():

        # Specialized ICs where the buddy is going to do other ICs
        lone_spl = ro_df[ro_df["role"].isna() & ro_df["special"].notna()]
        lone_spl = lone_spl[~lone_spl.duplicated("special", keep=False)].index.tolist()
        for spl_ic in lone_spl:
            role = ro_df.at[spl_ic, "special"]
            if role_dict[role].tasks:
                ro_df.at[spl_ic, "role"] = role
                task = role_dict[role].tasks[0]
                ro_df.at[spl_ic, task.name] += 1
                role_dict[role].tasks.remove(task)

        role = role_dict[role_name]
        if role.tasks:
            no_role_pool = ro_df[ro_df["role"].isna()].sample(frac=1.0, random_state=seed)
            if role.role_type == "partially_specialized":
                no_role_spl = no_role_pool[no_role_pool['special'] == role.name].sample(frac=1.0, random_state=seed)
                new_ics = no_role_spl.nsmallest(1, "general_merit").index.tolist()
                no_role_pool = no_role_pool[no_role_pool['special'] != role.name].sample(frac=1.0, random_state=seed)
                new_ics += no_role_pool.nsmallest(role.strength - 1, "general_merit").index.tolist()
            elif role.role_type == "specialized":
                no_role_pool = no_role_pool[no_role_pool['special'] == role.name].sample(frac=1.0, random_state=seed)
                new_ics = no_role_pool.nsmallest(role.strength, "general_merit").index.tolist()
            else:
                no_role_spl = no_role_pool[no_role_pool['special'].notna()].drop_duplicates(subset="special")
                no_role_pool = pd.concat(
                    [no_role_spl, no_role_pool[no_role_pool['special'].isna()]]).sample(frac=1.0, random_state=seed)
                new_ics = no_role_pool.nsmallest(role.strength, "general_merit").index.tolist()

            task_per_role = split_role(role)
            for ic_4d, tasks in zip(new_ics, task_per_role):
                ro_df.at[ic_4d, "role"] = role.name
                for task in tasks:
                    ro_df.at[ic_4d, task.name] += 1
                    role_dict[role_name].tasks.remove(task)

    ro_df["role"] = ro_df["role"].apply(lambda s: s if s else "backup")
    for task in task_dict.values():
        ro_df["toilet_merit_new"] += ro_df[task.name] * task.toilet_merit
        ro_df["general_merit_new"] += ro_df[task.name] * task.general_merit

    ro_df["toilet_merit_new"] = np.round(ro_df["toilet_merit_new"], 3)
    ro_df["general_merit_new"] = np.round(ro_df["general_merit_new"], 3)
    ro_df["toilet_merit"] = np.round(ro_df["toilet_merit"], 3)
    ro_df["general_merit"] = np.round(ro_df["general_merit"], 3)
    if not details:
        del ro_df["special"], ro_df["misc_role"], ro_df["history"]
    ro_df.to_csv(out_csv)


def main():
    from datetime import datetime

    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    task_dict = {task.name: task for task in map((lambda item: Task(**item)), config["tasks"].values())}
    role_dict = {role.name: role for role in map((lambda item: Role(task_dict, **item)), config["roles"].values())}

    seed = int(datetime.today().strftime('%Y%m%d'))
    generate(out_csv="assigned_ro.csv", yaml_path="save.yaml", task_dict=task_dict, role_dict=role_dict, seed=seed)


if __name__ == "__main__":
    main()
