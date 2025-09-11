from llm_common.prometheus import HttpxClientWithMonitoring


class LLMHttpClient(HttpxClientWithMonitoring):
    name_for_monitoring = "llm"
