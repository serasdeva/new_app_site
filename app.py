from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FileField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length
from wtforms import ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import json

import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)  # Generate a random secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///photostudio.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    duration = db.Column(db.String(50))
    price = db.Column(db.String(50))
    image_filename = db.Column(db.String(200))

class PortfolioItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    image_filename = db.Column(db.String(200), nullable=False)
    category = db.relationship('Category', backref=db.backref('portfolio_items', lazy=True))

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    category = db.relationship('Category', backref=db.backref('requests', lazy=True))

# Forms
class QuickRequestForm(FlaskForm):
    client_name = StringField('Ваше имя', validators=[DataRequired(), Length(min=2, max=100)])
    phone = StringField('Телефон', validators=[DataRequired(), Length(min=5, max=20)])
    category_id = SelectField('Тематика', coerce=int, validators=[DataRequired()])

class ContactForm(FlaskForm):
    client_name = StringField('Ваше имя', validators=[DataRequired(), Length(min=2, max=100)])
    message = TextAreaField('Сообщение', validators=[DataRequired()])

class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])

class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Подтвердите пароль', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Зарегистрироваться')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Это имя пользователя уже занято.')
    
    def validate_confirm_password(self, confirm_password):
        if self.password.data != confirm_password.data:
            raise ValidationError('Пароли не совпадают.')

class CategoryForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Описание', validators=[DataRequired()])
    duration = StringField('Продолжительность', validators=[Length(max=50)])
    price = StringField('Цена', validators=[Length(max=50)])
    image = FileField('Изображение')

class PortfolioForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired(), Length(max=200)])
    category_id = SelectField('Категория', coerce=int, validators=[DataRequired()])
    image = FileField('Изображение', validators=[DataRequired()])

class ReviewForm(FlaskForm):
    client_name = StringField('Имя клиента', validators=[DataRequired(), Length(max=100)])
    text = TextAreaField('Отзыв', validators=[DataRequired()])

class RequestForm(FlaskForm):
    client_name = StringField('Имя клиента', validators=[DataRequired(), Length(max=100)])
    phone = StringField('Телефон', validators=[DataRequired(), Length(max=20)])
    category_id = SelectField('Категория', coerce=int)
    message = TextAreaField('Сообщение')

# Routes
@app.route('/')
def index():
    categories = Category.query.all()
    portfolio_items = PortfolioItem.query.limit(6).all()
    quick_request_form = QuickRequestForm()
    quick_request_form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    return render_template('index.html', categories=categories[:3], portfolio_items=portfolio_items, quick_request_form=quick_request_form)

@app.route('/services')
def services():
    categories = Category.query.all()
    return render_template('services.html', categories=categories)

@app.route('/portfolio')
def portfolio():
    portfolio_items = PortfolioItem.query.all()
    categories = Category.query.all()
    return render_template('portfolio.html', portfolio_items=portfolio_items, categories=categories)

@app.route('/about')
def about():
    reviews = Review.query.order_by(Review.date.desc()).limit(6).all()
    return render_template('about.html', reviews=reviews)

@app.route('/contacts', methods=['GET', 'POST'])
def contacts():
    form = ContactForm()
    if form.validate_on_submit():
        contact_request = Request(
            client_name=form.client_name.data,
            phone="",
            message=form.message.data
        )
        db.session.add(contact_request)
        db.session.commit()
        flash('Спасибо за ваше сообщение! Мы свяжемся с вами в ближайшее время.', 'success')
        return redirect(url_for('contacts'))
    return render_template('contacts.html', form=form)

@app.route('/submit_request', methods=['POST'])
def submit_request():
    form = QuickRequestForm()
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    if form.validate_on_submit():
        new_request = Request(
            client_name=form.client_name.data,
            phone=form.phone.data,
            category_id=form.category_id.data
        )
        db.session.add(new_request)
        db.session.commit()
        flash('Ваша заявка успешно отправлена! Мы свяжемся с вами в ближайшее время.', 'success')
        return redirect(url_for('index'))
    else:
        flash('Пожалуйста, заполните все обязательные поля.', 'error')
        return redirect(url_for('index'))

