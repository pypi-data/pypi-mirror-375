import json
import random
import shlex
import string
import time
from typing import Optional

import requests
from beaker import (
    Beaker,
    BeakerDataMount,
    BeakerDataset,
    BeakerEnvVar,
    BeakerExperimentSpec,
    BeakerJob,
    BeakerJobPriority,
    BeakerWorkloadStatus,
)
from rich.console import Console

from minienv.backend import Backend
from minienv.constants import SERVER_DIR

class SilentConsole:
    """ A mock version of rich.console """
    def __getattr__(self, _):
        def noop(*args, **kwargs):
            return self
        return noop

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

# console = Console()
console = SilentConsole()

AUS_CLUSTERS = [
    "ai2/saturn-cirrascale",
    "ai2/neptune-cirrascale",
    "ai2/jupiter-cirrascale-2",
    "ai2/ceres-cirrascale",
]

DEFAULT_ENTRYPOINT = ["bash", "-c", "python /server/main.py"]


def get_rand_suffix(k):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=k))


def launch_beaker_job(
    name,
    description,
    docker_image,
    port = None,
    server_mount: Optional[BeakerDataset] = None,
    task_mount: Optional[BeakerDataset] = None,
    entrypoint: list[str] = DEFAULT_ENTRYPOINT,
    additional_mounts: dict[str, BeakerDataset] = {},
    env_vars: dict[str, str] = {},
    result_path="/results",
    workspace="ai2/rollouts",
) -> BeakerJob:
    beaker = Beaker.from_env()

    task_name = f"{name}-" + get_rand_suffix(k=4)

    beaker_env_vars = [
        BeakerEnvVar(name=key, value=str(value)) for key, value in env_vars.items()
    ]

    args = []

    if port is not None:
        args += ["--port", port]
        beaker_env_vars += [
            BeakerEnvVar(name="MINIENV_PORT", value=str(port)),
        ]
        assert server_mount is not None, \
            "Server code is required for port access!"

    datasets = []
    
    # Add server code
    if server_mount is not None:
        datasets += [
            BeakerDataMount.new(
                beaker=server_mount.id,
                mount_path="/server",
            )
        ]
        assert port is not None, \
            "Port is required for server access!"

    # Add task-specific files
    if task_mount is not None:
        datasets += [BeakerDataMount.new(
            beaker=task_mount.id,
            mount_path="/task",
        )]

    # Add additional volumes
    for mount_path, host_path in additional_mounts.items():
        datasets += [BeakerDataMount.new(
            mount_path=mount_path,
            beaker=host_path.id,
            # host_path
            # weka
            # result
        )]

    # Distinguish between docker-hosted and beaker-hosted images
    if '/' in docker_image:
        # this is a beaker image
        beaker_image = docker_image
        docker_image = None
    else:
        # this is a docker image
        docker_image = docker_image
        beaker_image = None

    if (beaker_image is None) == (docker_image is None):
        raise ValueError("Exactly one of beaker_image or docker_image must be specified", (beaker_image, docker_image))

    spec = BeakerExperimentSpec.new(
        task_name=task_name,
        description=description,
        docker_image=docker_image,
        beaker_image=beaker_image,
        priority=BeakerJobPriority.normal,
        preemptible=True,
        budget="ai2/oe-eval",
        cluster=AUS_CLUSTERS,
        result_path=result_path,
        datasets=datasets,
        env_vars=[
            BeakerEnvVar(name="PYTHONUNBUFFERED", value=str(1)),
        ] + beaker_env_vars,
        command=entrypoint,
        host_networking=True, # @davidh -- Careful with networking
        arguments=args,
    )

    console.print("[bold blue]Beaker experiment spec:[/bold blue]")
    console.print(spec)

    workspace_link = f"https://beaker.allen.ai/orgs/ai2/workspaces/{workspace.split('/')[1]}"

    # Create beaker experiment
    with console.status(f"[bold yellow]creating beaker experiment at[/] {workspace_link}", spinner="dots") as _:
        workload = beaker.experiment.create(
            spec=spec, 
            name=task_name, 
            workspace=workspace
        )

    # Wait for environment to initalize
    with console.status(f"[bold yellow]initializing beaker experiment at[/] {workspace_link}", spinner="dots") as _:
        while (job := beaker.workload.get_latest_job(workload)) is None:
            time.sleep(0.1)

    console.print(f"[bold green]environment setup complete:[/] {workspace_link}")

    # Wait for startup
    with console.status("[bold yellow]waiting for job to start...", spinner="dots") as _:
        while job.status.status in [
            BeakerWorkloadStatus.submitted,
            BeakerWorkloadStatus.queued,
            BeakerWorkloadStatus.initializing,
        ]:
            time.sleep(0.1)
            job = beaker.workload.get_latest_job(workload)
            if job is None:
                raise RuntimeError("beaker job failed to start")
    console.print("[bold green]job started![/bold green]")

    return job


def create_dataset(name: str, description: str, source_paths: list[str], target_dir: str = None):
    """Create beaker dataset"""
    beaker = Beaker.from_env()

    dataset_name = f"{name}-" + get_rand_suffix(k=4)

    # Create beaker dataset
    with console.status(
        f"[bold yellow]Creating dataset '{dataset_name}'...[/bold yellow]", spinner="dots"
    ) as _:
        dataset = beaker.dataset.create(
            dataset_name,
            *source_paths,
            target=target_dir,
            description=description,
            force=False,
            commit=True,
            strip_paths=False,
        )
    console.print(
        f"[bold green]dataset upload complete:[/bold green] {beaker.dataset.url(dataset)}"
    )

    # Print uploaded files
    files = list(beaker.dataset.list_files(dataset))
    for file in files:
        console.print(f" - {file.path} ({file.size} bytes)")

    return dataset


