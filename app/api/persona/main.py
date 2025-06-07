from datetime import datetime
import uuid
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import os
import json
from tempfile import NamedTemporaryFile

from data import data_chat_extraction, analyze_journal_entries,gen_mindlogpdf
from conv import extract_information_gemini, generate_rag, extract_graph_info
from mail import create_pdf_from_json, sendEmail  # You need to define this

from chat import reflection_chatbot
from dataSync import isPersonaUpdateNeeded, personaInfo, updatePersona
import json

app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.post("/getReport")
async def get_report(request: Request):
    try:
        payload = await request.json()
        authId = payload.get("authId")

        if not authId:
            return JSONResponse(content={"error": "Missing authId in request"}, status_code=400)
        if(isPersonaUpdateNeeded(authId)):
            info_json, graph_json = await updatePersona(authId)
        else:
            user_info = personaInfo(authId)
            if user_info:
                user_info_json = json.loads(user_info)
                info_json, graph_json = user_info_json.get("Info"), user_info_json.get("Graph")
            else:
                # Handle the case where user_info is None or empty
                return JSONResponse(content={"error": "User information not found or is empty"}, status_code=404)

        return JSONResponse(content={"info": info_json, "graph": graph_json}, status_code=200)

    except Exception as e:
        return JSONResponse(content={"error": f"Internal server error: {str(e)}"}, status_code=500)

@app.post("/chat")
async def chat(request: Request):
    try:
        payload = await request.json()
        authId = payload.get("authId")
        user_message = payload.get("userMessage")
        user_info = personaInfo(authId)

        if not authId or not user_message:
            return JSONResponse(content={"error": "Missing authId or userMessage in request"}, status_code=400)

        if not isPersonaUpdateNeeded(authId) or not user_info is None:
            # Generate RAG response
            rag_response = reflection_chatbot(user_message=user_message, user_info=user_info)
        else:
            # Update persona and then generate RAG response
            updatePersona(authId, user_message)
            rag_response = reflection_chatbot(user_message=user_message, user_info=user_info)
        if not rag_response:
            return JSONResponse(content={"error": "No response generated"}, status_code=404)

        return JSONResponse(content={"response": rag_response}, status_code=200)

    except Exception as e:
        return JSONResponse(content={"error": f"Internal server error: {str(e)}"}, status_code=500)
@app.post("/getMindLogReport")
async def get_report(request: Request):
    try:
        payload = await request.json()
        authId = payload.get("authId")
        user_email = payload.get("email")
        numdays = payload.get("numdays")

        if not authId or not user_email:
            return JSONResponse(content={"error": "Missing authId or email in request"}, status_code=400)

        # ✅ Generate unique filename using timestamp and UUID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]  # Shorten UUID for filename
        filename = f"mindlog_{authId}_{timestamp}_{unique_id}"
        

        

        # ✅ Generate the PDF at this unique path
        pdf_path= gen_mindlogpdf(authId, numdays, filename)

        # 📧 Send Email with PDF attached
        sendEmail(
            Name="SoulScript System",
            To=user_email,
            subject="Your MindLog Report",
            message="Attached is your report. Please review the PDF for detailed insights.",
            attachment_path=pdf_path
        )

        # 🧹 Clean up the file
        os.remove(pdf_path)
        os.remove(f"{filename}-mood_trend.png") 
        os.remove(f"{filename}-emotional_composition.png") 
        os.remove(f"{filename}-emotion_radar.png") 



        return JSONResponse(content={"message": "Email Sent"}, status_code=200)

    except Exception as e:
        return JSONResponse(content={"error": f"Internal server error: {str(e)}"}, status_code=500)