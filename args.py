import argparse
import dataclasses as dc
import os
from typing import List, Optional, Union

from simple_parsing import field, flag
from simple_parsing.helpers import Serializable, list_field


@dc.dataclass
class RequestLineArgs:
    """RequestSending module, 2 mode to choose: CONCURRENCY, RATE"""

    # mode to send requests
    mode: str = field(default='RATE', choices=['CONCURRENCY', 'RATE'])

    # number of processes to send requests
    concurrency: Optional[int] = None

    # speed of requests sending
    rate: Optional[float] = None

    # peak rate
    peak_rate: Optional[float] = None

    # peak percent
    peak_percent: Optional[float] = 0

    # peak length
    peak_length: Optional[float] = None

    # already request_interval_list json file to load
    load_request_interval_list_path: Optional[str] = None

    def _validate(self):  # noqa: C901
        if self.load_request_interval_list_path is not None:
            if not os.path.exists(self.load_request_interval_list_path):
                raise FileNotFoundError(
                    f"--load_request_interval_list_path not found: {self.load_request_interval_list_path}"
                )
            return  # load path work will skip other values' check

        if self.mode is None:
            raise ValueError("--mode must be set")

        # CONCURRENCY mode check
        if self.mode == 'CONCURRENCY':
            if self.concurrency is None or self.concurrency <= 0:
                raise ValueError(
                    f"--concurrency must be set and over 0 when --mode equals to 'CONCURRENCY': {None if self.concurrency else self.concurrency}"
                )
        # RATE mode check
        if self.mode == 'RATE':
            if self.rate is None or self.rate <= 0:
                raise ValueError(
                    f"--rate must be set and over 0 when --mode equals to 'RATE': {None if self.rate is None else self.rate}"
                )
            if self.peak_rate is not None and self.peak_rate <= self.rate:
                raise ValueError(f"--peak_rate({self.peak_rate}) must larger than --rate({self.rate})")
            else:
                self.peak_rate = 3 * self.rate  # init default peak_rate as 3 * rate
            if self.peak_percent >= 1 or self.peak_percent < 0:
                raise ValueError(f"--peak_percent must in the range of [0,1): {self.peak_percent}")
            if self.peak_length is not None and self.peak_length <= 0:
                raise ValueError("--peak_length must be larger than 0.")


