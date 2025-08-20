from enum import Enum

# Defined Roles (ENUM gives clarity, safety and consistency when dealing with a fixed set of roles)
class Role(str, Enum):
  ADMIN= "admin"
  USER= "user"
  OWNER= "owner"