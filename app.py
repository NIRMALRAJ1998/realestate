from flask import Flask, render_template, request, redirect, url_for
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, inspect
import traceback

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-very-secret-key-1234'  # Change this to a more secure key
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
csrf = CSRFProtect(app)

# Database connection with enhanced configuration
DB_URI = "postgresql://postgres:5432@localhost:5432/youtube_data1"
engine = create_engine(
    DB_URI,
    echo=True,  # Show all SQL queries
    pool_pre_ping=True,  # Check connection health
    connect_args={"connect_timeout": 5}  # Timeout after 5 seconds
)

meta = MetaData()

# Define table structure
contacts = Table(
    'contacts', meta,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String(100), nullable=False),
    Column('email', String(100), nullable=False),
    Column('subject', String(200), nullable=False),
    Column('message', String(500), nullable=False)
)

# Database initialization and verification
def initialize_database():
    print("\n=== DATABASE INITIALIZATION ===")
    try:
        with engine.connect() as conn:
            # Verify connection
            print("✅ Database connection successful!")
            
            # List all tables
            tables = conn.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """).fetchall()
            print("Existing tables:", [t[0] for t in tables])
            
            # Create tables if needed
            meta.create_all(conn)
            print("✔ Tables verified/created")
            
            # Show contacts table structure
            inspector = inspect(engine)
            print("\nTable columns:")
            for column in inspector.get_columns('contacts'):
                print(f"- {column['name']}: {column['type']}")
                
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        print(traceback.format_exc())

initialize_database()

@app.route('/')
def index():
    return render_template('real_estate.html')

@app.route('/submit', methods=['POST'])
def submit():
    print("\n=== FORM SUBMISSION STARTED ===")
    print(f"Request method: {request.method}")
    print(f"Form data: {request.form}")
    
    if request.method != 'POST':
        print("⚠ Not a POST request")
        return "Method not allowed", 405
        
    try:
        # Validate form data
        required_fields = ['name', 'email', 'subject', 'message']
        missing = [field for field in required_fields if field not in request.form]
        if missing:
            raise ValueError(f"Missing required fields: {missing}")
            
        name = request.form['name'].strip()
        email = request.form['email'].strip()
        subject = request.form['subject'].strip()
        message = request.form['message'].strip()
        
        print(f"\nData to insert:")
        print(f"Name: {name}")
        print(f"Email: {email}")
        print(f"Subject: {subject}")
        print(f"Message: {message}")

        # Database operation with transaction
        with engine.begin() as conn:  # Automatically commits or rolls back
            ins = contacts.insert().values(
                name=name,
                email=email,
                subject=subject,
                message=message
            )
            result = conn.execute(ins)
            print(f"\n✔ Insert successful - Rows affected: {result.rowcount}")
            if hasattr(result, 'inserted_primary_key'):
                print(f"New record ID: {result.inserted_primary_key}")
                
        return redirect(url_for('index'))
        
    except Exception as e:
        print("\n!!! ERROR !!!")
        print(f"Type: {type(e)}")
        print(f"Error: {e}")
        print(f"Traceback:\n{traceback.format_exc()}")
        
        # Return error details (in development only)
        return f"""
            <h1>Error</h1>
            <p>{str(e)}</p>
            <pre>{traceback.format_exc()}</pre>
            <p><a href="/">Return to form</a></p>
        """, 500

if __name__ == '__main__':
    print("\n=== STARTING APPLICATION ===")
    try:
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5000,
            threaded=True
        )
    except Exception as e:
        print(f"Failed to start application: {e}")
        print(traceback.format_exc())