# coding: utf-8

"""
    Application and settings
"""

from flask import Flask


def create_app():
    return Flask(__name__)


app = create_app()
import views  # silence
import login  # silence
