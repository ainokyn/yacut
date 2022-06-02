from flask import jsonify, request

from . import app, db
from .error_handlers import InvalidAPIUsage
from .models import URL_map
from .views import get_long, get_unique_short_id


@app.route('/api/id/', methods=['POST'])
def create_id():
    data = request.get_json()
    if not data:
        raise InvalidAPIUsage('Отсутствует тело запроса')
    if 'url' not in data:
        raise InvalidAPIUsage(f"{data['url']} является обязательным полем!")
    if len(data['custom_id']) > 16:
        raise InvalidAPIUsage('Указано недопустимое имя для короткой ссылки')
    if 'custom_id' not in data:
        data['custom_id'] = get_unique_short_id()
    if 'custom_id' in data and URL_map.query.filter_by(short=data['custom_id']).first() is not None:
        raise InvalidAPIUsage('Указано недопустимое имя для короткой ссылки')
    original = data['url']
    short = request.host_url + data['custom_id']
    url_obj = URL_map(original=original, short=short)
    db.session.add(url_obj)
    db.session.commit()
    return jsonify({'create_id': url_obj.to_dict()}), 201


@app.route('/api/id/<short_id>/', methods=['GET'])
def get_url(short_id):
    long = get_long(short_id)
    if long:
        return jsonify({'url': long}), 200
    raise InvalidAPIUsage('Указанный id не найден')
