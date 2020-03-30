import pytest
from classes.user import User

@pytest.fixture(scope='session')
async def dummy_user():
    u = await User.create(
        id='de58dd1453a64fe4be9e',
        username='37ebb3ba1453f985e785',
        password_hash=ARGON.hash('055071c9b1c48946ceae'),
        role='USER'
    )
    u.password = '055071c9b1c48946ceae'
    return u

@pytest.fixture(scope='session')
async def dummy_admin():
    u = await User.create(
        id='4a3ceb040a3d81ead4af',
        username='aa4a3863d8a09867a53c',
        password_hash=ARGON.hash('530b095674764823ace8'),
        role='ADMIN'
    )
    u.password('530b095674764823ace8')
    return u
