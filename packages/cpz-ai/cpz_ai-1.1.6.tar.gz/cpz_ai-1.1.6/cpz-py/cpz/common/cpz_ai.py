from __future__ import annotations

import io
import os
from typing import Any, Mapping, Optional, List, Dict

import requests

from .logging import get_logger


class CPZAIClient:
    """Client for accessing CPZ AI database (strategies and files)"""

    # Default platform REST URL (not configurable via env for end-users)
    DEFAULT_API_URL = "https://api-ai.cpz-lab.com/cpz"

    def __init__(self, url: str, api_key: str, secret_key: str, user_id: str = None, is_admin: bool = False) -> None:
        self.url = url.rstrip("/")
        self.api_key = api_key
        self.secret_key = secret_key
        self.user_id = user_id
        self.is_admin = is_admin
        self.logger = get_logger()

    @staticmethod
    def from_env(environ: Optional[Mapping[str, str]] = None) -> "CPZAIClient":
        env = environ or os.environ
        # URL is fixed by SDK; do not require env variable
        url = CPZAIClient.DEFAULT_API_URL
        api_key = env.get("CPZ_AI_API_KEY", "")
        secret_key = env.get("CPZ_AI_SECRET_KEY", "")
        user_id = env.get("CPZ_AI_USER_ID", "")
        is_admin = env.get("CPZ_AI_IS_ADMIN", "false").lower() == "true"
        return CPZAIClient(url=url, api_key=api_key, secret_key=secret_key, user_id=user_id, is_admin=is_admin)

    @staticmethod
    def from_keys(api_key: str, secret_key: str, user_id: Optional[str] = None, is_admin: bool = False) -> "CPZAIClient":
        """Create client from keys only, using built-in default URL."""
        return CPZAIClient(url=CPZAIClient.DEFAULT_API_URL, api_key=api_key, secret_key=secret_key, user_id=user_id or "", is_admin=is_admin)

    def _headers(self) -> dict[str, str]:
        return {
            "apikey": self.secret_key,  # Use service role key for full access
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json",
        }

    def health(self) -> bool:
        """Check if the CPZ AI Platform is accessible"""
        try:
            resp = requests.get(f"{self.url}/", headers=self._headers(), timeout=10)
            return resp.status_code < 500
        except Exception as exc:  # noqa: BLE001
            self.logger.error("cpz_ai_platform_health_error", error=str(exc))
            return False

    def get_strategies(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get user's strategies from strategies table"""
        try:
            params = {"limit": limit, "offset": offset}
            
            # Filter by user_id unless admin
            if not self.is_admin and self.user_id:
                params["user_id"] = f"eq.{self.user_id}"
            
            resp = requests.get(
                f"{self.url}/strategies",
                headers=self._headers(),
                params=params,
                timeout=10
            )
            if resp.status_code == 200:
                return resp.json()
            else:
                self.logger.error("cpz_ai_get_strategies_error", status=resp.status_code, response=resp.text)
                return []
        except Exception as exc:  # noqa: BLE001
            self.logger.error("cpz_ai_get_strategies_exception", error=str(exc))
            return []

    def get_strategy(self, strategy_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific strategy by ID"""
        try:
            resp = requests.get(
                f"{self.url}/strategies",
                headers=self._headers(),
                params={"id": f"eq.{strategy_id}"},
                timeout=10
            )
            if resp.status_code == 200:
                strategies = resp.json()
                return strategies[0] if strategies else None
            else:
                self.logger.error("cpz_ai_get_strategy_error", status=resp.status_code, response=resp.text)
                return None
        except Exception as exc:  # noqa: BLE001
            self.logger.error("cpz_ai_get_strategy_exception", error=str(exc))
            return None

    def create_strategy(self, strategy_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new strategy"""
        try:
            # Automatically set user_id unless admin
            if not self.is_admin and self.user_id:
                strategy_data["user_id"] = self.user_id
            
            resp = requests.post(
                f"{self.url}/strategies",
                headers=self._headers(),
                json=strategy_data,
                timeout=10
            )
            if resp.status_code == 201:
                return resp.json()[0] if resp.json() else None
            else:
                self.logger.error("cpz_ai_create_strategy_error", status=resp.status_code, response=resp.text)
                return None
        except Exception as exc:  # noqa: BLE001
            self.logger.error("cpz_ai_create_strategy_exception", error=str(exc))
            return None

    def update_strategy(self, strategy_id: str, strategy_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing strategy"""
        try:
            resp = requests.patch(
                f"{self.url}/strategies",
                headers=self._headers(),
                params={"id": f"eq.{strategy_id}"},
                json=strategy_data,
                timeout=10
            )
            if resp.status_code == 200:
                return resp.json()[0] if resp.json() else None
            else:
                self.logger.error("cpz_ai_update_strategy_error", status=resp.status_code, response=resp.text)
                return None
        except Exception as exc:  # noqa: BLE001
            self.logger.error("cpz_ai_update_strategy_exception", error=str(exc))
            return None

    def delete_strategy(self, strategy_id: str) -> None:
        """Delete a strategy"""
        try:
            resp = requests.delete(
                f"{self.url}/strategies",
                headers=self._headers(),
                params={"id": f"eq.{strategy_id}"},
                timeout=10
            )
            return resp.status_code == 200
        except Exception as exc:  # noqa: BLE001
            self.logger.error("cpz_ai_delete_strategy_error", error=str(exc))
            return False

    def get_files(self, bucket_name: str = "default") -> List[Dict[str, Any]]:
        """Get files from a storage bucket"""
        try:
            # For user-specific access, use user-specific bucket or filter by prefix
            if not self.is_admin and self.user_id:
                # Use user-specific bucket name
                user_bucket = f"{bucket_name}-{self.user_id}"
                bucket_name = user_bucket
            
            resp = requests.get(
                f"{self.url}/storage/object/list/{bucket_name}",
                headers=self._headers(),
                timeout=10
            )
            if resp.status_code == 200:
                files = resp.json()
                
                # Filter files by user_id unless admin
                if not self.is_admin and self.user_id and files:
                    # Filter files that belong to this user
                    user_files = []
                    for file in files:
                        # Check if file path contains user_id or if metadata indicates ownership
                        if (self.user_id in file.get('name', '') or 
                            file.get('metadata', {}).get('user_id') == self.user_id):
                            user_files.append(file)
                    return user_files
                
                return files
            else:
                self.logger.error("cpz_ai_get_files_error", status=resp.status_code, response=resp.text)
                return []
        except Exception as exc:  # noqa: BLE001
            self.logger.error("cpz_ai_get_files_exception", error=str(exc))
            return []

    def get_file(self, bucket_name: str, file_path: str) -> Optional[Dict[str, Any]]:
        """Get file metadata from storage"""
        try:
            resp = requests.get(
                f"{self.url}/storage/object/info/{bucket_name}/{file_path}",
                headers=self._headers(),
                timeout=10
            )
            if resp.status_code == 200:
                return resp.json()
            else:
                self.logger.error("cpz_ai_get_file_error", status=resp.status_code, response=resp.text)
                return None
        except Exception as exc:  # noqa: BLE001
            self.logger.error("cpz_ai_get_file_exception", error=str(exc))
            return None

    def upload_file(self, bucket_name: str, file_path: str, file_content: bytes, content_type: str = "application/octet-stream") -> Optional[Dict[str, Any]]:
        """Upload a file to storage"""
        try:
            # For user-specific access, use user-specific bucket
            if not self.is_admin and self.user_id:
                user_bucket = f"{bucket_name}-{self.user_id}"
                bucket_name = user_bucket
                
                # Add user_id to file path for organization
                if not file_path.startswith(f"{self.user_id}/"):
                    file_path = f"{self.user_id}/{file_path}"
            
            headers = self._headers()
            headers["Content-Type"] = content_type
            
            resp = requests.post(
                f"{self.url}/storage/object/{bucket_name}/{file_path}",
                headers=headers,
                data=file_content,
                timeout=30
            )
            if resp.status_code == 200:
                return resp.json()
            else:
                self.logger.error("cpz_ai_upload_file_error", status=resp.status_code, response=resp.text)
                return None
        except Exception as exc:  # noqa: BLE001
            self.logger.error("cpz_ai_upload_file_exception", error=str(exc))
            return None

    def upload_csv_file(self, bucket_name: str, file_path: str, csv_content: str, encoding: str = "utf-8") -> Optional[Dict[str, Any]]:
        """Upload a CSV file to storage"""
        try:
            csv_bytes = csv_content.encode(encoding)
            return self.upload_file(bucket_name, file_path, csv_bytes, "text/csv")
        except Exception as exc:  # noqa: BLE001
            self.logger.error("cpz_ai_upload_csv_exception", error=str(exc))
            return None

    def upload_dataframe(self, bucket_name: str, file_path: str, df: Any, format: str = "csv", **kwargs) -> Optional[Dict[str, Any]]:
        """Upload a pandas DataFrame to storage"""
        try:
            if format.lower() == "csv":
                csv_content = df.to_csv(index=False, **kwargs)
                return self.upload_csv_file(bucket_name, file_path, csv_content)
            elif format.lower() == "json":
                json_content = df.to_json(orient="records", **kwargs)
                json_bytes = json_content.encode("utf-8")
                return self.upload_file(bucket_name, file_path, json_bytes, "application/json")
            elif format.lower() == "parquet":
                # Convert DataFrame to parquet bytes
                buffer = io.BytesIO()
                df.to_parquet(buffer, index=False, **kwargs)
                buffer.seek(0)
                return self.upload_file(bucket_name, file_path, buffer.getvalue(), "application/octet-stream")
            else:
                raise ValueError(f"Unsupported format: {format}. Use 'csv', 'json', or 'parquet'")
        except Exception as exc:  # noqa: BLE001
            self.logger.error("cpz_ai_upload_dataframe_exception", error=str(exc))
            return None

    def download_file(self, bucket_name: str, file_path: str) -> Optional[bytes]:
        """Download a file from storage"""
        try:
            # For user-specific access, use user-specific bucket
            if not self.is_admin and self.user_id:
                user_bucket = f"{bucket_name}-{self.user_id}"
                bucket_name = user_bucket
                
                # Add user_id to file path if not already present
                if not file_path.startswith(f"{self.user_id}/"):
                    file_path = f"{self.user_id}/{file_path}"
            
            resp = requests.get(
                f"{self.url}/storage/object/{bucket_name}/{file_path}",
                headers=self._headers(),
                timeout=30
            )
            if resp.status_code == 200:
                return resp.content
            else:
                self.logger.error("cpz_ai_download_file_error", status=resp.status_code, response=resp.text)
                return None
        except Exception as exc:  # noqa: BLE001
            self.logger.error("cpz_ai_download_file_exception", error=str(exc))
            return None

    def download_csv_to_dataframe(self, bucket_name: str, file_path: str, encoding: str = "utf-8", **kwargs) -> Optional[Any]:
        """Download a CSV file and load it into a pandas DataFrame"""
        try:
            import pandas as pd
            
            file_content = self.download_file(bucket_name, file_path)
            if file_content:
                csv_content = file_content.decode(encoding)
                return pd.read_csv(io.StringIO(csv_content), **kwargs)
            return None
        except Exception as exc:  # noqa: BLE001
            self.logger.error("cpz_ai_download_csv_exception", error=str(exc))
            return None

    def download_json_to_dataframe(self, bucket_name: str, file_path: str, **kwargs) -> Optional[Any]:
        """Download a JSON file and load it into a pandas DataFrame"""
        try:
            import pandas as pd
            
            file_content = self.download_file(bucket_name, file_path)
            if file_content:
                json_content = file_content.decode("utf-8")
                return pd.read_json(json_content, **kwargs)
            return None
        except Exception as exc:  # noqa: BLE001
            self.logger.error("cpz_ai_download_json_exception", error=str(exc))
            return None

    def download_parquet_to_dataframe(self, bucket_name: str, file_path: str, **kwargs) -> Optional[Any]:
        """Download a Parquet file and load it into a pandas DataFrame"""
        try:
            import pandas as pd
            
            file_content = self.download_file(bucket_name, file_path)
            if file_content:
                buffer = io.BytesIO(file_content)
                return pd.read_parquet(buffer, **kwargs)
            return None
        except Exception as exc:  # noqa: BLE001
            self.logger.error("cpz_ai_download_parquet_exception", error=str(exc))
            return None

    def list_files_in_bucket(self, bucket_name: str, prefix: str = "", limit: int = 100) -> List[Dict[str, Any]]:
        """List files in a storage bucket with optional prefix filtering"""
        try:
            # For user-specific access, use user-specific bucket
            if not self.is_admin and self.user_id:
                user_bucket = f"{bucket_name}-{self.user_id}"
                bucket_name = user_bucket
                
                # Add user_id to prefix for filtering
                if prefix and not prefix.startswith(f"{self.user_id}/"):
                    prefix = f"{self.user_id}/{prefix}"
                elif not prefix:
                    prefix = f"{self.user_id}/"
            
            params = {"limit": limit}
            if prefix:
                params["prefix"] = prefix
                
            resp = requests.get(
                f"{self.url}/storage/object/list/{bucket_name}",
                headers=self._headers(),
                params=params,
                timeout=10
            )
            if resp.status_code == 200:
                files = resp.json()
                
                # Filter files by user_id unless admin
                if not self.is_admin and self.user_id and files:
                    # Filter files that belong to this user
                    user_files = []
                    for file in files:
                        # Check if file path contains user_id or if metadata indicates ownership
                        if (self.user_id in file.get('name', '') or 
                            file.get('metadata', {}).get('user_id') == self.user_id):
                            user_files.append(file)
                    return user_files
                
                return files
            else:
                self.logger.error("cpz_ai_list_files_error", status=resp.status_code, response=resp.text)
                return []
        except Exception as exc:  # noqa: BLE001
            self.logger.error("cpz_ai_list_files_exception", error=str(exc))
            return []

    def create_bucket(self, bucket_name: str, public: bool = False) -> bool:
        """Create a new storage bucket"""
        try:
            # For user-specific access, create user-specific bucket
            if not self.is_admin and self.user_id:
                user_bucket = f"{bucket_name}-{self.user_id}"
                bucket_name = user_bucket
            
            bucket_data = {
                "name": bucket_name,
                "public": public
            }
            
            resp = requests.post(
                f"{self.url}/storage/bucket",
                headers=self._headers(),
                json=bucket_data,
                timeout=10
            )
            return resp.status_code == 200
        except Exception as exc:  # noqa: BLE001
            self.logger.error("cpz_ai_create_bucket_exception", error=str(exc))
            return False

    def delete_file(self, bucket_name: str, file_path: str) -> bool:
        """Delete a file from storage"""
        try:
            # For user-specific access, use user-specific bucket
            if not self.is_admin and self.user_id:
                user_bucket = f"{bucket_name}-{self.user_id}"
                bucket_name = user_bucket
                
                # Add user_id to file path if not already present
                if not file_path.startswith(f"{self.user_id}/"):
                    file_path = f"{self.user_id}/{file_path}"
            
            resp = requests.delete(
                f"{self.url}/storage/object/{bucket_name}/{file_path}",
                headers=self._headers(),
                timeout=10
            )
            return resp.status_code == 200
        except Exception as exc:  # noqa: BLE001
            self.logger.error("cpz_ai_delete_file_error", error=str(exc))
            return False

    def list_tables(self) -> list[str]:
        """List available tables in the CPZ AI Platform"""
        try:
            meta = requests.get(f"{self.url}/metadata", headers=self._headers(), timeout=10)
            if meta.status_code == 200:
                data = meta.json()
                return sorted(list(data.keys())) if isinstance(data, dict) else []
        except Exception as exc:  # noqa: BLE001
            self.logger.warning("cpz_ai_metadata_error", error=str(exc))
        try:
            resp = requests.get(f"{self.url}/", headers=self._headers(), timeout=10)
            if resp.status_code == 200 and isinstance(resp.json(), dict):
                return sorted(resp.json().keys())
        except Exception as exc:  # noqa: BLE001
            self.logger.warning("cpz_ai_list_tables_error", error=str(exc))
        return []

    def list_trading_credentials(self) -> list[Dict[str, Any]]:
        """Return all trading credentials rows accessible to this key."""
        try:
            resp = requests.get(f"{self.url}/trading_credentials", headers=self._headers(), timeout=10)
            if resp.status_code == 200 and isinstance(resp.json(), list):
                return resp.json()
        except Exception as exc:  # noqa: BLE001
            self.logger.warning("cpz_ai_list_trading_credentials_error", error=str(exc))
        try:
            resp = requests.get(f"{self.url}/trading_credentials", headers=self._headers(), params={"select": "*"}, timeout=10)
            if resp.status_code == 200 and isinstance(resp.json(), list):
                return resp.json()
        except Exception as exc:  # noqa: BLE001
            self.logger.warning("cpz_ai_list_trading_credentials_pgrest_error", error=str(exc))
        return []

    # --- Orders ---
    def record_order(
        self,
        *,
        order_id: str,
        symbol: str,
        side: str,
        qty: float,
        type: str,
        time_in_force: str,
        broker: str,
        env: str,
        strategy_id: Optional[str] = None,
        status: Optional[str] = None,
        filled_at: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Persist an execution record into CPZ orders table.

        Writes to consolidated gateway first (POST /orders) and falls back to
        PostgREST path if needed.
        """
        payload: Dict[str, Any] = {
            "order_id": order_id,
            "symbol": symbol,
            "side": side,
            "qty": qty,
            "order_type": type,
            "time_in_force": time_in_force,
            "broker": broker,
            "env": env,
        }
        if strategy_id:
            payload["strategy_id"] = strategy_id
        if status:
            payload["status"] = status
        if filled_at:
            payload["filled_at"] = filled_at

        headers = self._headers()
        try:
            resp = requests.post(f"{self.url}/orders", headers=headers, json=payload, timeout=10)
            if 200 <= resp.status_code < 300:
                try:
                    data = resp.json()
                except Exception:
                    data = None
                return data
        except Exception as exc:  # noqa: BLE001
            self.logger.warning("cpz_ai_record_order_error", error=str(exc))

        # Fallback to PostgREST
        try:
            resp = requests.post(
                f"{self.url}/orders",
                headers=headers,
                json=payload,
                timeout=10,
            )
            if 200 <= resp.status_code < 300:
                try:
                    data = resp.json()
                    if isinstance(data, dict) and data.get("id"):
                        return data
                    if isinstance(data, list) and data:
                        first = data[0]
                        if isinstance(first, dict) and first.get("id"):
                            return first
                    # Try to fetch the row when body lacks id
                    params: Dict[str, str] = {"select": "*", "order": "created_at.desc", "limit": "1"}
                    for key in ("user_id", "account_id", "broker", "strategy_id", "symbol", "status"):
                        if key in payload and payload[key] is not None:
                            params[key] = f"eq.{payload[key]}"
                    rr = requests.get(f"{self.url}/orders", headers=headers, params=params, timeout=8)
                    if rr.ok:
                        found = rr.json()
                        if isinstance(found, list) and found:
                            row = found[0]
                            if isinstance(row, dict):
                                return row
                    # Relax filters and retry without broker/account_id
                    relaxed = {k: v for k, v in params.items() if k not in ("broker", "account_id")}
                    rr2 = requests.get(f"{self.url}/orders", headers=headers, params=relaxed, timeout=8)
                    if rr2.ok:
                        found = rr2.json()
                        if isinstance(found, list) and found:
                            row = found[0]
                            if isinstance(row, dict):
                                return row
                except Exception:
                    return None
        except Exception as exc:  # noqa: BLE001
            self.logger.warning("cpz_ai_record_order_pgrest_error", error=str(exc))
        return None

    def echo(self) -> dict[str, Any]:
        """Test connection to CPZ AI Platform"""
        try:
            resp = requests.get(f"{self.url}/", headers=self._headers(), timeout=10)
            return {"status": resp.status_code, "ok": resp.ok}
        except Exception as exc:  # noqa: BLE001
            return {"status": 0, "ok": False, "error": str(exc)}


# Legacy alias for backward compatibility (will be removed in future versions)
# Use CPZAIClient instead
