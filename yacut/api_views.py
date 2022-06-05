import re
from http import HTTPStatus

from flask import jsonify, request

from . import app, db
from .constant import pattern, pattern_2
from .error_handlers import APIError
from .models import URL_map
from .views import get_unique_short_id


@app.route('/api/id/', methods=['POST'])
def create_id():
    data = request.get_json()
    if not data:
        raise APIError('Отсутствует тело запроса')
    if 'url' not in data:
        raise APIError('\"url\" является обязательным полем!')
    if not re.match(pattern, data['url']):
        return jsonify({"message": 'Недопустимое значение \"url\"'
                        }), HTTPStatus.BAD_REQUEST
    if 'custom_id' not in data or data['custom_id'] == "" or data['custom_id'] is None:
        data['custom_id'] = get_unique_short_id()
    else:
        short = data['custom_id']
        if (len(data['custom_id']) > 16) or (not
                                             re.match(
                                                 pattern_2, data['custom_id'])
                                             ):
            return jsonify({'message':
                            'Указано недопустимое имя для короткой ссылки'
                            }), HTTPStatus.BAD_REQUEST
        if URL_map.query.filter_by(short=data['custom_id']
                                   ).first() is not None:
            return jsonify({'message':
                            f'Имя "{short}" уже занято.'
                            }), HTTPStatus.BAD_REQUEST
    url_obj = URL_map(original=data['url'], short=data['custom_id'])
    db.session.add(url_obj)
    db.session.commit()
    link = request.host_url + data['custom_id']
    return jsonify({'url': data['url'],
                    'short_link': link}), HTTPStatus.CREATED


@app.route('/api/id/<short_id>/', methods=['GET'])
def get_url(short_id):
    obj = URL_map.query.filter_by(short=short_id).first()
    if obj:
        return jsonify({'url': obj.original}), HTTPStatus.OK
    return jsonify({'message': 'Указанный id не найден'}), HTTPStatus.NOT_FOUND
