from flask import jsonify, request

from . import app, db
from .error_handlers import InvalidAPIUsage
from .models import URL_map
from .views import get_unique_short_id


@app.route('/api/id/', methods=['POST'])
def create_id():
    data = request.get_json()
    if not data:
        raise Exception('Отсутствует тело запроса', 400)
    original = data['url']
    if 'url' not in data:
        raise Exception(f"{original} является обязательным полем!", 400)
    if 'custom_id' not in data or data['custom_id'] is None or data['custom_id'] == "":
        short = get_unique_short_id()
    if 'custom_id' in data:
        short = data['custom_id']
        if len(data['custom_id']) > 16:
            return jsonify({'message': 'Указано недопустимое имя для короткой ссылки'}), 400
        if URL_map.query.filter_by(short=data['custom_id']).first() is not None:
            raise InvalidAPIUsage(f'Имя "{short}" уже занято.', 400)
    url_obj = URL_map(original=original, short=short)
    db.session.add(url_obj)
    db.session.commit()
    return jsonify({'create_id': url_obj.to_dict()}), 201


@app.route('/api/id/<short_id>/', methods=['GET'])
def get_url(short_id):
    obj = URL_map.query.filter_by(short=short_id).first()
    if obj:
        return jsonify({'url': obj.original}), 200
    raise InvalidAPIUsage('Указанный id не найден', 404)
