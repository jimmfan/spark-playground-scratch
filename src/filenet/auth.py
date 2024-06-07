import requests
import re

# Attempt to access the FileNet URL
filenet_url = 'https://<filenet_url>/path/to/resource'
response = requests.get(filenet_url)

# Check if the response is a redirect to Okta
if response.status_code == 200:
    # Extract baseUrl and fromUri from the response text
    base_url_match = re.search(r'baseUrl:\s*"([^"]+)"', response.text)
    from_uri_match = re.search(r'fromUri:\s*"([^"]+)"', response.text)

    if base_url_match and from_uri_match:
        base_url = base_url_match.group(1)
        from_uri = from_uri_match.group(1)
        print(f"Base URL found: {base_url}")
        print(f"From URI found: {from_uri}")
        
        # Construct the Okta auth URL
        okta_auth_url = f"{base_url}/api/v1/authn"

        username = 'your_username'
        password = 'your_password'

        payload = {
            'username': username,
            'password': password,
            'options': {
                'multiOptionalFactorEnroll': True,
                'warnBeforePasswordExpired': True
            }
        }

        response = requests.post(okta_auth_url, json=payload)
        auth_response = response.json()

        if auth_response.get('status') == 'MFA_REQUIRED':
            state_token = auth_response['stateToken']
            factors = auth_response['_embedded']['factors']
            # You can list the available factors and choose one
            for factor in factors:
                print(f"Factor ID: {factor['id']}, Factor Type: {factor['factorType']}")

            # Assuming the SMS factor ID is 'sms_factor_id'
            sms_factor_id = '<sms_factor_id>'

            factor_endpoint = f'/api/v1/authn/factors/{sms_factor_id}/verify'
            factor_url = base_url + factor_endpoint

            factor_payload = {
                'stateToken': state_token
            }

            factor_response = requests.post(factor_url, json=factor_payload)
            mfa_challenge_response = factor_response.json()

            pass_code = input('Enter the MFA passcode sent to your device: ')

            verify_endpoint = f'/api/v1/authn/factors/{sms_factor_id}/verify'
            verify_url = base_url + verify_endpoint

            verify_payload = {
                'stateToken': state_token,
                'passCode': pass_code
            }

            verify_response = requests.post(verify_url, json=verify_payload)
            verify_result = verify_response.json()

            if verify_result.get('status') == 'SUCCESS':
                session_token = verify_result['sessionToken']
            else:
                print('MFA verification failed.')
                exit(1)

            session_endpoint = f'/api/v1/sessions'
            session_url = base_url + session_endpoint

            session_payload = {
                'sessionToken': session_token
            }

            session_response = requests.post(session_url, json=session_payload)
            session_result = session_response.json()

            if session_response.status_code == 200:
                okta_session_cookie = session_result['id']
            else:
                print('Failed to create session.')
                exit(1)

            # Access FileNet with the session cookie
            cookies = {
                'sid': okta_session_cookie
            }

            response = requests.get(filenet_url, cookies=cookies)

            if response.status_code == 200:
                print('Successfully accessed FileNet.')
                print(response.content)
            else:
                print('Failed to access FileNet.')
    else:
        print("baseUrl or fromUri not found in the response.")
else:
    print("Failed to access FileNet.")
