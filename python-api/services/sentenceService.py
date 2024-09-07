from common import constant, functionHelper
from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np
# from sklearn.decomposition import PCA
# from sklearn.metrics.pairwise import cosine_similarity

class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class ModelSentence(metaclass=SingletonMeta):
    def __init__(self):
        self.tokenizer = None
        self.model = None

    def __loadModel__(self):
        """Load model follow constant config
        """
        if self.model is None:
            functionHelper.writeLog("Loading model", constant.START_LOG)
            
            self.model = AutoModel.from_pretrained(constant.PHOBERT_BASE_PATH)
            
            functionHelper.writeLog("Loaded model", constant.END_LOG)
        else:
            functionHelper.writeLog("Loaded model", constant.END_LOG)


        if self.tokenizer is None:
            functionHelper.writeLog("Loading tokenizer", constant.START_LOG)
            
            self.tokenizer = AutoTokenizer.from_pretrained(
                constant.PHOBERT_BASE_PATH, use_fast=True
            )

            functionHelper.writeLog("Loaded tokenizer", constant.END_LOG)
        else:
            functionHelper.writeLog("Loaded tokenizer", constant.END_LOG)


    def storageModel(self):
        self.tokenizer.save_pretrained(constant.TOKENIZER_PATH)
        self.model.save_pretrained(constant.MODEL_PATH)

    def reloadModel(self):
        if self.model is None or self.tokenizer is None:
            print("============> Loading model and tokenizer")
            self.tokenizer = AutoTokenizer.from_pretrained(constant.TOKENIZER_PATH)
            self.model = AutoModel.from_pretrained(constant.TOKENIZER_PATH)
            print("============> Loaded model and tokenizer")
        else:
            print("============> Model and tokenizer already loaded")

    def encodeSentence(self, sentence):

        inputs = self.tokenizer(
            sentence, return_tensors="pt", truncation=True, padding=True
        )
        with torch.no_grad():
            outputs = self.model(**inputs)

        embeddings = outputs.last_hidden_state.mean(dim=1)

        return embeddings

    def tokenizeArrayObject(self, arr):
        return [
            self.tokenizer(item, return_tensors="pt", truncation=True, padding=True)
            for item in arr
        ]

    def _padAndConcat(self, tensors):
        """
        padding câu để các câu có độ dài bằng nhau
        """
        if not tensors:
            raise ValueError("List of tensors is empty")
        maxLength = max(tensor.size(1) for tensor in tensors)
        paddedTensors = []
        for tensor in tensors:
            padLength = maxLength - tensor.size(1)

            if padLength > 0:
                paddedTensor = torch.cat(
                    [
                        tensor,
                        torch.zeros(tensor.size(0), padLength, dtype=tensor.dtype),
                    ],
                    dim=1,
                )
            else:
                paddedTensor = tensor

            paddedTensors.append(paddedTensor)

        concatenatedTensor = torch.cat(paddedTensors, dim=0)

        return concatenatedTensor

    def embeddingArrayObject(self, arr):
        batch = {}

        for key in arr[0]:
            tensors = [item[key] for item in arr]
            batch[key] = self._padAndConcat(tensors)

        with torch.no_grad():
            outputs = self.model(**batch)

        batchEmbedding = outputs.last_hidden_state.mean(dim=1)
        return batchEmbedding
