from fastapi import FastAPI, UploadFile, File, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from services.ai_service import ai_service
import os
import json

# Database Imports
import models, schemas, crud
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AgriScan AI Backend",
    description="Precision Agriculture API for Drone Analysis",
    version="1.0.0"
)

# CORS Configuration
origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:3000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("static/scans", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

os.makedirs("temp", exist_ok=True)
app.mount("/temp", StaticFiles(directory="temp"), name="temp")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def root():
    return {"message": "AgriScan AI API is running with SQLite Database!"}

@app.post("/api/v1/scan/upload")
async def upload_scan(
    file: UploadFile = File(...), 
    user_name: str = Query("Farmer", description="Name of the user"),
    lang: str = Query("en", description="Language for action plan"),
    db: Session = Depends(get_db)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    os.makedirs("temp", exist_ok=True)
    
    try:
        file_location = f"temp/{file.filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(await file.read())
            
        # 1. Run AI Analysis
        result = await ai_service.analyze_image(file_location, user_name=user_name)
        
        # 2. Save to Database
        scan_create = schemas.ScanCreate(
            image_path=file_location,
            user_name=user_name,
            location_lat=20.296,
            location_lon=85.824
        )
        
        result_create = schemas.ScanResultCreate(
            health_score=float(result.get('health_score', 0)),
            yield_prediction=result.get('yield_forecast', {}).get('value', "Unknown"),
            pest_detected_count=int(result.get('pest_count', 0)),
            weather_temp=result.get('weather_temp'),
            weather_humidity=result.get('weather_humidity'),
            weather_desc=result.get('weather_desc'),
            n_level=result.get('n_level', "Optimal"),
            p_level=result.get('p_level', "Optimal"),
            k_level=result.get('k_level', "Optimal"),
            raw_json_output=result
        )
        
        db_scan = crud.create_scan_entry(db, scan_create, result_create)
        
        # 3. Translation Logic for Response
        if lang == 'hi':
            translated_actions = []
            for action in result.get('action_plan', []):
                if "Nitrogen" in action:
                    translated_actions.append("ज़ोन ए में नाइट्रोजन उर्वरक डालें")
                elif "Pest" in action:
                    translated_actions.append("कीटों का पता चला: तुरंत कीटनाशक का छिड़काव करें")
                elif "Irrigation" in action:
                    translated_actions.append("नियमित सिंचाई बनाए रखें")
                else:
                    translated_actions.append(action)
            result['action_plan'] = translated_actions
            
        # Add DB ID to response for tracking
        result['db_id'] = db_scan.id
            
        return result
    except Exception as e:
        print(f"Error processing image: {e}")
        raise HTTPException(status_code=500, detail="AI Processing Failed")

@app.get("/api/v1/scans")
async def get_scans(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    scans = db.query(models.Scan).order_by(models.Scan.timestamp.desc()).offset(skip).limit(limit).all()
    # Ensure nested relationships are loaded if needed, but Pydantic orm_mode handles lazy access mostly.
    return scans

@app.get("/api/v1/dashboard/stats")
async def get_dashboard_stats():
    return ai_service.get_dashboard_stats()

@app.get("/api/v1/map/layers/{scan_id}")
async def get_map_layers(scan_id: str):
    return {
        "rgb_url": "https://images.unsplash.com/photo-1625246333195-5848c4281413?q=80&w=1000&auto=format&fit=crop",
        "ndvi_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/NDVI_map.jpg/640px-NDVI_map.jpg", 
        "pest_map_url": "https://images.unsplash.com/photo-1599596818167-937d2b23a525"
    }

@app.get("/video_feed")
async def video_feed(file_path: str = None):
    from fastapi.responses import StreamingResponse
    
    # Default simulation video if none provided
    # In a real scenario, this would come from the database or an upload
    if not file_path:
        # Check if we have a demo video, otherwise fail gracefully
        file_path = "static/demo_simulation.mp4" 
        if not os.path.exists(file_path):
             return JSONResponse(status_code=404, content={"message": "No video source available for simulation."})

    return StreamingResponse(
        ai_service.generate_video_stream(file_path), 
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@app.post("/api/v1/chat", response_model=schemas.ChatResponse)
async def chat_with_agriscan(request: schemas.ChatRequest):
    """
    Mode 2: Kisan Chatbot for Q&A
    """
    return ai_service.chat_with_kisan(request.query)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
