#include <iterator>
#include <memory>
#include <sstream> // __str__
#include <vector>

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

void bind_pyrol_1(std::function< pybind11::module &(std::string const &namespace_) > &M)
{
	{ // std::vector file:bits/stl_vector.h line:428
		pybind11::class_<std::vector<double>, Teuchos::RCP<std::vector<double>>> cl(M("std"), "vector_double_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new std::vector<double>(); } ) );
		cl.def( pybind11::init<const class std::allocator<double> &>(), pybind11::arg("__a") );

		cl.def( pybind11::init( [](unsigned long const & a0){ return new std::vector<double>(a0); } ), "doc" , pybind11::arg("__n"));
		cl.def( pybind11::init<unsigned long, const class std::allocator<double> &>(), pybind11::arg("__n"), pybind11::arg("__a") );

		cl.def( pybind11::init( [](unsigned long const & a0, const double & a1){ return new std::vector<double>(a0, a1); } ), "doc" , pybind11::arg("__n"), pybind11::arg("__value"));
		cl.def( pybind11::init<unsigned long, const double &, const class std::allocator<double> &>(), pybind11::arg("__n"), pybind11::arg("__value"), pybind11::arg("__a") );

		cl.def( pybind11::init( [](std::vector<double> const &o){ return new std::vector<double>(o); } ) );
		cl.def( pybind11::init<const class std::vector<double> &, const class std::allocator<double> &>(), pybind11::arg("__x"), pybind11::arg("__a") );

		cl.def("assign", (class std::vector<double> & (std::vector<double>::*)(const class std::vector<double> &)) &std::vector<double>::operator=, "C++: std::vector<double>::operator=(const class std::vector<double> &) --> class std::vector<double> &", pybind11::return_value_policy::automatic, pybind11::arg("__x"));
		cl.def("assign", (void (std::vector<double>::*)(unsigned long, const double &)) &std::vector<double>::assign, "C++: std::vector<double>::assign(unsigned long, const double &) --> void", pybind11::arg("__n"), pybind11::arg("__val"));
		cl.def("size", (unsigned long (std::vector<double>::*)() const) &std::vector<double>::size, "C++: std::vector<double>::size() const --> unsigned long");
		cl.def("max_size", (unsigned long (std::vector<double>::*)() const) &std::vector<double>::max_size, "C++: std::vector<double>::max_size() const --> unsigned long");
		cl.def("resize", (void (std::vector<double>::*)(unsigned long)) &std::vector<double>::resize, "C++: std::vector<double>::resize(unsigned long) --> void", pybind11::arg("__new_size"));
		cl.def("resize", (void (std::vector<double>::*)(unsigned long, const double &)) &std::vector<double>::resize, "C++: std::vector<double>::resize(unsigned long, const double &) --> void", pybind11::arg("__new_size"), pybind11::arg("__x"));
		cl.def("shrink_to_fit", (void (std::vector<double>::*)()) &std::vector<double>::shrink_to_fit, "C++: std::vector<double>::shrink_to_fit() --> void");
		cl.def("capacity", (unsigned long (std::vector<double>::*)() const) &std::vector<double>::capacity, "C++: std::vector<double>::capacity() const --> unsigned long");
		cl.def("empty", (bool (std::vector<double>::*)() const) &std::vector<double>::empty, "C++: std::vector<double>::empty() const --> bool");
		cl.def("reserve", (void (std::vector<double>::*)(unsigned long)) &std::vector<double>::reserve, "C++: std::vector<double>::reserve(unsigned long) --> void", pybind11::arg("__n"));
		cl.def("__getitem__", (double & (std::vector<double>::*)(unsigned long)) &std::vector<double>::operator[], "C++: std::vector<double>::operator[](unsigned long) --> double &", pybind11::return_value_policy::automatic, pybind11::arg("__n"));
		cl.def("at", (double & (std::vector<double>::*)(unsigned long)) &std::vector<double>::at, "C++: std::vector<double>::at(unsigned long) --> double &", pybind11::return_value_policy::automatic, pybind11::arg("__n"));
		cl.def("front", (double & (std::vector<double>::*)()) &std::vector<double>::front, "C++: std::vector<double>::front() --> double &", pybind11::return_value_policy::automatic);
		cl.def("back", (double & (std::vector<double>::*)()) &std::vector<double>::back, "C++: std::vector<double>::back() --> double &", pybind11::return_value_policy::automatic);
		cl.def("data", (double * (std::vector<double>::*)()) &std::vector<double>::data, "C++: std::vector<double>::data() --> double *", pybind11::return_value_policy::automatic);
		cl.def("push_back", (void (std::vector<double>::*)(const double &)) &std::vector<double>::push_back, "C++: std::vector<double>::push_back(const double &) --> void", pybind11::arg("__x"));
		cl.def("pop_back", (void (std::vector<double>::*)()) &std::vector<double>::pop_back, "C++: std::vector<double>::pop_back() --> void");
		cl.def("swap", (void (std::vector<double>::*)(class std::vector<double> &)) &std::vector<double>::swap, "C++: std::vector<double>::swap(class std::vector<double> &) --> void", pybind11::arg("__x"));
		cl.def("clear", (void (std::vector<double>::*)()) &std::vector<double>::clear, "C++: std::vector<double>::clear() --> void");
	}
}
