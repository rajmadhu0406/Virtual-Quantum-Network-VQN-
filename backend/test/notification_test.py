# tests/test_notification.py
import asyncio
import json
import pytest
from notification import send_email

# Use pytest-asyncio for async tests
@pytest.mark.asyncio
async def test_send_email_success(monkeypatch):
    # Create a fake SES client to simulate sending email
    class FakeSESClient:
        async def send_email(self, **kwargs):
            # Simulate a successful email sending response
            return {"MessageId": "fake-id"}
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc, tb):
            pass

    # Monkeypatch the ses_client used in send_email function
    async def fake_client(*args, **kwargs):
        return FakeSESClient()
    
    from notification import ses_session
    monkeypatch.setattr(ses_session, "client", lambda service, region_name=None: fake_client())

    # Call send_email with test parameters
    await send_email(
        to_email="recipient@example.com",
        subject="Test Email",
        body_text="This is a test email."
    )
    # If no exception, the email sending is considered successful.
