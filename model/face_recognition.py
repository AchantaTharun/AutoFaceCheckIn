
import numpy as np
from facenet_pytorch import InceptionResnetV1
import torch

device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
facenet = InceptionResnetV1(pretrained='vggface2', device=device).eval()

def generate_embeddings(face):
    #print(f"------------- {face}")
    tensor_face = torch.from_numpy(face.transpose((2, 0, 1))[np.newaxis, ...]).float()

    
    with torch.no_grad():
        embeddings = facenet(tensor_face).numpy()

    return embeddings