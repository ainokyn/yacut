import re

from flask import jsonify, request

from . import app, db
from .constant import pattern, pattern_2
from .error_handlers import InvalidAPI
from .models import URL_map
from .views import get_unique_short_id


@app.route('/api/id/', methods=['POST'])
def create_id():
    data = request.get_json()
    try:
        data = request.get_json()
        if not data:
            raise InvalidAPI('Отсутствует тело запроса')
    except Exception:
        return jsonify({"message": 'Отсутствует тело запроса'}), 400
    original = data['url']
    if not original:
        raise InvalidAPI('\"url\" является обязательным полем!')
    if not re.match(pattern, data['url']):
        return jsonify({"message": 'Недопустимое значение \"url\"'
                        }), 400
    if 'custom_id' not in data or data['custom_id'] == "" or data['custom_id'] is None:
        data['custom_id'] = get_unique_short_id()
    if 'custom_id' in data:
        short = data['custom_id']
        if (len(data['custom_id']) > 16) or (not
                                             re.match(
                                                 pattern_2, data['custom_id'])
                                             ):
            return jsonify({'message':
                            'Указано недопустимое имя для короткой ссылки'
                            }), 400
        if URL_map.query.filter_by(short=data['custom_id']
                                   ).first() is not None:
            return jsonify({'message': f'Имя "{short}" уже занято.'}), 400
    url_obj = URL_map(original=original, short=short)
    db.session.add(url_obj)
    db.session.commit()
    link = request.host_url + short
    return jsonify({'url': original,
                    'short_link': link}), 201


@app.route('/api/id/<short_id>/', methods=['GET'])
def get_url(short_id):
    obj = URL_map.query.filter_by(short=short_id).first()
    if obj:
        return jsonify({'url': obj.original}), 200
    return jsonify({'message': 'Указанный id не найден'}), 404
