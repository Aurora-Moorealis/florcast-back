# flower_detection_sentinelhub.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import joblib
import numpy as np
from datetime import datetime, timedelta
from sentinelhub import SentinelHubClient

app = FastAPI(
    title="Global Flower Detection API - SentinelHub",
    description="Detect flower coverage using Sentinel-2 satellite imagery",
    version="1.0.0"
)

# Configuration
SENTINEL_CONFIG = {
    "client_id": "your-client-id",
    "client_secret": "your-client-secret", 
    "instance_id": "your-instance-id"
}

# Initialize clients
sh_client = SentinelHubClient(**SENTINEL_CONFIG)
model_assets = joblib.load('physics_coverage_model.joblib')

class DetectionRequest(BaseModel):
    coordinates: List[float]  # [lat, lon]
    date: str  # YYYY-MM-DD
    area_km: float = 2.0
    resolution: int = 10

class DetectionResponse(BaseModel):
    flower_coverage: float
    confidence: float
    coverage_category: str
    coordinates: List[float]
    date: str
    area_km: float
    valid_pixel_ratio: float

class TemporalAnalysisRequest(BaseModel):
    coordinates: List[float]
    start_date: str
    end_date: str
    interval_days: int = 10

class TemporalAnalysisResponse(BaseModel):
    coordinates: List[float]
    time_series: List[Dict[str, float]]
    peak_flowering_date: str
    peak_coverage: float
    trend: str  # increasing, decreasing, stable

