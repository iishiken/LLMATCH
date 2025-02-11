from vllm import LLM, SamplingParams
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from typing import List, Optional

app = FastAPI()
llm = LLM(model="elyza/ELYZA-japanese-Llama-2-7b-instruct")  # 日本語モデルを使用

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 512

class ChatResponse(BaseModel):
    content: str

@app.post("/v1/chat/completions", response_model=ChatResponse)
async def chat_completions(request: ChatRequest):
    try:
        # メッセージを結合してプロンプトを作成
        prompt = ""
        for msg in request.messages:
            if msg.role == "system":
                prompt += f"システム: {msg.content}\n\n"
            elif msg.role == "user":
                prompt += f"ユーザー: {msg.content}\n\n"
            elif msg.role == "assistant":
                prompt += f"アシスタント: {msg.content}\n\n"

        # 推論パラメータの設定
        sampling_params = SamplingParams(
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )

        # 推論の実行
        outputs = llm.generate([prompt], sampling_params)
        response_text = outputs[0].outputs[0].text.strip()

        return ChatResponse(content=response_text)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 