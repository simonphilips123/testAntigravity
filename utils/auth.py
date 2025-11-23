import google_auth_oauthlib.flow
from googleapiclient.discovery import build
import streamlit as st
import os

class GoogleAuth:
    def __init__(self):
        # Load secrets
        try:
            if "google" in st.secrets:
                c_id = st.secrets["google"]["client_id"]
                c_secret = st.secrets["google"]["client_secret"]

                # Check for placeholders
                if "YOUR_CLIENT_ID_HERE" in c_id or "YOUR_CLIENT_SECRET_HERE" in c_secret:
                    self.client_config = None
                    return

                self.client_config = {
                    "web": {
                        "client_id": c_id,
                        "client_secret": c_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [st.secrets["google"]["redirect_uri"]],
                    }
                }
                self.redirect_uri = st.secrets["google"]["redirect_uri"]
            else:
                self.client_config = None
        except Exception:
            self.client_config = None

    def get_auth_url(self):
        if not self.client_config:
            return None

        flow = google_auth_oauthlib.flow.Flow.from_client_config(
            self.client_config,
            scopes=['https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile', 'openid'],
            redirect_uri=self.redirect_uri
        )

        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        return authorization_url

    def get_user_info(self, code):
        if not self.client_config:
            return None

        try:
            flow = google_auth_oauthlib.flow.Flow.from_client_config(
                self.client_config,
                scopes=['https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile', 'openid'],
                redirect_uri=self.redirect_uri
            )

            flow.fetch_token(code=code)
            credentials = flow.credentials

            service = build('oauth2', 'v2', credentials=credentials)
            user_info = service.userinfo().get().execute()
            return user_info
        except Exception as e:
            st.error(f"Authentication failed: {e}")
            return None
