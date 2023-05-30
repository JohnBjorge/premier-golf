from prefect_gcp import GcpCredentials
from prefect_gcp.cloud_storage import GcsBucket
from dotenv import load_dotenv
import os


# pull in credentials from .env file
load_dotenv()

credentials_block = GcpCredentials(
    service_account_info=os.getenv("GCP_SERVICE_ACCOUNT_INFO") # service account info object, wrap in single quotes in .env file
)
credentials_block.save("golf-scraper-gcp-creds", overwrite=True)


bucket_block = GcsBucket(
    gcp_credentials=GcpCredentials.load("golf-scraper-gcp-creds"),
    bucket=os.getenv("GCS_BUCKET_NAME"),  # GCS bucket name
)

bucket_block.save("golf-scraper-gcs", overwrite=True)
