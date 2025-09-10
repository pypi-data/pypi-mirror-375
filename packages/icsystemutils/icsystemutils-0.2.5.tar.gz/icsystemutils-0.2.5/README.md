`icsystemutils` is a library for querying system resources (cpu, gpu, network etc).

It is used in higher-level packages and tools in [Irish Centre for High End Computing (ICHEC)](https://www.ichec.ie) research and workflows.

# Features #

You can read system CPU info on Linux or Mac via system APIs with JSON output:

``` shell
icsystemutils read_cpu
```

You can read a system's NVIDIA GPU info and output:

``` shell
icsystemutils read_gpu
```

You can run a resource monitor that outputs CPU and memory use to a file with:


``` shell
icsystemutils monitor
```

You can also run this monitor on GPUs and record their use to a CSV with:


```shell
icsystemutils monitor --include gpu --output_path <path_to_csv_dir>
```

You can run a resource monitor that outputs NVIDIA GPU use to a file with:


You can postprocess a log file with:

``` shell
icsystemutils tracing --trace_file <file_with_traces> --trace_config <trace_config_file>
```

The log file should have traces in the format `timestamp | thread_id | message` where the timestamp is Unix time as a float with whole numbers representing seconds. The `message` is used to determine start and end points for events. `The trace_config_file` is a json file used to match strings in the message with Event start and end flags. The output is a series of trace events in json format, which can be used to generate plots with `icplot` or used in further analysis. 


# Installation #

You can install it with:

``` shell
pip install icsystemutils
```

# License #

This project is Copyright of the Irish Centre for High End Computing. You can use it under the terms of the GPLv3+, which further details in the included LICENSE file.
