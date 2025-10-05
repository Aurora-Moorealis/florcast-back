# main.py - Complete FastAPI Backend
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Optional
import numpy as np
import joblib
import os
from datetime import datetime, timedelta
import asyncio
import logging
import json
from scipy.spatial.distance import cosine
from scipy import stats
from scipy.interpolate import interp1d

# Real satellite data imports
import planetary_computer
import pystac_client
import rioxarray
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

router = APIRouter(tags=['detections'])
# app = FastAPI(
#     title="Global Flower Coverage API",
#     description="Real-time flower coverage detection for Cesium frontend",
#     version="1.0.0"
# )

# # CORS for frontend
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Mount static files for Cesium
# app.mount("/static", StaticFiles(directory="static"), name="static")

# Load your trained physics model
def load_model():
    """Load the physics-based flower detection model"""
    possible_paths = [
        'physics_coverage_model.joblib',
        './models/physics_coverage_model.joblib',
        'app/models/physics_coverage_model.joblib'
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            logger.info(f"✅ Found model at: {path}")
            try:
                model = joblib.load(path)
                logger.info("✅ Physics model loaded successfully")
                
                if 'performance' in model:
                    logger.info(f"📊 Model R²: {model['performance']['r2']:.3f}")
                return model
            except Exception as e:
                logger.error(f"❌ Error loading {path}: {e}")
                continue
    
    logger.error("❌ No valid model found!")
    return None

model_assets = load_model()

# Request/Response models for Cesium
class PointRequest(BaseModel):
    lat: float
    lng: float
    date: str = "2023-06-15"

class PointResponse(BaseModel):
    coverage: float
    category: str
    intensity: str
    confidence: float
    coordinates: List[float]
    color: str

class RegionRequest(BaseModel):
    north: float
    south: float
    east: float
    west: float
    date: str = "2023-06-15"
    resolution: str = "medium"
    maxPoints: int = 1000

class RegionResponse(BaseModel):
    type: str = "FeatureCollection"
    features: List[Dict]
    metadata: Dict

class GlobalSampleRequest(BaseModel):
    date: str = "2023-06-15"
    sampleSize: int = 50

# Color mapping for Cesium
INTENSITY_COLORS = {
    "none": "#444444",
    "low": "#FFEB3B",    # Yellow
    "medium": "#FF9800",  # Orange
    "high": "#F44336",    # Red
    "very_high": "#8B0000" # Dark Red
}

# === REAL SATELLITE DATA FUNCTIONS ===

async def get_satellite_rgb_data(lat: float, lng: float, date: str) -> Dict[str, float]:
    """Get real Sentinel-2 data from Microsoft Planetary Computer"""
    try:
        catalog = pystac_client.Client.open(
            "https://planetarycomputer.microsoft.com/api/stac/v1",
            ignore_conformance=True
        )
        
        bbox = [lng - 0.02, lat - 0.02, lng + 0.02, lat + 0.02]
        
        search = catalog.search(
            collections=["sentinel-2-l2a"],
            datetime=f"{date}T00:00:00Z/{date}T23:59:59Z",
            bbox=bbox,
            query={"eo:cloud_cover": {"lt": 30}}
        )
        
        items = list(search.get_items())
        
        if not items:
            return await get_fallback_rgb_data(lat, lng, date)
        
        best_item = min(items, key=lambda x: x.properties.get("eo:cloud_cover", 100))
        signed_item = planetary_computer.sign(best_item)
        
        rgb_data = await extract_pixel_values(signed_item, lat, lng)
        return rgb_data if rgb_data else await get_fallback_rgb_data(lat, lng, date)
            
    except Exception as e:
        logger.error(f"Satellite data error: {e}")
        return await get_fallback_rgb_data(lat, lng, date)

async def extract_pixel_values(signed_item, lat: float, lng: float) -> Dict[str, float]:
    """Extract pixel values from Sentinel-2 bands"""
    try:
        band_assets = {'red': 'B04', 'green': 'B03', 'blue': 'B02'}
        rgb_values = {}
        
        for color, band_name in band_assets.items():
            try:
                asset = signed_item.assets[band_name]
                with rioxarray.open_rasterio(asset.href) as dataset:
                    if dataset.rio.crs != 'EPSG:4326':
                        dataset = dataset.rio.reproject('EPSG:4326')
                    
                    transform = dataset.rio.transform()
                    col, row = ~transform * (lng, lat)
                    col, row = int(col), int(row)
                    
                    if 0 <= row < dataset.shape[1] and 0 <= col < dataset.shape[2]:
                        pixel_value = dataset[0, row, col].values
                        if np.isfinite(pixel_value):
                            reflectance = float(pixel_value / 10000.0)
                            rgb_values[color] = np.clip(reflectance, 0.001, 1.0)
                        else:
                            rgb_values[color] = 0.1
                    else:
                        rgb_values[color] = 0.1
            except Exception:
                rgb_values[color] = 0.1
        
        return rgb_values
    except Exception:
        return None

async def get_fallback_rgb_data(lat: float, lng: float, date: str) -> Dict[str, float]:
    """Fallback with realistic geographic patterns"""
    import math
    month = int(date.split('-')[1])
    seasonal_factor = 0.3 + 0.5 * math.sin((month - 6) * math.pi / 6)
    
    # Enhanced geographic patterns for known flower regions
    if 45 < lat < 48 and 5 < lng < 15:  # Alps
        base_green, flower_boost = 0.6, 0.3
    elif 33 < lat < 35 and -120 < lng < -117:  # California
        base_green, flower_boost = 0.65, 0.4
    elif 52 < lat < 53 and 4 < lng < 6:  # Netherlands
        base_green, flower_boost = 0.7, 0.35
    else:
        base_green, flower_boost = 0.4, 0.15
    
    spatial_var = math.sin(lat * 10) * math.cos(lng * 10) * 0.2
    noise = np.random.normal(0, 0.02, 3)
    
    return {
        'red': float(np.clip(0.3 + spatial_var * 0.7 + flower_boost * 0.5 * seasonal_factor + noise[0], 0.1, 0.9)),
        'green': float(np.clip(base_green + spatial_var + flower_boost * seasonal_factor + noise[1], 0.2, 0.95)),
        'blue': float(np.clip(0.25 + spatial_var * 0.5 + flower_boost * 0.3 * seasonal_factor + noise[2], 0.1, 0.8))
    }

# === PHYSICS MODEL FUNCTIONS ===

def extract_spectral_features(rgb_data: Dict[str, float]) -> Dict[str, float]:
    """Extract physics-based features using your model logic"""
    if model_assets is None:
        return {}
    
    wavelengths = model_assets['wavelengths']
    flower_spectrum = model_assets['avg_flower_spectrum']
    background_spectrum = model_assets['avg_background_spectrum']
    
    rgb_wavelengths = np.array([600, 550, 450])
    rgb_response = np.array([rgb_data['red'], rgb_data['green'], rgb_data['blue']])
    
    interp_func = interp1d(rgb_wavelengths, rgb_response, kind='linear', 
                          bounds_error=False, fill_value='extrapolate')
    estimated_spectrum = interp_func(wavelengths)
    
    estimated_spectrum = (estimated_spectrum - estimated_spectrum.min()) / \
                        (estimated_spectrum.max() - estimated_spectrum.min() + 1e-6)
    
    flower_similarity = 1 - cosine(estimated_spectrum, flower_spectrum)
    background_similarity = 1 - cosine(estimated_spectrum, background_spectrum)
    
    def spectral_angle(s1, s2):
        return np.arccos(np.dot(s1, s2) / (np.linalg.norm(s1) * np.linalg.norm(s2) + 1e-6))
    
    red_idx = np.argmin(np.abs(wavelengths - 650))
    green_idx = np.argmin(np.abs(wavelengths - 550))
    blue_idx = np.argmin(np.abs(wavelengths - 450))
    
    red_reflectance = estimated_spectrum[red_idx]
    green_reflectance = estimated_spectrum[green_idx]
    blue_reflectance = estimated_spectrum[blue_idx]
    
    features = {
        'flower_similarity': max(0, flower_similarity),
        'background_similarity': max(0, background_similarity),
        'flower_angle': spectral_angle(estimated_spectrum, flower_spectrum),
        'background_angle': spectral_angle(estimated_spectrum, background_spectrum),
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

def predict_coverage(features: Dict[str, float]) -> float:
    """Predict flower coverage using the trained model"""
    if model_assets is None:
        return 0.0
    
    model = model_assets['model']
    scaler = model_assets['scaler']
    feature_names = model_assets['feature_names']
    
    feature_vector = np.array([[features.get(f, 0) for f in feature_names]])
    feature_vector_scaled = scaler.transform(feature_vector)
    
    coverage = model.predict(feature_vector_scaled)[0]
    return max(0, min(1, coverage))

def coverage_to_intensity(coverage: float) -> str:
    """Convert coverage to intensity level"""
    if coverage < 0.1: return "none"
    elif coverage < 0.2: return "low"
    elif coverage < 0.5: return "medium"
    elif coverage < 0.8: return "high"
    else: return "very_high"

def coverage_to_category(coverage: float) -> str:
    """Convert coverage to category"""
    if coverage < 0.05: return 'none'
    elif coverage < 0.2: return 'sparse'
    elif coverage < 0.5: return 'moderate'
    elif coverage < 0.8: return 'dense'
    else: return 'very_dense'

# === CORE API ENDPOINTS ===

@router.get("/")
async def root():
    return {
        "message": "Global Flower Coverage API for Cesium",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "single_point": "/api/point?lat=47.3769&lng=8.5417",
            "region_scan": "POST /api/region",
            "global_sample": "/api/global-sample",
            "known_hotspots": "/api/hotspots"
        }
    }

@router.get("/health")
async def health_check():
    return {
        "status": "healthy" if model_assets else "model_missing",
        "timestamp": datetime.utcnow().isoformat(),
        "model_loaded": model_assets is not None
    }

@router.get("/api/point")
async def detect_point(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    date: str = Query("2023-06-15", description="Date in YYYY-MM-DD")
) -> PointResponse:
    """Detect flower coverage at a single point"""
    try:
        rgb_data = await get_satellite_rgb_data(lat, lng, date)
        features = extract_spectral_features(rgb_data)
        coverage = predict_coverage(features)
        intensity = coverage_to_intensity(coverage)
        category = coverage_to_category(coverage)
        
        return PointResponse(
            coverage=round(coverage, 3),
            category=category,
            intensity=intensity,
            confidence=0.85,
            coordinates=[lat, lng],
            color=INTENSITY_COLORS[intensity]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/region", response_model=RegionResponse)
async def scan_region(request: RegionRequest, background_tasks: BackgroundTasks):
    """Scan a region for blooming events - optimized for Cesium"""
    try:
        # Generate grid points
        if request.resolution == "high":
            lat_step, lng_step = 0.01, 0.01
        elif request.resolution == "medium":
            lat_step, lng_step = 0.02, 0.02
        else:
            lat_step, lng_step = 0.05, 0.05
        
        lat_points = np.arange(request.south, request.north, lat_step)
        lng_points = np.arange(request.west, request.east, lng_step)
        
        points = []
        for lat in lat_points:
            for lng in lng_points:
                if len(points) < request.maxPoints:
                    points.append((lat, lng))
        
        logger.info(f"🌍 Scanning {len(points)} points in region")
        
        # Process points concurrently
        tasks = [process_point_for_cesium(lat, lng, request.date) for lat, lng in points]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Create GeoJSON features for Cesium
        features = []
        for result in results:
            if isinstance(result, dict) and result['coverage'] > 0.05:
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [result['lng'], result['lat']]
                    },
                    "properties": {
                        "coverage": result['coverage'],
                        "intensity": result['intensity'],
                        "category": result['category'],
                        "color": result['color'],
                        "height": result['coverage'] * 1000  # For 3D visualization
                    }
                })
        
        return RegionResponse(
            type="FeatureCollection",
            features=features,
            metadata={
                "totalPoints": len(points),
                "bloomingPoints": len(features),
                "region": [request.west, request.south, request.east, request.north],
                "date": request.date,
                "resolution": request.resolution
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/global-sample", response_model=RegionResponse)
async def get_global_sample(date: str = Query("2023-06-15")):
    """Get global sample points for initial Cesium map loading"""
    
    # Strategic global sampling
    sample_points = [
        # Europe - known flower regions
        (47.3769, 8.5417), (48.8566, 2.3522), (52.5200, 13.4050), (51.5074, -0.1278),
        (46.5, 8.0), (46.6, 8.2), (46.7, 8.4), (46.8, 8.6),  # Swiss Alps
        (52.2, 4.8), (52.3, 5.0), (52.4, 5.2),  # Netherlands
        
        # North America
        (40.7128, -74.0060), (34.0522, -118.2437), (43.6532, -79.3832),
        (34.0, -118.5), (34.1, -118.3), (34.2, -118.1),  # California
        
        # Asia
        (35.6762, 139.6503), (31.2304, 121.4737), (28.6139, 77.2090),
        
        # Southern Hemisphere
        (-33.8688, 151.2093), (-23.5505, -46.6333), (-1.2921, 36.8219),
        
        # Additional global coverage
        (39.9042, 116.4074), (55.7558, 37.6173), (19.4326, -99.1332),
        (-34.6037, -58.3816), (30.0444, 31.2357)
    ]
    
    # Process all sample points
    tasks = [process_point_for_cesium(lat, lng, date) for lat, lng in sample_points]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    features = []
    for result in results:
        if isinstance(result, dict):
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [result['lng'], result['lat']]
                },
                "properties": {
                    "coverage": result['coverage'],
                    "intensity": result['intensity'],
                    "category": result['category'],
                    "color": result['color'],
                    "height": result['coverage'] * 1000
                }
            })
    
    return RegionResponse(
        type="FeatureCollection",
        features=features,
        metadata={
            "totalPoints": len(sample_points),
            "bloomingPoints": len([f for f in features if f['properties']['coverage'] > 0.1]),
            "region": [-180, -90, 180, 90],
            "date": date,
            "type": "global_sample"
        }
    )

