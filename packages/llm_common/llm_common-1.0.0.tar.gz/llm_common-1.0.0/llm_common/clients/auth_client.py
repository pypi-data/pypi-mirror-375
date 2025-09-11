from llm_common.prometheus import HttpxClientWithMonitoring


class AuthHttpClient(HttpxClientWithMonitoring):
    name_for_monitoring = "auth_api"

    def clear_resource_path(self, resource: str):
        if resource.startswith("/api/check"):
            return "api/check/{telegram_user_id}"

        return super().clear_resource_path(resource)
