import os
import subprocess

import subprocess


def run_sbt_command(pdf_path):
    command = f'sbt "runMain org.allenai.pdffigures2.FigureExtractorVisualizationCli {pdf_path}"'

    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("Command output:")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running the command: {e}")
        print("Error output:")
        print(e.stderr)


run_sbt_command("//2312.10997v5.pdf")