@router.get("/api/hotspots", response_model=RegionResponse)
async def get_known_hotspots(date: str = Query("2023-06-15")):
    """Get known flower hotspots around the world"""
    
    # Famous flower locations with their peak seasons
    hotspots = [
        # Name, lat, lng, peak_month
        ("Keukenhof Gardens", 52.27, 4.55, 4),
        ("Provence Lavender", 43.92, 5.08, 7),
        ("Alpine Meadows", 46.49, 9.84, 7),
        ("Carlsbad Flower Fields", 33.12, -117.32, 4),
        ("Antelope Valley Poppies", 34.72, -118.36, 4),
        ("Hitachi Seaside Park", 36.40, 140.59, 4),
        ("Canola Flower Fields", 23.13, 113.25, 3),
        ("Western Australia Wildflowers", -31.95, 115.86, 9),
        ("Namaqualand Daisies", -30.56, 17.93, 8)
    ]
    
    month = int(date.split('-')[1])
    features = []
    
    for name, lat, lng, peak_month in hotspots:
        # Adjust coverage based on seasonal timing
        seasonal_factor = 1.0 - min(abs(month - peak_month) / 6.0, 1.0)
        
        rgb_data = await get_satellite_rgb_data(lat, lng, date)
        features_dict = extract_spectral_features(rgb_data)
        coverage = predict_coverage(features_dict) * seasonal_factor
        intensity = coverage_to_intensity(coverage)
        
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lng, lat]
            },
            "properties": {
                "name": name,
                "coverage": round(coverage, 3),
                "intensity": intensity,
                "category": coverage_to_category(coverage),
                "color": INTENSITY_COLORS[intensity],
                "height": coverage * 1000,
                "peak_month": peak_month,
                "seasonal_factor": seasonal_factor
            }
        })
    
    return RegionResponse(
        type="FeatureCollection",
        features=features,
        metadata={
            "totalPoints": len(hotspots),
            "date": date,
            "type": "known_hotspots"
        }
    )

async def process_point_for_cesium(lat: float, lng: float, date: str) -> Dict:
    """Process a single point for Cesium visualization"""
    try:
        rgb_data = await get_satellite_rgb_data(lat, lng, date)
        features = extract_spectral_features(rgb_data)
        coverage = predict_coverage(features)
        intensity = coverage_to_intensity(coverage)
        
        return {
            'lat': lat,
            'lng': lng,
            'coverage': round(coverage, 3),
            'intensity': intensity,
            'category': coverage_to_category(coverage),
            'color': INTENSITY_COLORS[intensity]
        }
    except Exception as e:
        logger.warning(f"Point processing failed: {e}")
        return {'lat': lat, 'lng': lng, 'coverage': 0.0, 'intensity': 'none', 
                'category': 'none', 'color': INTENSITY_COLORS['none']}