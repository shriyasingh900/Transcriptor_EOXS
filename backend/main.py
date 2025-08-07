
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import tempfile
import os
import shutil
import traceback
from transcription import process_multiple_audios

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/transcribe/")
async def transcribe(files: List[UploadFile] = File(...)):
    if len(files) > 50:
        raise HTTPException(status_code=400, detail="You can upload up to 50 files only.")

    tmp_dir = tempfile.mkdtemp()
    saved_paths = []

    try:
        for file in files:
            if not file.content_type.startswith("audio/"):
                raise HTTPException(status_code=400, detail=f"{file.filename} is not an audio file.")

            tmp_path = os.path.join(tmp_dir, file.filename)
            with open(tmp_path, "wb") as f:
                f.write(await file.read())
            saved_paths.append(tmp_path)

        # Process all audio files
        result = process_multiple_audios(saved_paths)
        return {"transcript": result}

    except Exception as e:
        print("Error during transcription:\n", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

