"""
Some scripts to run prior to committing.

Because a Batch Script wasn't reliable enough
"""
import subprocess

subprocess.run('python replicate_files.py', shell=True)
subprocess.run('python static_analysis.py', shell=True)
subprocess.run('python clean_project_files.py', shell=True)

exit(0)