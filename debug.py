# debug.py
from constants import LOGIN_ENDPOINT, REGISTER_ENDPOINT
print(f"LOGIN_ENDPOINT = {LOGIN_ENDPOINT}")
print(f"REGISTER_ENDPOINT = {REGISTER_ENDPOINT}")

from clients.AuthAPI import AuthAPI
print(f"В AuthAPI: LOGIN_ENDPOINT = {AuthAPI.L if hasattr(AuthAPI, 'LOGIN_ENDPOINT') else 'не определен'}")