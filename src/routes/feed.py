import os
from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from models import db, Post, Like
from services.storage import upload_to_seaweed, get_file_url

feed_bp = Blueprint('feed', __name__) 

@feed_bp.route('/')
def show_feed():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    birds_data = []
    user_id = session.get('user_id')
    for post in posts:
        likes_count = post.likes.count()
        is_liked = False
        if user_id:
            is_liked = Like.query.filter_by(user_id=user_id, post_id=post.id).first() is not None
        file_url = get_file_url(post.image_filename)

        birds_data.append({
            "id": post.id,
            "name": post.title,
            "desc": post.description,
            "loc": post.location,
            "img": file_url,
            "likes_count": likes_count,
            "is_liked": is_liked
        })

    if not birds_data:
        birds_data = [{"id": 0, "name": "No posts yet", "desc": "Sign in and upload", "loc": "Nowhere", "img": "", "likes_count": 0, "is_liked": False}]
    return render_template('feed.html', birds_data=birds_data, username=session.get('login', 'User'))

@feed_bp.route('/like/<int:post_id>', methods=['POST'])
def toggle_like(post_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    user_id = session['user_id']
    existing_like = Like.query.filter_by(user_id=user_id, post_id=post_id).first()

    if existing_like:
        db.session.delete(existing_like)
        db.session.commit()
        action = 'unliked'
    else:
        new_like = Like(user_id=user_id, post_id=post_id)
        db.session.add(new_like)
        db.session.commit()
        action = 'liked'

    likes_count = Like.query.filter_by(post_id=post_id).count()
    return jsonify({'action': action, 'likes_count': likes_count})

@feed_bp.route('/upload', methods=['POST'])
def upload():
    if 'user_id' not in session:
        return redirect(url_for('auth.index'))

    file = request.files.get('photo')
    object_key = None
    if file and file.filename != '':
        file.stream.seek(0)
        object_key = upload_to_seaweed(file.stream, file.filename)

    new_post = Post(
        title=request.form.get('title'),
        location=request.form.get('location'),
        description=request.form.get('description'),
        image_filename=object_key,
        user_id=session['user_id']
    )
    db.session.add(new_post)
    db.session.commit()

    return redirect(url_for('feed.show_feed'))
#