@app.post("/detect-flowers", response_model=DetectionResponse)
async def detect_flowers(request: DetectionRequest):
    """Detect flower coverage for a specific location and date"""
    try:
        # 1. Get Sentinel-2 data
        raw_bands = sh_client.get_sentinel_data(
            coordinates=request.coordinates,
            date=request.date,
            buffer_km=request.area_km,
            resolution=request.resolution
        )
        
        # 2. Preprocess bands
        processed_bands = sh_client.preprocess_bands(raw_bands)
        
        # 3. Calculate valid pixel ratio
        valid_pixels = ~np.isnan(processed_bands['B02'])
        valid_ratio = np.sum(valid_pixels) / valid_pixels.size
        
        if valid_ratio < 0.3:  # Require at least 30% valid pixels
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient valid data (only {valid_ratio:.1%} clear pixels)"
            )
        
        # 4. Extract features and predict
        features = extract_sentinel_features(processed_bands)
        coverage = predict_coverage(features)
        
        # 5. Determine category
        category = coverage_to_category(coverage)
        
        return DetectionResponse(
            flower_coverage=coverage,
            confidence=0.85,  # Based on your model's R²
            coverage_category=category,
            coordinates=request.coordinates,
            date=request.date,
            area_km=request.area_km,
            valid_pixel_ratio=valid_ratio
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/temporal-analysis", response_model=TemporalAnalysisResponse)
async def temporal_analysis(request: TemporalAnalysisRequest):
    """Analyze flower coverage over time"""
    try:
        start = datetime.strptime(request.start_date, "%Y-%m-%d")
        end = datetime.strptime(request.end_date, "%Y-%m-%d")
        
        time_series = []
        current_date = start
        
        while current_date <= end:
            date_str = current_date.strftime("%Y-%m-%d")
            
            try:
                # Get coverage for this date
                raw_bands = sh_client.get_sentinel_data(
                    coordinates=request.coordinates,
                    date=date_str,
                    buffer_km=2.0
                )
                
                processed_bands = sh_client.preprocess_bands(raw_bands)
                features = extract_sentinel_features(processed_bands)
                coverage = predict_coverage(features)
                
                time_series.append({
                    "date": date_str,
                    "coverage": coverage,
                    "status": "success"
                })
                
            except Exception as e:
                time_series.append({
                    "date": date_str,
                    "coverage": 0.0,
                    "status": f"error: {str(e)}"
                })
            
            current_date += timedelta(days=request.interval_days)
        
        # Find peak flowering
        successful_readings = [ts for ts in time_series if ts["status"] == "success"]
        if successful_readings:
            peak = max(successful_readings, key=lambda x: x["coverage"])
            peak_date = peak["date"]
            peak_coverage = peak["coverage"]
        else:
            peak_date = "unknown"
            peak_coverage = 0.0
        
        # Determine trend
        trend = analyze_trend(time_series)
        
        return TemporalAnalysisResponse(
            coordinates=request.coordinates,
            time_series=time_series,
            peak_flowering_date=peak_date,
            peak_coverage=peak_coverage,
            trend=trend
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def extract_sentinel_features(bands_data: Dict[str, np.ndarray]) -> Dict[str, float]:
    """Extract physics-based features from Sentinel-2 bands"""
    # Use the same feature extraction logic from your notebook
    # but adapted for Sentinel-2 bands
    
    wavelengths = model_assets['wavelengths']
    flower_spectrum = model_assets['avg_flower_spectrum']
    background_spectrum = model_assets['avg_background_spectrum']
    
    # Calculate mean reflectance for each band (ignoring NaN/cloudy pixels)
    blue_mean = np.nanmean(bands_data['B02'])  # 490nm
    green_mean = np.nanmean(bands_data['B03'])  # 560nm
    red_mean = np.nanmean(bands_data['B04'])    # 665nm
    nir_mean = np.nanmean(bands_data['B08'])    # 842nm
    
    # Create estimated spectrum (similar to your approach)
    sentinel_wavelengths = np.array([490, 560, 665, 842])
    sentinel_response = np.array([blue_mean, green_mean, red_mean, nir_mean])
    
    from scipy.interpolate import interp1d
    interp_func = interp1d(sentinel_wavelengths, sentinel_response, 
                          kind='linear', bounds_error=False, fill_value='extrapolate')
    estimated_spectrum = interp_func(wavelengths)
    
    # Normalize
    estimated_spectrum = (estimated_spectrum - estimated_spectrum.min()) / \
                        (estimated_spectrum.max() - estimated_spectrum.min() + 1e-6)
    
    # Calculate all the physics-based features from your model
    from scipy.spatial.distance import cosine
    from scipy import stats
    
    flower_similarity = 1 - cosine(estimated_spectrum, flower_spectrum)
    background_similarity = 1 - cosine(estimated_spectrum, background_spectrum)
    
    def spectral_angle(s1, s2):
        return np.arccos(np.dot(s1, s2) / (np.linalg.norm(s1) * np.linalg.norm(s2) + 1e-6))
    
    # ... include all your feature calculations from the notebook
    # This should match exactly what you trained on
    
    features = {
        'flower_similarity': max(0, flower_similarity),
        'background_similarity': max(0, background_similarity),
        # Include all 15 features from your model
        # ... 
    }
    
    return features

def predict_coverage(features: Dict[str, float]) -> float:
    """Predict flower coverage using the trained model"""
    model = model_assets['model']
    scaler = model_assets['scaler']
    feature_names = model_assets['feature_names']
    
    # Create feature vector in correct order
    feature_vector = np.array([[features[f] for f in feature_names]])
    feature_vector_scaled = scaler.transform(feature_vector)
    
    coverage = model.predict(feature_vector_scaled)[0]
    return max(0, min(1, coverage))  # Ensure valid range

def coverage_to_category(coverage: float) -> str:
    """Convert coverage value to category"""
    if coverage < 0.05:
        return 'No Flowers'
    elif coverage < 0.2:
        return 'Sparse (1-20%)'
    elif coverage < 0.5:
        return 'Moderate (20-50%)'
    elif coverage < 0.8:
        return 'Dense (50-80%)'
    else:
        return 'Very Dense (80-100%)'

def analyze_trend(time_series: List[Dict]) -> str:
    """Analyze flowering trend over time"""
    successful = [ts for ts in time_series if ts["status"] == "success"]
    if len(successful) < 2:
        return "insufficient_data"
    
    coverages = [ts["coverage"] for ts in successful]
    
    # Simple trend analysis
    if len(coverages) >= 3:
        first_half = np.mean(coverages[:len(coverages)//2])
        second_half = np.mean(coverages[len(coverages)//2:])
        
        if second_half > first_half + 0.05:
            return "increasing"
        elif second_half < first_half - 0.05:
            return "decreasing"
    
    return "stable"

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/")
async def root():
    return {
        "message": "Global Flower Detection API",
        "version": "1.0.0",
        "model_performance": model_assets['performance']
    }