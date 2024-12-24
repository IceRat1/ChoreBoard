import functools

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
        'SELECT g.id, g.title, g.created, u.username FROM user_groups ug'
        ' JOIN groups g ON ug.groupid = g.id'
        ' JOIN user u ON g.author_id = u.id'
        ' WHERE ug.userid = ?',
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

def get_group(id):
    db = get_db()
    group = db.execute(
        'SELECT g.id, title, created'
        ' FROM groups g'
        ' WHERE g.id = ?',
        (id,)
    ).fetchone()

    if group is None:
        abort(404, f"Group id {id} doesn't exist.")
    
    ug = db.execute(
        'SELECT * FROM user_groups ug'
        ' WHERE ug.userid = ? AND ug.groupid = ?',
        (g.user['id'], id)
    ).fetchone()

    if ug is None:
        abort(403)
    
    return group

@bp.route('/<int:id>/home', methods=('GET','POST'))
@login_required
def home(id):
    db = get_db()
    group = get_group(id)
    chores = db.execute(
        'SELECT c.id, c.title, c.created, c.reward, u.username FROM chores c'
        ' JOIN user u ON c.author_id = u.id'
        ' WHERE c.user_id = ? AND c.group_id = ?',
        (g.user['id'], id)
    ).fetchall()
    members = db.execute(
        'SELECT u.id, u.username FROM user_groups ug'
        ' JOIN user u ON ug.userid = u.id'
        ' JOIN groups g ON ug.groupid = g.id'
        ' WHERE ug.groupid = ?',
        (id,)
    ).fetchall()


    return render_template('board/home.html', group=group, chores=chores, members=members)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_group(id)
    db = get_db()
    db.execute('DELETE FROM groups WHERE id = ?', (id,))
    db.execute('DELETE FROM user_groups WHERE user_groups.groupid = ?', (id,))
    db.commit()
    return redirect(url_for('board.index'))

@bp.route('/<int:id>/add', methods=('GET', 'POST'))
@login_required
def add(id):
    if request.method == 'POST':
        db = get_db()
        userid = request.form['userid']
        error = None

        if not userid:
            error = "Please enter an id."
        elif db.execute('SELECT * from user u WHERE u.id = ?', (userid,)).fetchone() is None:
            error = "That user doesn't exist."
        else:
            try:
                db.execute(
                    "INSERT INTO user_groups (userid, groupid) VALUES (?, ?)",
                    (userid, id)
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {userid} is already in the group."
            else:

                return redirect(url_for("board.home", id=id))
        flash(error)
    
    return render_template('board/add.html')

@bp.route('/<int:id>/requestboard', methods=('GET', 'POST'))
@login_required
def requestboard(id):
    db = get_db()
    requests = db.execute(
        'SELECT c.id, c.title, c.created, c.author_id, c.group_id, c.reward, u.username FROM chores c'
        ' JOIN user u ON c.author_id = u.id'
        ' WHERE c.user_id IS NULL AND c.group_id = ?',
        (id,)
    ).fetchall()
    
    return render_template('board/requestboard.html', id=id, requests=requests)

@bp.route('/<int:id>/requestboard/new', methods=('GET', 'POST'))
@login_required
def newrequest(id):
    if request.method == 'POST':
        title = request.form['title']
        reward = request.form['reward']
        error = None

        if not title:
            error = 'Title is required.'
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            if not reward:
                db.execute(
                'INSERT INTO chores (title, author_id, group_id)'
                ' VALUES (?, ?, ?)',
                (title, g.user['id'], id)
                )
            else:
                db.execute(
                'INSERT INTO chores (title, author_id, group_id, reward)'
                ' VALUES (?, ?, ?, ?)',
                (title, g.user['id'], id, reward)
                )

            db.commit()
            return redirect(url_for('board.requestboard', id=id))
    return render_template('board/addrequest.html')

def get_chore(id):
    db = get_db()
    chore = db.execute(
        'SELECT *'
        ' FROM chores c'
        ' WHERE c.id = ?',
        (id,)
    ).fetchone()

    if chore is None:
        abort(404, f"Chore id {id} doesn't exist.")
    
    return chore

@bp.route('/<int:groupid>/requestboard/<int:choreid>/update', methods=('GET', 'POST'))
@login_required
def updaterequest(groupid, choreid):
    chore = get_chore(choreid)
    if request.method == 'POST':
        title = request.form['title']
        reward = request.form['reward']
        error = None

        if not title:
            error = 'Title is required.'
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            if not reward:
                db.execute(
                'UPDATE chores SET title = ?'
                ' WHERE id = ?',
                (title, choreid)
                )
            else:
                db.execute(
                'UPDATE chores SET title = ?, reward = ?'
                ' WHERE id = ?',
                (title, reward, choreid)
                )

            db.commit()
            return redirect(url_for('board.requestboard', id=groupid))
    return render_template('board/updaterequest.html', groupid=groupid, chore=chore)

@bp.route('/<int:groupid>/requestboard/<int:choreid>/delete', methods=('POST',))
@login_required
def deleterequest(groupid, choreid):
    get_chore(choreid)
    db = get_db()
    db.execute('DELETE FROM chores WHERE id = ?', (choreid,))
    db.commit()
    return redirect(url_for('board.requestboard', id=groupid))


@bp.route('/<int:groupid>/requestboard/<int:choreid>/accept', methods=('GET','POST'))
@login_required
def acceptrequest(groupid, choreid):
    get_chore(choreid)
    db = get_db()
    db.execute('UPDATE chores SET user_id = ? WHERE id = ?', (g.user['id'], choreid))
    db.commit()
    return redirect(url_for('board.requestboard', id=groupid))