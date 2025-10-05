# global_flower_api.py
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import numpy as np
import joblib
import pandas as pd
from datetime import datetime
import asyncio
import logging
from scipy.spatial.distance import cosine
from scipy import stats
from scipy.interpolate import interp1d

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Global Flower Coverage API",
    description="Real-time flower coverage detection using physics-based ML model",
    version="1.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load your trained physics model from notebook
try:
    model_assets = joblib.load('physics_coverage_model.joblib')
    logger.info("✅ Physics model loaded successfully")
    logger.info(f"📊 Model R²: {model_assets['performance']['r2']:.3f}")
except Exception as e:
    logger.error(f"Failed to load model: {e}")
    model_assets = None

class PointDetectionRequest(BaseModel):
    lat: float
    lng: float
    date: str = "2025-10-04"  

class PointDetectionResponse(BaseModel):
    coverage: float
    category: str
    intensity: str
    confidence: float
    coordinates: List[float]

class RegionScanRequest(BaseModel):
    north: float
    south: float 
    east: float
    west: float
    date: str = "2024-10-04"
    resolution: str = "medium"  

class BloomingEvent(BaseModel):
    lat: float
    lng: float 
    coverage: float
    intensity: str
    category: str

class RegionScanResponse(BaseModel):
    events: List[BloomingEvent]
    totalPoints: int
    bloomingPoints: int
    date: str
    region: Dict

# === YOUR NOTEBOOK'S PHYSICS MODEL LOGIC ===

def extract_spectral_features_from_rgb(rgb_data: Dict[str, float], wavelengths: np.ndarray, 
                                      flower_spectrum: np.ndarray, background_spectrum: np.ndarray) -> Dict[str, float]:
    
    # Convert RGB to approximate spectral response
    rgb_wavelengths = np.array([600, 550, 450]) # Important peaks
    rgb_response = np.array([rgb_data['red'], rgb_data['green'], rgb_data['blue']])
    
    # Interpolate to match spectral library resolution 
    interp_func = interp1d(rgb_wavelengths, rgb_response, kind='linear', 
                          bounds_error=False, fill_value='extrapolate')
    estimated_spectrum = interp_func(wavelengths)
    
    # Normalize
    estimated_spectrum = (estimated_spectrum - estimated_spectrum.min()) / \
                        (estimated_spectrum.max() - estimated_spectrum.min() + 1e-6)
    
    # Calculate spectral matching metrics
    flower_similarity = 1 - cosine(estimated_spectrum, flower_spectrum)
    background_similarity = 1 - cosine(estimated_spectrum, background_spectrum)
    
    def spectral_angle(s1, s2):
        return np.arccos(np.dot(s1, s2) / (np.linalg.norm(s1) * np.linalg.norm(s2) + 1e-6))
    
    flower_angle = spectral_angle(estimated_spectrum, flower_spectrum)
    background_angle = spectral_angle(estimated_spectrum, background_spectrum)
    
    # Calculate spectral indices at key wavelengths 
    red_idx = np.argmin(np.abs(wavelengths - 650))
    green_idx = np.argmin(np.abs(wavelengths - 550)) 
    blue_idx = np.argmin(np.abs(wavelengths - 450))
    
    red_reflectance = estimated_spectrum[red_idx]
    green_reflectance = estimated_spectrum[green_idx]
    blue_reflectance = estimated_spectrum[blue_idx]
    
    # Feature set from the model netbook
    features = {
        'flower_similarity': max(0, flower_similarity),
        'background_similarity': max(0, background_similarity),
        'flower_angle': flower_angle,
        'background_angle': background_angle,
        'spectral_match_ratio': flower_similarity / (background_similarity + 1e-6),
        'reflectance_450nm': blue_reflectance,
        'reflectance_550nm': green_reflectance,
        'reflectance_650nm': red_reflectance,
        'spectral_slope': (red_reflectance - blue_reflectance) / (650 - 450 + 1e-6),
        'green_peak_ratio': green_reflectance / ((red_reflectance + blue_reflectance)/2 + 1e-6),
        'flower_color_ratio': green_reflectance / (red_reflectance + 1e-6),
        'spectral_entropy': stats.entropy(estimated_spectrum + 1e-6),
        'spectral_variance': np.var(estimated_spectrum)
    }
    
    return features

def predict_flower_coverage(features: Dict[str, float]) -> float:
    """Predict using your trained Random Forest model"""
    if model_assets is None:
        return 0.0
    
    model = model_assets['model']
    scaler = model_assets['scaler']
    feature_names = model_assets['feature_names']
    
    # Feature vector
    feature_vector = np.array([[features.get(f, 0) for f in feature_names]])
    feature_vector_scaled = scaler.transform(feature_vector)
    
    coverage = model.predict(feature_vector_scaled)[0]
    return max(0, min(1, coverage))

