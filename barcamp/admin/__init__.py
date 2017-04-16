# coding: utf-8
from flask import Blueprint, render_template, abort, request, flash, redirect, url_for
from jinja2 import TemplateNotFound

from ..login_misc import check_admin, login_redirect
from ..models.pages import Pages, PageForm
from ..models.tiles import Tiles, TileForm
from ..barcamp import app

admin = Blueprint('admin', __name__)

@admin.before_request
def admin_login_required():
    if not check_admin():
        return login_redirect()


@admin.route('/')
def dashboard():
    return render_template('admin/dashboard.html')


@admin.route('/stranky/')
def page_list():
    pages = Pages(app.redis, app.config['YEAR'])
    return render_template(
        'admin/page_list.html',
        pages=pages.get_all()
    )


@admin.route('/stranky/odstranit/<uri>/')
def page_delete(uri):
    pages = Pages(app.redis, app.config['YEAR'])
    pages.delete(uri)
    flash(u'Stránka byla smazána', 'success')
    return redirect(url_for('admin.page_list'))


@admin.route(
    "/stranky/pridat/",
    methods=['GET', 'POST'],
    defaults={'uri': None})
@admin.route('/stranky/<uri>/', methods=['GET', 'POST'])
def page_edit(uri):
    pages = Pages(app.redis, app.config['YEAR'])
    page = {}
    if uri:
        data = pages.get(uri)
        if data:
            page = data

    if request.method == "POST":
        form = PageForm(request.form)
        if form.validate():
            page = pages.update(form.data)
            flash(u'Stránka byla uložena', 'success')
            return redirect(url_for('admin.page_edit', uri=page['uri']))
    else:
        form = PageForm(**page)
    return render_template(
        'admin/page_detail.html',
        form=form,
        page=page
    )

@admin.route('/boxiky/')
def tile_list():
    tiles = Tiles(app.redis, app.config['YEAR'])
    return render_template(
        'admin/tile_list.html',
        tiles=tiles.get_all()
    )


@admin.route('/boxiky/odstranit/<idx>/')
def tile_delete(idx):
    tiles = Tiles(app.redis, app.config['YEAR'])
    tiles.delete(idx)
    flash(u'Stránka byla smazána', 'success')
    return redirect(url_for('admin.tile_list'))


@admin.route(
    "/boxiky/pridat/",
    methods=['GET', 'POST'],
    defaults={'idx': None})
@admin.route('/boxiky/<idx>/', methods=['GET', 'POST'])
def tile_edit(idx):
    tiles = Tiles(app.redis, app.config['YEAR'])
    tile = {}
    if idx:
        data = tiles.get(idx)
        if data:
            tile = data

    if request.method == "POST":
        form = TileForm(request.form)
        if form.validate():
            data = form.data
            if idx:
                data['idx'] = idx

            tile = tiles.update(data)
            flash(u'Stránka byla uložena', 'success')
            return redirect(url_for('admin.tile_edit', idx=tile['idx']))
    else:
        form = TileForm(**tile)
    return render_template(
        'admin/tile_detail.html',
        form=form,
        tile=tile
    )