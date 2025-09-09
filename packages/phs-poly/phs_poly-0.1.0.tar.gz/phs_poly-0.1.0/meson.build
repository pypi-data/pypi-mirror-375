project('phs_poly', 'c', 'fortran')

py_mod = import('python').find_installation('python3')

# Get NumPy include directory from Python
numpy_inc = run_command(py_mod, ['-c', 'import numpy; print(numpy.get_include())'],
                        capture : true).stdout().strip()

phs_poly_mod = py_mod.extension_module(
  'phs_poly',
  sources : [
    'phs_poly_wrapper.c',
    'phs_poly_c.f90',
    'phs_poly_approx.f90',
  ],
  include_directories : include_directories(numpy_inc),
  install : true,
)
