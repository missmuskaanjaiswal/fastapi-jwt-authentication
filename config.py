import os

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "development-secret-key"
)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
