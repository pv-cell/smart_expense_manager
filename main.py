import argparse
import mysql.connector
import logging
import asyncio
import os

from app.async_tasks import simulate_notifications, notification_queue

from app.services.user_service import UserService
from app.services.group_service import GroupService
from app.services.expense_service import ExpenseService
from app.services.balance_service import BalanceService

from app.repositories.user_repository_mysql import UserRepositoryMySQL
from app.repositories.group_repository_mysql import GroupRepositoryMySQL
from app.repositories.expense_repository_mysql import ExpenseRepositoryMySQL
from app.services.user_service import UserService

from app.async_tasks import simulate_notifications

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def build_services():
    
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST", "mysql"),
        user=os.getenv("DB_USER", "appuser"),
        password=os.getenv("DB_PASSWORD", "apppassword"),
        database=os.getenv("DB_NAME", "expense_manager"),
    )
    user_repo = UserRepositoryMySQL()
    group_repo = GroupRepositoryMySQL(conn)
    expense_repo = ExpenseRepositoryMySQL(conn)

    user_service = UserService(user_repo)
    group_service = GroupService(group_repo)
    expense_service = ExpenseService(expense_repo)
    balance_service = BalanceService(group_service, expense_service)

    return user_service, group_service, expense_service, balance_service


def create_user_cmd(name):
    user_service, _, _, _ = build_services()
    user = user_service.create_user(name)
    print(f"User created: id={user.id}, name={user.name}")


def create_group_cmd(name):
    _, group_service, _, _ = build_services()
    try:
        group = group_service.create_group(name)
        print(f"Group created: id={group.id}, name={group.name}")
    except ValueError as e:
        print(f"Error: {e}")


def add_user_to_group_cmd(group_id, user_id):
    _, group_service, _, _ = build_services()
    group_service.add_user_to_group(group_id, user_id)
    print(f"User {user_id} added to group {group_id}")


def list_users_cmd():
    user_service, _, _, _ = build_services()
    users = user_service.list_users()

    print("ID   Name")
    for u in users:
        print(f"{u.id}   {u.name}")


def list_groups_cmd():
    _, group_service, _, _ = build_services()
    groups = group_service.list_group()

    print("ID   Name")
    for g in groups:
        print(f"{g.id}   {g.name}")


def get_user_id_by_name(user_service, name):
    users = user_service.list_users()
    for user in users:
        if user.name == name:
            return user.id
    raise ValueError(f"User '{name}' not found")


def get_group_id_by_name(group_service, name):
    groups = group_service.list_group()
    for group in groups:
        if group.name == name:
            return group.id
    raise ValueError(f"Group '{name}' not found")


