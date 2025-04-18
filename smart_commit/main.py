import os
import sys
import google.generativeai as genai
from dotenv import load_dotenv
import subprocess

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=api_key)

model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

def ask_gemini(prompt):
    response=model.generate_content(prompt)
    return response.text.strip()




def get_git_diff():
    try:
        diff=subprocess.check_output(["git" ,"diff" , "--cached"], text=True)
        return diff.strip()
    except subprocess.CalledProcessError as e:
        print ("error getting diff" , e)
        return ""
    

def commit_with_message(message):
    try:
        subprocess.run(["git", "commit", "-m", message])
        print("successfuly commited ")
    except subprocess.CalledProcessError as e:
        print("Git commit failed", e)

def get_staged_files():
    try:
        files = subprocess.check_output(["git", "diff", "--cached", "--name-only"], text=True).splitlines()
        return files
    except subprocess.CalledProcessError as e:
        print("Error getting staged files:", e)
        return []
    
diff = get_git_diff()

if not diff:
    print("No staged changes found. Stage your files with `git add` before running this.")
    sys.exit(0)
staged_files = get_staged_files()
files_str = ", ".join(staged_files)

prompt = f"""Generate a concise but descriptive git commit message based on the following diff, use git commit covebctional terms :\n\n{diff}  files changed:{files_str}"""
commit_message = ask_gemini(prompt)
print(commit_message)



user_input=input("Do you want to commit with this messaage ? (y/n)").strip().lower()
if user_input == 'y':
    commit_with_message(commit_message)
else:
    print("Commit aborted.")
    sys.exit(0)


