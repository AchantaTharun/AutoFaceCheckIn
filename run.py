from flask import Flask, render_template, request, url_for, redirect, session, Response, request, jsonify
from pymongo import MongoClient
import bcrypt
import base64
import gridfs
import codecs
import os
from io import BytesIO
from model.detect_face import detect_face, detect_face_from_stream
from model.train import process_image_and_save_embeddings
from tempfile import NamedTemporaryFile
from model.face_recognition import generate_embeddings
from flask_socketio import SocketIO, emit
from database.pinecone import query_pinecone
import json
import threading
from collections import Counter

app = Flask(__name__)
app.secret_key = "83a2e48c95f4d7a0e2e334572bd4b4c71cf68ae16c85f2d80d1c37f8c9d36c1e896ecae3d43a8b2eef9a302813fbf14c47a3b6a5f53b3e0c0d6244ff53b10d8f"
socketio = SocketIO(app)

def MongoDB():
    client = MongoClient("mongodb://127.0.0.1:27017/")
    db = client.get_database('AutoFaceCheckIn')
    records = db.users
    images = db.images
    grid_fs = gridfs.GridFS(db)
    schedule_c = db.schedule_c
    return records, images, grid_fs, schedule_c
records, images, grid_fs, schedule_c = MongoDB()



@app.route("/", methods=['post', 'get'])
def index():
    message = ''
    if "email" in session:
        if session["role"] == "user":
            email = session["email"]
            return redirect(url_for('user'))
        else:
            email = session["email"]
            return redirect(url_for('admin'))
    if request.method == "POST":
        user = request.form.get("fullname")
        email = request.form.get("email")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        user_found = records.find_one({"name": user})
        email_found = records.find_one({"email": email})
        if user_found:
            message = 'There already is a user by that name'
            return render_template('index.html', message=message)
        if email_found:
            message = 'This email already exists in database'
            return render_template('index.html', message=message)
        if password1 != password2:
            message = 'Passwords should match!'
            return render_template('index.html', message=message)
        else:
            hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())
            user_input = {'name': user, 'email': email, 'password': hashed, 'role': 'user'}
            records.insert_one(user_input)
            
            user_data = records.find_one({"email": email})
            new_email = user_data['email']
            session["email"] = new_email
            session["role"] = "user"
            session["username"] = user_data["name"]
            return redirect(url_for('user'))
    return render_template('index.html')

@app.route("/login", methods=["POST", "GET"])
def login():
    message = 'Please login to your account'
    if "email" in session:
        if session["role"] == "user":
            return redirect(url_for('user'))
        else:
            return redirect(url_for('admin'))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        email_found = records.find_one({"email": email})
        if email_found:
            email_val = email_found['email']
            role = email_found['role']
            passwordcheck = email_found['password']
            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                session["email"] = email_val
                session["role"] = role
                session["username"] = email_found["name"]
                if role == "user":
                    return redirect(url_for('user'))
                else:
                    return redirect(url_for('admin'))
            else:
                if "email" in session:
                    if session["role"] == "user":
                        return redirect(url_for('user'))
                    else:
                       return redirect(url_for('admin'))
                message = 'Wrong password'
                return render_template('login.html', message=message)
        else:
            message = 'Email not found'
            return render_template('login.html', message=message)
    return render_template('login.html', message=message)

@app.route('/user')
def user():
    if "email" in session:
        if session["role"] == "user":
            email = session["email"]
            image_count = images.count_documents({'email': email})
            return render_template('user.html', email=email, remaining_images=10-image_count, image_count=image_count)
        else:
            return redirect(url_for('admin'))
    else:
        return redirect(url_for("login"))
    
@app.route('/admin')
def admin():
    if "email" in session:
        if session["role"] == "user":
            return redirect(url_for('user'))
        else:
            email = session["email"]
            return render_template('admin.html', email=email)
    else:
        return redirect(url_for("login"))

@app.route("/logout", methods=["POST", "GET"])
def logout():
    if "email" in session:
        session.pop("email", None)
        return render_template("signout.html")
    else:
        return render_template('index.html')

