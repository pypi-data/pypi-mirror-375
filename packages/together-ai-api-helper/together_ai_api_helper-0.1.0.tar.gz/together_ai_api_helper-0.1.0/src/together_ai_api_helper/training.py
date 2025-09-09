"""Fine-tuning job management for Together AI models.

This module provides comprehensive functionality for managing Together AI fine-tuning jobs,
including job creation, monitoring, cancellation, and integration with Hugging Face repositories.

Key features:
- Automated fine-tuning job lifecycle management
- Real-time job monitoring with event streaming
- Training file validation and upload
- Automatic Hugging Face repository creation
- Robust error handling and job cancellation
- Interactive monitoring with keyboard interrupts

Classes:
    TrainingConfig: Configuration for fine-tuning jobs
    TrainingClient: Main client for training operations

Example:
    from together_ai_api_helper.training import TrainingClient, TrainingConfig

    client = TrainingClient()

    # Without uploading to Hugging Face
    config = TrainingConfig(
        model="mistralai/Mistral-7B-Instruct-v0.1",
        training_file="training_data.jsonl",
        suffix="my-custom-model",
        **other_together_ai_params
    )

    # With uploading to Hugging Face
    config_default = TrainingConfig(
        model="mistralai/Mistral-7B-Instruct-v0.1",
        training_file="training_data.jsonl",
        suffix="my-custom-model",
        hf_account="username",  # Creates username/{model}-{suffix}-{timestamp}
        **other_together_ai_params
    )

    # Start and monitor training job
    model_name = client.start_job(config)
    print(f"Training completed: {model_name}")
"""

import os
import time
from typing import Any, cast

import together
from huggingface_hub import create_repo
from pydantic import BaseModel
from together import Together
from together.types import FinetuneResponse

from .common import CommonClient


class TrainingConfig(BaseModel):
    """Configuration for fine-tuning jobs.

    Attributes:
        model: Base model name to fine-tune
        training_file_path: Path to the training data file (JSONL format),
            optional if training_file is provided
        training_file: ID of the training data file in the Together filesystem,
            optional if training_file_path is provided
        suffix: A suffix to be appended to the model name (must be ≤40 characters)
        hf_account: Optional Hugging Face account name for model upload (default: None)
        hf_relative_repo_name: Optional repository name within the account
            (default: uses model-suffix-timestamp format)
        hf_token: Optional Hugging Face token for model upload (default: None)

    Note:
        All other attributes from Together.resources.finetune.FinetuneRequest are supported.
        See https://github.com/togethercomputer/together-python/blob/main/src/together/resources/finetune.py#L46
        for more options.
    """

    model: str
    training_file_path: str | None = None
    training_file: str | None = None
    suffix: str | None = None  # Must be no longer than 40 characters
    hf_account: str | None = None
    hf_relative_repo_name: str | None = None
    hf_token: str | None = None


