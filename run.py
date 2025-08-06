from app import create_app
from app.db.setup_db import init_db

init_db()
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
