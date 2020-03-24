"""init global password hasher"""
from argon2 import PasswordHasher

ARGON = PasswordHasher()
