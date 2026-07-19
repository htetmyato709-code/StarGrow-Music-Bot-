# ==========================
# database.py
# ==========================

import os
import json
from config import USERS_DB, GROUPS_DB


def _create_file(path):
    folder = os.path.dirname(path)

    if folder and not os.path.exists(folder):
        os.makedirs(folder)

    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump([], f)


_create_file(USERS_DB)
_create_file(GROUPS_DB)


def load_users():
    with open(USERS_DB, "r", encoding="utf-8") as f:
        return json.load(f)


def save_users(users):
    with open(USERS_DB, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4)


def add_user(user_id):
    users = load_users()

    if user_id not in users:
        users.append(user_id)
        save_users(users)


def remove_user(user_id):
    users = load_users()

    if user_id in users:
        users.remove(user_id)
        save_users(users)


def load_groups():
    with open(GROUPS_DB, "r", encoding="utf-8") as f:
        return json.load(f)


def save_groups(groups):
    with open(GROUPS_DB, "w", encoding="utf-8") as f:
        json.dump(groups, f, indent=4)


def add_group(chat_id):
    groups = load_groups()

    if chat_id not in groups:
        groups.append(chat_id)
        save_groups(groups)


def remove_group(chat_id):
    groups = load_groups()

    if chat_id in groups:
        groups.remove(chat_id)
        save_groups(groups)
