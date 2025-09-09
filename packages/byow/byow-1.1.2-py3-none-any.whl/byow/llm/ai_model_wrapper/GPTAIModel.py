import torch.nn as nn
import torch
from llm.ai_model.model.GPTModel import GPTModel
from llm.ai_model.configurations.ModelConfigurations import GPT_CONFIG_124M
from llm.base_module.tokenizer.TikTokenTokenizer import TikTokenTokenizer

class GPTAIModel():

    def __init__(self, base_model):
        self.model = GPTModel(cfg=GPT_CONFIG_124M)
        self.tokenizer = TikTokenTokenizer()

    def __text_to_token_ids(self, text):
        return torch.tensor(self.tokenizer.encode(text)).unsqueeze(0)

    def __token_ids_to_text(self, token_ids):
        return self.tokenizer.decode(token_ids.squeeze(0).tolist())
    
    def asnwerQuery(self, text, max_new_tokens, context_size):

        idx = self.__text_to_token_ids(text=text)

        for _ in range(max_new_tokens):
            
            idx_cond = idx[:, -context_size:]
            with torch.no_grad():
                logits = self.model(idx_cond)
            logits = logits[:, -1, :]  
            probas = torch.softmax(logits, dim=-1)
            idx_next = torch.argmax(probas, dim=-1, keepdim=True)
            idx = torch.cat((idx, idx_next), dim=1)

        return self.__token_ids_to_text(idx)