def coverage_to_category(coverage: float) -> str:
    """Convert to frontend-friendly categories"""
    if coverage < 0.05:
        return 'none'
    elif coverage < 0.2:
        return 'sparse'
    elif coverage < 0.5:
        return 'moderate'
    elif coverage < 0.8:
        return 'dense'
    else:
        return 'very_dense'

def coverage_to_intensity(coverage: float) -> str:
    """Convert to intensity levels for mapping"""
    if coverage < 0.1:
        return "none"
    elif coverage < 0.2:
        return "low"
    elif coverage < 0.5:
        return "medium"
    elif coverage < 0.8:
        return "high"
    else:
        return "very_high"

# === MOCK SATELLITE DATA ===

async def get_satellite_rgb_data(lat: float, lng: float, date: str) -> Dict[str, float]:
    """Mock function to get RGB values from satellite data"""
    # Replace Sentinel2 data from data of Planetary Computer
    
    # Simulate seasonal and geographic patterns
    import math
    
    # Seasonal effect (summer = more flowers)
    month = int(date.split('-')[1])
    seasonal_factor = 0.3 + 0.5 * math.sin((month - 6) * math.pi / 6)  # Peak in June
    
    # Geographic patterns (simulate flower hotspots)
    # European alpine flowers
    if 45 < lat < 48 and 5 < lng < 15:
        base_green = 0.6
    # California poppies  
    elif 33 < lat < 35 and -120 < lng < -117:
        base_green = 0.7
    # Dutch tulips
    elif 52 < lat < 53 and 4 < lng < 6:
        base_green = 0.65
    # Default background
    else:
        base_green = 0.4
    
    # Add some random flower patches
    flower_patch = math.sin(lat * 10) * math.cos(lng * 10) * 0.2 + 0.1
    
    green = base_green + flower_patch * seasonal_factor
    red = 0.3 + flower_patch * 0.1 * seasonal_factor
    blue = 0.2 + flower_patch * 0.05 * seasonal_factor
    
    # Add noise
    noise = np.random.normal(0, 0.02, 3)
    red = np.clip(red + noise[0], 0.1, 0.8)
    green = np.clip(green + noise[1], 0.2, 0.9) 
    blue = np.clip(blue + noise[2], 0.1, 0.7)
    
    return {
        'red': float(red),
        'green': float(green),
        'blue': float(blue)
    }

# === ENDPOINTS FOR FRONTEND ===

@app.get("/")
async def root():
    return {
        "message": "Global Flower Coverage API",
        "model": "Physics-based Random Forest",
        "performance": model_assets['performance'] if model_assets else "Model not loaded",
        "endpoints": {
            "single_point": "/api/point",
            "region_scan": "/api/region", 
            "global_sample": "/api/global-sample"
        }
    }

@app.get("/api/point")
async def detect_single_point(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"), 
    date: str = Query("2023-06-15", description="Date in YYYY-MM-DD")
) -> PointDetectionResponse:
    """Detect flower coverage at a single point"""
    try:
        logger.info(f"Point detection: ({lat}, {lng}) on {date}")
        
        # Get satellite RGB data
        rgb_data = await get_satellite_rgb_data(lat, lng, date)
        
        if model_assets is None:
            raise HTTPException(status_code=500, detail="Model not loaded")
        
        # Extract features using your notebook logic
        features = extract_spectral_features_from_rgb(
            rgb_data,
            model_assets['wavelengths'],
            model_assets['avg_flower_spectrum'], 
            model_assets['avg_background_spectrum']
        )
        
        # Predict coverage
        coverage = predict_flower_coverage(features)
        category = coverage_to_category(coverage)
        intensity = coverage_to_intensity(coverage)
        
        return PointDetectionResponse(
            coverage=round(coverage, 3),
            category=category,
            intensity=intensity,
            confidence=0.85,  # Based on your R² score
            coordinates=[lat, lng]
        )
        
    except Exception as e:
        logger.error(f"Point detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/region")
