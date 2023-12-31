from text2vec import SentenceModel 

model = SentenceModel('shibing624/text2vec-bge-large-chinese')


def Embedding(txt):
    sentence = txt
    vec = model.encode(sentence)
    return vec.tolist()