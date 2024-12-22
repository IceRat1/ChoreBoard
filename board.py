from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from werkzeug.exceptions import abort

from choreboard.auth import login_required
from choreboard.db import get_db

bp = Blueprint('board', __name__)

@bp.route('/')
@login_required
def index():
    db = get_db()
    groups = db.execute(
        'SELECT * FROM groups'
        ' WHERE EXISTS (SELECT userid, groupid' 
        ' FROM user_groups'
        ' WHERE (user_groups.groupid = groups.id AND user_groups.userid = ?))',
        (g.user['id'],)
    ).fetchall()
    return render_template('board/index.html', groups=groups)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title'] 
        error = None

        if not title:
            error = 'Title is required.'
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO groups (title, author_id)'
                ' VALUES (?, ?)',
                (title, g.user['id'])
            )
            db.commit()
            db.execute(
                'INSERT INTO user_groups (userid, groupid)'
                ' VALUES (?, (SELECT id'
                                ' FROM groups'
                                ' ORDER BY created DESC'
                                ' LIMIT 1) )',
                (g.user['id'],)
            )
            db.commit()
            return redirect(url_for('board.index'))
    return render_template('board/create.html')
