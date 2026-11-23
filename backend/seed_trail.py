# reads .gpx files and seeds the database with the trail data (using Haversine formula to calculate distances between points)

from pathlib import Path

import gpxpy
import gpxpy.geo

from app.database import SessionLocal, engine
from app.models import Milestone, Trail

GPX_FILE_PATH = Path(__file__).parent / "data" / "testKokorinsko.gpx"

def load_points_from_gpx(file_path: Path) -> list[tuple[float, float]]:
    # Load points from a GPX file and return them as a list of (latitude, longitude) tuples.
    with open(file_path, "r", encoding="utf-8") as gpx_file:
        gpx = gpxpy.parse(gpx_file)
        
    points = list[tuple[float, float]] = []
    
    # Iterate through all tracks, segments, and points in the GPX file to extract latitude and longitude.
    # I have to do this, bcs this is how .gpx file is saved, it can have multiple tracks and segments, so I need to iterate through all of them to get all points.
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                points.append((point.latitude, point.longitude))\
    
    # Some apps dont use the hiearchy of tracks and segments, so I need to check if there are any points in the routes
    if not points:
        for route in gpx.routes:
            for point in route.points:
                points.append((point.latitude, point.longitude))
                
    return points
    
def haversine_distance(points: list[tuple[float, float]]) -> list[float]:
    # Calculate the Haversine distance between two points on the Earth specified by their latitude and longitude.
    adding_km = []
    for i in range(len(points)-1):
        prev_lat, prev_lng = points[i - 1]
        curr_lat, curr_lng = points[i]
        distance = gpxpy.geo.haversine_distance(prev_lat, prev_lng, curr_lat, curr_lng) / 1000  # Convert to kilometers
        adding_km.append(adding_km[-1] + distance)
        
        return adding_km

def seed_trail_database():
    # Database tables for testing
    Base.metadata.create_all(bind=engine)
    
    if not GPX_FILE_PATH.exists():
        raise FileNotFoundError(f"GPX file not found at {GPX_FILE_PATH}")
    
    db = SessionLocal()
    
    try:
        trail_title = "kokorinsko (test)"
        existing_trail = db.query(Trail).filter(Trail.title == trail_title).first()
        if existing_trail:
            print(f"Trail '{trail_title}' already exists in the database. Skipping seeding.")
            return
        
        raw_points = load_points_from_gpx(GPX_FILE_PATH)
        print(f"Loaded {len(raw_points)} points from GPX file.")
        
        adding_km = haversine_distance(raw_points)
        total_distance_km = round(adding_km[-1], 2)

        #covert to JSON format [[lat, lng], ...] for gpx_data column
        gpx_json_data = [[lat, lng] for lat, lng in raw_points]

        new_trail = Trail(
            title=trail_title,
            description=(
                "Turistická trasa malebnou krajinou Kokořínska mezi pískovcovými skalami, "
                "hlubokými roklemi a lesními vyhlídkami."
            ),
            total_distance_km=total_distance_km,
            cover_image_url=None,
            gpx_data=gpx_json_data,
        )
        db.add(new_trail)
        db.flush()

        #Test 3 milestones on the trail at 20%, 55%, and 90% of the total distance
        last_idx = len(raw_points) - 1
        milestone_specs = [
            (
                int(last_idx * 0.20),
                "Skalní vyhlídka na trase",
                "První zastavení s výhledem na zalesněná údolí a pískovcové útvary Kokořínska.",
            ),
            (
                int(last_idx * 0.55),
                "Pískovcová rokle",
                "Polovina cesty vede chladným kaňonem lemovaným mechem a skalními převisy.",
            ),
            (
                int(last_idx * 0.90),
                "Závěrečný hřeben",
                "Poslední vyhlídkový úsek před cílem dnešní výpravy.",
            ),
        ]

        for idx, title, desc in milestone_specs:
            lat, lng = raw_points[idx]
            km_pos = round(adding_km[idx], 2)

            milestone = Milestone(
                trail_id=new_trail.id,
                km_position=km_pos,
                title=title,
                description=desc,
                latitude=lat,
                longitude=lng,
                mapillary_image_url=None,
                is_360=False,
                wiki_image_url=None,
            )
            db.add(milestone)

        db.commit()
        print(
            f"Done, trail saved '{new_trail.title}' "
            f"({total_distance_km} km, {len(gpx_json_data)} GPS points) with 3 milestones."
        )
    except Exception as exc:
        db.rollback()
        print(f"Error while seeding the database: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()