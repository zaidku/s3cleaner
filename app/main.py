from flask import Flask


from s3_cleaner import s3_bp

app = Flask(__name__)
app.register_blueprint(s3_bp, url_prefix='/api')

@app.route('/')
def index():
    return "S3 Cleaner Service is running."

if __name__ == '__main__':
    app.run(debug=True)
