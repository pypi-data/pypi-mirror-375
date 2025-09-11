#include <ROL_TimeStamp.hpp>
#include <Teuchos_RCPDecl.hpp>
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

void bind_pyrol_2(std::function< pybind11::module &(std::string const &namespace_) > &M)
{
	{ // std::vector file:bits/stl_vector.h line:428
		pybind11::class_<std::vector<std::vector<double>>, Teuchos::RCP<std::vector<std::vector<double>>>> cl(M("std"), "vector_std_vector_double_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new std::vector<std::vector<double>>(); } ) );
		cl.def( pybind11::init<const class std::allocator<class std::vector<double> > &>(), pybind11::arg("__a") );

		cl.def( pybind11::init( [](unsigned long const & a0){ return new std::vector<std::vector<double>>(a0); } ), "doc" , pybind11::arg("__n"));
		cl.def( pybind11::init<unsigned long, const class std::allocator<class std::vector<double> > &>(), pybind11::arg("__n"), pybind11::arg("__a") );

		cl.def( pybind11::init( [](unsigned long const & a0, const class std::vector<double> & a1){ return new std::vector<std::vector<double>>(a0, a1); } ), "doc" , pybind11::arg("__n"), pybind11::arg("__value"));
		cl.def( pybind11::init<unsigned long, const class std::vector<double> &, const class std::allocator<class std::vector<double> > &>(), pybind11::arg("__n"), pybind11::arg("__value"), pybind11::arg("__a") );

		cl.def( pybind11::init( [](std::vector<std::vector<double>> const &o){ return new std::vector<std::vector<double>>(o); } ) );
		cl.def( pybind11::init<const class std::vector<class std::vector<double> > &, const class std::allocator<class std::vector<double> > &>(), pybind11::arg("__x"), pybind11::arg("__a") );

		cl.def("assign", (class std::vector<class std::vector<double> > & (std::vector<std::vector<double>>::*)(const class std::vector<class std::vector<double> > &)) &std::vector<std::vector<double>>::operator=, "C++: std::vector<std::vector<double>>::operator=(const class std::vector<class std::vector<double> > &) --> class std::vector<class std::vector<double> > &", pybind11::return_value_policy::automatic, pybind11::arg("__x"));
		cl.def("assign", (void (std::vector<std::vector<double>>::*)(unsigned long, const class std::vector<double> &)) &std::vector<std::vector<double>>::assign, "C++: std::vector<std::vector<double>>::assign(unsigned long, const class std::vector<double> &) --> void", pybind11::arg("__n"), pybind11::arg("__val"));
		cl.def("size", (unsigned long (std::vector<std::vector<double>>::*)() const) &std::vector<std::vector<double>>::size, "C++: std::vector<std::vector<double>>::size() const --> unsigned long");
		cl.def("max_size", (unsigned long (std::vector<std::vector<double>>::*)() const) &std::vector<std::vector<double>>::max_size, "C++: std::vector<std::vector<double>>::max_size() const --> unsigned long");
		cl.def("resize", (void (std::vector<std::vector<double>>::*)(unsigned long)) &std::vector<std::vector<double>>::resize, "C++: std::vector<std::vector<double>>::resize(unsigned long) --> void", pybind11::arg("__new_size"));
		cl.def("resize", (void (std::vector<std::vector<double>>::*)(unsigned long, const class std::vector<double> &)) &std::vector<std::vector<double>>::resize, "C++: std::vector<std::vector<double>>::resize(unsigned long, const class std::vector<double> &) --> void", pybind11::arg("__new_size"), pybind11::arg("__x"));
		cl.def("shrink_to_fit", (void (std::vector<std::vector<double>>::*)()) &std::vector<std::vector<double>>::shrink_to_fit, "C++: std::vector<std::vector<double>>::shrink_to_fit() --> void");
		cl.def("capacity", (unsigned long (std::vector<std::vector<double>>::*)() const) &std::vector<std::vector<double>>::capacity, "C++: std::vector<std::vector<double>>::capacity() const --> unsigned long");
		cl.def("empty", (bool (std::vector<std::vector<double>>::*)() const) &std::vector<std::vector<double>>::empty, "C++: std::vector<std::vector<double>>::empty() const --> bool");
		cl.def("reserve", (void (std::vector<std::vector<double>>::*)(unsigned long)) &std::vector<std::vector<double>>::reserve, "C++: std::vector<std::vector<double>>::reserve(unsigned long) --> void", pybind11::arg("__n"));
		cl.def("__getitem__", (class std::vector<double> & (std::vector<std::vector<double>>::*)(unsigned long)) &std::vector<std::vector<double>>::operator[], "C++: std::vector<std::vector<double>>::operator[](unsigned long) --> class std::vector<double> &", pybind11::return_value_policy::automatic, pybind11::arg("__n"));
		cl.def("at", (class std::vector<double> & (std::vector<std::vector<double>>::*)(unsigned long)) &std::vector<std::vector<double>>::at, "C++: std::vector<std::vector<double>>::at(unsigned long) --> class std::vector<double> &", pybind11::return_value_policy::automatic, pybind11::arg("__n"));
		cl.def("front", (class std::vector<double> & (std::vector<std::vector<double>>::*)()) &std::vector<std::vector<double>>::front, "C++: std::vector<std::vector<double>>::front() --> class std::vector<double> &", pybind11::return_value_policy::automatic);
		cl.def("back", (class std::vector<double> & (std::vector<std::vector<double>>::*)()) &std::vector<std::vector<double>>::back, "C++: std::vector<std::vector<double>>::back() --> class std::vector<double> &", pybind11::return_value_policy::automatic);
		cl.def("data", (class std::vector<double> * (std::vector<std::vector<double>>::*)()) &std::vector<std::vector<double>>::data, "C++: std::vector<std::vector<double>>::data() --> class std::vector<double> *", pybind11::return_value_policy::automatic);
		cl.def("push_back", (void (std::vector<std::vector<double>>::*)(const class std::vector<double> &)) &std::vector<std::vector<double>>::push_back, "C++: std::vector<std::vector<double>>::push_back(const class std::vector<double> &) --> void", pybind11::arg("__x"));
		cl.def("pop_back", (void (std::vector<std::vector<double>>::*)()) &std::vector<std::vector<double>>::pop_back, "C++: std::vector<std::vector<double>>::pop_back() --> void");
		cl.def("swap", (void (std::vector<std::vector<double>>::*)(class std::vector<class std::vector<double> > &)) &std::vector<std::vector<double>>::swap, "C++: std::vector<std::vector<double>>::swap(class std::vector<class std::vector<double> > &) --> void", pybind11::arg("__x"));
		cl.def("clear", (void (std::vector<std::vector<double>>::*)()) &std::vector<std::vector<double>>::clear, "C++: std::vector<std::vector<double>>::clear() --> void");
	}
	{ // std::vector file:bits/stl_vector.h line:428
		pybind11::class_<std::vector<ROL::TimeStamp<double>>, Teuchos::RCP<std::vector<ROL::TimeStamp<double>>>> cl(M("std"), "vector_ROL_TimeStamp_double_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new std::vector<ROL::TimeStamp<double>>(); } ) );
		cl.def( pybind11::init<const class std::allocator<struct ROL::TimeStamp<double> > &>(), pybind11::arg("__a") );

		cl.def( pybind11::init( [](unsigned long const & a0){ return new std::vector<ROL::TimeStamp<double>>(a0); } ), "doc" , pybind11::arg("__n"));
		cl.def( pybind11::init<unsigned long, const class std::allocator<struct ROL::TimeStamp<double> > &>(), pybind11::arg("__n"), pybind11::arg("__a") );

		cl.def( pybind11::init( [](unsigned long const & a0, const struct ROL::TimeStamp<double> & a1){ return new std::vector<ROL::TimeStamp<double>>(a0, a1); } ), "doc" , pybind11::arg("__n"), pybind11::arg("__value"));
		cl.def( pybind11::init<unsigned long, const struct ROL::TimeStamp<double> &, const class std::allocator<struct ROL::TimeStamp<double> > &>(), pybind11::arg("__n"), pybind11::arg("__value"), pybind11::arg("__a") );

		cl.def( pybind11::init( [](std::vector<ROL::TimeStamp<double>> const &o){ return new std::vector<ROL::TimeStamp<double>>(o); } ) );
		cl.def( pybind11::init<const class std::vector<struct ROL::TimeStamp<double> > &, const class std::allocator<struct ROL::TimeStamp<double> > &>(), pybind11::arg("__x"), pybind11::arg("__a") );

		cl.def("assign", (class std::vector<struct ROL::TimeStamp<double> > & (std::vector<ROL::TimeStamp<double>>::*)(const class std::vector<struct ROL::TimeStamp<double> > &)) &std::vector<ROL::TimeStamp<double>>::operator=, "C++: std::vector<ROL::TimeStamp<double>>::operator=(const class std::vector<struct ROL::TimeStamp<double> > &) --> class std::vector<struct ROL::TimeStamp<double> > &", pybind11::return_value_policy::automatic, pybind11::arg("__x"));
		cl.def("assign", (void (std::vector<ROL::TimeStamp<double>>::*)(unsigned long, const struct ROL::TimeStamp<double> &)) &std::vector<ROL::TimeStamp<double>>::assign, "C++: std::vector<ROL::TimeStamp<double>>::assign(unsigned long, const struct ROL::TimeStamp<double> &) --> void", pybind11::arg("__n"), pybind11::arg("__val"));
		cl.def("size", (unsigned long (std::vector<ROL::TimeStamp<double>>::*)() const) &std::vector<ROL::TimeStamp<double>>::size, "C++: std::vector<ROL::TimeStamp<double>>::size() const --> unsigned long");
		cl.def("max_size", (unsigned long (std::vector<ROL::TimeStamp<double>>::*)() const) &std::vector<ROL::TimeStamp<double>>::max_size, "C++: std::vector<ROL::TimeStamp<double>>::max_size() const --> unsigned long");
		cl.def("resize", (void (std::vector<ROL::TimeStamp<double>>::*)(unsigned long)) &std::vector<ROL::TimeStamp<double>>::resize, "C++: std::vector<ROL::TimeStamp<double>>::resize(unsigned long) --> void", pybind11::arg("__new_size"));
		cl.def("resize", (void (std::vector<ROL::TimeStamp<double>>::*)(unsigned long, const struct ROL::TimeStamp<double> &)) &std::vector<ROL::TimeStamp<double>>::resize, "C++: std::vector<ROL::TimeStamp<double>>::resize(unsigned long, const struct ROL::TimeStamp<double> &) --> void", pybind11::arg("__new_size"), pybind11::arg("__x"));
		cl.def("shrink_to_fit", (void (std::vector<ROL::TimeStamp<double>>::*)()) &std::vector<ROL::TimeStamp<double>>::shrink_to_fit, "C++: std::vector<ROL::TimeStamp<double>>::shrink_to_fit() --> void");
		cl.def("capacity", (unsigned long (std::vector<ROL::TimeStamp<double>>::*)() const) &std::vector<ROL::TimeStamp<double>>::capacity, "C++: std::vector<ROL::TimeStamp<double>>::capacity() const --> unsigned long");
		cl.def("empty", (bool (std::vector<ROL::TimeStamp<double>>::*)() const) &std::vector<ROL::TimeStamp<double>>::empty, "C++: std::vector<ROL::TimeStamp<double>>::empty() const --> bool");
		cl.def("reserve", (void (std::vector<ROL::TimeStamp<double>>::*)(unsigned long)) &std::vector<ROL::TimeStamp<double>>::reserve, "C++: std::vector<ROL::TimeStamp<double>>::reserve(unsigned long) --> void", pybind11::arg("__n"));
		cl.def("__getitem__", (struct ROL::TimeStamp<double> & (std::vector<ROL::TimeStamp<double>>::*)(unsigned long)) &std::vector<ROL::TimeStamp<double>>::operator[], "C++: std::vector<ROL::TimeStamp<double>>::operator[](unsigned long) --> struct ROL::TimeStamp<double> &", pybind11::return_value_policy::automatic, pybind11::arg("__n"));
		cl.def("at", (struct ROL::TimeStamp<double> & (std::vector<ROL::TimeStamp<double>>::*)(unsigned long)) &std::vector<ROL::TimeStamp<double>>::at, "C++: std::vector<ROL::TimeStamp<double>>::at(unsigned long) --> struct ROL::TimeStamp<double> &", pybind11::return_value_policy::automatic, pybind11::arg("__n"));
		cl.def("front", (struct ROL::TimeStamp<double> & (std::vector<ROL::TimeStamp<double>>::*)()) &std::vector<ROL::TimeStamp<double>>::front, "C++: std::vector<ROL::TimeStamp<double>>::front() --> struct ROL::TimeStamp<double> &", pybind11::return_value_policy::automatic);
		cl.def("back", (struct ROL::TimeStamp<double> & (std::vector<ROL::TimeStamp<double>>::*)()) &std::vector<ROL::TimeStamp<double>>::back, "C++: std::vector<ROL::TimeStamp<double>>::back() --> struct ROL::TimeStamp<double> &", pybind11::return_value_policy::automatic);
		cl.def("data", (struct ROL::TimeStamp<double> * (std::vector<ROL::TimeStamp<double>>::*)()) &std::vector<ROL::TimeStamp<double>>::data, "C++: std::vector<ROL::TimeStamp<double>>::data() --> struct ROL::TimeStamp<double> *", pybind11::return_value_policy::automatic);
		cl.def("push_back", (void (std::vector<ROL::TimeStamp<double>>::*)(const struct ROL::TimeStamp<double> &)) &std::vector<ROL::TimeStamp<double>>::push_back, "C++: std::vector<ROL::TimeStamp<double>>::push_back(const struct ROL::TimeStamp<double> &) --> void", pybind11::arg("__x"));
		cl.def("pop_back", (void (std::vector<ROL::TimeStamp<double>>::*)()) &std::vector<ROL::TimeStamp<double>>::pop_back, "C++: std::vector<ROL::TimeStamp<double>>::pop_back() --> void");
		cl.def("swap", (void (std::vector<ROL::TimeStamp<double>>::*)(class std::vector<struct ROL::TimeStamp<double> > &)) &std::vector<ROL::TimeStamp<double>>::swap, "C++: std::vector<ROL::TimeStamp<double>>::swap(class std::vector<struct ROL::TimeStamp<double> > &) --> void", pybind11::arg("__x"));
		cl.def("clear", (void (std::vector<ROL::TimeStamp<double>>::*)()) &std::vector<ROL::TimeStamp<double>>::clear, "C++: std::vector<ROL::TimeStamp<double>>::clear() --> void");
	}
}
