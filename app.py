from __init__ import create_app

app = create_app()
app.secret_key = 'your_secret_key'  # Add your secret key

if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True)