@dc.dataclass
class PromptGenerationArgs:
    """PromptGeneration module, 4 mode to choose: default, custom, normal, shareGPT"""

    # mode to generate prompts
    prompt_mode: str = field(default='default', choices=['default', 'custom', 'normal', 'shareGPT', 'chatml'])

    # prompt type for chatml data
    prompt_type: str = "chatml_prompt"

    # prompt filter type for chatml data
    filter_type: str = "truncation"

    # set the prompt_len of all prompts to a fixed value
    prompt_len: Optional[int] = None

    # set the max_new_tokens of all prompts to a fixed value
    max_new_tokens: Optional[int] = None

     # set the max_input_len of all prompts to a fixed value
    max_input_len: Optional[int] = None
    min_input_len: Optional[int] = None

    # set the max_output_len of all prompts to a fixed value
    max_output_len: Optional[int] = None
    min_output_len: Optional[int] = None 

    # source prompt list of [default, custom] mode
    # `''` seperated prompts, e.g. "--prompt_source_list 'why sky is blue?' 'see you tomorrow' 'hello my friend'"
    # support multiple ones
    prompt_source_list: List[str] = list_field(default=[])

    # source prompt file path, needed in [normal, shareGPT] mode
    prompt_source_path: Optional[str] = None

    # max accepted input prompt length for the target model, unit is tokens
    model_max_input_len: Optional[int] = None

    # target model max new generation length, unit is tokens
    model_max_output_len: Optional[int] = None

    # max accepted sequence length for the target model, generally equals to input+output
    model_max_sequence_len: Optional[int] = None

    # adds a percentage of the specified length(always very long) of the prompt, among [0,1]
    long_prompt_percent: float = 0

    # the added long prompts' length
    long_prompt_tokens: int = 1000

    # mean of all prompts generated
    mean: Optional[int] = None

    # size of generated prompts
    size: Optional[int] = None

    # shuffle prompts in [normal] mode, random choose prompts from source list/file in
    # [shareGPT] mode
    random: bool = flag(False, action='store_true')

    # tokenizer dir, to calculate the prompt length
    tokenizer_dir: Optional[str] = None

    # already existing prompt list file path to load
    load_promptlist_path: Optional[str] = None

    # trust remote code or not when loading tokenizer
    trust_remote_code: bool = flag(False, action='store_true')

    def _validate(self):  # noqa: C901
        if self.load_promptlist_path is not None:
            if not os.path.exists(self.load_promptlist_path):
                raise FileNotFoundError(f"--load_promptlist_path not found: {self.load_promptlist_path}")
            return  # path work will skip other values check
        if self.prompt_mode is None:
            raise ValueError("--prompt_mode must be set")
        if self.max_new_tokens is not None and self.max_new_tokens <= 0:
            raise ValueError(f"--max_new_tokens must over 0: {self.max_new_tokens}")
        if self.tokenizer_dir is None:
            raise ValueError("--tokenizer_dir must be set")
        # default mode check
        if self.prompt_mode == 'default':
            if self.max_new_tokens is None:
                raise ValueError("--max_new_tokens must be set when --prompt_mode equals to [default]'")
        # custom mode check
        if self.prompt_mode == 'custom':
            if self.max_new_tokens is None:
                raise ValueError("--max_new_tokens must be set when --prompt_mode equals to [custom]'")
            if not self.prompt_source_list:
                raise ValueError("--prompt_source_list must be set when --prompt_mode equals to [custom]")
        # shareGPT mode check
        if self.prompt_mode == 'shareGPT':
            if self.prompt_source_path is None:
                raise ValueError("--prompt_source_path must be set at least when --prompt_mode equals to [shareGPT]")
            if not os.path.exists(self.prompt_source_path):
                raise FileNotFoundError(f"--prompt_source_path not found: {self.prompt_source_path}")
        # normal mode check
        if self.prompt_mode == 'normal':
            if self.model_max_input_len is None or self.model_max_input_len <= 0:
                raise ValueError(
                    "--model_max_input_len must be set and over 0 when --prompt_mode equals to [normal]: "
                    + f"{None if self.model_max_input_len is None else self.model_max_input_len}"
                )
            if self.model_max_output_len is None or self.model_max_output_len <= 0:
                raise ValueError(
                    "--model_max_output_len must be set and over 0 when --prompt_mode equals to [normal]: "
                    + f"{None if self.model_max_output_len is None else self.model_max_output_len}"
                )
            if self.model_max_sequence_len is None or self.model_max_sequence_len <= 0:
                raise ValueError(
                    "--model_max_sequence_len must be set and over 0 when --prompt_mode equals to [normal]: "
                    + f"{None if self.model_max_sequence_len is None else self.model_max_sequence_len}"
                )
            if (
                self.model_max_sequence_len <= self.model_max_input_len
                or self.model_max_sequence_len <= self.model_max_output_len
            ):
                raise ValueError(
                    "--model_max_sequence_len cannot be smaller than or equal to --model_max_input_len and --model_max_output_len"
                )
            if self.mean is None or self.mean <= 0:
                raise ValueError(
                    f"--mean must be set and over 0 when --prompt_mode equals to [normal]: {None if self.mean is None else self.mean}"
                )
            if self.prompt_source_path is None:
                raise ValueError("--prompt_source_path must be set when --prompt_mode equals to [normal]")
            elif not os.path.exists(self.prompt_source_path):
                raise FileNotFoundError(f"--prompt_source_path not found: {self.prompt_source_path}")
            if self.long_prompt_percent < 0 or self.long_prompt_percent > 1:
                raise ValueError(f"--long_prompt_percent must be in the range of [0,1]: {self.long_prompt_percent}")
            if self.long_prompt_tokens <= 0:
                raise ValueError(f"--long_prompt_tokens must over 0: {self.long_prompt_tokens}")
        # chatml mode check
        if self.prompt_mode == 'chatml':
            if self.model_max_input_len is None or self.model_max_input_len <= 0:
                raise ValueError(
                    "--model_max_input_len must be set and over 0 when --prompt_mode equals to [chatml]: "
                    + f"{None if self.model_max_input_len is None else self.model_max_input_len}"
                )
            if self.prompt_source_path is None:
                raise ValueError("--prompt_source_path must be set when --prompt_mode equals to [chatml]")
            elif not os.path.exists(self.prompt_source_path):
                raise FileNotFoundError(f"--prompt_source_path not found: {self.prompt_source_path}")
            if self.max_new_tokens is None:
                raise ValueError("--max_new_tokens must be set when --prompt_mode equals to [chatml]'")
            if self.tokenizer_dir is None:
                raise ValueError("--tokenizer_dir must be set")
        # custom mode check
        if self.prompt_mode == 'custom_length':
            if self.max_new_tokens is None or self.max_new_tokens <= 0:
                raise ValueError(
                    "--max_new_tokens must be set and over 0 when --prompt_mode equals to [custom_length]: "
                    + f"{None if self.max_new_tokens is None else self.max_new_tokens}"
                )
            if self.prompt_len is None or self.prompt_len <= 0:
                raise ValueError(
                    "--prompt_len must be set and over 0 when --prompt_mode equals to [custom_length]: "
                    + f"{None if self.prompt_len is None else self.prompt_len}"
                )



