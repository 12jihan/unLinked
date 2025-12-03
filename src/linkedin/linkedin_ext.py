import os


class LinkedInExt:
    m_access_token = os.getenv("ACCESS_TOKEN")
    m_api_version: str | None = os.getenv("API_VERSION")
    m_user_id: str | None = os.getenv("USER_ID")

    m_url_text: str = "https://api.linkedin.com/v2/ugcPosts"
    m_url_register: str = "https://api.linkedin.com/v2/ugcPosts"
    m_url_multimedia: str = "https://api.linkedin.com/v2/ugcPosts"

    def __init__(self):
        pass

    # LinkedIn Tokens
