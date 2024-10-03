from secrets import AUTH0_AUDIENCE, AUTH0_DOMAIN

import requests
from fastapi import HTTPException
from jose import jwt


# Function to verify the JWT token
def verify_jwt(token: str):
    header = jwt.get_unverified_header(token)
    rsa_key = get_rsa_key(header)

    try:
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            audience=AUTH0_AUDIENCE,
            issuer=f"https://{AUTH0_DOMAIN}/",
        )
        return payload
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# Get the RSA key from Auth0 to validate the JWT
def get_rsa_key(header):
    jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
    jwks = requests.get(jwks_url).json()

    rsa_key = {}
    for key in jwks["keys"]:
        if key["kid"] == header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"],
            }
            break
    return rsa_key
