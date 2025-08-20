from fastapi import Depends, HTTPException, status
from .utils import oauth2
from .roles import Role

def require_role(*allowed_roles):
  def role_checker(current_user = Depends(oauth2.get_current_user)):
    if current_user.role not in allowed_roles:
      raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access Denied")
    return current_user
  return role_checker

# Usage
admin_required = require_role(Role.ADMIN)
owner_or_admin_required = require_role(Role.OWNER, Role.ADMIN)
user_or_owner_required = require_role(Role.USER, Role.OWNER)


# PERMISSIONS = {
#   Role.USER: {
#     "users": [""],
#     "venues": ["read_all"],
#     "bookings":["create", "read_own",  "update_own", "delete_own"]

#   },
#   Role.OWNER: {
#     "users": [""],
#     "venues": ["read_all", "read_own", "create", "update_own", "delete_own"],
#     "bookings":["create", "read_own", "update_own", "delete_own"]

#   },
#   Role.ADMIN: {
#     "users": ["create", "read_all", "update_all", "delete_all", ],
#     "venues": ["create", "read_all", "update_all", "delete_all", ],
#     "bookings":["create", "read_all", "update_all", "delete_all", ]
#   }
# }

