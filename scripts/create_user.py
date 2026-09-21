from getpass import getpass

from sqlalchemy import select

from app.database import SessionLocal
from app.models.user import User
from app.security import hash_password


def main():
    email = input("Email: ").strip().lower()
    password = getpass("Contraseña: ")
    password_confirmation = getpass("Repetir contraseña: ")

    if password != password_confirmation:
        raise ValueError("Las contraseñas no coinciden.")

    if len(password) < 10:
        raise ValueError("La contraseña debe tener al menos 10 caracteres.")

    with SessionLocal() as db:
        existing_user = db.scalar(
            select(User).where(User.email == email)
        )

        if existing_user:
            raise ValueError("Ya existe un usuario con ese email.")

        user = User(
            email=email,
            password_hash=hash_password(password),
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        print(f"Usuario creado correctamente. ID: {user.id}")


if __name__ == "__main__":
    main()