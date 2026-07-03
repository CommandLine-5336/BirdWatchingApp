from flask import Blueprint, render_template, request, session, redirect, url_for
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def index():
    error = None
    if request.method == 'POST':
        form_username = request.form.get('username')
        password = request.form.get('password')
        action = request.form.get('action')
       
        if not form_username or not password:
            return render_template('auth.html', error="Both fields are required!")
       
        if action == 'register':
            return _handle_registration(form_username, password)
        
        elif action == "login":
            return _handle_login(form_username, password)
        
    return render_template('auth.html', error=error)

def _handle_registration(form_username, password):
            existing_user = User.query.filter_by(login=form_username).first()
            if not existing_user:
                hash_pw = generate_password_hash(password)
                new_user = User(login=form_username, password=hash_pw)
                db.session.add(new_user)
                db.session.commit()
                
                session['user_id'] = new_user.id
                session['username'] = new_user.login
                return redirect(url_for('feed.show_feed'))
            else:
                return render_template('auth.html', error="Username already taken!")
            
def _handle_login(form_username, password):
            user = User.query.filter_by(login=form_username).first()
            if user and check_password_hash(user.password, password):
                session['user_id'] = user.id
                session['username'] = user.login
                return redirect(url_for('feed.show_feed'))
            else: 
                return render_template('auth.html', error="Invalid username or password")

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.index'))