# Admin panel
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            # Store admin session info
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Неверный логин или пароль', 'error')
    return render_template('admin/login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Регистрация прошла успешно! Теперь вы можете войти.', 'success')
        return redirect(url_for('admin_login'))
    return render_template('admin/register.html', form=form)

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    total_requests = Request.query.count()
    total_portfolio = PortfolioItem.query.count()
    total_reviews = Review.query.count()
    
    recent_requests = Request.query.order_by(Request.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                          total_requests=total_requests, 
                          total_portfolio=total_portfolio, 
                          total_reviews=total_reviews,
                          recent_requests=recent_requests)

@app.route('/admin/categories')
def admin_categories():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)

@app.route('/admin/categories/add', methods=['GET', 'POST'])
def admin_add_category():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    form = CategoryForm()
    if form.validate_on_submit():
        filename = None
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            filepath = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename)
            form.image.data.save(filepath)
        
        category = Category(
            name=form.name.data,
            description=form.description.data,
            duration=form.duration.data,
            price=form.price.data,
            image_filename=filename
        )
        db.session.add(category)
        db.session.commit()
        flash('Категория успешно добавлена!', 'success')
        return redirect(url_for('admin_categories'))
    
    return render_template('admin/category_form.html', form=form, title='Добавить категорию')

@app.route('/admin/categories/edit/<int:id>', methods=['GET', 'POST'])
def admin_edit_category(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    category = Category.query.get_or_404(id)
    form = CategoryForm(obj=category)
    
    if form.validate_on_submit():
        if form.image.data:
            # Delete old image if exists
            if category.image_filename:
                old_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], category.image_filename)
                if os.path.exists(old_path):
                    os.remove(old_path)
            
            filename = secure_filename(form.image.data.filename)
            filepath = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename)
            form.image.data.save(filepath)
            category.image_filename = filename
        
        category.name = form.name.data
        category.description = form.description.data
        category.duration = form.duration.data
        category.price = form.price.data
        
        db.session.commit()
        flash('Категория успешно обновлена!', 'success')
        return redirect(url_for('admin_categories'))
    
    return render_template('admin/category_form.html', form=form, title='Редактировать категорию', category=category)

@app.route('/admin/categories/delete/<int:id>', methods=['POST'])
def admin_delete_category(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    category = Category.query.get_or_404(id)
    
    # Delete associated portfolio items
    for item in category.portfolio_items:
        if item.image_filename:
            img_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], item.image_filename)
            if os.path.exists(img_path):
                os.remove(img_path)
        db.session.delete(item)
    
    # Delete category image
    if category.image_filename:
        img_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], category.image_filename)
        if os.path.exists(img_path):
            os.remove(img_path)
    
    db.session.delete(category)
    db.session.commit()
    flash('Категория успешно удалена!', 'success')
    return redirect(url_for('admin_categories'))

@app.route('/admin/portfolio')
def admin_portfolio():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    portfolio_items = PortfolioItem.query.all()
    categories = Category.query.all()
    return render_template('admin/portfolio.html', portfolio_items=portfolio_items, categories=categories)

@app.route('/admin/portfolio/add', methods=['GET', 'POST'])
def admin_add_portfolio():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    form = PortfolioForm()
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    
    if form.validate_on_submit():
        filename = secure_filename(form.image.data.filename)
        filepath = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename)
        form.image.data.save(filepath)
        
        portfolio_item = PortfolioItem(
            title=form.title.data,
            category_id=form.category_id.data,
            image_filename=filename
        )
        db.session.add(portfolio_item)
        db.session.commit()
        flash('Работа успешно добавлена!', 'success')
        return redirect(url_for('admin_portfolio'))
    
    return render_template('admin/portfolio_form.html', form=form, title='Добавить работу')

@app.route('/admin/portfolio/edit/<int:id>', methods=['GET', 'POST'])
def admin_edit_portfolio(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    portfolio_item = PortfolioItem.query.get_or_404(id)
    form = PortfolioForm(obj=portfolio_item)
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    
    if form.validate_on_submit():
        if form.image.data:
            # Delete old image if exists
            if portfolio_item.image_filename:
                old_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], portfolio_item.image_filename)
                if os.path.exists(old_path):
                    os.remove(old_path)
            
            filename = secure_filename(form.image.data.filename)
            filepath = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename)
            form.image.data.save(filepath)
            portfolio_item.image_filename = filename
        
        portfolio_item.title = form.title.data
        portfolio_item.category_id = form.category_id.data
        
        db.session.commit()
        flash('Работа успешно обновлена!', 'success')
        return redirect(url_for('admin_portfolio'))
    
    return render_template('admin/portfolio_form.html', form=form, title='Редактировать работу', portfolio_item=portfolio_item)

