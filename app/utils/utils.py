from passlib.context import CryptContext

pwd_context=CryptContext(schemes=['bcrypt'], deprecated="auto")

# Function to hash password [once hashed cannot be unhashed]
def hash(password: str):
  return pwd_context.hash(password)

# Password Verification [Compares Plain Password to Hashed Password after hashing]
def verify(plain_password, hashed_password):
  return pwd_context.verify(plain_password, hashed_password)