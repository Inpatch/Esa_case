"""
Pull CAMS solar radiation time series for Copenhagen from the Copernicus
Atmosphere Data Store (ADS), using plain `requests` (no cdsapi library).

Fill in API_KEY below, then run:
    python get_copenhagen_solar.py
"""


try:
    from dotenv import load_dotenv, find_dotenv
    import os

    if not load_dotenv():
        load_dotenv(find_dotenv())
except:
    print("Check your .env file")

import time
import requests

# ---- CONFIG ---------------------------------------------------------------

API_KEY = os.getenv("API_KEY_ADS")   # from https://ads.atmosphere.copernicus.eu/profile
BASE_URL = "https://ads.atmosphere.copernicus.eu/api"
DATASET = "cams-solar-radiation-timeseries"

REQUEST_BODY = {
    "inputs": {
        "sky_type": "observed_cloud",          # or "clear_sky"
        "location": {"latitude": 55.68, "longitude": 12.57},  # Copenhagen
        "altitude": ["-999."],
        "date": ["2024-01-01/2024-12-31"],     # edit date range as needed
        "time_step": "1hour",
        "time_reference": "universal_time",
        "format": "csv",
    }
}

OUTPUT_FILE = "data/copenhagen_solar.csv"

# ---- SCRIPT -----------------------------------------------------------------

session = requests.Session()
session.headers.update({
    "PRIVATE-TOKEN": API_KEY,   # ADS uses this header for the API key
    "Content-Type": "application/json",
})


def submit_job():
    url = f"{BASE_URL}/retrieve/v1/processes/{DATASET}/execution"
    resp = session.post(url, json=REQUEST_BODY)
    resp.raise_for_status()
    data = resp.json()
    job_id = data["jobID"]
    print(f"Submitted job: {job_id}")
    return job_id


def wait_for_job(job_id, poll_seconds=5, timeout_seconds=1800):
    url = f"{BASE_URL}/retrieve/v1/jobs/{job_id}"
    waited = 0
    while waited < timeout_seconds:
        resp = session.get(url)
        resp.raise_for_status()
        status = resp.json()["status"]
        print(f"  status: {status} (waited {waited}s)")
        if status == "successful":
            return
        if status in ("failed", "dismissed"):
            raise RuntimeError(f"Job ended with status: {status}")
        time.sleep(poll_seconds)
        waited += poll_seconds
    raise TimeoutError("Job did not finish within timeout")


def get_download_url(job_id):
    url = f"{BASE_URL}/retrieve/v1/jobs/{job_id}/results"
    resp = session.get(url)
    resp.raise_for_status()
    data = resp.json()
    # result asset location is nested under "asset" -> "value" -> "href"
    return data["asset"]["value"]["href"]


def download_file(file_url, output_path):
    resp = session.get(file_url, stream=True)
    resp.raise_for_status()
    with open(output_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"Saved to {output_path}")


if __name__ == "__main__":

    job_id = submit_job()
    wait_for_job(job_id)
    file_url = get_download_url(job_id)
    download_file(file_url, OUTPUT_FILE)