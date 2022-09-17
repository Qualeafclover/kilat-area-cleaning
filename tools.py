from typing import *


class Task:
    name: str
    role: str
    toilet_merit: float = 0.0
    general_merit: float = 0.0

    def __init__(self, **kwargs):
        for _ in map((lambda kv: setattr(self, kv[0], kv[1])), kwargs.items()):
            pass

    def __repr__(self):
        return f"\n" \
               f"\ttask name            = {self.name}\n" \
               f"\trole name            = {self.role}\n" \
               f"\ttoilet merit points  = {self.toilet_merit}\n" \
               f"\tgeneral merit points = {self.general_merit}\n"


class Recruit:
    four_d: int = 0
    specialization: str = None
    misc_role: str = None
    toilet_merit: float = 0.0
    general_merit: float = 0.0
    history: List[str] = []

    def __init__(self, **kwargs):
        for _ in map((lambda kv: setattr(self, kv[0], kv[1])), kwargs.items()):
            pass

    def __repr__(self):
        return f"\n" \
               f"4D                   = {self.four_d}\n" \
               f"specialization       = {self.specialization}\n" \
               f"misc role            = {self.misc_role}\n" \
               f"toilet merit points  = {self.toilet_merit}\n" \
               f"general merit points = {self.general_merit}\n" \
               f"task history         = {self.history}\n"


class Role:
    name: str
    role_type: str = None
    strength: int = 0
    tasks: List[Task] = None

    def __init__(self, task_dict: dict, **kwargs):
        for _ in map((lambda kv: setattr(self, kv[0], kv[1])), kwargs.items()):
            pass
        self.tasks = list(map((lambda s: task_dict[s]), self.tasks))

    def __repr__(self):
        return f"\n" \
               f"role name         = {self.name}\n" \
               f"role type         = {self.role_type}\n" \
               f"strength expected = {self.strength}\n" \
               f"tasks             = {self.tasks}\n"


def split_role(role: Role):
    rtask_dict = {task.name: task for task in role.tasks}
    rtask_list = sorted([(task.general_merit, task.name) for task in role.tasks], reverse=True)
    task_per_role = [[] for _ in range(role.strength)]
    for rtask in rtask_list:
        tpr_sum = [sum(st[0] for st in role) for role in task_per_role]
        min_index = tpr_sum.index(min(tpr_sum))
        task_per_role[min_index].append(rtask)
    task_per_role = [[rtask_dict[st[1]] for st in role] for role in task_per_role]
    return task_per_role


def main():
    import yaml
    from pprint import pprint

    with open("save.yaml.bkp", "r") as f:
        recruits = yaml.safe_load(f)["recruits"]
    recruits = list(map((lambda item: Recruit(**item)), recruits.values()))
    # pprint(recruits)

    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    task_dict = {task.name: task for task in map((lambda item: Task(**item)), config["tasks"].values())}
    role_dict = {role.name: role for role in map((lambda item: Role(task_dict, **item)), config["roles"].values())}
    split_role(role_dict["bunk_ic"])
    # print(role_dict["bunk_ic"])


if __name__ == "__main__":
    main()
