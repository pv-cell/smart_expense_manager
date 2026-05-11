import logging
from app.domain.models.user import User

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, repo):
        self.repo = repo
        self.users = {}

    def create_user(self, name):
        name = name.strip()

        if not name:
            raise ValueError("User name cannot be empty")

        existing_user = self.repo.get_user_by_name(name)
        if existing_user is not None:
            raise ValueError(f"User '{name}' already exists")

        user = User(None, name)

        try:
            user_id = self.repo.create_user(user)
            user.id = user_id

            logger.info(f"User created: {user.name} (ID={user_id})")
            return user
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise

    def get_user(self, user_id):
        if user_id in self.users:
            return self.users[user_id]

        try:
            user = self.repo.get_user(user_id)
            if not user:
                return None

            self.users[user.id] = user
            return user

        except Exception as e:
            logger.error(f"Failed to fetch user {user_id} : {e} ")
            raise

    def list_users(self):
        if not self.users:
            try:
                users = self.repo.list_users()
                for user in users:

                    self.users[user.id] = user
            except Exception as e:
                logger.error(f"Failed to list users from MySQL: {e}")
                raise

        return list(self.users.values())

    def get_user_by_name(self, name):
        users = self.list_users()  # reuse existing logic
        for user in users:
            if user.name == name:
                return user
        raise ValueError(f"User '{name}' not found")
