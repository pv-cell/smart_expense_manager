import logging
from app.domain.models.group import Group

logger = logging.getLogger(__name__)


class GroupService:
    def __init__(self, repo):
        self.repo = repo
        self.groups = {}

    def create_group(self, name):
        name = name.strip()

        if not name:
            raise ValueError("Group name canot be empty")

        existing_groups = self.list_group()
        for group in existing_groups:
            if group.name == name:
                raise ValueError(f"Group '{name}' already exists")

        group = Group(None, name)

        try:
            group_id = self.repo.create_group(group)
            group.id = group_id
            self.groups[group_id] = group
            logger.info(f"Group created: {group.name} (ID={group_id})")
            return group
        except Exception as e:
            logger.error(f"Failed to create group: {e}")
            raise

    def add_user_to_group(self, group_id, user_id):
        group = self.get_group(group_id)
        if not group:
            raise ValueError("Group not found")

        if user_id in group.members:
            logger.info("User already in group")
            return False

        try:
            self.repo.add_user_to_group(group_id, user_id)

            group.add_member(user_id)
            logger.info(f"User {user_id} added to group {group_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add user to group: {e}")
            raise

    def remove_user_from_group(self, group_id, user_id):
        group = self.get_group(group_id)
        if not group:
            raise ValueError("Group not found")

        if user_id not in group.members:
            raise ValueError("User not in group")

        try:
            self.repo.remove_user_from_group(group_id, user_id)

            group.remove_member(user_id)
            logger.info(f"User {user_id} removed from group {group_id} ")
        except Exception as e:
            logger.error(f"Failed to remove user from group: {e}")
            raise

    def get_group(self, group_id):
        if group_id in self.groups:
            return self.groups[group_id]

        try:
            row = self.repo.get_group(group_id)
            if not row:
                return None

            group = Group(row["id"], row["name"])

            members = self.repo.get_group_members(group_id)
            for user_id in members:
                group.add_member(user_id)

            self.groups[group.id] = group
            return group
        except Exception as e:
            logger.error(f"Failed to fetch group {group_id}: {e}")
            raise

    def list_group(self):
        if not self.groups:
            try:
                rows = self.repo.list_groups()
                for row in rows:
                    group = Group(row["id"], row["name"])
                    members = self.repo.get_group_members(row["id"])
                    for user_id in members:
                        group.add_member(user_id)
                    self.groups[group.id] = group
            except Exception as e:
                logger.error(f"Failed to list groups: {e}")
                raise

        return list(self.groups.values())

    def get_group_by_name(self, name):
        groups = self.list_group()
        for group in groups:
            if group.name == name:
                return group
        raise ValueError(f"Group '{name}' not found")

    def list_group_members(self, group_name):
        group = self.get_group_by_name(group_name)
        if not group:
            raise ValueError(f"Group '{group_name}' not found")

        rows = self.repo.list_group_members(group.id)
        return rows