@dc.dataclass
class ServingBenchmarkArgs(Serializable):
    """Serving benchmark, consists of PromptGeneration, RequestSending, BenchmarkStatistics modules"""

    # ReuqestSending Module
    rs_opts: RequestLineArgs = field(default_factory=RequestLineArgs)

    # PromptGeneration Module
    pmt_opts: PromptGenerationArgs =field(default_factory=PromptGenerationArgs)

    # display details to standard output
    verbose: bool = flag(False, action='store_true')

    # save info into log files
    log: bool = flag(False, action='store_true')

    # log level
    log_level: Optional[str] = field(default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])

    # target framework of serving benchmark
    framework: Optional[str] = field(default="bladellm", choices=['bladellm', 'vllm', 'tgi', 'dashscope'])

    # request type for bladellm
    request_type: Optional[str] = field(default="oai_completions", choices=['generate', 'chat', 'oai_completions'])

    # sequence generation ignore eos
    ignore_eos: bool = flag(False, action="store_true")

    # adjoining tokens generation max time
    timeout: int = 30

    # limit mode of benchmark
    stop: Optional[str] = field(default='prompt', choices=['prompt', 'time'])

    # seconds to run benchmark
    seconds: Optional[int] = None

    # the server url requests sent to
    url: Optional[str] = None

    # the authorization token requests sent to EAS service
    auth: Optional[str] = None

    # cache dir to save cache, prompt/request caches, etc.
    cache_dir: str = None

    # log dir to save log, result, etc.
    log_dir: str = None

    # result dir to save result
    result_dir: str = None

    # md path to save
    md_path: str = None

    # json path to save
    json_path: str = None

    # model type of framework, no real effect, just used to generate file names.
    model_type: str = None

    # model path used to generate txt.
    model_path: str = None

    def _validate(self):  # noqa: C901
        self.rs_opts._validate()
        self.pmt_opts._validate()
        if self.framework is None:
            raise ValueError("--framework cannot be empty.")
        if self.stop is None:
            raise ValueError("--stop cannot be empty.")
        if self.url is None:
            raise ValueError("--url cannot be empty.")
        if self.stop == 'time' and self.seconds is None:
            raise ValueError("--seconds cannot be empty when --stop equals to [time]")
        if self.seconds is not None and self.seconds <= 0:
            raise ValueError(f"--seconds must be over 0: {self.seconds}")
        if self.model_type is None:
            raise ValueError("--model_type cannot be empty.")
        if self.md_path or self.json_path:
            if not (self.json_path and self.md_path):
                raise ValueError("--md_path or --json_path Either set none or set all")
        if self.framework == 'bladellm':
            if self.request_type == 'generate' and not self.url.endswith('/generate_stream'):
                raise ValueError("For BladeLLM generate benchmark, the url must end with '/generate_stream' ")
            elif self.request_type == 'chat' and not self.url.endswith('/chat_stream'):
                raise ValueError("For BladeLLM chat benchmark, the url must end with '/chat_stream' ")
            elif self.request_type == 'oai_completions' and not self.url.endswith('/v1/completions'):
                raise ValueError("For BladeLLM OpenAI completion benchmark, the url must end with '/v1/completions' ")

    @classmethod
    def from_cli_args(cls, args: Union[argparse.Namespace, dict]) -> "ServingBenchmarkArgs":
        attrs = [attr.name for attr in dc.fields(cls)]
        if isinstance(args, dict):
            serving_benchmark_args = cls(**{attr: args.get(attr) for attr in attrs})
            serving_benchmark_args.rs_opts = RequestLineArgs(**serving_benchmark_args.rs_opts)
            serving_benchmark_args.pmt_opts = PromptGenerationArgs(**serving_benchmark_args.pmt_opts)
        else:
            serving_benchmark_args = cls(**{attr: getattr(args, attr) for attr in attrs})
        return serving_benchmark_args
