from typing import Optional

from .db import get_connection, password_hash


def authenticate(login: str, password: str) -> Optional[dict]:
    with get_connection() as conn:
        row = conn.execute(
            '''
            SELECT u.user_id, u.login, u.last_name, u.first_name, u.patronymic,
                   r.role_code, r.role_name
            FROM users u
            JOIN roles r ON r.role_id = u.role_id
            WHERE u.login = ? AND u.password_hash = ? AND u.is_active = 1
            ''',
            (login.strip(), password_hash(password)),
        ).fetchone()
        return dict(row) if row else None


def guest_user() -> dict:
    return {
        'user_id': None,
        'login': 'guest',
        'last_name': 'Гость',
        'first_name': '',
        'patronymic': '',
        'role_code': 'guest',
        'role_name': 'Гость',
    }


def full_name(user: dict) -> str:
    parts = [user.get('last_name', ''), user.get('first_name', ''), user.get('patronymic', '')]
    return ' '.join(part for part in parts if part).strip() or user.get('role_name', 'Пользователь')