async def main():
    asyncio.create_task(simulate_notifications())

    parser = argparse.ArgumentParser(description="Smart Group Expense Manager")
    subparsers = parser.add_subparsers(dest="command")

    # list-users
    subparsers.add_parser("list-users")

    # list-groups
    subparsers.add_parser("list-groups")

    balance_parser = subparsers.add_parser(
        "show-balances", help="Show balances for a group"
    )
    balance_parser.add_argument("--group", required=True, help="Group name")

    # create-user
    create_user_parser = subparsers.add_parser("create-user")
    create_user_parser.add_argument("--name", required=True)

    # create-group
    create_group_parser = subparsers.add_parser("create-group")
    create_group_parser.add_argument("--name", required=True)

    parser_list_members = subparsers.add_parser(
        "list-group-members", help="List users in a group"
    )
    parser_list_members.add_argument("--group", required=True)

    # add-user-to-group
    add_member_parser = subparsers.add_parser("add-user-to-group")
    add_member_parser.add_argument("--group", required=True)
    add_member_parser.add_argument("--user", required=True)

    # add-expense
    add_expense_parser = subparsers.add_parser("add-expense")
    add_expense_parser.add_argument("--group", required=True)
    add_expense_parser.add_argument("--paid-by", required=True)
    add_expense_parser.add_argument("--amount", type=float, required=True)
    add_expense_parser.add_argument("--users", required=True)
    add_expense_parser.add_argument("--desc", required=True)

    add_expense_parser.add_argument(
        "--split-type", choices=["equal", "custom", "percentage"], default="equal"
    )

    add_expense_parser.add_argument("--custom-splits", help="user:amount,user:amount")

    add_expense_parser.add_argument("--percentages", help="user:percent,user:percent")

    args = parser.parse_args()

    if args.command == "create-user":
        try:
            create_user_cmd(args.name)
        except ValueError as e:
            print(f"Error: {e}")
            return

    elif args.command == "create-group":
        create_group_cmd(args.name)

    elif args.command == "add-user-to-group":
        user_service, group_service, _, _ = build_services()

        group = group_service.get_group_by_name(args.group)
        user = user_service.get_user_by_name(args.user)

        added = group_service.add_user_to_group(group.id, user.id)

        if added:
            print(f"{user.name} added to {group.name}")
        else:
            print(f"{user.name} is already in {group.name}")

    elif args.command == "add-expense":
        user_service, group_service, expense_service, _ = build_services()

        split_type = args.split_type.lower()
        print("DEBUG split_type =", split_type)
        custom_splits = None

        # VALIDATION FOR SPLIT TYPES
        if split_type == "custom" and not args.custom_splits:
            raise ValueError("--custom-splits is required when split-type is custom")

        if split_type == "percentage" and not args.percentages:
            raise ValueError("--percentages is required when split-type is percentage")

        group = group_service.get_group_by_name(args.group)
        paid_by = user_service.get_user_by_name(args.paid_by)

        user_names = args.users.split(",")
        user_ids = []

        for name in user_names:
            user = user_service.get_user_by_name(name)
            user_ids.append(user.id)

        if split_type == "custom":
            custom_splits = {}
            entries = args.custom_splits.split(",")

            for entry in entries:
                entry = entry.strip()

                parts = entry.split(":")
                if len(parts) != 2:
                    raise ValueError(
                        "Invalid --custom-splits format. Use user:amount,user:amount"
                    )

                name, amount = parts
                user = user_service.get_user_by_name(name.strip())
                custom_splits[user.id] = float(amount)

        elif split_type == "percentage":
            custom_splits = {}
            entries = args.percentages.split(",")

            for entry in entries:
                name, percent = entry.split(":")
                user = user_service.get_user_by_name(name)
                custom_splits[user.id] = float(percent)

        expense_service.add_expense(
            group_id=group.id,
            amount=args.amount,
            paid_by=paid_by.id,
            user_ids=user_ids,
            split_type=split_type,
            custom_splits=custom_splits,
            description=args.desc,
        )
        await notification_queue.put(
            f"New expense added in group {group.name}: {args.desc} ({args.amount})"
        )

        print(f"Expense added to {group.name}")

    elif args.command == "list-group-members":
        _, group_service, _, _ = build_services()

        members = group_service.list_group_members(args.group)

        print(f"Group: {args.group}")
        for member in members:
            print(f"- {member['name']}")

    elif args.command == "show-balances":
        user_service, group_service, expense_service, balance_service = build_services()

        group = group_service.get_group_by_name(args.group)
        balances = balance_service.show_balances(args.group)

        print("User\tBalance")

        for user_id, balance in balances.items():
            user = user_service.get_user(user_id)
            print(f"{user.name}\t{balance}")

        settlements = balance_service.generate_settlement(group.id)
        if settlements:
            print("\nSettlement Suggestions:")
            for debtor_id, creditor_id, amount in settlements:
                debtor = user_service.get_user(debtor_id)
                creditor = user_service.get_user(creditor_id)
                print(f"{debtor.name} pays {creditor.name} {amount:.2f}")
        else:
            print("\nNo settlements needed")

    elif args.command == "list-users":
        list_users_cmd()

    elif args.command == "list-groups":
        list_groups_cmd()

    else:
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())
