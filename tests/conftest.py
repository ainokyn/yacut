import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv
from mixer.backend.flask import mixer as _mixer

from yacut import yacut

load_dotenv()

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
sys.path.append(str(BASE_DIR))


try:
    from yacut import db
    from yacut.models import URL_map
except NameError:
    raise AssertionError(
        'Не обнаружен объект приложения. Создайте экземпляр класса Flask и назовите его app.',
    )
except ImportError as exc:
    if any(obj in exc.name for obj in ['models', 'URL_map']):
        raise AssertionError('В файле models не найдена модель URL_map')
    raise AssertionError('Не обнаружен объект класса SQLAlchemy. Создайте его и назовите db.')


@pytest.fixture
def default_app():
    with yacut.app_context():
        yield yacut


@pytest.fixture
def _app(tmp_path):
    db_path = tmp_path / 'test_db.sqlite3'
    db_uri = 'sqlite:///' + str(db_path)
    yacut.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': db_uri,
        'WTF_CSRF_ENABLED': False,
    })
    with yacut.app_context():
        db.create_all()
    yield yacut
    db.drop_all()
    db.session.close()
    db_path.unlink()


@pytest.fixture
def client(_app):
    return _app.test_client()


@pytest.fixture
def cli_runner():
    return yacut.test_cli_runner()


@pytest.fixture
def mixer():
    _mixer.init_app(yacut)
    return _mixer


@pytest.fixture
def short_python_url(mixer):
    return mixer.blend(URL_map, original='https://www.python.org', short='py')
