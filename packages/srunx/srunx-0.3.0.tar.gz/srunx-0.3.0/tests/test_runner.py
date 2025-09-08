"""Tests for srunx.runner module."""

from unittest.mock import Mock, patch

import pytest
import yaml

from srunx.exceptions import WorkflowValidationError
from srunx.models import Job, JobEnvironment, JobStatus, ShellJob, Workflow
from srunx.runner import WorkflowRunner, run_workflow_from_file


class TestWorkflowRunner:
    """Test WorkflowRunner class."""

    def test_workflow_runner_init(self):
        """Test WorkflowRunner initialization."""
        job = Job(
            name="test_job",
            command=["echo", "hello"],
            environment=JobEnvironment(conda="test_env"),
        )
        workflow = Workflow(name="test_workflow", jobs=[job])

        runner = WorkflowRunner(workflow)

        assert runner.workflow is workflow
        assert runner.slurm is not None

    def test_get_independent_jobs(self):
        """Test getting independent jobs."""
        job1 = Job(
            name="independent1",
            command=["echo", "1"],
            environment=JobEnvironment(conda="env"),
        )
        job2 = Job(
            name="dependent",
            command=["echo", "2"],
            environment=JobEnvironment(conda="env"),
            depends_on=["independent1"],
        )
        job3 = Job(
            name="independent2",
            command=["echo", "3"],
            environment=JobEnvironment(conda="env"),
        )

        workflow = Workflow(name="test", jobs=[job1, job2, job3])
        runner = WorkflowRunner(workflow)

        independent = runner.get_independent_jobs()

        assert len(independent) == 2
        assert job1 in independent
        assert job3 in independent
        assert job2 not in independent

    def test_get_independent_jobs_empty(self):
        """Test getting independent jobs when all have dependencies."""
        job1 = Job(
            name="job1",
            command=["echo", "1"],
            environment=JobEnvironment(conda="env"),
            depends_on=["job2"],
        )
        job2 = Job(
            name="job2",
            command=["echo", "2"],
            environment=JobEnvironment(conda="env"),
            depends_on=["job1"],  # Circular dependency
        )

        workflow = Workflow(name="test", jobs=[job1, job2])
        runner = WorkflowRunner(workflow)

        independent = runner.get_independent_jobs()

        assert len(independent) == 0

    def test_from_yaml_simple(self, temp_dir):
        """Test loading workflow from simple YAML."""
        yaml_content = {
            "name": "test_workflow",
            "jobs": [
                {
                    "name": "job1",
                    "command": ["echo", "hello"],
                    "environment": {"conda": "test_env"},
                }
            ],
        }

        yaml_path = temp_dir / "workflow.yaml"
        with open(yaml_path, "w") as f:
            yaml.dump(yaml_content, f)

        runner = WorkflowRunner.from_yaml(yaml_path)

        assert runner.workflow.name == "test_workflow"
        assert len(runner.workflow.jobs) == 1
        assert runner.workflow.jobs[0].name == "job1"
        assert runner.workflow.jobs[0].command == ["echo", "hello"]

    def test_from_yaml_complex(self, temp_dir):
        """Test loading workflow from complex YAML."""
        yaml_content = {
            "name": "complex_workflow",
            "jobs": [
                {
                    "name": "preprocess",
                    "command": ["python", "preprocess.py"],
                    "environment": {"conda": "ml_env"},
                    "resources": {
                        "nodes": 1,
                        "cpus_per_task": 4,
                        "memory_per_node": "16GB",
                    },
                },
                {
                    "name": "train",
                    "command": ["python", "train.py"],
                    "depends_on": ["preprocess"],
                    "environment": {"conda": "ml_env"},
                    "resources": {
                        "nodes": 1,
                        "gpus_per_node": 1,
                        "time_limit": "2:00:00",
                    },
                },
            ],
        }

        yaml_path = temp_dir / "complex.yaml"
        with open(yaml_path, "w") as f:
            yaml.dump(yaml_content, f)

        runner = WorkflowRunner.from_yaml(yaml_path)

        assert runner.workflow.name == "complex_workflow"
        assert len(runner.workflow.jobs) == 2

        preprocess_job = next(j for j in runner.workflow.jobs if j.name == "preprocess")
        train_job = next(j for j in runner.workflow.jobs if j.name == "train")

        assert preprocess_job.resources.cpus_per_task == 4
        assert preprocess_job.resources.memory_per_node == "16GB"
        assert train_job.depends_on == ["preprocess"]
        assert train_job.resources.gpus_per_node == 1

    def test_from_yaml_shell_job(self, temp_dir):
        """Test loading workflow with shell job."""
        yaml_content = {
            "name": "shell_workflow",
            "jobs": [{"name": "shell_job", "path": "/path/to/script.sh"}],
        }

        yaml_path = temp_dir / "shell.yaml"
        with open(yaml_path, "w") as f:
            yaml.dump(yaml_content, f)

        runner = WorkflowRunner.from_yaml(yaml_path)

        assert len(runner.workflow.jobs) == 1
        job = runner.workflow.jobs[0]
        assert isinstance(job, ShellJob)
        assert job.script_path == "/path/to/script.sh"

    def test_from_yaml_nonexistent_file(self):
        """Test loading workflow from nonexistent file."""
        with pytest.raises(FileNotFoundError):
            WorkflowRunner.from_yaml("/nonexistent/file.yaml")

    def test_from_yaml_malformed_yaml(self, temp_dir):
        """Test loading workflow from malformed YAML."""
        yaml_path = temp_dir / "malformed.yaml"
        with open(yaml_path, "w") as f:
            f.write("invalid: yaml: content: [")

        with pytest.raises(yaml.YAMLError):
            WorkflowRunner.from_yaml(yaml_path)

    def test_from_yaml_missing_name(self, temp_dir):
        """Test loading workflow without name (uses default)."""
        yaml_content = {
            "jobs": [
                {
                    "name": "job1",
                    "command": ["echo", "test"],
                    "environment": {"conda": "env"},
                }
            ]
        }

        yaml_path = temp_dir / "no_name.yaml"
        with open(yaml_path, "w") as f:
            yaml.dump(yaml_content, f)

        runner = WorkflowRunner.from_yaml(yaml_path)

        assert runner.workflow.name == "unnamed"

    def test_from_yaml_with_args(self, temp_dir):
        """Test loading workflow with args and template rendering."""
        yaml_content = {
            "name": "args_workflow",
            "args": {
                "dataset_name": "test-dataset",
                "model_path": "/models/bert",
                "batch_size": 16,
                "output_dir": "/outputs/experiment",
            },
            "jobs": [
                {
                    "name": "preprocess",
                    "command": [
                        "python",
                        "preprocess.py",
                        "--dataset",
                        "{{ dataset_name }}",
                        "--output",
                        "{{ output_dir }}/preprocessed",
                    ],
                    "work_dir": "{{ output_dir }}",
                    "environment": {"conda": "ml_env"},
                },
                {
                    "name": "train",
                    "command": [
                        "python",
                        "train.py",
                        "--model",
                        "{{ model_path }}",
                        "--data",
                        "{{ output_dir }}/preprocessed",
                        "--batch-size",
                        "{{ batch_size }}",
                    ],
                    "depends_on": ["preprocess"],
                    "work_dir": "{{ output_dir }}",
                    "environment": {"conda": "ml_env"},
                },
            ],
        }

        yaml_path = temp_dir / "args_workflow.yaml"
        with open(yaml_path, "w") as f:
            yaml.dump(yaml_content, f)

        runner = WorkflowRunner.from_yaml(yaml_path)

        assert runner.workflow.name == "args_workflow"
        assert runner.args == {
            "dataset_name": "test-dataset",
            "model_path": "/models/bert",
            "batch_size": 16,
            "output_dir": "/outputs/experiment",
        }
        assert len(runner.workflow.jobs) == 2

        # Check that Jinja templates were rendered correctly
        preprocess_job = next(j for j in runner.workflow.jobs if j.name == "preprocess")
        train_job = next(j for j in runner.workflow.jobs if j.name == "train")

        # Check preprocess job
        assert preprocess_job.command == [
            "python",
            "preprocess.py",
            "--dataset",
            "test-dataset",
            "--output",
            "/outputs/experiment/preprocessed",
        ]
        assert preprocess_job.work_dir == "/outputs/experiment"

        # Check train job
        assert train_job.command == [
            "python",
            "train.py",
            "--model",
            "/models/bert",
            "--data",
            "/outputs/experiment/preprocessed",
            "--batch-size",
            "16",
        ]
        assert train_job.work_dir == "/outputs/experiment"
        assert train_job.depends_on == ["preprocess"]

    def test_from_yaml_no_args(self, temp_dir):
        """Test loading workflow without args section."""
        yaml_content = {
            "name": "no_args_workflow",
            "jobs": [
                {
                    "name": "simple_job",
                    "command": ["echo", "hello"],
                    "environment": {"conda": "test_env"},
                }
            ],
        }

        yaml_path = temp_dir / "no_args.yaml"
        with open(yaml_path, "w") as f:
            yaml.dump(yaml_content, f)

        runner = WorkflowRunner.from_yaml(yaml_path)

        assert runner.workflow.name == "no_args_workflow"
        assert runner.args == {}
        assert len(runner.workflow.jobs) == 1

        job = runner.workflow.jobs[0]
        assert job.command == ["echo", "hello"]

    def test_from_yaml_invalid_template(self, temp_dir):
        """Test loading workflow with invalid Jinja template."""
        yaml_content = {
            "name": "invalid_template_workflow",
            "args": {"valid_var": "value"},
            "jobs": [
                {
                    "name": "invalid_job",
                    "command": ["echo", "{{ undefined_var }}"],
                    "environment": {"conda": "test_env"},
                }
            ],
        }

        yaml_path = temp_dir / "invalid_template.yaml"
        with open(yaml_path, "w") as f:
            yaml.dump(yaml_content, f)

        with pytest.raises(WorkflowValidationError, match="Template rendering failed"):
            WorkflowRunner.from_yaml(yaml_path)

    def test_render_jobs_with_args_static_method(self):
        """Test _render_jobs_with_args static method."""
        args = {
            "dataset": "mnist",
            "epochs": 10,
            "output": "/results",
        }

        jobs_data = [
            {
                "name": "train",
                "command": [
                    "python",
                    "train.py",
                    "--dataset",
                    "{{ dataset }}",
                    "--epochs",
                    "{{ epochs }}",
                ],
                "work_dir": "{{ output }}",
            }
        ]

        rendered_jobs = WorkflowRunner._render_jobs_with_args(jobs_data, args)

        assert len(rendered_jobs) == 1
        job = rendered_jobs[0]
        assert job["command"] == [
            "python",
            "train.py",
            "--dataset",
            "mnist",
            "--epochs",
            "10",
        ]
        assert job["work_dir"] == "/results"

    def test_render_jobs_with_args_no_args(self):
        """Test _render_jobs_with_args with no args."""
        jobs_data = [
            {
                "name": "simple_job",
                "command": ["echo", "hello"],
            }
        ]

        rendered_jobs = WorkflowRunner._render_jobs_with_args(jobs_data, {})

        assert rendered_jobs == jobs_data

    def test_render_jobs_with_args_empty_args(self):
        """Test _render_jobs_with_args with empty args dict."""
        jobs_data = [
            {
                "name": "simple_job",
                "command": ["echo", "hello"],
            }
        ]

        rendered_jobs = WorkflowRunner._render_jobs_with_args(jobs_data, {})

        assert rendered_jobs == jobs_data

    @patch("srunx.runner.Slurm")
    def test_run_simple_workflow(self, mock_slurm_class):
        """Test running simple workflow."""
        mock_slurm = Mock()
        mock_slurm_class.return_value = mock_slurm

        # Create a job that will be "completed"
        job = Job(
            name="test_job",
            command=["echo", "test"],
            environment=JobEnvironment(conda="env"),
        )
        job.status = JobStatus.COMPLETED

        # Mock the slurm.run method to return the completed job
        mock_slurm.run.return_value = job

        workflow = Workflow(name="test", jobs=[job])
        runner = WorkflowRunner(workflow)

        results = runner.run()

        assert len(results) == 1
        assert "test_job" in results
        assert results["test_job"] is job
        mock_slurm.run.assert_called_once_with(job)

    @patch("srunx.runner.Slurm")
    def test_run_workflow_with_dependencies(self, mock_slurm_class):
        """Test running workflow with dependencies."""
        mock_slurm = Mock()
        mock_slurm_class.return_value = mock_slurm

        job1 = Job(
            name="job1", command=["echo", "1"], environment=JobEnvironment(conda="env")
        )
        job2 = Job(
            name="job2",
            command=["echo", "2"],
            environment=JobEnvironment(conda="env"),
            depends_on=["job1"],
        )

        # Ensure jobs start in PENDING status for dependency tests
        job1._status = JobStatus.PENDING
        job2._status = JobStatus.PENDING

        # Set up mock to return completed jobs
        def mock_run(job):
            job.status = JobStatus.COMPLETED
            return job

        mock_slurm.run.side_effect = mock_run

        workflow = Workflow(name="test", jobs=[job1, job2])
        runner = WorkflowRunner(workflow)

        results = runner.run()

        assert len(results) == 2
        assert "job1" in results
        assert "job2" in results
        assert mock_slurm.run.call_count == 2

    @patch("srunx.runner.Slurm")
    def test_run_workflow_job_failure(self, mock_slurm_class):
        """Test running workflow with job failure."""
        mock_slurm = Mock()
        mock_slurm_class.return_value = mock_slurm

        job = Job(
            name="failing_job",
            command=["false"],
            environment=JobEnvironment(conda="env"),
        )

        # Mock slurm.run to raise an exception
        mock_slurm.run.side_effect = RuntimeError("Job failed")

        workflow = Workflow(name="test", jobs=[job])
        runner = WorkflowRunner(workflow)

        with pytest.raises(RuntimeError):
            runner.run()

    def test_parse_job_simple(self):
        """Test parsing simple job from dict."""
        job_data = {
            "name": "test_job",
            "command": ["python", "script.py"],
            "environment": {"conda": "env"},
        }

        job = WorkflowRunner.parse_job(job_data)

        assert isinstance(job, Job)
        assert job.name == "test_job"
        assert job.command == ["python", "script.py"]
        assert job.environment.conda == "env"

    def test_parse_job_with_resources(self):
        """Test parsing job with resources."""
        job_data = {
            "name": "gpu_job",
            "command": ["python", "train.py"],
            "environment": {"conda": "ml_env"},
            "resources": {"nodes": 2, "gpus_per_node": 1, "memory_per_node": "32GB"},
        }

        job = WorkflowRunner.parse_job(job_data)

        assert job.resources.nodes == 2
        assert job.resources.gpus_per_node == 1
        assert job.resources.memory_per_node == "32GB"

    def test_parse_job_with_dependencies(self):
        """Test parsing job with dependencies."""
        job_data = {
            "name": "dependent_job",
            "command": ["python", "process.py"],
            "environment": {"conda": "env"},
            "depends_on": ["job1", "job2"],
        }

        job = WorkflowRunner.parse_job(job_data)

        assert job.depends_on == ["job1", "job2"]

    def test_parse_shell_job(self):
        """Test parsing shell job."""
        job_data = {"name": "shell_job", "path": "/path/to/script.sh"}

        job = WorkflowRunner.parse_job(job_data)

        assert isinstance(job, ShellJob)
        assert job.name == "shell_job"
        assert job.script_path == "/path/to/script.sh"

    def test_parse_job_both_path_and_command(self):
        """Test parsing job with both path and command (should fail)."""
        job_data = {
            "name": "invalid_job",
            "command": ["echo", "test"],
            "path": "/path/to/script.sh",
        }

        with pytest.raises(WorkflowValidationError):
            WorkflowRunner.parse_job(job_data)

    def test_parse_job_with_directories(self):
        """Test parsing job with custom directories."""
        job_data = {
            "name": "dir_job",
            "command": ["python", "script.py"],
            "environment": {"conda": "env"},
            "log_dir": "/custom/logs",
            "work_dir": "/custom/work",
        }

        job = WorkflowRunner.parse_job(job_data)

        assert job.log_dir == "/custom/logs"
        assert job.work_dir == "/custom/work"

    @patch("srunx.runner.WorkflowRunner.from_yaml")
    @patch("srunx.runner.WorkflowRunner.run")
    def test_execute_from_yaml(self, mock_run, mock_from_yaml):
        """Test execute_from_yaml method."""
        mock_runner = Mock()
        mock_from_yaml.return_value = mock_runner
        mock_results = {"job1": Mock()}
        mock_runner.run.return_value = mock_results

        runner = WorkflowRunner(Workflow(name="test", jobs=[]))
        results = runner.execute_from_yaml("test.yaml")

        mock_from_yaml.assert_called_once_with("test.yaml")
        mock_runner.run.assert_called_once()
        assert results == mock_results


class TestRunWorkflowFromFile:
    """Test run_workflow_from_file convenience function."""

    @patch("srunx.runner.WorkflowRunner")
    def test_run_workflow_from_file(self, mock_runner_class):
        """Test run_workflow_from_file convenience function."""
        mock_runner = Mock()
        mock_runner_class.from_yaml.return_value = mock_runner
        mock_results = {"job1": Mock()}
        mock_runner.run.return_value = mock_results

        results = run_workflow_from_file("test.yaml")

        mock_runner_class.from_yaml.assert_called_once_with("test.yaml")
        mock_runner.run.assert_called_once()
        assert results == mock_results
