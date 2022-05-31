from flask import abort, flash, redirect, render_template, url_for, request
from . import app, db
from . forms import URLForm
from . models import URL_map
import secrets
import string
import re

pattern = re.compile(
        r'^(?:http|ftp)s?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?' 
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)


def get_unique_short_id():
    aphabet_and_nums = string.ascii_letters + string.digits
    short_id = ''.join(secrets.choice(
        aphabet_and_nums) for i in range(6))
    return(short_id)


@app.route('/', methods=['GET', 'POST'])
def index_view():
    form = URLForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            short = form.custom_id.data
            long = form.original_link.data
            if not re.match(pattern, long):
                flash('Длинная ссылка не URL!',
                      'error-message')
                return render_template('index.html', form=form)
            if not short:
                short = get_unique_short_id()
                flash('Ссылка сгенерирована автоматически!', 'gen-message')
            if URL_map.query.filter_by(short=short).first() is not None:
                flash('Такая коротка ссылка уже есть, попробуй снова!',
                      'error-message')
                return render_template('index.html', form=form)
            url = URL_map(
                original=form.original_link.data,
                short=short
            )
            db.session.add(url)
            db.session.commit()
            short_url = request.host_url + short
            flash('Твоя ссылка готова:',
                  'done-message')
            return render_template('index.html',
                                   short_url=short_url,
                                   form=form)
    return render_template('index.html', form=form)


@app.route('/<short>', methods=['GET'])
def short_url_view(short):
    obj = URL_map.query.filter_by(short=short).first()
    if obj:
        long = obj.original
        return redirect(long)
    abort(404)
