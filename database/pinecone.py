
from pinecone import Pinecone, ServerlessSpec

pc = Pinecone(api_key="")
index = pc.Index("autofacecheckin")

# pc.create_index(
#     name="autofacecheckin",
#     dimension=128, # Replace with your model dimensions
#     metric="euclidean", # Replace with your model metric
#     spec=ServerlessSpec(
#         cloud="aws",
#         region="us-east-1"
#     ) 
# )

def save_to_pinecone(embeddings):
    print(f"-----------{embeddings}")
    # embeddings_list = embeddings[0].tolist()
    index.upsert(embeddings)

def query_pinecone(newEmbeddings):
    embeddings_list = newEmbeddings.tolist()
    #print(f"111111 {embeddings_list[0]}")
    return index.query(vector=embeddings_list[0], top_k=5)