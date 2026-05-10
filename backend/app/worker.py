import time

from .db import SessionLocal, init_db
from .qos import process_one
from .seed import seed_database


def main() -> None:
    init_db()
    with SessionLocal() as db:
        seed_database(db)
    while True:
        with SessionLocal() as db:
            job = process_one(db)
        if not job:
            time.sleep(1.5)


if __name__ == "__main__":
    main()
