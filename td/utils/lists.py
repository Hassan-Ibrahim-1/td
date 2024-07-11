class List:

    def __init__(self, list_id: int, name: str):
        self.id = int(list_id)
        self.name = name
        self.task_ids = []

    def __repr__(self):
        return f"List({self.id}, {self.name})"
