import sqlite3 as sql
import streamlit as st

from pathlib import Path

from contextlib import contextmanager


def _try_get_db_config(cfg) -> dict:
    accepted_acronyms = ['db',
                         'database']

    for section, v in cfg.items():
        if section in accepted_acronyms:
            return v
        elif isinstance(v, dict):
            result = _try_get_db_config(v)
            if result:
                return result

    return {}

class ColumnExistError(Exception): pass

class Database:
    def __init__(self, table_name, cfg):
        self.cfg = _try_get_db_config(cfg)
        assert self.cfg, "Cannot find database configuration."

        self.path = self.cfg.get('path')

        self.table_name = table_name
        self._init_db()

    @contextmanager
    def _connect(self):
        conn = sql.connect(self.path)
        conn.row_factory = sql.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_db(self):
        if not self.table_name.isidentifier():
            raise ValueError(f"Invalid table name: {self.table_name}")

        with self._connect() as conn:
            conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    id INTEGER PRIMARY KEY
                )
            """)

    def _get_columns(self):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({self.table_name})")
            
            columns = [row[1] for row in cursor.fetchall()]

            return columns

    def _new_column(self, column_name, data_type, constrains):
        if column_name in self._get_columns():
            raise ColumnExistError \
                ("Failed to append new column: duplicate column name")
        
        with self._connect() as conn:
            conn.execute(f"ALTER TABLE {self.table_name} ADD COLUMN")

class UserDB(Database):
    def __init__(self, cfg):
        super().__init__('users', cfg)
        
        required_columns = {
            # identity
            "username":     ("TEXT", "NOT NULL UNIQUE"),
            "display_name": ("TEXT", "NOT NULL DEFAULT ''"),
            "email":        ("TEXT", "UNIQUE"),
            "whatsapp":     ("TEXT", "UNIQUE"),

            # auth -> 
            # "salt":         ("BLOB", "NOT NULL"),
            # "pw_hash":      ("BLOB", "NOT NULL"),

            # matching
            # "age":          ("INTEGER", ""),
            # "affiliation":  ("TEXT", "NOT NULL"),

            # state
            "is_active":    ("INTEGER", "NOT NULL DEFAULT 1"),
            # "is_admin":     ()"INTEGER", "NOT NULL DEFAULT 0"),
            "created_at":   ("TEXT", "NOT NULL DEFAULT CURRENT_TIMESTAMP"),
            # "last_login":   ("TEXT", ""),
        }

        for name, v in required_columns:
            try:
                self._new_column(name, *v)
            except: pass


    def get(self, user_id):
        pass

class CompetitionDB(Database):
    def __init__(self, cfg):
        super().__init__('competitions', cfg)

class ParticipantDB(Database):
    def __init__(self, cfg):
        super().__init__('participants', cfg)

class SkillDB(Database):
    def __init__(self, cfg):
        super().__init__('skills', cfg)

class TimeAvailabilityDB(Database):
    def __init__(self, cfg):
        super().__init__('availables', cfg)

if __name__ == "__main__":
    pass