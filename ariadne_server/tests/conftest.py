"""configuration file for pytest"""
import pytest
from tests.fixtures.info import info

def pytest_namespace():
    return {
        'users': [],
    }
