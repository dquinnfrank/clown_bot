import os
import json
import subprocess

current_dir = os.getcwd()

sys_info = {"base_directory" : current_dir}
json.dump(sys_info, open("sys_info.json", "w"))

auto_start_script = "cd {current_dir} && python driver.py".format(current_dir = current_dir)
with open("linux_run_on_start_2.sh", "w") as f:
	f.write(auto_start_script)

# TEMP need latest version of discordpy
sources_dir = os.path.expanduser(os.path.join("~", "Sources"))
pathlib.Path(sources_dir).mkdir(parents=True, exist_ok=True)

subprocess.run(["git", "clone", "https://github.com/Rapptz/discord.py"], cwd = sources_dir)
subprocess.run(["pip", "install", "-U", ".[voice]"], cwd = os.path.join(sources_dir, "discord.py"))