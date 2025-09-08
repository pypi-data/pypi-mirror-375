import atexit
import os

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from threading import Thread

from autoed.autoed import AutoedDaemon, kill_process_and_children
from autoed.server.auth import validate_token
from autoed.process.process_static import process_dir

autoed_daemon = AutoedDaemon()
with open(autoed_daemon.lock_file, 'w') as f:
    print('Starting autoed daemon')
    f.write("")

def shutdown():
    for indir in autoed_daemon.directories:
        pid = autoed_daemon.pids[indir]
        kill_process_and_children(int(pid))
    if os.path.exists(autoed_daemon.lock_file):
        os.remove(autoed_daemon.lock_file)
    if os.path.exists(autoed_daemon.dirs_file):
        os.remove(autoed_daemon.dirs_file)

atexit.register(shutdown)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter(prefix="/api/v1", dependencies=[Depends(validate_token)])


class Watcher(BaseModel):
    path: str
    pid: int


@router.get("/watchers")
async def get_watchers() -> list[Watcher]:
    return [
        {"path": d, "pid": autoed_daemon.pids[d]} for d in autoed_daemon.directories
    ]


class PID(BaseModel):
    pid: int


@router.get("/watchers/{path:path}/pid")
async def get_watcher_pid(path: str) -> PID:
    return {"pid": autoed_daemon.pids[f"{path}"]}


class WatcherSetup(BaseModel):
    path: str
    inotify: bool = False
    sleep_time: float = 30
    log_dir: str = ""
    slurm: bool = False
    config_file: str = ""


@router.post("/watcher")
async def start_watcher(watcher_setup: WatcherSetup):
    autoed_daemon.watch(
        dirname=watcher_setup.path,
        use_inotify=watcher_setup.inotify,
        sleep_time=watcher_setup.sleep_time,
        log_dir=watcher_setup.log_dir,
        local=not watcher_setup.slurm,
        config_file=watcher_setup.config_file or None,
    )


@router.delete("/watchers/{pid}")
async def stop_watcher(pid: str):
    if pid in autoed_daemon.pids.values():
        kill_process_and_children(int(pid))
        for d, _pid in autoed_daemon.pids.items():
            if _pid == pid:
                del autoed_daemon.pids[d]
                autoed_daemon.directories.remove(d)
                break

class ProcessSetup(BaseModel):
    path: str
    slurm: bool = True
    force: bool = True
    config_file: str = ""

@router.post("/process")
async def process(process_setup: ProcessSetup):
    command = f"autoed_process {process_setup.path}"
    if process_setup.force:
        command += " -f"
    process = subprocess.Popen(command, shell=True, env={**os.environ, "AUTOED_CONFIG_FILE": process_setup.config_file} if process_setup.config_file else None)
    return process.pid
