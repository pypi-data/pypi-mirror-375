import datetime
import json
import os
import sys
import time
import traceback
from typing import Any, Dict, Optional

import requests
import requests.auth
import yaml
from pushover import Pushover

VERSION = '0.1.1'

class Tracing:


    def __init__(self, context: Any, max_interval: int = 60) -> None:
        self.log("initialising tracing")

        self.start_time: float = time.time()

        timestamp: str = datetime.datetime.fromtimestamp(self.start_time).strftime('%Y-%m-%d %H:%M:%S')
        self.log(f"start time: {timestamp}")

        self.function_name: str

        if type(context) is str:
            self.function_name = context
        else:
            self.function_name = context.function_name

        if os.path.exists('/etc/tracing.yaml'):
            config: Dict[str, str] = yaml.safe_load(open('/etc/tracing.yaml').read())

            os.environ['TRACING_ENDPOINT'] = config['endpoint']
            os.environ['TRACING_PUSHOVER_USER'] = config['pushover_user']
            os.environ['TRACING_PUSHOVER_APP'] = config['pushover_app']

        self.endpoint: str = os.environ['TRACING_ENDPOINT']

        self.log(f"tracing endpoint: {self.endpoint}")

        self.auth: Optional[requests.auth.HTTPBasicAuth]

        if 'TRACING_USERNAME' in os.environ and 'TRACING_PASSWORD' in os.environ:
            self.auth = requests.auth.HTTPBasicAuth(
                os.environ['TRACING_USERNAME'],
                os.environ['TRACING_PASSWORD']
            )
        else:
            self.auth = None

        self.state: Dict[str, Any] = self.get_state()

        self.pushover: Pushover = Pushover(os.environ['TRACING_PUSHOVER_USER'], api_token=os.environ['TRACING_PUSHOVER_APP'])

        self.proxies: Dict[str, str]

        if 'SOCKS5_PROXY' in os.environ:
            self.proxies = {'https': f"socks5h://{os.environ['SOCKS5_PROXY']}"}
            self.log(f"using proxy: {os.environ['SOCKS5_PROXY']}")
        else:
            self.proxies = {}
            self.log("not using proxy")

        self.max_interval: int = max_interval
        self.last_report: float | None = None


    def log(self, message: str) -> None:
        if 'DEBUG' in os.environ:
            sys.stdout.write(message + "\n")
            sys.stdout.flush()


    def get_state(self) -> Dict[str, Any]:
        self.log(f"getting state for function: {self.function_name}")

        for i in range(0, 5):
            try:
                resp: requests.Response = requests.get(
                    f"{self.endpoint}/tracing/{self.function_name}",
                    timeout=10,
                    auth=self.auth,
                    proxies=self.proxies
                )

                data: Dict[str, Any] = json.loads(resp.text)

                self.log(f"state returned: {data}")

            except Exception:
                return {}

        return data


    def success(self) -> None:
        timestamp: int = int(time.time())
        runtime: float = time.time() - self.start_time

        if 'success' in self.state and not self.state['success']:
            self.pushover.send('resolved', self.function_name)

        if 'success' not in self.state or not self.state['success'] or self.last_report is None or (time.time() - self.last_report) > self.max_interval:
            try:
                self.send_state(True, timestamp, runtime)
                self.last_report = time.time()
            except Exception as e:
                sys.stderr.write(f"failed to send metrics: {str(e)}\n")
                sys.stderr.flush()

                raise e


    def send_state(self, success: bool, timestamp: int, runtime: float) -> None:
        self.log("emitting state:\n")
        self.log(f"success: {int(success)}\n")
        self.log(f"runtime: {runtime:.2f} seconds\n")

        for i in range(0, 5):
            try:
                resp: requests.Response = requests.post(
                    f"{self.endpoint}/tracing/{self.function_name}",
                    json={
                        'success': success,
                        'key': self.function_name,
                        'timestamp': timestamp,
                        'runtime': runtime,
                        'version': VERSION,
                    },
                    headers={
                        'Content-Type': 'application/json'
                    },
                    timeout=10,
                    auth=self.auth,
                    proxies=self.proxies
                )

                self.log(f"state response: {resp.status_code} - {resp.text}")

                if resp.status_code == 200:
                    break

            except Exception as e:
                self.log(f"error sending data: {e}")
                time.sleep(1)


    def failure(self) -> None:
        timestamp: int = int(time.time())
        runtime: float = time.time() - self.start_time

        self.state = self.get_state()

        exc_type, exc_value, exc_traceback = sys.exc_info()

        data: Dict[str, Any] = {
            'success': False,
            'key': self.function_name,
            'timestamp': timestamp,
            'runtime': runtime,
            'version': VERSION,
            'exception_type': str(exc_type.__name__) if exc_type else 'Unknown',
            'exception_message': str(exc_value),
        }

        report = False

        if 'exception_type' not in self.state or 'exception_message' not in self.state or data['exception_type'] != self.state['exception_type'] or \
            data['exception_message'] != self.state['exception_message']:

            trace_identifier: str = f"{self.function_name}_{int(time.time() * 1000000)}"

            content: str = f"Function: {self.function_name}\n"
            content += f"Runtime: {runtime:.2f} seconds\n"
            content += f"Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            content += traceback.format_exc()

            url: str = f"{self.endpoint}/trace/{self.function_name}/{trace_identifier}"

            exception: str = traceback.format_exception_only(*sys.exc_info()[:2])[-1].strip()

            self.pushover.send(exception, title=self.function_name, url=url)

            data['trace_identifier'] = trace_identifier
            data['trace'] = content

            report = True

        if 'success' in self.state and not self.state['success']:
            return

        if report:
            for i in range(0, 5):
                try:
                    resp: requests.Response = requests.post(
                        f"{self.endpoint}/tracing/{self.function_name}",
                        json=data,
                        headers={
                            'Content-Type': 'application/json'
                        },
                        timeout=10,
                        auth=self.auth,
                        proxies=self.proxies
                    )

                    if resp.status_code == 200:
                        break

                except Exception:
                    pass
