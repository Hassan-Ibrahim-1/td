class Task:

    def __init__(self, name: str, task_id: int, importance: int = 1, description: str = "") -> None:
        self.name = name
        self.id = int(task_id)
        self.importance = int(importance)
        self.description = description
        self.checklist = []
    
    @property
    def completed(self) -> bool:
        if self.name[-1] == '0':
            return False
        return True
    
    @property
    def num_done(self) -> int:
        done_items = 0
        for item in self.checklist:
            if item[-1] == '1':
                done_items += 1

        return done_items
    
    @property
    def num_undone(self) -> int:
        undone_items = 0
        for item in self.checklist:
            if item[-1] == '0':
                undone_items += 1

        return undone_items
    
    def add_item(self, item_name: str) -> None:
        self.checklist.append(item_name)
    
    def __repr__(self):
        return f"Task({self.id}, {self.name})"
