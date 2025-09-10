project('phs_poly', 'c', 'fortran',
  version: '0.2.1')

py_mod = import('python').find_installation('python3')

# Get NumPy include directory from Python
numpy_inc = run_command(py_mod, ['-c', 'import numpy; print(numpy.get_include())'],
                        capture : true).stdout().strip()

# Get compilers
cc = meson.get_compiler('c')
fc = meson.get_compiler('fortran')

# Find LAPACK
lapack_name = get_option('lapack')

# --- macOS SDK check ---
macos_new_enough = false
if host_machine.system() == 'darwin'
  r = run_command('xcrun', '-sdk', 'macosx', '--show-sdk-version', check : true)
  sdk_version = r.stdout().strip()
  macos_new_enough = sdk_version.version_compare('>=13.3')
endif

if lapack_name == 'openblas'
  lapack = dependency(['openblas','OpenBLAS'])
elif lapack_name == 'accelerate'
  if host_machine.system() != 'darwin'
    error('Accelerate LAPACK is only available on macOS')
  endif
  if not macos_new_enough
    error('Accelerate LAPACK requires macOS >= 13.3')
  endif

  if fc.get_id() == 'llvm-flang'
    # llvm-flang cannot handle Meson’s framework flags
    lapack = declare_dependency(link_args : ['-framework', 'Accelerate'])
  else
    # Other compilers (clang/gfortran) seem to be fine with framework handling
    lapack = dependency('accelerate')
  endif
else
  lapack = dependency(lapack_name)
endif

if not lapack.found()
  error('No LAPACK library detected! phs_poly needs one, please install it.')
endif

phs_poly_mod = py_mod.extension_module(
  'phs_poly',
  sources : [
    'phs_poly_wrapper.c',
    'phs_poly_c.f90',
    'phs_poly_approx.f90',
  ],
  include_directories : include_directories(numpy_inc),
  dependencies : [lapack],
  install : true,
)

