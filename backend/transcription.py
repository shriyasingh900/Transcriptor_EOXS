# import whisper
# import spacy
# import os
# import warnings
# from concurrent.futures import ProcessPoolExecutor
# from typing import List
# import multiprocessing

# # Suppress harmless FP16 warning on CPU
# warnings.filterwarnings("ignore", category=UserWarning, module="whisper")

# WHISPER_MODEL = "base"

# model = None
# nlp = None

# def initialize_models():
#     global model, nlp
#     if model is None:
#         print(f"Loading Whisper model ({WHISPER_MODEL})...")
#         model = whisper.load_model(WHISPER_MODEL)
#     if nlp is None:
#         print("Loading spaCy model...")
#         try:
#             nlp = spacy.load("en_core_web_sm")
#         except OSError:
#             from spacy.cli import download
#             download("en_core_web_sm")
#             nlp = spacy.load("en_core_web_sm")

# def spacy_sentence_split(text):
#     doc = nlp(text)
#     return [sent.text.strip() for sent in doc.sents if sent.text.strip()]

# def process_single_audio(index_and_path):
#     idx, file_path = index_and_path
#     try:
#         initialize_models()
#         result = model.transcribe(file_path)
#         raw_text = result["text"]
#         sentences = spacy_sentence_split(raw_text)
#         output = "\n".join(sentences)
#         return f"Transcript {idx} ({os.path.basename(file_path)})\n------------\n{output}\n"
#     except Exception as e:
#         return f"Transcript {idx} ({os.path.basename(file_path)})\n------------\nError processing file: {e}\n"

# def process_multiple_audios(file_paths: List[str]) -> str:
#     max_workers = min(8, multiprocessing.cpu_count())
#     try:
#         with ProcessPoolExecutor(max_workers=max_workers) as executor:
#             results = executor.map(process_single_audio, enumerate(file_paths, 1))
#             return "\n".join(results)
#     except Exception as e:
#         print("Multiprocessing error:", e)
#         raise

## Latest Final Version

# import whisper
# import spacy
# import os
# import warnings
# from pydub import AudioSegment
# from tempfile import mkdtemp
# import shutil
# from concurrent.futures import ProcessPoolExecutor
# from typing import List
# import multiprocessing

# # ✅ Force pydub to use ffmpeg — this prevents the pyaudioop error
# AudioSegment.converter = "C:\ffmpeg\ffmpeg-7.1.1-full_build\bin"  # ⚠️ Change if needed (e.g., "C:\\ffmpeg\\bin\\ffmpeg.exe" on Windows)

# # ✅ Suppress harmless warnings from Whisper
# warnings.filterwarnings("ignore", category=UserWarning, module="whisper")

# WHISPER_MODEL = "base"

# model = None
# nlp = None

# def initialize_models():
#     global model, nlp
#     if model is None:
#         print(f"Loading Whisper model ({WHISPER_MODEL})...")
#         model = whisper.load_model(WHISPER_MODEL)
#     if nlp is None:
#         print("Loading spaCy model...")
#         try:
#             nlp = spacy.load("en_core_web_sm")
#         except OSError:
#             from spacy.cli import download
#             download("en_core_web_sm")
#             nlp = spacy.load("en_core_web_sm")

# def spacy_sentence_split(text):
#     doc = nlp(text)
#     return [sent.text.strip() for sent in doc.sents if sent.text.strip()]

# def split_audio(file_path, chunk_length_ms=60_000):
#     """
#     Splits an audio file into chunks using ffmpeg via pydub.
#     This avoids using audioop and prevents pyaudioop errors.
#     """
#     audio = AudioSegment.from_file(file_path)  # optionally specify format=...
#     chunks = []
#     for i in range(0, len(audio), chunk_length_ms):
#         chunk = audio[i:i + chunk_length_ms]
#         chunks.append(chunk)
#     return chunks

# def transcribe_large_audio(file_path):
#     """
#     Transcribes audio using Whisper.
#     - If file size > 15MB → splits into chunks and transcribes piece-by-piece.
#     - Else → processes directly using whisper.
#     """
#     initialize_models()

#     file_size_mb = os.path.getsize(file_path) / (1024 * 1024)  # size in MB
#     CHUNK_THRESHOLD_MB = 15

#     if file_size_mb <= CHUNK_THRESHOLD_MB:
#         print(f"Processing normally: {os.path.basename(file_path)} ({file_size_mb:.2f} MB)")
#         try:
#             result = model.transcribe(file_path)
#             return result.get("text", "").strip()
#         except Exception as e:
#             print(f"Error processing file normally: {e}")
#             return ""
#     else:
#         print(f"Processing in chunks: {os.path.basename(file_path)} ({file_size_mb:.2f} MB)")
#         temp_dir = mkdtemp()
#         chunks = split_audio(file_path, chunk_length_ms=60_000)

#         full_transcription = ""

#         for i, chunk in enumerate(chunks):
#             chunk_filename = os.path.join(temp_dir, f"chunk_{i}.wav")
#             chunk.export(chunk_filename, format="wav")
#             try:
#                 result = model.transcribe(chunk_filename)
#                 transcription = result.get("text", "").strip()
#                 full_transcription += transcription + " "
#             except Exception as e:
#                 print(f"Error in chunk {i}: {e}")
#                 continue

