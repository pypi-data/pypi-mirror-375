from _typeshed import Incomplete
from minjiang_client.experiment import Experiment
from minjiang_client.group.cloud_group import CloudGroup as CloudGroup
from minjiang_client.waveform import WavePackage as WavePackage
from minjiang_host_client.base.channel import Channel as Channel
from minjiang_host_client.base.worker import Worker as Worker
from minjiang_host_client.utils.terminate import check_terminate_signal as check_terminate_signal
from typing import Any

class CompilerWorker(Worker):
    space_name: str | None
    local_space_timestamp: int | None
    exp_json: dict | None
    def __init__(self, name: str, group_name: str, in_chl: Channel = None, out_chl: Channel = None) -> None: ...
    @property
    def group(self) -> CloudGroup: ...
    @group.setter
    def group(self, value: CloudGroup): ...
    def callback(self, wave_package: WavePackage, exp_obj: Experiment, pos: list, steps: int, options: dict): ...
    def compile(self, wave_package: WavePackage, exp_obj: Experiment, pos: list, steps: int, options: dict): ...
    exp_id: Incomplete
    def process_data(self, data: Any = None): ...
