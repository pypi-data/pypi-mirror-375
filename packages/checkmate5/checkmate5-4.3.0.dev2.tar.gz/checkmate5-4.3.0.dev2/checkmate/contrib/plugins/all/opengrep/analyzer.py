# -*- coding: utf-8 -*-

from checkmate.lib.analysis.base import BaseAnalyzer

import logging
import os
import tempfile
import json
import subprocess

logger = logging.getLogger(__name__)


class OpengrepAnalyzer(BaseAnalyzer):
    def __init__(self, *args, **kwargs):
        super(OpengrepAnalyzer, self).__init__(*args, **kwargs)
        try:
            result = subprocess.check_output(
                ["opengrep", "--version"], stderr=subprocess.DEVNULL
            ).strip()
        except subprocess.CalledProcessError:
            logger.error(
                "Cannot initialize opengrep analyzer: Executable is missing, please install it."
            )
            raise

    def summarize(self, items):
        pass

    def analyze(self, file_revision):
        issues = []
        tmpdir = "/tmp/" + file_revision.project.pk

        # This block handles directory creation. Note: It's often safer to use
        # Python's tempfile module for secure temporary file/directory handling
        # instead of constructing paths manually in /tmp/.
        if not os.path.exists(os.path.dirname(tmpdir + "/" + file_revision.path)):
            try:
                os.makedirs(os.path.dirname(tmpdir + "/" + file_revision.path))
            except OSError as exc:  # Guard against race condition
                # Import 'errno' is missing for this check (import errno)
                if exc.errno != 17:  # 17 corresponds to errno.EEXIST
                    raise
        
        # Opened file handle. It's crucial to ensure this is closed properly.
        # Using tempfile.NamedTemporaryFile for the entire process is generally
        # safer and handles cleanup more robustly.
        f = open(tmpdir + "/" + file_revision.path, "wb")

        # This variable 'fout' is created but not used in the provided logic.
        # It can likely be removed.
        fout = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        result = {}

        try:
            # The 'with f:' block ensures the file is properly closed,
            # but 'f' was already opened outside this block.
            # For best practice, open the file directly within the 'with' statement.
            with f:
                try:
                    f.write(file_revision.get_file_content())
                except UnicodeDecodeError:
                    # Handle cases where the file content might not be decodable as text.
                    # This often occurs with binary files.
                    pass

            # Get the file extension from the temporary file's name.
            file_name = f.name
            _, file_extension = os.path.splitext(file_name)

            # Remove the leading dot from the extension (e.g., '.php' becomes 'php').
            if file_extension:
                file_extension = file_extension[1:]

            # Construct the base rule path.
            base_rules_path = "/root/opengrep-rules"

            # Determine the specific rule folder based on the extension.
            if file_extension:
                rules_folder = file_extension.lower()  # Convert to lowercase for consistency
                rules_path = os.path.join(base_rules_path, rules_folder)
            else:
                rules_path = base_rules_path # Use the base path if no extension

            # Execute the opengrep command.
            try:
                result = subprocess.check_output(
                    [
                        "opengrep",
                        "scan",
                        "-f",
                        rules_path,  # Dynamically set the rules path
                        "--no-git-ignore",
                        "--json",
                        f.name,
                    ],
                    stderr=subprocess.DEVNULL,
                ).strip()
            except subprocess.CalledProcessError as e:
                # Handle cases where opengrep command fails (e.g., non-zero exit code).
                print(f"Opengrep command failed with error: {e}")
                print(f"Output: {e.output.decode(errors='ignore')}") # Decode output for printing
            except FileNotFoundError:
                # Handle cases where 'opengrep' command itself is not found.
                print("Error: 'opengrep' command not found. Make sure it's in your PATH.")

            # Process the JSON result from opengrep.
            # This 'try' block was originally at a different indentation level.
            # It should ideally be part of the main analysis flow, possibly
            # after the subprocess call.
            try:
                json_result = json.loads(result)

                for issue in json_result["results"]:
                    location = (
                        ((issue["start"]["line"], None), (issue["start"]["line"], None)),
                    )
                    val = issue["check_id"]
                    val = val.replace("root.", "")
                    val = val.title().replace("_", "")

                    issues.append(
                        {
                            "code": val,
                            "location": location,
                            "data": issue["extra"]["message"],
                            "file": file_revision.path,
                            "line": issue["start"]["line"],
                            "fingerprint": self.get_fingerprint_from_code(
                                file_revision, location, extra_data=issue["extra"]["message"]
                            ),
                        }
                    )
            except: # This is a bare except, which catches all exceptions.
                    # It's better to catch specific exceptions, like json.JSONDecodeError,
                    # and log errors instead of silently passing.
                pass

        except Exception as e:
            # Catch any other unexpected errors during file writing or processing.
            print(f"An unexpected error occurred: {e}")

        finally:
            # The 'finally' block must align with its 'try' block.
            # Ensure the temporary file 'f' is closed and deleted here if it was opened.
            # In your original code, 'f' was opened, but there was no explicit close
            # or deletion in the finally block for the manual file creation.
            # Using tempfile.NamedTemporaryFile with its own 'with' context usually
            # handles this automatically.
            return {"issues": issues}
