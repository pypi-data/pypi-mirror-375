#!/usr/bin/python3
# -*- coding: utf8 -*-
# Copyright (c) 2025 ZWDX, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from minjiang_client.group.cloud_group import CloudGroup
from minjiang_host_client.server.final import FinalServer
from minjiang_host_client.server.main import MainServer
from minjiang_host_client.server.result import ResultServer
from minjiang_host_client.server.tasks import TasksServer
from minjiang_host_client.server.waveform import WaveformServer
from minjiang_host_client.workers.compiler import CompilerWorker
from minjiang_host_client.workers.post_process import PostProcessWorker
from minjiang_host_client.workers.puller import PullerWorker
from minjiang_host_client.workers.pusher import PusherWorker
from minjiang_host_client.workers.qhal import QHALWorker
from minjiang_host_client.base.channel import Channel
from multiprocessing import shared_memory
from typing import Callable

__VERSION__ = [0, 3, 0]


class Main(object):

    def __init__(self, group_name: str, manual_compiler: Callable = None, manual_qhal: Callable = None,
                 manual_post_process: Callable = None):

        self.group_name = group_name

        # Channel
        self.chl_puller_task = Channel("chl_puller_task_" + group_name, create=True)
        self.chl_compiler_task = Channel("chl_compiler_task_" + group_name, create=True)
        self.chl_compiler_waveform = Channel("chl_compiler_waveform_" + group_name, create=True)
        self.chl_qhal_waveform = Channel("chl_qhal_waveform_" + group_name, create=True)
        self.chl_qhal_result = Channel("chl_qhal_result_" + group_name, create=True)
        self.chl_post_process_result = Channel("chl_post_process_result_" + group_name, create=True)
        self.chl_post_process_final = Channel("chl_post_process_final_" + group_name, create=True)
        self.chl_pusher_final = Channel("chl_pusher_final_" + group_name, create=True)

        # Server
        self.main_server = MainServer("main", self.group_name)
        self.tasks_server = TasksServer("tasks", self.group_name,
                                        self.chl_puller_task, self.chl_compiler_task)
        self.waveform_server = WaveformServer("waveform", self.group_name,
                                              self.chl_compiler_waveform, self.chl_qhal_waveform)
        self.result_server = ResultServer("result", self.group_name,
                                          self.chl_qhal_result, self.chl_post_process_result)
        self.final_server = FinalServer("final", self.group_name,
                                        self.chl_post_process_final, self.chl_pusher_final)

        # Worker
        self.pull_worker = PullerWorker("puller", self.group_name, None, self.chl_puller_task)
        self.push_worker = PusherWorker("pusher", self.group_name, self.chl_pusher_final, None)

        if manual_compiler is None:
            self.compiler_worker = CompilerWorker("compiler", self.group_name,
                                                  self.chl_compiler_task, self.chl_compiler_waveform)
        else:
            self.compiler_worker = manual_compiler("compiler", self.group_name,
                                                   self.chl_compiler_task, self.chl_compiler_waveform)

        if manual_qhal is None:
            self.qhal_worker = QHALWorker("qhal", self.group_name,
                                          self.chl_qhal_waveform, self.chl_qhal_result)
        else:
            self.qhal_worker = manual_qhal("qhal", self.group_name,
                                           self.chl_qhal_waveform, self.chl_qhal_result)

        if manual_post_process is None:
            self.post_process_worker = PostProcessWorker("post_process", self.group_name,
                                                         self.chl_post_process_result, self.chl_post_process_final)
        else:
            self.post_process_worker = manual_post_process("post_process", self.group_name,
                                                           self.chl_post_process_result, self.chl_post_process_final)

        # Process
        self.main_server_process = None
        self.tasks_server_process = None
        self.waveform_server_process = None
        self.result_server_process = None
        self.final_server_process = None
        self.pull_worker_process = None
        self.compiler_worker_process = None
        self.qhal_worker_process = None
        self.post_process_worker_process = None
        self.push_worker_process = None

        self.compiler_worker.group = CloudGroup(group_name)
        self.qhal_worker.group = CloudGroup(group_name)
        self.post_process_worker.group = CloudGroup(group_name)

    def run(self):
        try:
            # Make server's process
            self.main_server_process = self.main_server.make_process()
            self.tasks_server_process = self.tasks_server.make_process()
            self.waveform_server_process = self.waveform_server.make_process()
            self.result_server_process = self.result_server.make_process()
            self.final_server_process = self.final_server.make_process()

            # Make worker's process
            self.pull_worker_process = self.pull_worker.make_process()
            self.compiler_worker_process = self.compiler_worker.make_process()
            self.qhal_worker_process = self.qhal_worker.make_process()
            self.post_process_worker_process = self.post_process_worker.make_process()
            self.push_worker_process = self.push_worker.make_process()

            # Start
            self.main_server_process.start()
            self.tasks_server_process.start()
            self.waveform_server_process.start()
            self.result_server_process.start()
            self.final_server_process.start()
            self.pull_worker_process.start()
            self.compiler_worker_process.start()
            self.qhal_worker_process.start()
            self.post_process_worker_process.start()
            self.push_worker_process.start()

            # Join
            self.main_server_process.join()
            self.tasks_server_process.join()
            self.waveform_server_process.join()
            self.result_server_process.join()
            self.final_server_process.join()
            self.pull_worker_process.join()
            self.compiler_worker_process.join()
            self.qhal_worker_process.join()
            self.post_process_worker_process.join()
            self.push_worker_process.join()
        finally:
            # 清理共享内存
            self.chl_puller_task.close()
            self.chl_compiler_task.close()
            self.chl_compiler_waveform.close()
            self.chl_qhal_waveform.close()
            self.chl_qhal_result.close()
            self.chl_post_process_result.close()
            self.chl_post_process_final.close()
            self.chl_pusher_final.close()

            # 在Unix系统上需要手动取消链接
            if hasattr(shared_memory, 'unlink'):
                try:
                    shared_memory.SharedMemory(name="chl_puller_task_" + self.group_name).unlink()
                    shared_memory.SharedMemory(name="chl_compiler_task_" + self.group_name).unlink()
                    shared_memory.SharedMemory(name="chl_compiler_waveform_" + self.group_name).unlink()
                    shared_memory.SharedMemory(name="chl_qhal_waveform_" + self.group_name).unlink()
                    shared_memory.SharedMemory(name="chl_qhal_result_" + self.group_name).unlink()
                    shared_memory.SharedMemory(name="chl_post_process_result_" + self.group_name).unlink()
                    shared_memory.SharedMemory(name="chl_post_process_final_" + self.group_name).unlink()
                    shared_memory.SharedMemory(name="chl_pusher_final_" + self.group_name).unlink()
                except FileNotFoundError:
                    pass

            print("All processes stopped and shared memory cleaned up.")

    def stop(self):
        self.main_server.running.value = False
        self.tasks_server.running.value = False
        self.waveform_server.running.value = False
        self.result_server.running.value = False
        self.final_server.running.value = False
        self.pull_worker.running.value = False
        self.compiler_worker.running.value = False
        self.qhal_worker.running.value = False
        self.post_process_worker.running.value = False
        self.push_worker.running.value = False
