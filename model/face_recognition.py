
import numpy as np
from facenet_pytorch import InceptionResnetV1
import torch

facenet = InceptionResnetV1(pretrained='vggface2').eval()

def generate_embeddings(face):
    print(f"------------- {face}")
    tensor_face = torch.from_numpy(face.transpose((2, 0, 1))[np.newaxis, ...]).float()

    
    with torch.no_grad():
        embeddings = facenet(tensor_face).numpy()

    return embeddings