def get_hostname(job: BeakerJob, full_hostname=False):
    beaker = Beaker.from_env()
    node_id = job.assignment_details.node_id
    node = beaker.node.get(node_id)
    hostname = node.hostname
    if not full_hostname:
        hostname = hostname.replace('.reviz.ai2.in', '')
    return hostname


def ping_server(hostname: str, port: int, timeout: int = 20):
    """Ping server until it responds or timeout is reached"""
    url = f"http://{hostname}:{port}/ping"
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(2)

    return False


class BeakerBackend(Backend):
    """Beaker backend implementation."""
    
    def __init__(self, workspace: str = "ai2/rollouts"):
        self.workspace = workspace
        self.hostname: str = None
        self.port: int = None
        
    async def create_env(
        self, 
        task_name: str, 
        image: str, 
        task_files: Optional[list[str]] = None, 
        env_vars: dict[str, str] = {}
    ) -> None:
        port = random.randint(1_000, 10_000)

        server_dataset = create_dataset(
            name=f"minienv.{task_name}.server",
            description="server entrypoint",
            source_paths=[SERVER_DIR],
        )

        # Upload task-specific files
        task_dataset = None
        if task_files is not None:
            task_dataset = create_dataset(
                name=f"minienv.{task_name}.task",
                description="task files",
                source_paths=task_files,
            )

        job: BeakerJob = launch_beaker_job(
            name=f"minienv.{task_name}",
            server_mount=server_dataset,
            task_mount=task_dataset,
            description=f"A minienv rollout: '{task_name}' on '{image}'",
            docker_image=image,
            port=port,
            env_vars=env_vars,
            workspace=self.workspace,
        )

        hostname = get_hostname(job)

        # Wait for server to be ready
        with console.status("[bold yellow]waiting for server to be ready...", spinner="dots") as _:
            if not ping_server(hostname=hostname, port=port):
                console.print("[bold red]server failed to start within timeout![/bold red]")
                exit(1)
        console.print("[bold green]server is ready![/bold green]")

        ### you have to be on VPN to do this, but should add private key for extra layer of security. generate private/public key on execution

        self.hostname = hostname
        self.port = port

    async def exec_command(self, command: list[str], timeout: int = 60, cwd: str = None) -> tuple[str, str, int]:
        url = f"http://{self.hostname}:{self.port}/exec"
        
        if self.hostname is None or self.port is None:
            raise RuntimeError(f'Backend not intialized: {url}')
        
        headers = {"Content-Type": "application/json"}
        payload = {
            "command": command, 
            "timeout": timeout
        }

        if cwd is not None:
            payload["cwd"] = cwd
                
        if isinstance(command, list):
            command = shlex.join(command)
        
        with console.status(f"[bold yellow]executing command: {command}...", spinner="dots") as _:
            response = requests.post(
                url, 
                headers=headers, 
                data=json.dumps(payload), 
                timeout=timeout + 10
            )
        
        if response.status_code != 200:
            raise RuntimeError(f"Command execution failed: {response.status_code} {response.text}")

        response  = response.json()

        stdout    = response["stdout"]
        stderr    = response["stderr"]
        exit_code = response["exit_code"]

        return stdout, stderr, exit_code

    async def upload_file(self, content: bytes, destination: str) -> None:
        """Upload file content to the environment via HTTP API."""
        url = f"http://{self.hostname}:{self.port}/upload"
        headers = {"Content-Type": "application/json"}
        # Encode content as base64 for JSON transport
        import base64
        data = {
            "destination": destination,
            "content": base64.b64encode(content).decode('utf-8')
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code != 200:
            raise RuntimeError(f"File upload failed: {response.status_code} {response.text}")

    async def download_file(self, source: str) -> bytes:
        """Download file content from the environment via HTTP API."""
        url = f"http://{self.hostname}:{self.port}/download"
        headers = {"Content-Type": "application/json"}
        data = {"source": source}
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code != 200:
            raise RuntimeError(f"File download failed: {response.status_code} {response.text}")
        
        response_data = response.json()
        # Decode base64 content
        import base64
        return base64.b64decode(response_data["content"])

    async def teardown(self) -> bool:
        if self.hostname is None or self.port is None:
            # if a backend was never initialized, return
            return

        url = f"http://{self.hostname}:{self.port}/shutdown"
        response = requests.post(url)
        
        if response.status_code != 200:
            console.print(f"[bold red]Job failed to shut down. Response:[/bold red] {response}")
            return False
        
        response = response.json()

        if response["status"] == "shutting down":
            console.print("[bold green]Teardown successful![/bold green]")
            return True

        console.print("[bold red]Job failed to shut down[/bold red]")
        return False


if __name__ == "__main__":
    import asyncio
    
    async def main():
        backend = BeakerBackend()

        await backend.create_env(task_name="fibonacci", image="python:3.11-slim")

        stdout, stderr, exit_code = await backend.exec_command(["ls"], timeout=10)

        print(f"stdout: {stdout}")
        print(f"stderr: {stderr}")
        print(f"exit_code: {exit_code}")

        success = await backend.teardown()
        print(f"Teardown successful: {success}")
    
    asyncio.run(main())