@app.route('/capture', methods=['GET', 'POST'])
def capture():
    if session.get("role") != "user":
        return redirect(url_for('login'))

    user_name = session["username"]
    user_images_count = images.count_documents({'email': session["email"]})
    #user = records.find_one({'email': session["email"]})
    remaining_images = 10 - user_images_count

    if request.method == 'POST':
        if user_images_count >= 10:
            return jsonify({'error': 'You have reached the maximum limit of 10 images'})

        imageFile = request.files['image']

        with NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name
            imageFile.save(temp_file_path)

            faces = detect_face(temp_file_path)
        
        if not faces.any():
            os.unlink(temp_file_path)
            return jsonify({'error': 'No face detected in the image'})
        elif len(faces) > 1:
            os.unlink(temp_file_path)
            return jsonify({'error': 'Multiple faces detected in the image'})

        
        process_image_and_save_embeddings(temp_file_path,  f"{user_name}_{user_images_count+1}")
        
        folder_path = os.path.join("shots", user_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        image_path = os.path.join(folder_path, f"{user_name}_00{user_images_count + 1}.jpg")
        imageFile.save(image_path)

       # image = request.files['image']
        imageFile.seek(0)
        image_data = BytesIO(imageFile.read())

        id = grid_fs.put(image_data, content_type='image/jpeg', email=session["email"], number=user_images_count + 1)
        image_id = images.insert_one({'imageId': id, 'email': session["email"], 'number': user_images_count + 1}).inserted_id
        
        print(f"Image saved to MongoDB with ID: {image_id}")

        return jsonify({'success': True, 'message': 'Image saved', 'remainingImages': remaining_images-1})

    return render_template('capture.html')


@app.route('/imageData')
def image_data():
    user_images = images.find({'email': session["email"]}).limit(10)
    imgs = []
    for image in user_images:
        image_d = grid_fs.get(image['imageId'])
        base64_data = codecs.encode(image_d.read(), 'base64')
        imgs.append(base64_data.decode('utf-8'))
   
    return render_template('image_data.html', user_images=imgs)

class_schedule = {
    'Monday': ['Class A', 'Class B', 'Class C'],
    'Tuesday': ['Class D', 'Class E', 'Class F'],
    'Wednesday': ['Class G', 'Class H', 'Class I'],
    'Thursday': ['Class J', 'Class K', 'Class L'],
    'Friday': ['Class M', 'Class N', 'Class O']
}

@app.route('/schedule', methods=['GET', 'POST'])
def schedule():
    if request.method == 'POST':
        class_name = request.form['class_name']
        week_day = request.form['week_day']
        time_slot = request.form['time_slot']
        
        existing_class = schedule_c.find_one({'week_day': week_day, 'time_slot': time_slot})
        if existing_class:
            message = f"A class already exists on {week_day} at {time_slot}. Please choose a different time slot."
        else:
            schedule_c.insert_one({'class_name': class_name, 'week_day': week_day, 'time_slot': time_slot})
            message = f"Class '{class_name}' added successfully!"
        schedules = schedule_c.find()
        return render_template('schedule.html', schedules=schedules, message=message)

    schedules = list(schedule_c.find())

    return render_template('schedule.html', schedules=schedules)


@app.route('/livefeed')
def livefeed():
    return render_template('livefeed.html')

@socketio.on('stream_frame')
def handle_stream_frame(data):
    
    frame = data["frame"]
   
    faces = detect_face_from_stream(frame)
    #print(f"--------====== {faces}")
    if faces.any():
        embeddings = generate_embeddings(faces[0])
        
        results = query_pinecone(embeddings)
        
        names = [match['id'] for match in results['matches']]
        names_only = [name.split("_")[0] for name in names]
        name_counts = Counter(names_only)
        most_common_name = name_counts.most_common(1)[0][0]
        print('face_recognition_results', {'results': names})
        emit('face_recognition_results', {'results': most_common_name})



if __name__ == "__main__":
    socketio.run(app, debug=True, host='0.0.0.0', port=3000)
