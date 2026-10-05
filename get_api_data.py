import os
import time
import requests


try:
    from dotenv import load_dotenv, find_dotenv
    import os

    if not load_dotenv():
        load_dotenv(find_dotenv())


    HOST = os.getenv("HOST")
    if HOST is None:
        print("Variables not found. Check .env")

    else:
        PORT = os.getenv("PORT")
        USERNAME = os.getenv("USERNAME")
        PASSWORD = os.getenv("PASSWORD")
        DATABASE = os.getenv("DATABASE")

except:
    print("Cant load env")

API_URL = "https://cds.climate.copernicus.eu/api"
API_KEY = os.environ["API_KEY_ADS"]

DATASET = "satellite-land-surface-temperature"

REQUEST = {
    "variable": ["land_surface_temperature"],
    "observation_time": ["day"],
    "year": ["2020"],
    "month": ["07"],
    "version": ["v3_00"],
    "area": [55.69, 12.5, 55.65, 12.57],
}


headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}


# --------------------------------------------------
# 1. Submit job
# --------------------------------------------------

response = requests.post(
    f"{API_URL}/retrieve/v1/jobs",
    headers=headers,
    json={
        "dataset": DATASET,
        "request": REQUEST,
    },
)

response.raise_for_status()

job = response.json()

print("Job submitted:")
print(job)


# --------------------------------------------------
# 2. Get job ID
# --------------------------------------------------

job_id = job["job_id"]

print(f"\nJob ID: {job_id}")


# --------------------------------------------------
# 3. Wait for job to finish
# --------------------------------------------------

while True:

    response = requests.get(
        f"{API_URL}/retrieve/v1/jobs/{job_id}",
        headers=headers,
    )

    response.raise_for_status()

    job_status = response.json()

    state = job_status["status"]

    print("Status:", state)

    if state == "completed":
        break

    if state in ["failed", "cancelled"]:
        raise RuntimeError(f"Job failed: {job_status}")

    time.sleep(5)


# --------------------------------------------------
# 4. Download result
# --------------------------------------------------

result_url = job_status["result"]["href"]

print("Downloading:")
print(result_url)

response = requests.get(
    result_url,
    headers=headers,
    stream=True,
)

response.raise_for_status()

with open("lst_2020_07.nc", "wb") as f:

    for chunk in response.iter_content(chunk_size=1024 * 1024):

        if chunk:
            f.write(chunk)


print("\nSaved as lst_2020_07.nc")