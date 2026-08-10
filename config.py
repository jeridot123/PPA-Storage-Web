import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

LINES = [
    {"id": "1A", "capacity": 9, "allow_import": True},
    {"id": "2A", "capacity": 9, "allow_import": True},
    {"id": "1", "capacity": 9, "allow_import": True},
    {"id": "2", "capacity": 9, "allow_import": True},
    {"id": "3", "capacity": 9, "allow_import": True},
    {"id": "4", "capacity": 9, "allow_import": True},
    {"id": "5", "capacity": 10, "allow_import": False},
    {"id": "6", "capacity": 10, "allow_import": False},
    {"id": "7", "capacity": 10, "allow_import": False},
    {"id": "8", "capacity": 10, "allow_import": False},
    {"id": "9", "capacity": 10, "allow_import": False},
    {"id": "10", "capacity": 10, "allow_import": False},
    {"id": "11", "capacity": 10, "allow_import": False},
    {"id": "12", "capacity": 10, "allow_import": False},
    {"id": "13", "capacity": 10, "allow_import": False},
    {"id": "14", "capacity": 10, "allow_import": False},
    {"id": "15", "capacity": 10, "allow_import": False},
]

IMPORT_PREFIX = "IMP"

NEAREST_LINES = {
    "1A": ["2A", "1", "2", "3", "4"],
    "2A": ["1A", "1", "2", "3", "4"],

    "1": ["2", "3", "4", "5"],
    "2": ["1", "3", "4", "5"],
    "3": ["2", "4", "5", "6"],
    "4": ["3", "5", "6", "7"],

    "5": ["6", "4", "7", "3", "8"],
    "6": ["5", "7", "4", "8", "3"],
    "7": ["6", "8", "5", "9", "4"],
    "8": ["7", "9", "6", "10", "5"],
    "9": ["8", "10", "7", "11", "6"],
    "10": ["9", "11", "8", "12", "7"],
    "11": ["10", "12", "9", "13", "8"],
    "12": ["11", "13", "10", "14", "9"],
    "13": ["12", "14", "11", "15", "10"],
    "14": ["13", "15", "12", "11"],
    "15": ["14", "13", "12"]
}