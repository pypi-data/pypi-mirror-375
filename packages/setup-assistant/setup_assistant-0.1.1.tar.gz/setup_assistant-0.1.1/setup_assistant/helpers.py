import re
import pandas as pd
import pathlib
import io
import pandas as pd
from docx import Document
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

def parse_ai_response(response: str):
    """
    Convert AI text into a list of structured steps with commands.
    """
    steps = []
    matches = re.findall(r"Step\s*\d+:([\s\S]*?)(?=Step\s*\d+:|$)", response)
    for match in matches:
        command_match = re.findall(r"```(?:bash|sh)?\n(.*?)\n```", match, re.DOTALL)
        prompt_match = re.findall(r"Prompt:([\s\S]*?)(?=Prompt:|$)", match, re.DOTALL)
        steps.append(
            {
                "instruction": match.strip(),
                "command": command_match[0].strip() if command_match else None,
                "prompt": prompt_match,
            }
        )
    return steps


import re


def strip_commands(text: str) -> list[str]:
    """
    Extract bash/sh commands from ``` blocks as full multi-line commands.
    """
    # Find all ```bash or ```sh blocks
    blocks = re.findall(r"```(?:bash|sh)?\s*\n([\s\S]*?)```", text, re.DOTALL)

    # Return each block as a single command string
    commands = [block.strip() for block in blocks if block.strip()]

    return commands


def summarize_results(results):
    summary = []
    for r in results:
        summary.append(
            {
                "Command": r["command"],
                "Status": f"{r['status']}",
                "Output / Error": r.get("output")
                or r.get("stderr")
                or r.get("reason", ""),
            }
        )
    return pd.DataFrame(summary)


def ReadFile():
    try:
        with open("./input.md", "r") as file:
            data = file.read()
            print("File read successfully.")
            print(data)
            return data
    except FileNotFoundError:
        print("Error: The file 'input.txt' does not exist.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
    
def read_document(input_path: str) -> str:
    """
    Read a file and return its textual content.
    If DOCX, TXT, CSV, extracts text appropriately.
    """
    file_path = pathlib.Path(input_path)
    suffix = file_path.suffix.lower()
    extracted_text = ""


    if suffix == ".docx":
        doc = Document(file_path)
        extracted_text = "\n".join([p.text for p in doc.paragraphs])

    elif suffix == ".txt":
        extracted_text = file_path.read_text(encoding="utf-8")

    elif suffix == ".csv":
        df = pd.read_csv(file_path)
        extracted_text = df.to_string(index=False)

    else:
        raise ValueError(f"Unsupported file type: {suffix}")

    return extracted_text





def get_drive_service():
    """
    Authenticate and return a Google Drive API service.
    Uses `token.json` to cache credentials.
    If expired or missing, prompts login (console flow for notebooks).
    """
    creds = None
    token_path = pathlib.Path("token.json")

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("../../credentials.json", SCOPES)
            creds = flow.run_local_server(port=8098)

        token_path.write_text(creds.to_json())

    return build("drive", "v3", credentials=creds)


def extract_drive_file_id(url: str) -> str:
    """
    Extract file ID from a Google Drive URL.
    Supports:
    - https://drive.google.com/file/d/<id>/view?usp=sharing
    - https://drive.google.com/open?id=<id>
    - https://docs.google.com/document/d/<id>/edit
    """
    if "id=" in url:
        return url.split("id=")[1].split("&")[0]
    elif "/d/" in url:
        return url.split("/d/")[1].split("/")[0]
    else:
        raise ValueError(f"Invalid Google Drive URL: {url}")


def download_drive_file(file_id: str, output_path: str) -> str:
    """
    Download a file from Google Drive by file_id.
    Saves it to output_path and returns the path.
    """
    service = get_drive_service()
    request = service.files().get_media(fileId=file_id)

    output_path = pathlib.Path(output_path)
    with io.FileIO(output_path, "wb") as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            if status:
                print(f"Download {int(status.progress() * 100)}%")

    print(f"File downloaded to {output_path}")
    return str(output_path)

def download_google_doc_as_pdf(file_id: str, output_path: str) -> str:
    """
    Export a Google Doc (or Sheet/Slide) as PDF and save it locally.
    """
    service = get_drive_service()
    request = service.files().export_media(fileId=file_id, mimeType="application/pdf")

    output_path = pathlib.Path(output_path)
    with io.FileIO(output_path, "wb") as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            if status:
                print(f"Export {int(status.progress() * 100)}%")

    print(f"Google Doc exported as PDF to {output_path}")
    return str(output_path)


def getSystemInstructions(os_name):
    return f"""
            You are a tech-savvy setup assistant. Follow these rules exactly:

            1. Always respond with numbered steps: "Step 1:", "Step 2:", etc.  
            2. Always put shell commands inside ```bash``` or ```sh``` code blocks.  
            3. Target OS: {os_name}.  
            4. Do not require system restarts. Assume no admin privileges unless explicitly necessary.  
            5. Do not use interactive editors (nano, vim, pico, etc.).  
            6. When writing to files:
                - Prefer: echo "...content..." | tee <file>  
                - If using cat, always use a here-doc with BOTH opening and closing EOF markers:  
                    ```
                    cat <<'EOF' > file
                    content
                    EOF
                    ```
                - Never omit the closing EOF marker.  
            7. Do not use vague placeholders or example names. Provide concrete, copy-paste-ready instructions.  
            8. When instructing on `nvm` installation, explicitly include a step to `source` the updated shell file 
            (e.g., `source ~/.zshrc` or `source ~/.bashrc`) immediately after modifying it.  
            9. For prerequisites or installations, always check if the tool is already installed first.  
                - If installed, skip installation.  
                - If not, install it.  
            10. Use commands that can exit cleanly (avoid long-running daemons or interactive shells).  
            11. If a prerequisite must be completed before continuing (e.g., "install Homebrew first"), 
                only output that step. Do not continue with subsequent steps until instructed.  
            12. Only include a `Prompt:` if the current step requires follow-up work 
                (e.g., waiting for installation to finish or confirming a check result).  
                - If nothing needs to be done (the requirement is already satisfied), do NOT include a `Prompt:`.  
                - Format (when needed): `Prompt: <the exact prompt that needs to happen based on the result of the previous step>`. 
            13) Placeholders & secrets
                    • When a command needs a user-specific value (path, version, token, org/repo, etc.), DO NOT guess.
                        Keep an explicit placeholder in ALL_CAPS wrapped in angle brackets, e.g. <PROJECT_DIR>, <NPM_TOKEN>, <NODE_VERSION>.
                    • If a value was provided earlier in this session, substitute it; otherwise keep the placeholder.
                    • Never print or persist secrets in plain text. Prefer environment variables; avoid echoing secrets.
                        If a secret must be entered, show a non-interactive pattern with a placeholder (do NOT prompt).
                    • At the end of the response, include a “Replace Placeholders” checklist that lists each placeholder,
                        a one-line description, and an example value.

            14) Result & explanation (entry-level friendly)  
                    Only Provide this section when the Prompt starts with "Final Steps"
                    • At the end of executing all steps, include a single “Result & Next Steps (For a New Dev)” section.  
                    • Do not include a result section after each individual step.  
                    • This section must explain in simple terms:  
                        – What changed / what was installed or configured.  
                        – Why each step was necessary (brief rationale).  
                        – Which files were created or modified (with full paths).  
                    • Use short sentences, expand acronyms on first use, and avoid unexplained jargon.  
                    Lose for a new dev in the brackets everytime you give a result
                    
        """