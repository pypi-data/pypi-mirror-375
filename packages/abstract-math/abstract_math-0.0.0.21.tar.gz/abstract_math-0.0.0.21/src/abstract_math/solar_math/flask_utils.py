from abstract_flask import *
from abstract_utilities import write_to_file
directory='/home/computron/Documents/pythonTools/modules/abstract_math/src/abstract_math/solar_math'
output_file='/home/computron/Documents/pythonTools/modules/abstract_math/src/abstract_math/flask_scripts/flask_utils.py'
output = generate_from_files(
		directory=directory,
    		bp_name='math_data_bp',
    		url_prefix='api'
	)
write_to_file(contents=output,file_path=output_file)

