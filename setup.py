import os
import json

current_dir = os.getcwd()

sys_info = {"base_directory" : current_dir}
json.dump(sys_info, open("sys_info.json", "w"))

auto_start_script = "cd {current_dir} && python driver.py".format(current_dir = current_dir)
with open("linux_run_on_start_2.sh", "w") f:
	f.write(auto_start_script)