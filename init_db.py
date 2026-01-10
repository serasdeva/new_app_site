from app import app, db, User, Category, PortfolioItem, Review

def init_database():
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if admin user already exists
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin = User(username='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            print("Admin user created: username=admin, password=admin123")
        
        # Add sample categories if none exist
        if Category.query.count() == 0:
            categories_data = [
                {
                    'name': 'Портретная съемка',
                    'description': 'Профессиональная портретная съемка для вашего архива или подарка себе и близким.',
                    'duration': '1-2 часа',
                    'price': 'от 5000 руб'
                },
                {
                    'name': 'Свадебная съемка',
                    'description': 'Памятные кадры с самого важного дня в вашей жизни, созданные с любовью и вниманием к деталям.',
                    'duration': '6-8 часов',
                    'price': 'от 25000 руб'
                },
                {
                    'name': 'Детская фотосессия',
                    'description': 'Веселые и трогательные моменты с вашими малышами, которые останутся в памяти навсегда.',
                    'duration': '1-1.5 часа',
                    'price': 'от 6000 руб'
                },
                {
                    'name': 'Love Story',
                    'description': 'Романтическая фотосессия для двоих, запечатлевшая вашу историю любви и чувства.',
                    'duration': '2-3 часа',
                    'price': 'от 8000 руб'
                },
                {
                    'name': 'Предметная съемка',
                    'description': 'Профессиональная съемка товаров для коммерческих целей и каталогов.',
                    'duration': '2-4 часа',
                    'price': 'от 3000 руб'
                }
            ]
            
            for cat_data in categories_data:
                category = Category(**cat_data)
                db.session.add(category)
            
            print("Sample categories added.")
        
        # Add sample reviews if none exist
        if Review.query.count() == 0:
            sample_reviews = [
                {
                    'client_name': 'Анна Петрова',
                    'text': 'Замечательная студия! Фотограф очень профессиональный, чувствуется большой опыт. Результат превзошел все ожидания!'
                },
                {
                    'client_name': 'Михаил Сидоров',
                    'text': 'Делали свадебную фотосессию, остались очень довольны. Все получилось естественно и красиво.'
                },
                {
                    'client_name': 'Екатерина Волкова',
                    'text': 'Спасибо за отличные детские фотографии! Малыш чувствовал себя комфортно, не капризничал.'
                }
            ]
            
            for rev_data in sample_reviews:
                review = Review(**rev_data)
                db.session.add(review)
            
            print("Sample reviews added.")
        
        # Commit all changes
        db.session.commit()
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_database()