from django.http import HttpResponse
from django.urls import reverse
from django.shortcuts import redirect
from django.http import JsonResponse
import os
from google_auth_oauthlib import flow as _flow
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

SCOPE_OAUTH = ["https://www.googleapis.com/auth/calendar.events.readonly"]
SERVER_URL = "http://127.0.0.1:8000"

# local host
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Get the environment variables
client_id = os.environ.get("client_id")
client_secret = os.environ.get("client_secret")
redirect_uri = os.environ.get("redirect_uri")

def GoogleCalendarInitView(request):
    if(request.method=="GET"):
        # oauth2
        flow = _flow.Flow.from_client_config(
            client_config={
                "web": {
                    "client_id": client_id,
                    "project_id": "convin-oauth",
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://accounts.google.com/o/oauth2/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_secret": client_secret,
                    "redirect_uris": [redirect_uri],
                    "javascript_origins": ["http://127.0.0.1:8000"],
                }
            },
            scopes=SCOPE_OAUTH
        )

        flow.redirect_uri=SERVER_URL+reverse("getEvents")
        authorization_url, state = flow.authorization_url()
        request.session["state"]=state

        return redirect(authorization_url)

    return HttpResponse("Only supports GET requests.")

# Fetch user events
def GoogleCalendarRedirectView(request):
    if(request.method=="GET"):
        # Fetch Token
        state = request.session['state']

        if state is None:
            return redirect(reverse("initialize"))

        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file( "oauth-client.json", scopes=SCOPE_OAUTH, state=state)
        flow.redirect_uri = SERVER_URL+reverse("getEvents")
        authorization_response = request.get_full_path()
        flow.fetch_token(authorization_response=authorization_response)

        credentials = flow.credentials

        request.session['credentials'] = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}

        credentials = google.oauth2.credentials.Credentials(**request.session["credentials"])

        # get events
        calendar = googleapiclient.discovery.build("calendar", "v3", credentials=credentials)

        events = calendar.events().list(calendarId="primary").execute()

        return JsonResponse({
            "stauts": "success",
            "data": events,
        })

    return HttpResponse("Only supports GET requests.")