import json
import os
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse, RedirectResponse
from uvicorn import run as app_run

from typing import Optional

# Importing constants and pipeline modules from the project
from src.constants import APP_HOST, APP_PORT
from src.pipline.prediction_pipeline import VehicleData, VehicleDataClassifier
from src.pipline.training_pipeline import TrainingPipeline

# Initialize FastAPI application
app = FastAPI()

# Resolve paths from this file so static/templates work regardless of process CWD
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# #region agent log
def _agent_dbg(payload: dict) -> None:
    payload.setdefault("sessionId", "59a296")
    payload.setdefault("timestamp", int(time.time() * 1000))
    log_path = BASE_DIR / "debug-59a296.log"
    with log_path.open("a", encoding="utf-8") as _f:
        _f.write(json.dumps(payload) + "\n")


_cwd_static = Path("static")
_style_cwd = _cwd_static / "style.css"
_style_abs = STATIC_DIR / "style.css"
_agent_dbg(
    {
        "hypothesisId": "A,D",
        "location": "app.py:startup",
        "message": "static resolution vs cwd",
        "runId": "post-fix-2",
        "data": {
            "cwd": os.getcwd(),
            "static_dir_configured": str(STATIC_DIR),
            "relative_static_exists": _cwd_static.is_dir(),
            "absolute_static_exists": STATIC_DIR.is_dir(),
            "style_css_via_cwd_rel": _style_cwd.is_file(),
            "style_css_via_app_parent": _style_abs.is_file(),
            "style_size_if_abs": _style_abs.stat().st_size if _style_abs.is_file() else None,
        },
    }
)
# #endregion

# Set up Jinja2 template engine for rendering HTML templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Allow all origins for Cross-Origin Resource Sharing (CORS)
origins = ["*"]

# Configure middleware to handle CORS, allowing requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# #region agent log
@app.middleware("http")
async def _agent_static_mw(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/static"):
        _agent_dbg(
            {
                "hypothesisId": "A,B,C",
                "location": "app.py:middleware",
                "message": "static response",
                "runId": "post-fix-2",
                "data": {
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "content_type": response.headers.get("content-type"),
                },
            }
        )
    return response


# #endregion

class DataForm:
    """
    DataForm class to handle and process incoming form data.
    This class defines the vehicle-related attributes expected from the form.
    """
    def __init__(self, request: Request):
        self.request: Request = request
        self.Gender: Optional[int] = None
        self.Age: Optional[int] = None
        self.Driving_License: Optional[int] = None
        self.Region_Code: Optional[float] = None
        self.Previously_Insured: Optional[int] = None
        self.Annual_Premium: Optional[float] = None
        self.Policy_Sales_Channel: Optional[float] = None
        self.Vintage: Optional[int] = None
        self.Vehicle_Age_lt_1_Year: Optional[int] = None
        self.Vehicle_Age_gt_2_Years: Optional[int] = None
        self.Vehicle_Damage_Yes: Optional[int] = None
                

    async def get_vehicle_data(self):
        """
        Method to retrieve and assign form data to class attributes.
        This method is asynchronous to handle form data fetching without blocking.
        """
        form = await self.request.form()
        self.Gender = form.get("Gender")
        self.Age = form.get("Age")
        self.Driving_License = form.get("Driving_License")
        self.Region_Code = form.get("Region_Code")
        self.Previously_Insured = form.get("Previously_Insured")
        self.Annual_Premium = form.get("Annual_Premium")
        self.Policy_Sales_Channel = form.get("Policy_Sales_Channel")
        self.Vintage = form.get("Vintage")
        self.Vehicle_Age_lt_1_Year = form.get("Vehicle_Age_lt_1_Year")
        self.Vehicle_Age_gt_2_Years = form.get("Vehicle_Age_gt_2_Years")
        self.Vehicle_Damage_Yes = form.get("Vehicle_Damage_Yes")

# Route to render the main page with the form
@app.get("/", tags=["authentication"])
async def index(request: Request):
    """
    Renders the main HTML form page for vehicle data input.
    """
    # #region agent log
    try:
        _css_url_for = str(request.url_for("static", path="style.css"))
    except Exception as _e:
        _css_url_for = f"url_for_error:{type(_e).__name__}"
    _agent_dbg(
        {
            "hypothesisId": "F",
            "location": "app.py:index",
            "message": "GET /",
            "runId": "post-fix-2",
            "data": {
                "scheme": request.url.scheme,
                "path": request.url.path,
                "host": request.headers.get("host"),
                "css_href_in_template": "/static/style.css",
                "css_url_for_resolved": _css_url_for,
            },
        }
    )
    # #endregion
    return templates.TemplateResponse(
        request,
        "vehicledata.html",
        {"context": "Rendering"},
    )

# Route to trigger the model training process
@app.get("/train")
async def trainRouteClient():
    """
    Endpoint to initiate the model training pipeline.
    """
    try:
        train_pipeline = TrainingPipeline()
        train_pipeline.run_pipeline()
        return Response("Training successful!!!")

    except Exception as e:
        return Response(f"Error Occurred! {e}")

# Route to handle form submission and make predictions
@app.post("/")
async def predictRouteClient(request: Request):
    """
    Endpoint to receive form data, process it, and make a prediction.
    """
    try:
        form = DataForm(request)
        await form.get_vehicle_data()
        
        vehicle_data = VehicleData(
                                Gender= form.Gender,
                                Age = form.Age,
                                Driving_License = form.Driving_License,
                                Region_Code = form.Region_Code,
                                Previously_Insured = form.Previously_Insured,
                                Annual_Premium = form.Annual_Premium,
                                Policy_Sales_Channel = form.Policy_Sales_Channel,
                                Vintage = form.Vintage,
                                Vehicle_Age_lt_1_Year = form.Vehicle_Age_lt_1_Year,
                                Vehicle_Age_gt_2_Years = form.Vehicle_Age_gt_2_Years,
                                Vehicle_Damage_Yes = form.Vehicle_Damage_Yes
                                )

        # Convert form data into a DataFrame for the model
        vehicle_df = vehicle_data.get_vehicle_input_data_frame()

        # Initialize the prediction pipeline
        model_predictor = VehicleDataClassifier()

        # Make a prediction and retrieve the result
        value = model_predictor.predict(dataframe=vehicle_df)[0]

        # Interpret the prediction result as 'Response-Yes' or 'Response-No'
        status = "Response-Yes" if value == 1 else "Response-No"

        # Render the same HTML page with the prediction result
        return templates.TemplateResponse(
            request,
            "vehicledata.html",
            {"context": status},
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


# Mount static files last so API routes take precedence; use absolute path (not CWD-relative)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Main entry point to start the FastAPI server
if __name__ == "__main__":
    app_run(app, host=APP_HOST, port=APP_PORT)