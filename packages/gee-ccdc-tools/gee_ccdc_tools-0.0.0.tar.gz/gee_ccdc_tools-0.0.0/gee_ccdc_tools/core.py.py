import ee
import datetime

def initialize_ee(project='proyecto-cobertura-boscosa'):
    """Autenticación e inicialización de Google Earth Engine"""
    ee.Authenticate()
    ee.Initialize()

def load_assets():
    """Cargar límites de distritos y corregimientos"""
    Distrito = ee.FeatureCollection(
        "projects/proyecto-cobertura-boscosa/assets/Mapas_Panama/Lim_Distrito")
    Corregimientos = ee.FeatureCollection(
        "projects/proyecto-cobertura-boscosa/assets/Mapas_Panama/Lim_Corregimiento")
    return Distrito, Corregimientos

def filter_study_area(corregimientos, names_list):
    """Filtrar corregimientos según lista de nombres"""
    return corregimientos.filter(ee.Filter.inList('LMCO_NOMB', names_list))

def clip_collection(img_collection, study_area):
    """Recortar todas las imágenes de la colección a la zona de estudio"""
    return img_collection.map(lambda img: img.clip(study_area))

def apply_cloud_score_plus(img_col, roi, start, end, qa_band='cs_cdf', threshold=0.8):
    """Enmascaramiento con Cloud Score Plus"""
    cs_plus = ee.ImageCollection('GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED') \
        .filterBounds(roi).filterDate(start, end)
    
    joined = ee.Join.inner().apply(
        primary=img_col,
        secondary=cs_plus,
        condition=ee.Filter.equals(leftField='system:index', rightField='system:index')
    )

    def merge_and_mask(pair):
        primary = ee.Image(pair.get('primary'))
        score = ee.Image(pair.get('secondary')).select(qa_band)
        return primary.updateMask(score.gte(threshold))

    return ee.ImageCollection(joined.map(merge_and_mask))

def add_ndvi(img):
    """Añadir banda NDVI a imagen Sentinel-2"""
    ndvi = img.normalizedDifference(['B8', 'B12']).multiply(10000).int16().rename('ndvi')
    return img.addBands(ndvi)

def monthly_rgb_median(img_collection, study_area, year, month):
    """RGB mediana mensual"""
    start = ee.Date.fromYMD(year, month, 1)
    end = start.advance(1, 'month')
    monthly_collection = img_collection.filterDate(start, end).filterBounds(study_area)
    return monthly_collection.median().select(['B4', 'B3', 'B2','B8','B8A','B5','B12']).clip(study_area)

def monthly_ndvi_median(img_collection, study_area, year, month):
    """NDVI mediana mensual"""
    start = ee.Date.fromYMD(year, month, 1)
    end = start.advance(1, 'month')
    monthly = img_collection.filterDate(start, end).median()
    ndvi = monthly.normalizedDifference(['B8', 'B12']).rename('NDVI')
    return ndvi.clip(study_area)

def run_ccdc(img_collection):
    """Ejecutar CCDC sobre imágenes con NDVI"""
    s2_ndvi = img_collection.map(add_ndvi)
    ccdc = ee.Algorithms.TemporalSegmentation.Ccdc(
        s2_ndvi.select(['ndvi', 'B5', 'B12']),
        ['ndvi', 'B5', 'B12'],    # inputBands
        ['B5', 'B12'],            # tmaskBands
        8,                        # minObservations
        0.90,                     # chiSquareProbability
        0.80,                     # minNumOfObservations
        2,                        # minNumOfSegments
        50,                       # recoveryThreshold
        35000                     # lambda
    )
    # Último cambio
    tbreak = ccdc.select('tBreak')
    argmax = tbreak.arrayArgmax()
    argmax_scalar = argmax.arrayFlatten([['argmax_array']])
    last_break = tbreak.arrayGet(argmax_scalar).focal_min(1).focal_max(1)
    
    # Convertir a año y mes
    year = last_break.divide(1000*60*60*24*365.25).add(1970).floor()
    months_since_1970 = last_break.divide(1000*60*60*24*30.44).floor()
    month = months_since_1970.subtract(year.subtract(1970).multiply(12)).mod(12).add(1)
    year_month = year.multiply(100).add(month).rename('year_month')
    return year_month
