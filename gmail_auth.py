from app.services.gmail_client import get_gmail_service

if __name__ == "__main__":
    """
    Run this once to perform Gmail OAuth and create token.json.
    """
    service = get_gmail_service()
    profile = service.users().getProfile(userId="me").execute()
    print(f"Gmail auth successful for: {profile.get('emailAddress')}")