@app.route('/admin/portfolio/delete/<int:id>', methods=['POST'])
def admin_delete_portfolio(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    portfolio_item = PortfolioItem.query.get_or_404(id)
    
    # Delete image file
    if portfolio_item.image_filename:
        img_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], portfolio_item.image_filename)
        if os.path.exists(img_path):
            os.remove(img_path)
    
    db.session.delete(portfolio_item)
    db.session.commit()
    flash('Работа успешно удалена!', 'success')
    return redirect(url_for('admin_portfolio'))

@app.route('/admin/reviews')
def admin_reviews():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    reviews = Review.query.order_by(Review.date.desc()).all()
    return render_template('admin/reviews.html', reviews=reviews)

@app.route('/admin/reviews/add', methods=['GET', 'POST'])
def admin_add_review():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    form = ReviewForm()
    
    if form.validate_on_submit():
        review = Review(
            client_name=form.client_name.data,
            text=form.text.data
        )
        db.session.add(review)
        db.session.commit()
        flash('Отзыв успешно добавлен!', 'success')
        return redirect(url_for('admin_reviews'))
    
    return render_template('admin/review_form.html', form=form, title='Добавить отзыв')

@app.route('/admin/reviews/edit/<int:id>', methods=['GET', 'POST'])
def admin_edit_review(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    review = Review.query.get_or_404(id)
    form = ReviewForm(obj=review)
    
    if form.validate_on_submit():
        review.client_name = form.client_name.data
        review.text = form.text.data
        db.session.commit()
        flash('Отзыв успешно обновлен!', 'success')
        return redirect(url_for('admin_reviews'))
    
    return render_template('admin/review_form.html', form=form, title='Редактировать отзыв', review=review)

@app.route('/admin/reviews/delete/<int:id>', methods=['POST'])
def admin_delete_review(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    review = Review.query.get_or_404(id)
    db.session.delete(review)
    db.session.commit()
    flash('Отзыв успешно удален!', 'success')
    return redirect(url_for('admin_reviews'))

@app.route('/admin/requests')
def admin_requests():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    requests = Request.query.order_by(Request.created_at.desc()).all()
    categories = Category.query.all()
    return render_template('admin/requests.html', requests=requests, categories=categories)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))

# API endpoints for frontend filtering
@app.route('/api/portfolio/filter/<int:category_id>')
def filter_portfolio(category_id):
    if category_id == 0:  # All
        portfolio_items = PortfolioItem.query.all()
    else:
        portfolio_items = PortfolioItem.query.filter_by(category_id=category_id).all()
    
    result = []
    for item in portfolio_items:
        result.append({
            'id': item.id,
            'title': item.title,
            'image_url': f"/{app.config['UPLOAD_FOLDER']}/{item.image_filename}",
            'category_name': item.category.name
        })
    
    return jsonify(result)

def init_db():
    """Initialize the database with sample data"""
    with app.app_context():
        db.create_all()
        
        # Check if admin user exists
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(username='admin')
            admin_user.set_password('admin123')  # Change this in production!
            db.session.add(admin_user)
            
            # Add sample categories
            sample_categories = [
                {'name': 'Портретная съемка', 'description': 'Профессиональная портретная съемка для личного использования или деловых целей', 'duration': '1-2 часа', 'price': 'от 3000 руб'},
                {'name': 'Свадебная съемка', 'description': 'Полная документация вашего торжественного дня с авторским подходом', 'duration': '6-12 часов', 'price': 'от 15000 руб'},
                {'name': 'Детская съемка', 'description': 'Веселые и трогательные моменты с детьми в комфортной обстановке', 'duration': '1-2 часа', 'price': 'от 2500 руб'},
                {'name': 'Love Story', 'description': 'Романтическая фотосессия для молодоженов или пар', 'duration': '2-3 часа', 'price': 'от 4000 руб'},
                {'name': 'Предметная съемка', 'description': 'Продуктовая и предметная съемка для бизнеса и рекламы', 'duration': '2-4 часа', 'price': 'от 5000 руб'},
            ]
            
            for cat_data in sample_categories:
                category = Category(**cat_data)
                db.session.add(category)
            
            db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(debug=True)