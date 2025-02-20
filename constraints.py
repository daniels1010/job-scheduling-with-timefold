def define_constraints():
    return [
        # 1. Ensure tasks are assigned to workers with the required skills
        "valid_skill_match",

        # 2. Avoid assigning workers to unavailable dates
        "avoid_unavailable_dates",

        # 3. Prioritize high-priority tasks first
        "prioritize_important_tasks",
    ]
