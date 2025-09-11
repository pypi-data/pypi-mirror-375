# SPDX-FileCopyrightText: Copyright (c) 2025, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import os
import tempfile
import typing

from nat.builder.front_end import FrontEndBase
from nat.front_ends.fastapi.fastapi_front_end_config import FastApiFrontEndConfig
from nat.front_ends.fastapi.fastapi_front_end_plugin_worker import FastApiFrontEndPluginWorkerBase
from nat.front_ends.fastapi.main import get_app
from nat.utils.io.yaml_tools import yaml_dump

logger = logging.getLogger(__name__)


class FastApiFrontEndPlugin(FrontEndBase[FastApiFrontEndConfig]):

    def get_worker_class(self) -> type[FastApiFrontEndPluginWorkerBase]:
        from nat.front_ends.fastapi.fastapi_front_end_plugin_worker import FastApiFrontEndPluginWorker

        return FastApiFrontEndPluginWorker

    @typing.final
    def get_worker_class_name(self) -> str:

        if (self.front_end_config.runner_class):
            return self.front_end_config.runner_class

        worker_class = self.get_worker_class()

        return f"{worker_class.__module__}.{worker_class.__qualname__}"

    async def run(self):

        # Write the entire config to a temporary file
        with tempfile.NamedTemporaryFile(mode="w", prefix="nat_config", suffix=".yml", delete=False) as config_file:

            # Get as dict
            config_dict = self.full_config.model_dump(mode="json", by_alias=True, round_trip=True)

            # Write to YAML file
            yaml_dump(config_dict, config_file)

            # Save the config file path for cleanup (required on Windows due to delete=False workaround)
            config_file_name = config_file.name

            # Set the config file in the environment
            os.environ["NAT_CONFIG_FILE"] = str(config_file.name)

            # Set the worker class in the environment
            os.environ["NAT_FRONT_END_WORKER"] = self.get_worker_class_name()

        try:
            if not self.front_end_config.use_gunicorn:
                import uvicorn

                reload_excludes = ["./.*"]

                uvicorn.run("nat.front_ends.fastapi.main:get_app",
                            host=self.front_end_config.host,
                            port=self.front_end_config.port,
                            workers=self.front_end_config.workers,
                            reload=self.front_end_config.reload,
                            factory=True,
                            reload_excludes=reload_excludes)

            else:
                app = get_app()

                from gunicorn.app.wsgiapp import WSGIApplication

                class StandaloneApplication(WSGIApplication):

                    def __init__(self, app, options=None):
                        self.options = options or {}
                        self.app = app
                        super().__init__()

                    def load_config(self):
                        config = {
                            key: value
                            for key, value in self.options.items() if key in self.cfg.settings and value is not None
                        }
                        for key, value in config.items():
                            self.cfg.set(key.lower(), value)

                    def load(self):
                        return self.app

                options = {
                    "bind": f"{self.front_end_config.host}:{self.front_end_config.port}",
                    "workers": self.front_end_config.workers,
                    "worker_class": "uvicorn.workers.UvicornWorker",
                }

                StandaloneApplication(app, options=options).run()

        finally:
            try:
                os.remove(config_file_name)
            except OSError as e:
                logger.exception(f"Warning: Failed to delete temp file {config_file_name}: {e}")
