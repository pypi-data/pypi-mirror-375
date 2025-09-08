# -*- coding: utf-8 -*-
"""
<license>
  * Copyright (C) 2024-2025 Abdelmathin Habachi, contact@abdelmathin.com.
  *
  * https://abdelmathin.com
  * https://github.com/Abdelmathin/tachyons
  *
  * Permission is hereby granted, free of charge, to any person obtaining
  * a copy of this software and associated documentation files (the
  * "Software"), to deal in the Software without restriction, including
  * without limitation the rights to use, copy, modify, merge, publish,
  * distribute, sublicense, and/or sell copies of the Software, and to
  * permit persons to whom the Software is furnished to do so, subject to
  * the following conditions:
  *
  * The above copyright notice and this permission notice shall be
  * included in all copies or substantial portions of the Software.
  *
  * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
  * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
  * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
  * IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
  * CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
  * TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  * SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
  *
  * File   : tachyons/__main__.py
  * Created: 2025/08/30 21:59:05 GMT+1
  * Updated: 2025/08/30 21:59:11 GMT+1
</license>
"""
__author__    = "Abdelmathin Habachi"
__github__    = "https://github.com/Abdelmathin/tachyons"
__copyright__ = "Copyright (C) 2024-2025 Abdelmathin Habachi"
__license__   = "MIT"
__version__   = "0.1.0"

import os
import sys
import json

def help() -> int:
	return 1

def parse_kwargv(argv: list[str], options: list[str]) -> dict[str, str]:
	i: int = 0
	kwargv: dict[str, str] = {}
	while i < len(argv):
		argument: str = argv[i].lower()
		option  : str = argument.lower().split("=")[0].strip()
		if not (option.replace("_", "-") in options):
			print ( f"Unknown option: {option}" )
			exit( help())
		value: str = None
		if "=" in argument:
			value = argument[argument.index("=") + 1:].strip().strip('"').strip("'")
		elif (i + 1) < len(argv):
			value = argv[i + 1].strip().strip('"').strip("'")
			i += 1
		if value is None:
			print ( f"Missing value for option: {option}" )
			exit( help())
		option = option.replace("-", "_").strip("_")
		kwargv[option] = value
		i += 1
	return kwargv

def create_entrypoints(project_name: str, target_dir: str, next_config: str, default: str = "django_entrypoint") -> int:
	if target_dir.startswith("~"):
		target_dir = os.path.expanduser(target_dir)
	elif not target_dir.startswith("/"):
		target_dir = os.path.abspath(target_dir)
	if not os.path.exists(target_dir):
		print(f"Target directory does not exist: {target_dir}", file=sys.stderr )
		return 1
	templates: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entrypoints")
	for entrypoint in os.listdir(templates):
		template_path: str = os.path.join(templates, entrypoint)
		if not os.path.isfile(template_path):
			continue
		if not template_path.endswith("_entrypoint.py"):
			continue
		content: str = open(template_path, "r").read()
		content = content.replace("{{PROJECT_NAME}}", project_name)
		target_file: str = os.path.join(target_dir, "api", entrypoint)
		os.makedirs(os.path.dirname(target_file), exist_ok = True)
		with open(target_file, "w") as f:
			f.write( content )
	with open( os.path.join(target_dir, next_config + ".json"), "w") as f:
		f.write( json.dumps(
				{
					"routes": [
						{
						"src": "/(.*)",
						"dest": f"api/{default}.py"
						}
					]
				}, indent=4
			)
		)

def main(argc: int, argv: list[str]) -> int:
	if ( argv[1].strip().lower() in ["--create-entrypoints"] ):
		kwargv: dict[str, str] = parse_kwargv(argv[2:], ["--project-name", "--target-dir", "--next-config"])
		return (create_entrypoints(**kwargv))

if __name__ == "__main__":
    argv: list[str] = sys.argv
    argc: int = len( argv )
    exit( main( argc, argv ) )
