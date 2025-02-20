from enum import Enum

class Role(Enum):
    ADMIN = "ADMIN"
    MANAGER = "PROJECT_MANAGER"
    EMPLOYEE = "EMPLOYEE"

class User:
    def __init__(self, eid, first_name, last_name, password, role: Role):
        self.eid = eid
        self.first_name = first_name
        self.last_name = last_name
        self.password = password
        self.role = role

    def to_dict(self):
        return {
            "eid": self.eid,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "role": self.role.value
        }
