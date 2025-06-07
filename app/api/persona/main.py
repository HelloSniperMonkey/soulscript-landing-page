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


app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
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
        user_email = payload.get("email")  # 💡 Add email in the frontend request

        if not authId or not user_email:
            return JSONResponse(content={"error": "Missing authId or email in request"}, status_code=400)

        # Step 1: Extract chat + journal data using authId
        chat_data = data_chat_extraction(authId, "json")
        journal_json = analyze_journal_entries(authId)

        # Step 2: Generate combined RAG result
        rag_result = generate_rag(chat_data=chat_data, journal_analysis=journal_json)

        # Step 3: Extract info + graph in parallel
        info_task = asyncio.to_thread(extract_information_gemini, rag_result)
        graph_task = asyncio.to_thread(extract_graph_info, rag_result)
        info_json, graph_json = await asyncio.gather(info_task, graph_task)

        # Step 4: Generate PDF report from info + graph
        data = {
            "info": info_json,
            "graph": graph_json
        }

        # Save to temporary file
        with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            pdf_path = tmp.name
            create_pdf_from_json(data, pdf_path)

        # Step 5: Send Email with PDF attached
        sendEmail(
            Name="SoulScript System",
            To=user_email,
            subject="Your Therapy Assessment Report",
            message="Attached is your report.Please review the PDF for detailed insights.",
            attachment_path=pdf_path
        )

        # Optional: remove PDF after sending
        os.remove(pdf_path)

        return JSONResponse(content={"info": info_json, "graph": graph_json, "status": "Email Sent"}, status_code=200)

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