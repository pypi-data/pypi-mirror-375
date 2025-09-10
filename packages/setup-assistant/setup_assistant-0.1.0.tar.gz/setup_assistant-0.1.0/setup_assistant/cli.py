import typer
from setup_assistant.core import SetupAssistant
from rich import print

app = typer.Typer()

@app.command()
def run(path: str = None, url: str = None, use_file_api: bool = False):
    """
    Run setup assistant with either a local path or a URL.
    """
    assistant = SetupAssistant(api_key="AIzaSyAJbUs7a6PhhGYuFRGJyQmh4YLk4aqtvMY")
    steps = assistant.ask_ai_throughDocument(url=url, path=path, useFileAPI=use_file_api)
    results = assistant.run(steps)
    print(f"\n--- Execution Summary ---\n{results}")
    resultsPath = assistant.resultsSummaryFile(results)
    
    print(f"Results are in this file: {resultsPath}")
    

if __name__ == "__main__":
    app()
