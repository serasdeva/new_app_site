from app import app, db, init_db

if __name__ == '__main__':
    # Initialize the database
    init_db()
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)