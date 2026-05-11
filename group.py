class Group:
    def __init__(self, group_id, name):
        self.id = group_id
        self.name = name
        self.members = []

    def add_member(self, user_id):
        if user_id not in self.members:
            self.members.append(user_id)

    def remove_member(self, user_id):
        if user_id in self.members:
            self.members.remove(user_id)

    def __repr__(self):
        return f"Group(id={self.id},name='{self.name}', members={self.members})"