async def scan_region(request: RegionScanRequest) -> RegionScanResponse:
    """Scan a geographic region for blooming events"""
    try:
        logger.info(f"Region scan: {request.north},{request.south},{request.east},{request.west}")
        
        # Determine grid resolution
        if request.resolution == "high":
            grid_spacing = 0.01  # ~1km
        elif request.resolution == "medium": 
            grid_spacing = 0.02  # ~2km
        else:  # low
            grid_spacing = 0.05  # ~5km
        
        # Generate grid points
        lat_points = np.arange(request.south, request.north, grid_spacing)
        lng_points = np.arange(request.west, request.east, grid_spacing)
        
        points = []
        for lat in lat_points:
            for lng in lng_points:
                points.append((lat, lng))
        
        logger.info(f"Scanning {len(points)} points")
        
        # Process points concurrently
        tasks = []
        for lat, lng in points:
            task = process_grid_point(lat, lng, request.date)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect blooming events
        events = []
        for result in results:
            if isinstance(result, dict) and result['coverage'] > 0.1:  # Greater than 10% considered blooming event
                events.append(BloomingEvent(
                    lat=result['lat'],
                    lng=result['lng'],
                    coverage=result['coverage'],
                    intensity=result['intensity'],
                    category=result['category']
                ))
        
        return RegionScanResponse(
            events=events,
            totalPoints=len(points),
            bloomingPoints=len(events),
            date=request.date,
            region={
                "north": request.north,
                "south": request.south, 
                "east": request.east,
                "west": request.west
            }
        )
        
    except Exception as e:
        logger.error(f"Region scan error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/global-sample")
async def get_global_sample(date: str = Query("2023-06-15")) -> RegionScanResponse:
    """Get a sample of global flower coverage for initial map loading"""
    
    # Sample points around the world
    sample_points = [
        # Europe
        (47.3769, 8.5417),   # Zurich
        (48.8566, 2.3522),   # Paris
        (52.5200, 13.4050),  # Berlin
        (51.5074, -0.1278),  # London
        
        # North America
        (40.7128, -74.0060), # New York
        (34.0522, -118.2437), # Los Angeles
        (43.6532, -79.3832), # Toronto
        
        # Asia
        (35.6762, 139.6503), # Tokyo
        (31.2304, 121.4737), # Shanghai
        (28.6139, 77.2090),  # Delhi
        
        # Southern Hemisphere
        (-33.8688, 151.2093), # Sydney
        (-23.5505, -46.6333), # Sao Paulo
        (-1.2921, 36.8219),   # Nairobi
    ]
    
    # Add more dense sampling in known flower regions
    flower_regions = [
        # Swiss Alps (dense sampling)
        (46.5, 8.0), (46.6, 8.2), (46.7, 8.4), (46.8, 8.6),
        # California (dense sampling)  
        (34.0, -118.5), (34.1, -118.3), (34.2, -118.1),
        # Netherlands (dense sampling)
        (52.2, 4.8), (52.3, 5.0), (52.4, 5.2),
    ]
    
    all_points = sample_points + flower_regions
    
    # Process all points
    tasks = []
    for lat, lng in all_points:
        task = process_grid_point(lat, lng, date)
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    events = []
    for result in results:
        if isinstance(result, dict) and result['coverage'] > 0.05:  # Lower threshold for global view
            events.append(BloomingEvent(
                lat=result['lat'],
                lng=result['lng'],
                coverage=result['coverage'],
                intensity=result['intensity'],
                category=result['category']
            ))
    
    return RegionScanResponse(
        events=events,
        totalPoints=len(all_points),
        bloomingPoints=len(events),
        date=date,
        region={"north": 85, "south": -85, "east": 180, "west": -180}
    )

async def process_grid_point(lat: float, lng: float, date: str) -> Dict:
    """Process a single grid point for the frontend"""
    try:
        rgb_data = await get_satellite_rgb_data(lat, lng, date)
        
        if model_assets is None:
            return {'lat': lat, 'lng': lng, 'coverage': 0.0, 'intensity': 'none', 'category': 'none'}
        
        features = extract_spectral_features_from_rgb(
            rgb_data,
            model_assets['wavelengths'],
            model_assets['avg_flower_spectrum'],
            model_assets['avg_background_spectrum']
        )
        
        coverage = predict_flower_coverage(features)
        
        return {
            'lat': lat,
            'lng': lng,
            'coverage': round(coverage, 3),
            'intensity': coverage_to_intensity(coverage),
            'category': coverage_to_category(coverage)
        }
    except Exception as e:
        logger.warning(f"Grid point processing failed: {e}")
        return {'lat': lat, 'lng': lng, 'coverage': 0.0, 'intensity': 'none', 'category': 'none'}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy" if model_assets else "model_missing",
        "timestamp": datetime.utcnow().isoformat(),
        "model_performance": model_assets['performance'] if model_assets else None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)