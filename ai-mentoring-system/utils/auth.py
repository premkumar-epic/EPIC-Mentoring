"""
Authentication utilities - Role-based access control
"""
from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
    """Decorator to require user login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'info')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def require_role(*roles):
    """Decorator to require specific user role(s)"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'role' not in session:
                flash('Please login to access this page', 'info')
                return redirect(url_for('login'))

            if session.get('role') not in roles:
                flash('You do not have permission to access this page', 'error')
                return redirect(url_for('index'))

            return f(*args, **kwargs)
        return decorated_function
    return decorator

