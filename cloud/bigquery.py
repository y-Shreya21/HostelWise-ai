# HostelWise AI - Google BigQuery Helper Module
import pandas as pd
from google.cloud import bigquery
from .config import cloud_settings

class BigQueryManager:
    def __init__(self):
        self.project_id = cloud_settings.GCP_PROJECT
        self.dataset_name = cloud_settings.BIGQUERY_DATASET
        self.client = None
        self.is_active = False
        
        if self.project_id:
            try:
                self.client = bigquery.Client(project=self.project_id)
                self.is_active = True
                self._ensure_dataset_exists()
            except Exception as e:
                print(f"BigQuery Client initialization failed: {e}. Defaulting to local database.")
        else:
            print("GCP_PROJECT not configured. Running BigQuery Manager in Local SQLite mode.")

    def _ensure_dataset_exists(self):
        """Verify the BigQuery dataset exists, or attempt to create it."""
        if not self.is_active or not self.client:
            return
        try:
            dataset_ref = self.client.dataset(self.dataset_name)
            try:
                self.client.get_dataset(dataset_ref)
            except Exception:
                # Dataset does not exist, create it
                dataset = bigquery.Dataset(dataset_ref)
                dataset.location = "us"
                self.client.create_dataset(dataset)
                print(f"BigQuery Dataset '{self.dataset_name}' created successfully.")
        except Exception as e:
            print(f"Warning: BigQuery Dataset check failed ({e}). Operations will run locally.")
            self.is_active = False

    def create_table_from_schema(self, table_name: str, schema_fields: list) -> bool:
        """Creates a table in BigQuery using a list of SchemaFields."""
        if not self.is_active or not self.client:
            return False
        try:
            table_id = f"{self.project_id}.{self.dataset_name}.{table_name}"
            table = bigquery.Table(table_id, schema=schema_fields)
            self.client.create_table(table, exists_ok=True)
            print(f"BigQuery Table '{table_name}' verified/created.")
            return True
        except Exception as e:
            print(f"Failed to create BigQuery table '{table_name}': {e}")
            return False

    def insert_rows_json(self, table_name: str, json_rows: list) -> bool:
        """Stream insert JSON records into a BigQuery table."""
        if not self.is_active or not self.client:
            return False
        try:
            table_ref = self.client.dataset(self.dataset_name).table(table_name)
            errors = self.client.insert_rows_json(table_ref, json_rows)
            if errors:
                print(f"Errors inserting rows into BigQuery '{table_name}': {errors}")
                return False
            return True
        except Exception as e:
            print(f"BigQuery row insertion failed: {e}")
            return False

    def load_dataframe(self, df: pd.DataFrame, table_name: str, write_disposition: str = "WRITE_APPEND") -> bool:
        """Load a Pandas DataFrame directly into a BigQuery table."""
        if not self.is_active or not self.client:
            return False
        try:
            table_ref = self.client.dataset(self.dataset_name).table(table_name)
            job_config = bigquery.LoadJobConfig(
                write_disposition=write_disposition
            )
            job = self.client.load_table_from_dataframe(df, table_ref, job_config=job_config)
            job.result()  # Wait for the load job to complete
            print(f"Successfully loaded {len(df)} rows into BigQuery '{table_name}'.")
            return True
        except Exception as e:
            print(f"BigQuery DataFrame load failed: {e}")
            return False

    def query_to_dataframe(self, sql_query: str) -> pd.DataFrame:
        """Run a SQL query in BigQuery and return the result as a Pandas DataFrame."""
        if not self.is_active or not self.client:
            raise RuntimeError("BigQuery client is not active.")
        try:
            query_job = self.client.query(sql_query)
            return query_job.to_dataframe()
        except Exception as e:
            print(f"BigQuery query execution failed: {e}")
            raise e

# Global BigQuery manager instance
bq_manager = BigQueryManager()
