from datetime import datetime
import uuid
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import os
import json
from tempfile import NamedTemporaryFile

from data import data_chat_extraction, analyze_journal_entries,gen_mindlogpdf,json_to_md,save_to_pdf
from conv import extract_information_gemini, generate_rag, extract_graph_info
from mail import create_pdf_from_json, sendEmail  # You need to define this

from data import create_pdf_from_json_chat
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
    "http://localhost:3000"
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
        user_email = payload.get("email")

        if not authId or not user_email:
            return JSONResponse(content={"error": "Missing authId or email in request"}, status_code=400)

        # If update is needed → update and return, skip further processing
        if isPersonaUpdateNeeded(authId):
            info_json, graph_json = await updatePersona(authId)
            # Step: Generate PDF report from saved persona data
            data = {
                "info": info_json,
                "graph": graph_json
            }

            with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                pdf_path = tmp.name
                create_pdf_from_json(data, pdf_path)

            # Step: Send Email with PDF
            sendEmail(
                Name="SoulScript System",
                To=user_email,
                subject="Your Therapy Assessment Report",
                message="Attached is your report. Please review the PDF for detailed insights.",
                attachment_path=pdf_path
            )

            os.remove(pdf_path)
            return JSONResponse(content={
                "info": info_json,
                "graph": graph_json,
                "status": "Persona updated and stored. Skipping PDF generation."
            }, status_code=200)

        # Otherwise, fetch stored persona info and proceed to report/email
        persona_raw = personaInfo(authId)
        if not persona_raw:
            return JSONResponse(content={"error": "Stored persona data not found"}, status_code=404)

        persona_data = json.loads(persona_raw)
        info_json = persona_data.get("Info")
        graph_json = persona_data.get("Graph")

        if not info_json or not graph_json:
            return JSONResponse(content={"error": "Incomplete persona data"}, status_code=500)

        # Step: Generate PDF report from saved persona data
        data = {
            "info": info_json,
            "graph": graph_json
        }

        with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            pdf_path = tmp.name
            create_pdf_from_json(data, pdf_path)

        # Step: Send Email with PDF
        sendEmail(
            Name="SoulScript System",
            To=user_email,
            subject="Your Therapy Assessment Report",
            message="Attached is your report. Please review the PDF for detailed insights.",
            attachment_path=pdf_path
        )

        os.remove(pdf_path)

        return JSONResponse(content={
            "info": info_json,
            "graph": graph_json,
            "status": "Email sent using previously saved persona info."
        }, status_code=200)

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


import base64
from fastapi.responses import JSONResponse

@app.post("/getMindLogReport")
async def get_report(request: Request):
    try:
        payload = await request.json()
        authId = payload.get("authId")
        user_email = payload.get("email")
        numdays = payload.get("numdays")

        if not authId or not user_email:
            return JSONResponse(content={"error": "Missing authId or email"}, status_code=400)

        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        filename = f"mindlog_{authId}_{timestamp}_{unique_id}"
        pdf_path = gen_mindlogpdf(authId, numdays, filename)

        # Send email
        sendEmail(
            Name="SoulScript System",
            To=user_email,
            subject="Your MindLog Report",
            message="Attached is your report.",
            attachment_path=pdf_path
        )

        # Convert PDF to base64
        with open(pdf_path, "rb") as pdf_file:
            encoded_pdf = base64.b64encode(pdf_file.read()).decode("utf-8")

        # Clean up
        os.remove(pdf_path)
        os.remove(f"{filename}-mood_trend.png") 
        os.remove(f"{filename}-emotional_composition.png") 
        os.remove(f"{filename}-emotion_radar.png") 

        return JSONResponse(content={
            "message": "Report emailed and returned as base64",
            "pdf_base64": encoded_pdf
        })

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


import base64
from tempfile import NamedTemporaryFile
from fastapi.responses import JSONResponse

@app.post("/getChatSummary")
async def get_report(request: Request):
    try:
        payload = await request.json()
        authId = payload.get("authId")
        user_email = payload.get("email")

        # Step 1: Extract chat + journal data
        chat_data = data_chat_extraction(authId, "json")
        md_data = json_to_md(chat_data)

        # Step 2: Generate PDF into a temp file
        with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            pdf_path = tmp.name
            save_to_pdf(md_data, pdf_path)

        # Step 3: Send PDF via Email
        sendEmail(
            Name="SoulScript System",
            To=user_email,
            subject="Your Therapy Assessment Report",
            message="Attached is your report. Please review the PDF for detailed insights.",
            attachment_path=pdf_path
        )

        # Step 4: Encode PDF as base64 for frontend
        with open(pdf_path, "rb") as f:
            encoded_pdf = base64.b64encode(f.read()).decode("utf-8")

        # Step 5: Clean up
        os.remove(pdf_path)

        return JSONResponse(content={
            "status": "Email sent with report",
            "pdf_base64": encoded_pdf
        }, status_code=200)

    except Exception as e:
        return JSONResponse(content={"error": f"Internal server error: {str(e)}"}, status_code=500)
