from fastapi import HTTPException
from transformers import pipeline
from pydantic import BaseModel


class ExpansionQuery(BaseModel):
    query: str
    num_expansions: int = 5  # Default value set to 5

model_name = "roberta-base"
fill_mask = pipeline("fill-mask", model=model_name, tokenizer=model_name)

def expand_query(query: str, num_expansions: int):
    try:
        query_with_mask = query + " <mask>"
        suggestions = fill_mask(query_with_mask, top_k=num_expansions)
        
        expanded_queries = [suggestion["sequence"].replace("<s>", "").replace("</s>", "").strip() for suggestion in suggestions]
        return expanded_queries
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
