# Copyright 2025 Oliver Lambson
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

"""Core NATS Extensions - utilities providing additional features to Core NATS."""

from natsext._version import __version__
from natsext.requestmany import default_sentinel, request_many, request_many_msg

__all__ = [
    "__version__",
    "default_sentinel",
    "request_many",
    "request_many_msg",
]
