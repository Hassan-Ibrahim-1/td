class Workspace:

    def __init__(self, name, workspace_id):
        
        self.name = name
        self.id = int(workspace_id)
        self.list_ids = []

    def __repr__(self):
        return f"Workspace({self.id}, {self.name})"