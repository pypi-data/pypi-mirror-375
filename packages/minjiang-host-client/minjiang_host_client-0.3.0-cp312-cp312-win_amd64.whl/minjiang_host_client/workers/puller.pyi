from _typeshed import Incomplete
from minjiang_host_client.base.channel import Channel as Channel
from minjiang_host_client.base.worker import Worker as Worker
from minjiang_host_client.utils.terminate import list_terminate_signal as list_terminate_signal, remove_terminate_signal as remove_terminate_signal, write_terminate_signal as write_terminate_signal
from typing import Any

class PullerWorker(Worker):
    connection_status: Incomplete
    sent_signal_exp_id_list: Incomplete
    def __init__(self, name: str, group_name: str, in_chl: Channel = None, out_chl: Channel = None) -> None: ...
    def process_data(self, data: Any = None): ...