class TrainingClient(CommonClient):
    """Client for managing Together AI fine-tuning jobs.

    This client provides comprehensive fine-tuning job management including
    job creation, monitoring, cancellation, and integration with Hugging Face.
    """

    STATUSSES_TO_STOP_FOR: tuple[str, ...] = (
        "completed",
        "cancelled",
        "error",
        "user_error",
    )

    @staticmethod
    def _get_timestamp() -> str:
        return time.strftime("%Y-%m-%d_%H-%M-%S", time.gmtime(time.time()))

    def __init__(
        self,
        client: Together | None = None,
        log_file: str | None = "training.log",
        log_level: int | None = None,
    ):
        """Initialize the training client.

        Args:
            client: Optional Together client instance (creates new one if None)
            log_file: Path to log file for training operations, defaults to "training.log".
                If log_file is None, no log file will be created.
            log_level: The level of the logger, defaults to INFO.
        """
        super().__init__("training", client, log_file, log_level)
        self.latest_train_file_id = None
        self.latest_job_id = None

    def _verify_run_config(self, run_config: TrainingConfig) -> tuple[bool, dict[str, Any]]:
        if run_config.training_file_path is not None and run_config.training_file is not None:
            return False, {
                "error": "Training file path and training file ID cannot be provided at the same time"
            }
        if run_config.training_file is None:
            return self._verify_train_file(run_config.training_file_path)
        return True, {}

    def _verify_train_file(self, train_file: str | None) -> tuple[bool, dict[str, Any]]:
        if train_file is None:
            return False, {"error": "Training file path is required"}
        if not os.path.exists(train_file):
            raise FileNotFoundError(f"Training file {train_file} not found")
        sft_report = together.utils.check_file(train_file)
        return sft_report["is_check_passed"], sft_report

    def _latest_job_is_still_running(self) -> bool:
        if self.latest_job_id is None:
            return False
        job = self.client.fine_tuning.retrieve(self.latest_job_id)
        if job.status in self.STATUSSES_TO_STOP_FOR:
            return False
        return True

    def cancel_job(self, job_id: str | None = None) -> None:
        """Cancel a running fine-tuning job.

        Args:
            job_id: Optional job ID to cancel (uses latest job if None)
        """
        if job_id is None:
            job_id = self.latest_job_id
        if job_id is None:
            self.logger.error("No job ID provided and no latest job ID found")
            raise ValueError("No job ID provided and no latest job ID found")
        self.client.fine_tuning.cancel(job_id)
        self.logger.info("Cancelled job %s", job_id)

    def start_job(self, run_config: TrainingConfig) -> str:
        """Start a fine-tuning job and monitor it until completion.

        This method handles the complete fine-tuning workflow:
        1. Validates the latest job isn't running
        2. Verifies training file format
        3. Uploads training file to Together
        4. Optionally creates Hugging Face repository (if hf_account is provided)
        5. Starts the fine-tuning job
        6. Monitors progress until completion

        Args:
            run_config: Configuration for the fine-tuning job

        Returns:
            The name of the resulting fine-tuned model in the Together API format
        """
        if self._latest_job_is_still_running():
            self.logger.error("Latest job %s is still running, aborting", self.latest_job_id)
            self.logger.info("To cancel the latest job, run `client.cancel_job()`")
            raise ValueError(f"Latest job {self.latest_job_id} is still running, aborting")

        self.logger.info("Starting fine-tuning job with model %s...", run_config.model)

        is_check_passed, sft_report = self._verify_run_config(run_config)
        if not is_check_passed:
            self.logger.error("Config failed check with report: %s", sft_report)
            raise ValueError(f"Config failed check with report: {sft_report}")

        train_file_id = run_config.training_file
        if train_file_id is None:
            self.logger.info("Uploading train file %s...", run_config.training_file_path)
            train_file_id = self.client.files.upload(run_config.training_file_path, check=True).id
        self.logger.info("Train file ID: %s", train_file_id)

        ft_params = {
            "training_file": train_file_id,
            **run_config.model_dump(
                exclude_none=True,
                exclude={
                    "training_file_path",
                    "training_file",
                    "hf_account",
                    "hf_relative_repo_name",
                    "hf_token",
                },
            ),
        }
        if run_config.hf_account:
            hf_relative_repo_name = (
                run_config.hf_relative_repo_name
                or f"{run_config.model}-{run_config.suffix}-{self._get_timestamp()}".replace(
                    "/", "-"
                )
            )
            hf_full_repo_name = f"{run_config.hf_account}/{hf_relative_repo_name}"
            self.logger.info("Creating Hugging Face repo %s...", hf_full_repo_name)
            url = create_repo(hf_full_repo_name)
            self.logger.info("Hugging Face repo created at %s", url)
            ft_params["hf_api_token"] = run_config.hf_token or os.getenv("HF_TOKEN")
            ft_params["hf_output_repo_name"] = hf_relative_repo_name
        else:
            self.logger.info("No Hugging Face account specified, model will not be uploaded")

        self.logger.info("Starting fine-tuning job with model %s...", run_config.model)
        ft_resp: FinetuneResponse = self.client.fine_tuning.create(**ft_params)
        self.logger.info("Job ID: %s", ft_resp.id)

        self.latest_job_id = ft_resp.id

        self.monitor_job(ft_resp.id)
        if ft_resp.output_name is None:
            raise ValueError("Fine-tuning job did not produce an output name")
        return cast(str, ft_resp.output_name)

    def monitor_job(self, job_id: str) -> None:
        """Monitor a fine-tuning job until completion.

        Args:
            job_id: ID of the job to monitor

        Note:
            Press Ctrl+C once to cancel the job, twice to exit immediately.
            Continues monitoring until the job reaches a terminal state.
        """
        data_pointer = 0
        model_name = None
        job_status = None
        cancel_requested = False
        self.logger.info("Monitoring job %s...", job_id)
        while True:
            try:
                job = self.client.fine_tuning.retrieve(job_id)
                if model_name is None:
                    model_name = job.output_name
                    self.logger.info("Model name: %s", model_name)
                if job_status is None or job_status != job.status:
                    job_status = job.status
                    self.logger.info("Status: %s", job_status.value.capitalize())

                events = self.client.fine_tuning.list_events(job_id).data
                while data_pointer < len(events):
                    event = events[data_pointer]
                    self.logger.info(event.message)
                    data_pointer += 1

                if job.status in self.STATUSSES_TO_STOP_FOR:
                    self.logger.info(
                        'Job %s completed with status "%s"', job_id, job.status.value.capitalize()
                    )
                    break
                time.sleep(1)
            except KeyboardInterrupt:
                if not cancel_requested:
                    self.logger.info("Cancelling job %s", job_id)
                    self.client.fine_tuning.cancel(job_id)
                    cancel_requested = True
                    self.logger.info(
                        "To exit without waiting for the job to cancel, press Ctrl+C again"
                    )
                else:
                    self.logger.info(
                        "Exiting without waiting for the job to cancel "
                        "(it probably will cancel in a few seconds)"
                    )
                    break
