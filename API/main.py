from fastapi import FastAPI, HTTPException, Depends, status, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os
import uvicorn
import models
import schemas
import security
from database import engine, get_db
from detection_utils import initialize_detector, get_detector
from routers import user, history, chat, detection

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Load environment variables
load_dotenv()

# Initialize the image detector
MODEL_PATH = os.path.join(os.path.dirname(__file__), "my_model.h5")
print(f"Looking for model at: {MODEL_PATH}")

if not os.path.exists(MODEL_PATH):
    print(f"Warning: Model file not found at {MODEL_PATH}")
    print("The /detect endpoint will not be available until a valid model is provided.")
else:
    try:
        print("Attempting to load model...")
        initialize_detector(MODEL_PATH)
        print(f"Model initialized successfully from {MODEL_PATH}")
    except Exception as e:
        print(f"Warning: Could not initialize detector: {str(e)}")
        print("The /detect endpoint will not be available until the model is properly initialized.")

# Configure Gemini AI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    # Handle this error appropriately in a real application, maybe raise and let main.py handle it
    print("Warning: GEMINI_API_KEY not found in environment variables. Chat features may be limited.")
    # Optionally, set model to None or raise an exception based on desired behavior
    model = None
else:
    # Initialize Gemini model
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(model_name='gemini-pro')
        print("Successfully initialized Gemini API model")
    except Exception as e:
        print(f"Error initializing Gemini model: {str(e)}")
        model = None

app = FastAPI(
    title="FastAPI with Gemini AI and Image Detection",
    description="A FastAPI application that integrates with Google's Gemini AI and provides image detection",
    version="1.0.0",
    openapi_extra={
        "components": {
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT"
                }
            }
        }
    }
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Share the model with the chat router if available
if model is not None:
    chat.set_ai_model(model)
    print("Chat model set successfully")
else:
    print("Chat model not available")

# Include routers
app.include_router(user.router)
app.include_router(history.router)
app.include_router(chat.router)
app.include_router(detection.router)

@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI with Gemini AI and User Management"}

if __name__ == "__main__":
    # Get port from environment variable or use default
    port = int(os.getenv('PORT', 8000))
    # Run the app with uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)