from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import logging
import time
import sys
import os
from logging.handlers import RotatingFileHandler
from src.config import Config



def register_middleware(app: FastAPI):

    # need to cumunicate with other origin
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # need for oauth
    app.add_middleware(
        SessionMiddleware,
        secret_key=Config.SECRET_KEY,
        https_only=False,            # Set to True only in production over HTTPS
        same_site="lax"              # Allows cookies to persist across redirects
    )