#         shutil.rmtree(temp_dir)
#         return full_transcription.strip()

# def process_single_audio(index_and_path):
#     idx, file_path = index_and_path
#     try:
#         initialize_models()
#         raw_text = transcribe_large_audio(file_path)
#         sentences = spacy_sentence_split(raw_text)
#         output = "\n".join(sentences)
#         return f"Transcript {idx} ({os.path.basename(file_path)})\n------------\n{output}\n"
#     except Exception as e:
#         return f"Transcript {idx} ({os.path.basename(file_path)})\n------------\nError processing file: {e}\n"

# def process_multiple_audios(file_paths: List[str]) -> str:
#     """
#     Batch transcribes multiple audio files using multiprocessing.
#     Returns all transcriptions as a single formatted string.
#     """
#     max_workers = min(8, multiprocessing.cpu_count())
#     try:
#         with ProcessPoolExecutor(max_workers=max_workers) as executor:
#             results = executor.map(process_single_audio, enumerate(file_paths, 1))
#             return "\n".join(results)
#     except Exception as e:
#         print("Multiprocessing error:", e)
#         raise





import whisper
import spacy
import os
import warnings
import shutil
import ffmpeg
import math
import subprocess
from tempfile import mkdtemp
from concurrent.futures import ProcessPoolExecutor
from typing import List
import multiprocessing

# ✅ Suppress harmless Whisper warnings
warnings.filterwarnings("ignore", category=UserWarning, module="whisper")

WHISPER_MODEL = "base"
model = None
nlp = None

def initialize_models():
    global model, nlp
    if model is None:
        print(f"Loading Whisper model ({WHISPER_MODEL})...")
        model = whisper.load_model(WHISPER_MODEL)
    if nlp is None:
        print("Loading spaCy model...")
        try:
            nlp = spacy.load("en_core_web_sm")
        except OSError:
            from spacy.cli import download
            download("en_core_web_sm")
            nlp = spacy.load("en_core_web_sm")

def spacy_sentence_split(text):
    doc = nlp(text)
    return [sent.text.strip() for sent in doc.sents if sent.text.strip()]

def split_audio_ffmpeg(file_path, chunk_length_sec=60):
    """
    Splits the audio file using ffmpeg into chunks (default 60s).
    Returns a list of chunk file paths and a temporary directory to clean up.
    """
    probe = ffmpeg.probe(file_path)
    duration = float(probe['format']['duration'])
    total_chunks = math.ceil(duration / chunk_length_sec)

    temp_dir = mkdtemp()
    chunk_paths = []

    for i in range(total_chunks):
        start_time = i * chunk_length_sec
        output_path = os.path.join(temp_dir, f"chunk_{i}.wav")

        (
            ffmpeg
            .input(file_path, ss=start_time, t=chunk_length_sec)
            .output(output_path, format='wav')
            .overwrite_output()
            .run(quiet=True)
        )

        chunk_paths.append(output_path)

    return chunk_paths, temp_dir

def transcribe_large_audio(file_path):
    """
    Transcribes audio using Whisper.
    - If file size > 15MB → splits into chunks and transcribes piece-by-piece.
    - Else → processes directly using whisper.
    """
    initialize_models()

    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)  # size in MB
    CHUNK_THRESHOLD_MB = 15

    if file_size_mb <= CHUNK_THRESHOLD_MB:
        print(f"Processing normally: {os.path.basename(file_path)} ({file_size_mb:.2f} MB)")
        try:
            result = model.transcribe(file_path)
            return result.get("text", "").strip()
        except Exception as e:
            print(f"Error processing file normally: {e}")
            return ""
    else:
        print(f"Processing in chunks: {os.path.basename(file_path)} ({file_size_mb:.2f} MB)")
        chunk_paths, temp_dir = split_audio_ffmpeg(file_path)
        full_transcription = ""

        for i, chunk_path in enumerate(chunk_paths):
            try:
                result = model.transcribe(chunk_path)
                transcription = result.get("text", "").strip()
                full_transcription += transcription + " "
            except Exception as e:
                print(f"Error in chunk {i}: {e}")
                continue

        shutil.rmtree(temp_dir)
        return full_transcription.strip()

def process_single_audio(index_and_path):
    idx, file_path = index_and_path
    try:
        initialize_models()
        raw_text = transcribe_large_audio(file_path)
        sentences = spacy_sentence_split(raw_text)
        output = "\n".join(sentences)
        return f"Transcript {idx} ({os.path.basename(file_path)})\n------------\n{output}\n"
    except Exception as e:
        return f"Transcript {idx} ({os.path.basename(file_path)})\n------------\nError processing file: {e}\n"

def process_multiple_audios(file_paths: List[str]) -> str:
    """
    Batch transcribes multiple audio files using multiprocessing.
    Returns all transcriptions as a single formatted string.
    """
    max_workers = min(8, multiprocessing.cpu_count())
    try:
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            results = executor.map(process_single_audio, enumerate(file_paths, 1))
            return "\n".join(results)
    except Exception as e:
        print("Multiprocessing error:", e)
        raise
