from flask import Flask, jsonify, Response, request, render_template, redirect, url_for, flash
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import jwt
import datetime
import os
import cv2
from face_authenticator import FaceAuthenticator


camera_index=1

authenticator = FaceAuthenticator(
    camera_indexes=camera_index,  # Adjust the camera indexes as needed
    twilio_sid='sid_token_here',
    twilio_token='auth_token_here',
    twilio_phone_number='twilio_tele_number',
    recipient_phone_number='your_mms_number'
)
# authenticator.run()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'mycoolpassword')  # Use environment variable for production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///icey_users.db'  # SQLite database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 403
        try:
            jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except:
            return jsonify({'message': 'Token is invalid!'}), 403
        return f(*args, **kwargs)
    return decorated

@app.route('/start-authentication')
def start_authentication():
    authenticator.start()
    return redirect(url_for('video_feed'))

@app.route('/stop-authentication')
def stop_authentication():
    authenticator.stop()
    return redirect(url_for('video_feed'))

def generate_video_stream():
    while True:
        ret, frame = authenticator.video_capture.read()
        if not ret:
            break
        (flag, encodedImage) = cv2.imencode(".jpg", frame)
        if not flag:
            continue
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
               bytearray(encodedImage) + b'\r\n')

@app.route('/video-feed')
def video_feed():
    return Response(generate_video_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            token = jwt.encode({'user': username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'], algorithm="HS256")
            return redirect(url_for('content', token=token))
        flash('Invalid username or password')
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/content', methods=['GET'])
def content():
    return render_template('index.html')

@app.route('/')
def index():
    return render_template('login.html')

def init_db():
    db.create_all()  # Create database tables
    # Check if the admin user exists
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        # Create a new admin user
        new_admin = User(username='admin')
        new_admin.set_password('Password123!')
        db.session.add(new_admin)
        db.session.commit()
        print("Admin user created.")
    else:
        print("Admin user already exists.")

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True, ssl_context=('yourcert.pem', 'yourkey.pem'))  # Use SSL for HTTPS
