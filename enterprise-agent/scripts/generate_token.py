"""Generate a JWT Bearer token for API testing.

Usage:
    python scripts/generate_token.py
    python scripts/generate_token.py --tenant-id 00000000-0000-0000-0000-000000000001
"""
import argparse
import uuid

from app.security.auth import create_access_token


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a test JWT")
    parser.add_argument("--user-id", default="demo-user")
    parser.add_argument("--tenant-id", default=str(uuid.uuid4()))
    args = parser.parse_args()

    token = create_access_token(args.user_id, uuid.UUID(args.tenant_id))
    print(f"Tenant-ID : {args.tenant_id}")
    print(f"Bearer    : {token}")
    print()
    print(f"curl -H 'Authorization: Bearer {token}' \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{\"message\": \"Quelle est la politique de remboursement?\", \"session_id\": \"s1\"}' \\")
    print("     http://localhost:8000/api/v1/chat")


if __name__ == "__main__":
    main()
