# update_secrets.py
import re
import os

def parse_curl_and_update_env():
    """
    Parses a cURL command from 'curl_input.txt',
    extracts FPL authentication secrets, and updates the .env file.
    """
    print("--- FPL Secrets Updater ---")
    
    try:
        # Read the entire cURL command from the input file
        with open(".curl_input.txt", "r") as f:
            curl_command = f.read()

        if not curl_command.strip():
            print("❌ Error: '.curl_input.txt' is empty.")
            print("   Please paste your cURL command into '.curl_input.txt' and run again.")
            return

        # --- Use Regular Expressions to find the required values ---
        # Find Team ID from the main URL
        team_id_match = re.search(r"my-team/(\d+)/", curl_command)
        team_id = team_id_match.group(1) if team_id_match else None

        # Find the cookie string (works with both -b and -H 'cookie:')
        cookie_match = re.search(r"(?:-b|--cookie|-H 'cookie:)\s*'(.*?)'", curl_command, re.DOTALL)
        cookie = cookie_match.group(1).replace('\\\n', '') if cookie_match else None

        # Find the user-agent
        user_agent_match = re.search(r"-H 'user-agent: (.*?)'", curl_command)
        user_agent = user_agent_match.group(1) if user_agent_match else None
        
        # Find the x-api-authorization token
        auth_token_match = re.search(r"-H 'x-api-authorization: (.*?)'", curl_command)
        auth_token = auth_token_match.group(1) if auth_token_match else None

        if not all([team_id, cookie, user_agent, auth_token]):
            raise ValueError("Could not find all required values in 'curl_input.txt'.")

        # --- Write the extracted values to the .env file ---
        with open(".env", "w") as f:
            f.write(f'FPL_TEAM_ID="{team_id}"\n')
            f.write(f'FPL_COOKIE="{cookie}"\n')
            f.write(f'FPL_AUTH_TOKEN="{auth_token}"\n')
            f.write(f'FPL_USER_AGENT="{user_agent}"\n')

        print("\n✅ Success! Your .env file has been updated with fresh secrets.")

    except FileNotFoundError:
        print("❌ Error: 'curl_input.txt' not found.")
        print("   Please create the file in your project's root directory.")
    except Exception as e:
        print(f"\n❌ Error: An issue occurred. {e}")
        print("   Please make sure you copied the full cURL command correctly into 'curl_input.txt'.")


if __name__ == "__main__":
    parse_curl_and_update_env()