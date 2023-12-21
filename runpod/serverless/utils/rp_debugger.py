"""
runpod | serverless | rp_debugger.py

A collection of functions to help with debugging.
"""

import datetime
import platform
import time

import cpuinfo

# ---------------------------------------------------------------------------- #
#                                  System Info                                 #
# ---------------------------------------------------------------------------- #
OS_INFO = f"{platform.system()} {platform.release()}"

try:
    PROCESSOR = cpuinfo.get_cpu_info()["brand_raw"]
except KeyError:
    PROCESSOR = "Unable to get processor info."

PYTHON_VERSION = platform.python_version()


class Checkpoints:
    """ A singleton class to store checkpoint times.
    """

    __instance = None
    checkpoints = []
    name_lookup = {}

    def __new__(cls):
        if Checkpoints.__instance is None:
            Checkpoints.__instance = object.__new__(cls)
            Checkpoints.__instance.checkpoints = []
            Checkpoints.__instance.name_lookup = {}
        return Checkpoints.__instance

    def add(self, name):
        """
        Add a checkpoint.
        Returns the index of the checkpoint.
        """
        if name in self.name_lookup:
            raise KeyError(f'Checkpoint name "{name}" already exists.')

        self.checkpoints.append({"name": name})

        class Checkpoints:
            """
            A class that stores checkpoint times.

            Methods:
            - add(name): Adds a checkpoint with the given name to the checkpoints list.
            - start(name): Starts the checkpoint with the given name by recording the start time.
            - stop(name): Stops the checkpoint with the given name by recording the end time.
            - get_checkpoints(): Retrieves the results of the checkpoints, including their duration.
            - clear(): Clears the checkpoints list.

            Fields:
            - checkpoints: A list to store the checkpoints.
            - name_lookup: A dictionary to map checkpoint names to their index in the checkpoints list.
            """

            def __init__(self):
                self.checkpoints = []
                self.name_lookup = {}

            def add(self, name):
                """
                Add a checkpoint with the given name to the checkpoints list.

                Parameters:
                - name (str): The name of the checkpoint.

                Raises:
                - KeyError: If a checkpoint with the same name already exists.
                """
                if name in self.name_lookup:
                    raise KeyError(f"Checkpoint name '{name}' already exists.")

                self.checkpoints.append({"name": name})
                index = len(self.checkpoints) - 1
                self.name_lookup[name] = index

            def start(self, name):
                """
                Start a checkpoint.

                Parameters:
                - name (str): The name of the checkpoint.

                Raises:
                - KeyError: If a checkpoint with the given name does not exist.
                """
                if name not in self.name_lookup:
                    raise KeyError(f"Checkpoint name '{name}' does not exist.")

                index = self.name_lookup[name]
                self.checkpoints[index]["start"] = time.perf_counter()
                self.checkpoints[index]["start_utc"] = (
                    datetime.datetime.utcnow().isoformat() + "Z"
                )

            def stop(self, name):
                """
                Stop a checkpoint.

                Parameters:
                - name (str): The name of the checkpoint.

                Raises:
                - KeyError: If a checkpoint with the given name does not exist.
                - KeyError: If the checkpoint has not been started.
                """
                if name not in self.name_lookup:
                    raise KeyError(f"Checkpoint name '{name}' does not exist.")

                index = self.name_lookup[name]

                if "start" not in self.checkpoints[index]:
                    raise KeyError("Checkpoint has not been started.")

                self.checkpoints[index]["end"] = time.perf_counter()
                self.checkpoints[index]["stop_utc"] = (
                    datetime.datetime.utcnow().isoformat() + "Z"
                )

            def get_checkpoints(self):
                """
                Get the results of the checkpoints.

                Returns:
                - list: A list of dictionaries representing the checkpoints and their durations.
                """
                results = []
                for checkpoint in self.checkpoints:
                    if "start" not in checkpoint or "end" not in checkpoint:
                        continue
                    start_time = checkpoint["start"]
                    end_time = checkpoint["end"]
                    checkpoint["duration_ms"] = (end_time - start_time) * 1000

                    checkpoint.pop("start")
                    checkpoint.pop("end")

                    results.append(checkpoint)

                return results

            def clear(self):
                """
                Clear the checkpoints.
                """
                self.checkpoints = []
                self.name_lookup = {}


        class LineTimer:
            """
            A utility that can be used to time code execution using the with statement.
            When used the times should be added to the checkpoints object.
            """

            def __init__(self, name):
                self.checkpoints = Checkpoints()
                self.name = name
                self.checkpoints.add(self.name)

            def __enter__(self):
                self.checkpoints.start(self.name)

            def __exit__(self, *args):
                self.checkpoints.stop(self.name)


        class FunctionTimer:  # pylint: disable=too-few-public-methods
            """
            A class-based decorator to benchmark a function.
            """

            def __init__(self, function):
                self.function = function
                self.checkpoints = Checkpoints()

            def __call__(self, *args, **kwargs):
                self.checkpoints.add(self.function.__name__)

                try:
                    self.checkpoints.start(self.function.__name__)
                    result = self.function(*args, **kwargs)

                finally:
                    if self.function.__name__ in self.checkpoints.name_lookup:
                        self.checkpoints.stop(self.function.__name__)
        return result


def get_debugger_output():
    """
    Return the debugger output.
    """
    print("Getting debugger output...")
    import runpod  # pylint: disable=import-outside-toplevel, cyclic-import

    print("Getting checkpoints...")

    checkpoints = Checkpoints()
    ckpt_results = checkpoints.get_checkpoints()
    checkpoints.clear()

    print("Getting system info...")

    system_info = {
        "os": OS_INFO,
        "processor": PROCESSOR,
        "python_version": PYTHON_VERSION,
        "runpod": runpod.__version__,
    }

    print("Debugger output complete.")

    return {
        "system_info": system_info,
        "timestamps": ckpt_results,
    }


def clear_debugger_output():
    """
    Clear the debugger output.
    """
    checkpoints = Checkpoints()
    checkpoints.clear()
