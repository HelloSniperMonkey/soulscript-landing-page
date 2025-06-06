from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio

from data import data_chat_extraction, analyze_journal_entries
from conv import extract_information_gemini, generate_rag, extract_graph_info

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

        if not authId:
            return JSONResponse(content={"error": "Missing authId in request"}, status_code=400)

        # Step 1: Extract chat + journal data using authId
        chat_data = data_chat_extraction(authId, "json")
        journal_json = analyze_journal_entries(authId)

        # Step 2: Generate combined RAG result
        rag_result = generate_rag(chat_data=chat_data, journal_analysis=journal_json)

        # Step 3: Extract info + graph in parallel
        info_task = asyncio.to_thread(extract_information_gemini, rag_result)
        graph_task = asyncio.to_thread(extract_graph_info, rag_result)
        info_json, graph_json = await asyncio.gather(info_task, graph_task)

        return JSONResponse(content={"info": info_json, "graph": graph_json}, status_code=200)

    except Exception as e:
        return JSONResponse(content={"error": f"Internal server error: {str(e)}"}, status_code=500)
