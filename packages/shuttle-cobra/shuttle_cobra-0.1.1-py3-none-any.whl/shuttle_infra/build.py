import base64
import io
import json
import logging
import os
import tarfile
from pathlib import Path
from typing import Optional

import docker
import pathspec
from docker.errors import BuildError

from .common import BotoSession

logger = logging.getLogger(__name__)


class DockerContextPathMissing(Exception):
    """Raised when the docker context input directory does not exist"""


class ImagePushError(Exception):
    """Raised when pushing a Docker image to a registry fails"""


# pylint: disable-next=too-few-public-methods
class DockerClient:
    def __init__(self, boto_session: BotoSession) -> None:
        session = boto_session.session
        ecr = session.client("ecr", endpoint_url=boto_session.endpoint_url)

        auth = ecr.get_authorization_token()
        auth_data = auth["authorizationData"][0]
        token = base64.b64decode(auth_data["authorizationToken"]).decode()
        username, password = token.split(":")
        registry = auth_data["proxyEndpoint"].replace("https://", "")

        # Handle local testing
        if registry[-4:] == "4566":
            idx = boto_session.endpoint_url.rindex(":")
            registry = registry[:-4] + boto_session.endpoint_url[idx + 1 :]

        # Initialize Docker client
        self.client = docker.from_env()
        self.client.login(username=username, password=password, registry=registry)

        # Verify Docker is running
        self.client.ping()

    def _load_dockerignore(self, directory: Path) -> Optional[pathspec.PathSpec]:
        """Load .dockerignore file from a directory if it exists."""
        dockerignore_path = directory / ".dockerignore"
        if dockerignore_path.exists():
            try:
                with open(dockerignore_path, "r", encoding="utf-8") as f:
                    patterns = f.read().splitlines()
                return pathspec.PathSpec.from_lines('gitwildmatch', patterns)
            except Exception as e:
                logger.warning("Failed to read .dockerignore file at %s: %s", dockerignore_path, e)
        return None

    def _create_build_context(self, dockerfile_path: Path) -> io.BytesIO:
        """Create a tar archive for the Docker build context."""
        tar_stream = io.BytesIO()

        # Create an in-memory tar file from the build context directory
        logger.debug("Creating build context tar from %s", dockerfile_path)
        with tarfile.open(fileobj=tar_stream, mode="w") as tar:
            base_dir = dockerfile_path.absolute()
            
            for root, dirs, files in base_dir.walk():
                # Load .dockerignore file for current directory
                dockerignore_spec = self._load_dockerignore(Path(root))
                
                # Filter directories using .dockerignore patterns
                if dockerignore_spec:
                    # Remove ignored directories from dirs list to prevent os.walk from traversing them
                    dirs_to_remove = []
                    for dir_name in dirs:
                        dir_rel_path = os.path.relpath(os.path.join(root, dir_name), base_dir)
                        if dockerignore_spec.match_file(dir_rel_path) or dockerignore_spec.match_file(dir_rel_path + '/'):
                            dirs_to_remove.append(dir_name)
                    
                    for dir_name in dirs_to_remove:
                        dirs.remove(dir_name)

                # Process files
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, base_dir)
                    
                    # Check if file should be ignored
                    should_ignore = False
                    if dockerignore_spec and dockerignore_spec.match_file(rel_path):
                        should_ignore = True
                    
                    if not should_ignore:
                        tar.add(file_path, arcname=rel_path)

            # Read the contents of the Dockerfile into memory
            dockerfile = Path(__file__).parent.joinpath("Dockerfile").resolve()
            with open(dockerfile, "rb") as fp:
                dockerfile_contents = fp.read()

            # Write the Dockerfile to the tar
            info = tarfile.TarInfo(name="Dockerfile")
            info.size = len(dockerfile_contents)
            tar.addfile(info, io.BytesIO(dockerfile_contents))

        tar_stream.seek(0)
        return tar_stream

    def _push_image(self, repository_name: str, image_tag: str) -> None:
        """Helper to push Docker image and handle push logs/errors."""
        full_tag = f"{repository_name}:{image_tag}"
        logger.debug("Pushing image to repository: %s", full_tag)
        push_errors = []

        for log_line in self.client.images.push(
            repository_name, image_tag
        ).splitlines():
            log = json.loads(log_line)
            if "stream" in log and log["stream"].strip():
                logger.debug(log["stream"].strip())
            elif "status" in log and log["status"].strip():
                logger.debug(log["status"].strip())

            # Consolidate error checking for 'error' and 'errorDetail' keys
            if "error" in log or ("errorDetail" in log and log["errorDetail"]):
                error_msg = log.get("error", "").strip()
                error_detail_msg = log.get("errorDetail", {}).get("message", "").strip()

                full_error = "Unknown Docker image push error"
                if error_msg and error_detail_msg:
                    full_error = f"{error_msg} ({error_detail_msg})"
                elif error_msg:
                    full_error = error_msg
                elif error_detail_msg:
                    full_error = error_detail_msg

                push_errors.append(full_error)
                logger.error("Docker image push error: %s", full_error)

        if push_errors:
            raise ImagePushError(
                f"Failed to push Docker image: {' | '.join(push_errors)}"
            )

        logger.debug("Successfully pushed image: %s", full_tag)

    def build(
        self,
        repository_name: str,
        dockerfile_path: Path,
        image_tag: str = "latest",
    ) -> str:
        if not dockerfile_path.exists():
            raise DockerContextPathMissing(
                "Docker context directory does not exist or is not a directory"
            )

        try:
            image_name = f"{repository_name}:{image_tag}"
            logger.debug("Building Docker image with context from %s", dockerfile_path)

            tar_stream = self._create_build_context(dockerfile_path)

            logger.debug("Building image: %s", image_name)

            # Build the Docker image using the custom context
            _image, build_logs = self.client.images.build(
                fileobj=tar_stream,
                custom_context=True,
                tag=image_name,
                rm=True,
                forcerm=True,
            )

            # Log build output
            for log in build_logs:
                if "stream" in log:
                    log_line = log["stream"].strip()
                    if log_line:
                        logger.debug(log_line)

            logger.debug("Successfully built image: %s", image_name)

            # Push the image
            self._push_image(repository_name, image_tag)

            return image_name

        except BuildError as e:
            for log in getattr(e, "build_log", []):
                if "stream" in log:
                    log_line = log["stream"].strip()
                    if log_line:
                        logger.error(log_line)
            raise
