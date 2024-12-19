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
        ' WHERE EXISTS (SELECT * FROM user_groups WHERE groups.id = user_groups.groupid AND user.id = user_groups.userid)'
        ' WHERE user.id = ?'
        (g.user['id'],)
    ).fetchall()
    return render_template('board/index.html', groups=groups)
