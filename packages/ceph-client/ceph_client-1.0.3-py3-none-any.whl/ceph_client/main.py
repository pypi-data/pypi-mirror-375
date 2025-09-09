import os
from typing import BinaryIO, Optional

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from loguru import logger


class CephClient:
    """Client for interacting with Ceph S3-compatible storage."""

    def __init__(
        self,
        endpoint_url: Optional[str] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        region: str = "us-east-1",
        verify_ssl: bool = True,
    ):
        """
        Initialize Ceph S3 client.

        Args:
            endpoint_url: S3 endpoint URL (defaults to env var CEPH_ENDPOINT_URL)
            access_key: Access key ID (defaults to env var CEPH_ACCESS_KEY)
            secret_key: Secret access key (defaults to env var CEPH_SECRET_KEY)
            region: AWS region (defaults to us-east-1)
            verify_ssl: Whether to verify SSL certificates
        """
        # Get credentials from environment variables if not provided
        self.endpoint_url = endpoint_url or os.getenv("CEPH_ENDPOINT_URL")
        self.access_key = access_key or os.getenv("CEPH_ACCESS_KEY")
        self.secret_key = secret_key or os.getenv("CEPH_SECRET_KEY")
        self.region = region
        self.verify_ssl = verify_ssl

        if not all([self.endpoint_url, self.access_key, self.secret_key]):
            raise ValueError(
                "Missing required configuration. Please provide endpoint_url, "
                "access_key, and secret_key or set CEPH_ENDPOINT_URL, "
                "CEPH_ACCESS_KEY, and CEPH_SECRET_KEY environment variables."
            )

        logger.debug(f"Initializing Ceph client with endpoint: {self.endpoint_url}")

        # Initialize S3 client
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region,
            verify=self.verify_ssl,
        )

        logger.info("Ceph S3 client initialized successfully")

    def upload_file(
        self,
        file_path: str,
        bucket: str,
        object_key: str,
        metadata: Optional[dict] = None,
    ) -> bool:
        """
        Upload a file to Ceph S3 storage.

        Args:
            file_path: Path to the file to upload
            bucket: S3 bucket name
            object_key: S3 object key (path in bucket)
            metadata: Optional metadata to attach to the object

        Returns:
            True if upload was successful, False otherwise
        """
        try:
            extra_args = {}
            if metadata:
                extra_args["Metadata"] = metadata

            logger.debug(f"Uploading {file_path} to s3://{bucket}/{object_key}")
            self.s3_client.upload_file(
                file_path,
                bucket,
                object_key,
                ExtraArgs=extra_args if extra_args else None,
            )
            logger.info(
                f"Successfully uploaded {file_path} to s3://{bucket}/{object_key}"
            )
            return True

        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            return False
        except NoCredentialsError:
            logger.error("Credentials not available")
            return False
        except ClientError as e:
            logger.error(f"Failed to upload file: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during upload: {e}")
            return False

    def download_file(self, bucket: str, object_key: str, file_path: str) -> bool:
        """
        Download a file from Ceph S3 storage.

        Args:
            bucket: S3 bucket name
            object_key: S3 object key (path in bucket)
            file_path: Local path where the file should be saved

        Returns:
            True if download was successful, False otherwise
        """
        try:
            logger.debug(f"Downloading s3://{bucket}/{object_key} to {file_path}")

            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            self.s3_client.download_file(bucket, object_key, file_path)
            logger.info(
                f"Successfully downloaded s3://{bucket}/{object_key} to {file_path}"
            )
            return True

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            if error_code == "404":
                logger.error(f"Object not found: s3://{bucket}/{object_key}")
            else:
                logger.error(f"Failed to download file: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during download: {e}")
            return False

    def upload_file_object(
        self,
        file_obj: BinaryIO,
        bucket: str,
        object_key: str,
        metadata: Optional[dict] = None,
    ) -> bool:
        """
        Upload a file-like object to Ceph S3 storage.

        Args:
            file_obj: File-like object to upload
            bucket: S3 bucket name
            object_key: S3 object key (path in bucket)
            metadata: Optional metadata to attach to the object

        Returns:
            True if upload was successful, False otherwise
        """
        try:
            extra_args = {}
            if metadata:
                extra_args["Metadata"] = metadata

            logger.debug(f"Uploading file object to s3://{bucket}/{object_key}")
            self.s3_client.upload_fileobj(
                file_obj,
                bucket,
                object_key,
                ExtraArgs=extra_args if extra_args else None,
            )
            logger.info(
                f"Successfully uploaded file object to s3://{bucket}/{object_key}"
            )
            return True

        except NoCredentialsError:
            logger.error("Credentials not available")
            return False
        except ClientError as e:
            logger.error(f"Failed to upload file object: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during upload: {e}")
            return False

    def create_bucket(self, bucket: str) -> bool:
        """
        Create a new S3 bucket.

        Args:
            bucket: Bucket name to create

        Returns:
            True if bucket was created or already exists, False otherwise
        """
        try:
            self.s3_client.create_bucket(Bucket=bucket)
            logger.info(f"Created bucket: {bucket}")
            return True
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            if (
                error_code == "BucketAlreadyExists"
                or error_code == "BucketAlreadyOwnedByYou"
            ):
                logger.info(f"Bucket already exists: {bucket}")
                return True
            logger.error(f"Failed to create bucket: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error creating bucket: {e}")
            return False

    def list_objects(self, bucket: str, prefix: str = "") -> list:
        """
        List objects in a bucket.

        Args:
            bucket: S3 bucket name
            prefix: Optional prefix to filter objects

        Returns:
            List of object keys
        """
        try:
            response = self.s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)

            if "Contents" not in response:
                return []

            return [obj["Key"] for obj in response["Contents"]]

        except ClientError as e:
            logger.error(f"Failed to list objects: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error listing objects: {e}")
            return []

    def delete_file(self, bucket: str, object_key: str) -> bool:
        """
        Delete a file from Ceph S3 storage.

        Args:
            bucket: S3 bucket name
            object_key: S3 object key (path in bucket)

        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            logger.debug(f"Deleting s3://{bucket}/{object_key}")
            self.s3_client.delete_object(Bucket=bucket, Key=object_key)
            logger.info(f"Successfully deleted s3://{bucket}/{object_key}")
            return True

        except ClientError as e:
            logger.error(f"Failed to delete file: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during deletion: {e}")
            return False
