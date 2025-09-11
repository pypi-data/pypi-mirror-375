
/******************
 * Config Options *
 ******************/

/* Define for runtime debug checking support. */
/* #undef HAVE_ROL_DEBUG */

/* Define for performance timer support. */
/* #undef ROL_TIMERS */

/* Define for python interface support. */
#define ENABLE_PYBIND11_PYROL

/* Define support for automated ParameterList validation. */
/* #undef ENABLE_PARAMETERLIST_VALIDATION */

/* Define the Fortran name mangling to be used for BLAS/LAPACK */
#ifndef F77_BLAS_MANGLE
 #define F77_BLAS_MANGLE(name,NAME) name ## _
#endif
