# COST-DAEMON-UMLIP-BENCHMARK

## Description
The COST-DAEMON-UMLIP-BENCHMARK contains code to run MD-simulations both with VASP and ase using atomate2.

## Installation
pip install -e .


## Usage
To create inputs for the MD or relaxation use the create-inputs command.    
It will rescale the density and create inputs for a relaxation (--write_relax_input) at that fixed density and for the MD simulation.

For benchmark data use the src/atomate2_workflows/create_inputs_files_for_benchmark.py script set PMG_VASP_PSP_DIR in .pmgrc.yaml  

## Contributing
Contributions are welcome from anyone. The current contributors to this project are:
- Jonathan Schmidt
- Ivor Lončarić

If you would like to contribute, please reach out to the maintainers or submit a pull request.

## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Contact
For any questions or concerns regarding this project, please contact us via email at [123@gmail.com](mailto:123@gmail.com).

## Acknowledgments
This work was supported by the European project .. . 
