"""configuration file for pytest"""
import pytest
from fixtures.info import info

def pytest_namespace():
    return {
        'users': [],
    }
