import requests

# Replace with your actual values
client_id = "86xnygv0qp2y8c"
client_secret = "f268sd3b3280GMrG"
redirect_uri = "https://www.linkedin.com/developers/tools/oauth/redirect"
access_token = "AQXlLGhB8AQ1Wax7cM2JnxuxweB3f4IY4oUdYc88ANxDd9hrpTBO7Gt5aB0tBgVhIz_HcF6hDwtxmbghIietcQ0tCR8V-L4UER8_qQ5t-7gfdufHdHT2fxZU-I0XbdshBqjgfYNDWWb8SFFPUbsj9wJkbMUZIBnZiF9LEB3gzgU9XyOdT_WFrZdhw88k3mPdPY9e_3tMcPXM988Ot0hLcju8RtFsE4-pQJOd3G_fqXsogEUhvsKYCT5vALBGj0ULxU4Wb0PwVOqIEWpPR7VzRJoJC-DtfQKPyGpuTY_L6lvrWTS4bhDqajE0VKC-sGg7YeXceO21SxYG1uCyAVl6ztXezfIsZA"

# Fetch user's skills
url = f"https://api.linkedin.com/v2/me?projection=(id,skills)"
headers = {"Authorization": f"Bearer {access_token}"}

try:
    response = requests.get(url, headers=headers)
    data = response.json()
    skills = data.get("skills", {}).get("elements", [])
    print("hi")
    for skill in skills:
        skill_name = skill.get("name")
        print(f"Skill: {skill_name}")

except Exception as e:
    print(f"Error fetching skills: {e}")
