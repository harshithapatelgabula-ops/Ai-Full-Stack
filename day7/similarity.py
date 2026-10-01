from sentence_transformers import SentenceTransformer, util
model = SentenceTransformer("all-MiniLM-L6-v2")
sentences = [ "I love playing football",
             " I enjoy palying soccer",
             "I like eating pizza"]
sentence_embedding = model.encode(sentences)
# print(sentence_embedding[0])
similarity1 = util.cos_sim(sentence_embedding[0],sentence_embedding[1])
print(similarity1.item())