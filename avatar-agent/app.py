import os
import subprocess
import shutil
from fastapi import FastAPI, File, UploadFile, Request, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import time
import asyncio

app = FastAPI(title="Avatar Agent API")

# Global dict to store status of generation for simple polling
generation_status = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure directories exist
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUTS_DIR = os.path.join(BASE_DIR, "inputs")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
STATIC_DIR = os.path.join(BASE_DIR, "static")

os.makedirs(INPUTS_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

# Mount static files to serve frontend
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/outputs", StaticFiles(directory=OUTPUTS_DIR), name="outputs")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open(os.path.join(STATIC_DIR, "index.html"), "r", encoding="utf-8") as f:
        return f.read()

@app.post("/generate")
def generate_avatar(
    image: UploadFile = File(...),
    audio: UploadFile = File(...),
    quality: str = Form("fast")
):
    timestamp = str(int(time.time()))
    generation_status[timestamp] = "بدء رفع الملفات..."
    try:
        # Generate unique filenames using timestamp to avoid overwrites
        timestamp = int(time.time())
        img_ext = os.path.splitext(image.filename)[1]
        audio_ext = os.path.splitext(audio.filename)[1]
        
        img_filename = f"photo_{timestamp}{img_ext}"
        audio_filename = f"voice_{timestamp}{audio_ext}"
        
        img_path = os.path.join(INPUTS_DIR, img_filename)
        audio_path = os.path.join(INPUTS_DIR, audio_filename)
        
        # Save uploaded files
        with open(img_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
            
        with open(audio_path, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)
            
            
        # Define output path where SadTalker writes
        # Assuming run_avatar.sh writes to outputs directory
        # We need to run the script
        
        script_path = os.path.join(BASE_DIR, "run_avatar.sh")
        
        generation_status[timestamp] = "جاري تشغيل محرك الذكاء الاصطناعي (SadTalker)..."
        print(f"Running script: {script_path} {img_path} {audio_path} {quality}")
        
        process = subprocess.Popen(
            [script_path, img_path, audio_path, quality],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=BASE_DIR
        )
        
        # Read output line by line to update status (polling trick)
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            if line:
                decoded = line.decode('utf-8').strip()
                print(f"STDOUT: {decoded}")
                if "3DMM Extraction for source image" in decoded:
                    generation_status[timestamp] = "جاري استخراج معالم الوجه 3D... (الخطوة 1/3)"
                elif "using safetensor as default" in decoded:
                    generation_status[timestamp] = "جاري تهيئة النماذج... (الخطوة 2/3)"
                elif "Animation" in decoded or "animate" in decoded.lower():
                    generation_status[timestamp] = "جاري تحريك الوجه وإنشاء الفيديو... (الخطوة 3/3)"

        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            print(f"Error executing SadTalker: {stderr.decode('utf-8')}")
            return {"status": "error", "message": "Failed to generate video", "details": stderr.decode('utf-8')}
        
        # Finding the most recent mp4 file in outputs directory AND its subdirectories
        # (since SadTalker generates names based on input/date and usually places them in a timestamped folder)
        mp4_files = []
        for root, dirs, files in os.walk(OUTPUTS_DIR):
            for f in files:
                if f.endswith('.mp4'):
                    mp4_files.append(os.path.join(root, f))
                    
        if not mp4_files:
            return {"status": "error", "message": "Process succeeded but no MP4 output found"}
            
        # Sort by modification time
        mp4_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        latest_mp4_abs_path = mp4_files[0]
        
        # We need the relative path from OUTPUTS_DIR to serve it
        latest_mp4_rel_path = os.path.relpath(latest_mp4_abs_path, OUTPUTS_DIR)
        output_url = f"/outputs/{latest_mp4_rel_path}"
        
        return {
            "status": "success",
            "message": "Avatar generated successfully",
            "video_url": output_url
        }
        
    except Exception as e:
        print(f"Internal error: {str(e)}")
        generation_status[timestamp] = "حدث خطأ غير متوقع"
        return {"status": "error", "message": str(e)}

@app.get("/status/{timestamp}")
async def get_status(timestamp: str):
    if timestamp == "latest":
        if generation_status:
            # Return the chronological latest status value (last added or updated)
            # In a real app we'd use session IDs, but this works for a local single-user app
            latest_status = list(generation_status.values())[-1]
            return {"status": latest_status}
        return {"status": "جاري المعالجة..."}
    return {"status": generation_status.get(timestamp, "جاري المعالجة...")}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
