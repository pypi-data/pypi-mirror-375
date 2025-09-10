from plane.api_client import ApiClient
from plane.configuration import Configuration
from plane.oauth.api import OAuthApi
from plane.oauth.models import OAuthConfig

from plane_adk.agent.handlers import AgentEventHandler, IssueEventHandler
from plane_adk.agent.models import Credentials, TokenDetails, WorkspaceDetails


class PlaneAgent:
    issue: AgentEventHandler
    token_details: TokenDetails = None
    workspace_details: WorkspaceDetails

    def __init__(self, credentials: Credentials):
        self.credentials = credentials
        if credentials.access_token:
            self.token_details = TokenDetails(
                access_token=credentials.access_token,
            )
        self._initialize()
        configuration = Configuration(
            host=credentials.base_url,
            access_token=self.token_details.access_token,
        )
        api_client = ApiClient(configuration)
        self.issue = IssueEventHandler(api_client, self.workspace_details)

    def process_webhook(self, webhook: dict):
        if (
            webhook["event"] in ["issue", "issue_comment"]
            and webhook["action"] != "deleted"
        ):
            self.issue.process_webhook(webhook)

    def _initialize(self):
        oauth_config = OAuthConfig(
            client_id=self.credentials.client_id,
            client_secret=self.credentials.client_secret,
            redirect_uri=self.credentials.redirect_uri,
        )
        oauth_api = OAuthApi(
            oauth_config=oauth_config,
            base_url=self.credentials.base_url,
        )

        if not self.token_details or not self.token_details.access_token:
            self._fetch_token()

        app_installations = oauth_api.get_app_installations(
            self.token_details.access_token, self.credentials.app_installation_id
        )
        if not app_installations:
            raise ValueError("No app installations found")
        app_installation = app_installations[0]
        self.workspace_details = WorkspaceDetails(
            slug=app_installation.workspace_detail.slug,
            id=app_installation.workspace,
            bot_user_id=app_installation.app_bot,
        )

    def _fetch_token(self):
        oauth_config = OAuthConfig(
            client_id=self.credentials.client_id,
            client_secret=self.credentials.client_secret,
            redirect_uri=self.credentials.redirect_uri,
        )
        oauth_api = OAuthApi(
            oauth_config=oauth_config,
            base_url=self.credentials.base_url,
        )
        token_response = oauth_api.get_bot_token(self.credentials.app_installation_id)
        self.token_details = TokenDetails(
            access_token=token_response.access_token,
            expires_in=token_response.expires_in,
            token_type=token_response.token_type,
            scope=token_response.scope,
        )
