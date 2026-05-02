from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


class ReplyRequest(BaseModel):
    message: str
    tone: str = "Professional"
    language: str = "English"
    context: str = ""
    style_examples: str = ""
    about_me: str = ""


@app.get("/")
def root():
    return FileResponse("static/index.html")


@app.post("/api/generate")
async def generate_reply(req: ReplyRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message is required")

    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not set in .env file")

    system = "You are Replai, an AI assistant that writes email and message replies on behalf of the user. Write a reply that sounds natural, human, and matches the requested tone. Output ONLY the reply text itself, ready to send. No explanations, no preamble."

    if req.about_me:
        system += f"\n\nAbout the user: {req.about_me}"
    if req.style_examples:
        system += f"\n\nExamples of how the user writes:\n{req.style_examples}"

    user_prompt = f"Write a {req.tone.lower()} reply to the following message"
    if req.language != "Auto":
        user_prompt += f" in {req.language}"
    user_prompt += f":\n\n---\n{req.message}\n---"
    if req.context:
        user_prompt += f"\n\nExtra instructions: {req.context}"

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                GROQ_URL,
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user_prompt}
                    ],
                    "max_tokens": 1024,
                    "temperature": 0.7
                }
            )
            data = response.json()

            if response.status_code != 200:
                raise HTTPException(status_code=500, detail=data.get("error", {}).get("message", "Groq API error"))

            reply = data["choices"][0]["message"]["content"]
            return {"reply": reply}

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Request timed out, try again")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


app.mount("/", StaticFiles(directory="static", html=True), name="static")
