from model.detect_face import detect_face

from database.pinecone import save_to_pinecone
from model.face_recognition import generate_embeddings

def process_image_and_save_embeddings(filename, username):
    faces = detect_face(filename)

    if faces.any():
        embeddings = generate_embeddings(faces[0])
        embeddings_list = embeddings.tolist()
        print(f"========={embeddings_list[0]}")
        save_to_pinecone([{"id": username, "values": embeddings_list[0]}])
    else:
        print("No faces detected in the image")