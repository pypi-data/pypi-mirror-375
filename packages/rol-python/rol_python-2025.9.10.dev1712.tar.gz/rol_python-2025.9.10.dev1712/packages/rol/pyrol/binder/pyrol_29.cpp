#include <ROL_TypeE_Algorithm.hpp>
#include <sstream> // __str__

#include <functional>
#include <pybind11/pybind11.h>
#include <string>
#include <Teuchos_RCP.hpp>


#ifndef BINDER_PYBIND11_TYPE_CASTER
	#define BINDER_PYBIND11_TYPE_CASTER
	PYBIND11_DECLARE_HOLDER_TYPE(T, Teuchos::RCP<T>, false)
	PYBIND11_DECLARE_HOLDER_TYPE(T, T*, false)
	PYBIND11_MAKE_OPAQUE(Teuchos::RCP<void>)
#endif

void bind_pyrol_29(std::function< pybind11::module &(std::string const &namespace_) > &M)
{
	{ // ROL::TypeE::AlgorithmState file:ROL_TypeE_Algorithm.hpp line:26
		pybind11::class_<ROL::TypeE::AlgorithmState<double>, Teuchos::RCP<ROL::TypeE::AlgorithmState<double>>, ROL::AlgorithmState<double>> cl(M("ROL::TypeE"), "AlgorithmState_double_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new ROL::TypeE::AlgorithmState<double>(); } ) );
		cl.def( pybind11::init( [](ROL::TypeE::AlgorithmState<double> const &o){ return new ROL::TypeE::AlgorithmState<double>(o); } ) );
		cl.def_readwrite("searchSize", &ROL::TypeE::AlgorithmState<double>::searchSize);
		cl.def_readwrite("stepVec", &ROL::TypeE::AlgorithmState<double>::stepVec);
		cl.def_readwrite("gradientVec", &ROL::TypeE::AlgorithmState<double>::gradientVec);
		cl.def_readwrite("constraintVec", &ROL::TypeE::AlgorithmState<double>::constraintVec);
		cl.def("reset", (void (ROL::TypeE::AlgorithmState<double>::*)()) &ROL::TypeE::AlgorithmState<double>::reset, "C++: ROL::TypeE::AlgorithmState<double>::reset() --> void");
		cl.def("assign", (struct ROL::TypeE::AlgorithmState<double> & (ROL::TypeE::AlgorithmState<double>::*)(const struct ROL::TypeE::AlgorithmState<double> &)) &ROL::TypeE::AlgorithmState<double>::operator=, "C++: ROL::TypeE::AlgorithmState<double>::operator=(const struct ROL::TypeE::AlgorithmState<double> &) --> struct ROL::TypeE::AlgorithmState<double> &", pybind11::return_value_policy::automatic, pybind11::arg(""));
		cl.def_readwrite("iter", &ROL::AlgorithmState<double>::iter);
		cl.def_readwrite("minIter", &ROL::AlgorithmState<double>::minIter);
		cl.def_readwrite("nfval", &ROL::AlgorithmState<double>::nfval);
		cl.def_readwrite("ncval", &ROL::AlgorithmState<double>::ncval);
		cl.def_readwrite("ngrad", &ROL::AlgorithmState<double>::ngrad);
		cl.def_readwrite("value", &ROL::AlgorithmState<double>::value);
		cl.def_readwrite("minValue", &ROL::AlgorithmState<double>::minValue);
		cl.def_readwrite("gnorm", &ROL::AlgorithmState<double>::gnorm);
		cl.def_readwrite("cnorm", &ROL::AlgorithmState<double>::cnorm);
		cl.def_readwrite("snorm", &ROL::AlgorithmState<double>::snorm);
		cl.def_readwrite("aggregateGradientNorm", &ROL::AlgorithmState<double>::aggregateGradientNorm);
		cl.def_readwrite("aggregateModelError", &ROL::AlgorithmState<double>::aggregateModelError);
		cl.def_readwrite("flag", &ROL::AlgorithmState<double>::flag);
		cl.def_readwrite("iterateVec", &ROL::AlgorithmState<double>::iterateVec);
		cl.def_readwrite("lagmultVec", &ROL::AlgorithmState<double>::lagmultVec);
		cl.def_readwrite("minIterVec", &ROL::AlgorithmState<double>::minIterVec);
		cl.def_readwrite("statusFlag", &ROL::AlgorithmState<double>::statusFlag);
		cl.def("reset", (void (ROL::AlgorithmState<double>::*)()) &ROL::AlgorithmState<double>::reset, "C++: ROL::AlgorithmState<double>::reset() --> void");
		cl.def("assign", (struct ROL::AlgorithmState<double> & (ROL::AlgorithmState<double>::*)(const struct ROL::AlgorithmState<double> &)) &ROL::AlgorithmState<double>::operator=, "C++: ROL::AlgorithmState<double>::operator=(const struct ROL::AlgorithmState<double> &) --> struct ROL::AlgorithmState<double> &", pybind11::return_value_policy::automatic, pybind11::arg(""));
	}
}
