# -*- coding: utf-8 -*-


import argparse
import os
import sys

import torch
import uvicorn
from fastapi import FastAPI
from loguru import logger
from pydantic import BaseModel, Field
from starlette.middleware.cors import CORSMiddleware

from langchain.text_splitter import SpacyTextSplitter
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.text_splitter import CharacterTextSplitter


# sys.path.append('..')
from text2vec import SentenceModel


class Item(BaseModel):
    input: str = Field(..., max_length=512)

class Item2(BaseModel):
    input: str = Field(...)


pwd_path = os.path.abspath(os.path.dirname(__file__))
use_cuda = torch.cuda.is_available()
logger.info(f'use_cuda:{use_cuda}')
# Use fine-tuned model
parser = argparse.ArgumentParser()

parser.add_argument("--model_name_or_path", type=str, default="shibing624/text2vec-bge-large-chinese",
                    help="Model save dir or model name")
# parser.add_argument("--model_name_or_path", type=str, default="shibing624/text2vec-base-chinese",
#                     help="Model save dir or model name")
args = parser.parse_args()
s_model = SentenceModel(args.model_name_or_path)

# define the app
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"])


@app.get('/')
async def index():
    return {"message": "index, docs url: /docs"}


@app.get('/emb')
async def emb(input: str):
    try:
        embeddings = s_model.encode(input, normalize_embeddings=True)
        result_dict = [{'embedding': embeddings.tolist()}]
        logger.debug(f"Successfully get sentence embeddings, q:{input}")
        return result_dict
    except Exception as e:
        logger.error(e)
        return {'status': False, 'msg': e}, 400


@app.post('/emb')
async def emb(item: Item):
    try:
        embeddings = s_model.encode(item.input, normalize_embeddings=True)
        result_dict = [{'embedding': embeddings.tolist()}]
        logger.debug(f"Successfully get sentence embeddings, q:{item.input}")
        return result_dict
    except Exception as e:
        logger.error(e)
        return {'status': False, 'msg': e}, 400


text_splitter = RecursiveCharacterTextSplitter(
    # Set a really small chunk size, just to show.
    chunk_size = 256,
    chunk_overlap  = 20
)

text_splitter2 = CharacterTextSplitter(
    separator = "\n",
    chunk_size = 256,
    chunk_overlap  = 20
)

@app.post('/chunk')
async def chunk(item: Item2):
    try:
        text_splitter = SpacyTextSplitter()
        # docs = text_splitter.split_text(item.input)
        docs = text_splitter2.create_documents([item.input])

        logger.debug(f"Successfully get chunking")
        return docs
    except Exception as e:
        logger.error(e)
        return {'status': False, 'msg': e}, 400

import loader
@app.post('/load_file')
async def emb(doc: loader.RequestModel):
    try:
        loader.load_file(doc)
        logger.debug(f"Successfully load file, q:{doc}")
        return "ok"
    except Exception as e:
        logger.error(e)
        return {'status': False, 'msg': e}, 400


if __name__ == '__main__':
    uvicorn.run(app=app, host='0.0.0.0', port=8001)