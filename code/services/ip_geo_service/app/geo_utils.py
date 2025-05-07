<<<<<<< HEAD
=======
import sys
print("Using Python from:", sys.executable)
>>>>>>> 559b5ec3b653abaa04c9216dae5df4a7e8cf14d0
import IP2Location

# Load local DB
db = IP2Location.IP2Location("IP2LOCATION-LITE-DB1.BIN")

def get_geolocation(ip: str):
    try:
        record = db.get_all(ip)
        return {
            "ip": ip,
            "country": record.country_short,
            "region": record.region,
            "city": record.city
        }
    except Exception as e:
        return {"error": str(e)}
