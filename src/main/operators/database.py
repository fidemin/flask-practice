import random

from sqlalchemy import Table, Column, Integer, MetaData, Text, Date, text

from src.main import db
from src.main.operators.operator import Operator


class CreateLargeTableOperator(Operator):
    def __init__(self, *, table_name, row_count=100000):
        self.table_name = table_name
        self.row_count = row_count

    def execute(self):
        db.session.execute(text(f"DROP TABLE IF EXISTS temp.{self.table_name}"))
        db.session.commit()

        table = Table(
            self.table_name,
            MetaData(),
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("username", Text, nullable=False),
            Column("description", Text, nullable=False),
            Column("login_date", Date, nullable=False),
            schema="temp",
        )

        table.create(db.engine)

        for rows in self._chunks(self.row_count, 10000):
            db.session.execute(table.insert(), rows)
            db.session.commit()

    def _chunks(self, row_count, chunk_size: int):
        names = ['user1', 'user2', 'user3', 'user4', 'user5', 'user6', 'user7', 'user8', 'user9', 'user10']

        descriptions = [
            "abcde1234_" * 20,
            "thisis_" * 20,
            "hello_" * 20,
        ]

        login_dates = [
            '2023-01-01',
            '2023-01-02',
            '2023-01-03',
        ]
        count = 0

        while count < row_count:
            name_idx = random.randint(0, len(names) - 1)
            name = names[name_idx]
            desc_idx = random.randint(0, len(descriptions) - 1)
            description = descriptions[desc_idx]
            login_date_idx = random.randint(0, len(login_dates) - 1)
            login_date = login_dates[login_date_idx]

            rows = []
            for _ in range(chunk_size):
                row = {
                    "username": name,
                    "description": description,
                    "login_date": login_date,
                }

                rows.append(row)
                count += 1

                if count >= row_count:
                    break
            yield rows
