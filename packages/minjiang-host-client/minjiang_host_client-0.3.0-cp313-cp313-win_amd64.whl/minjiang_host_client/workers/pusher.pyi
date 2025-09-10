from _typeshed import Incomplete
from minjiang_host_client.base.channel import Channel as Channel
from minjiang_host_client.base.worker import Worker as Worker
from minjiang_host_client.utils.local import get_cache_dir as get_cache_dir, set_cache_dir as set_cache_dir
from minjiang_host_client.utils.terminate import check_terminate_signal as check_terminate_signal
from typing import Any

__MAX_UPLOAD_DURATION__: int
__MAX_UPLOAD_STEPS__: int

class PusherWorker(Worker):
    space_name: str | None
    organization_id: int | None
    pos: list[int] | None
    steps: int | None
    total_steps: int | None
    compiled_sweep_len: list[int] | None
    exp_json: dict | None
    exp_options: dict[str, Any] | None
    minio: Incomplete
    result: Incomplete
    result_cache: Incomplete
    result_obj: Incomplete
    last_upload_time: int
    last_upload_step: int
    chunk_id: int
    chunk_item_start: int
    cache_dir: Incomplete
    def __init__(self, name: str, group_name: str, in_chl: Channel = None, out_chl: Channel = None) -> None: ...
    exp_id: Incomplete
    def process_data(self, data: Any = None): ...
