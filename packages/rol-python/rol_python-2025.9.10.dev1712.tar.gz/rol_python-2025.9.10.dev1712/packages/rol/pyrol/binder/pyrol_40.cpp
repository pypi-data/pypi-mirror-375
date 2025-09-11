#include <PyROL_Teuchos_Custom.hpp>
#include <Teuchos_ArrayView.hpp>
#include <Teuchos_ArrayViewDecl.hpp>
#include <Teuchos_ENull.hpp>
#include <Teuchos_GlobalMPISession.hpp>
#include <Teuchos_RCPNode.hpp>
#include <Teuchos_VerbosityLevel.hpp>
#include <Teuchos_as.hpp>
#include <Teuchos_basic_oblackholestream.hpp>
#include <ios>
#include <iterator>
#include <locale>
#include <memory>
#include <ostream>
#include <sstream> // __str__
#include <streambuf>
#include <string>
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

void bind_pyrol_40(std::function< pybind11::module &(std::string const &namespace_) > &M)
{
	{ // Teuchos::ArrayView file:Teuchos_ArrayViewDecl.hpp line:90
		pybind11::class_<Teuchos::ArrayView<float>, Teuchos::RCP<Teuchos::ArrayView<float>>> cl(M("Teuchos"), "ArrayView_float_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ArrayView<float>(); } ), "doc" );
		cl.def( pybind11::init<enum Teuchos::ENull>(), pybind11::arg("null_arg") );

		cl.def( pybind11::init( [](float * a0, long const & a1){ return new Teuchos::ArrayView<float>(a0, a1); } ), "doc" , pybind11::arg("p"), pybind11::arg("size"));
		cl.def( pybind11::init<float *, long, const enum Teuchos::ERCPNodeLookup>(), pybind11::arg("p"), pybind11::arg("size"), pybind11::arg("rcpNodeLookup") );

		cl.def( pybind11::init( [](Teuchos::ArrayView<float> const &o){ return new Teuchos::ArrayView<float>(o); } ) );
		cl.def("assign", (class Teuchos::ArrayView<float> & (Teuchos::ArrayView<float>::*)(const class Teuchos::ArrayView<float> &)) &Teuchos::ArrayView<float>::operator=, "C++: Teuchos::ArrayView<float>::operator=(const class Teuchos::ArrayView<float> &) --> class Teuchos::ArrayView<float> &", pybind11::return_value_policy::automatic, pybind11::arg("array"));
		cl.def("is_null", (bool (Teuchos::ArrayView<float>::*)() const) &Teuchos::ArrayView<float>::is_null, "C++: Teuchos::ArrayView<float>::is_null() const --> bool");
		cl.def("size", (long (Teuchos::ArrayView<float>::*)() const) &Teuchos::ArrayView<float>::size, "C++: Teuchos::ArrayView<float>::size() const --> long");
		cl.def("toString", (std::string (Teuchos::ArrayView<float>::*)() const) &Teuchos::ArrayView<float>::toString, "C++: Teuchos::ArrayView<float>::toString() const --> std::string");
		cl.def("getRawPtr", (float * (Teuchos::ArrayView<float>::*)() const) &Teuchos::ArrayView<float>::getRawPtr, "C++: Teuchos::ArrayView<float>::getRawPtr() const --> float *", pybind11::return_value_policy::automatic);
		cl.def("data", (float * (Teuchos::ArrayView<float>::*)() const) &Teuchos::ArrayView<float>::data, "C++: Teuchos::ArrayView<float>::data() const --> float *", pybind11::return_value_policy::automatic);
		cl.def("__getitem__", (float & (Teuchos::ArrayView<float>::*)(long) const) &Teuchos::ArrayView<float>::operator[], "C++: Teuchos::ArrayView<float>::operator[](long) const --> float &", pybind11::return_value_policy::automatic, pybind11::arg("i"));
		cl.def("front", (float & (Teuchos::ArrayView<float>::*)() const) &Teuchos::ArrayView<float>::front, "C++: Teuchos::ArrayView<float>::front() const --> float &", pybind11::return_value_policy::automatic);
		cl.def("back", (float & (Teuchos::ArrayView<float>::*)() const) &Teuchos::ArrayView<float>::back, "C++: Teuchos::ArrayView<float>::back() const --> float &", pybind11::return_value_policy::automatic);
		cl.def("view", (class Teuchos::ArrayView<float> (Teuchos::ArrayView<float>::*)(long, long) const) &Teuchos::ArrayView<float>::view, "C++: Teuchos::ArrayView<float>::view(long, long) const --> class Teuchos::ArrayView<float>", pybind11::arg("offset"), pybind11::arg("size"));
		cl.def("__call__", (class Teuchos::ArrayView<float> (Teuchos::ArrayView<float>::*)(long, long) const) &Teuchos::ArrayView<float>::operator(), "C++: Teuchos::ArrayView<float>::operator()(long, long) const --> class Teuchos::ArrayView<float>", pybind11::arg("offset"), pybind11::arg("size"));
		cl.def("__call__", (const class Teuchos::ArrayView<float> & (Teuchos::ArrayView<float>::*)() const) &Teuchos::ArrayView<float>::operator(), "C++: Teuchos::ArrayView<float>::operator()() const --> const class Teuchos::ArrayView<float> &", pybind11::return_value_policy::automatic);
		cl.def("getConst", (class Teuchos::ArrayView<const float> (Teuchos::ArrayView<float>::*)() const) &Teuchos::ArrayView<float>::getConst, "C++: Teuchos::ArrayView<float>::getConst() const --> class Teuchos::ArrayView<const float>");
		cl.def("assign", (void (Teuchos::ArrayView<float>::*)(const class Teuchos::ArrayView<const float> &) const) &Teuchos::ArrayView<float>::assign, "C++: Teuchos::ArrayView<float>::assign(const class Teuchos::ArrayView<const float> &) const --> void", pybind11::arg("array"));
		cl.def("begin", (float * (Teuchos::ArrayView<float>::*)() const) &Teuchos::ArrayView<float>::begin, "C++: Teuchos::ArrayView<float>::begin() const --> float *", pybind11::return_value_policy::automatic);
		cl.def("end", (float * (Teuchos::ArrayView<float>::*)() const) &Teuchos::ArrayView<float>::end, "C++: Teuchos::ArrayView<float>::end() const --> float *", pybind11::return_value_policy::automatic);
		cl.def("assert_not_null", (const class Teuchos::ArrayView<float> & (Teuchos::ArrayView<float>::*)() const) &Teuchos::ArrayView<float>::assert_not_null, "C++: Teuchos::ArrayView<float>::assert_not_null() const --> const class Teuchos::ArrayView<float> &", pybind11::return_value_policy::automatic);
		cl.def("assert_in_range", (const class Teuchos::ArrayView<float> & (Teuchos::ArrayView<float>::*)(long, long) const) &Teuchos::ArrayView<float>::assert_in_range, "C++: Teuchos::ArrayView<float>::assert_in_range(long, long) const --> const class Teuchos::ArrayView<float> &", pybind11::return_value_policy::automatic, pybind11::arg("offset"), pybind11::arg("size"));
		cl.def("access_private_ptr", (float * (Teuchos::ArrayView<float>::*)() const) &Teuchos::ArrayView<float>::access_private_ptr, "C++: Teuchos::ArrayView<float>::access_private_ptr() const --> float *", pybind11::return_value_policy::automatic);

		cl.def("__str__", [](Teuchos::ArrayView<float> const &o) -> std::string { std::ostringstream s; using namespace Teuchos; s << o; return s.str(); } );
	}
	{ // Teuchos::ArrayView file:Teuchos_ArrayViewDecl.hpp line:400
		pybind11::class_<Teuchos::ArrayView<const float>, Teuchos::RCP<Teuchos::ArrayView<const float>>> cl(M("Teuchos"), "ArrayView_const_float_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ArrayView<const float>(); } ), "doc" );
		cl.def( pybind11::init<enum Teuchos::ENull>(), pybind11::arg("null_arg") );

		cl.def( pybind11::init( [](const float * a0, long const & a1){ return new Teuchos::ArrayView<const float>(a0, a1); } ), "doc" , pybind11::arg("p"), pybind11::arg("size"));
		cl.def( pybind11::init<const float *, long, const enum Teuchos::ERCPNodeLookup>(), pybind11::arg("p"), pybind11::arg("size"), pybind11::arg("rcpNodeLookup") );

		cl.def( pybind11::init( [](Teuchos::ArrayView<const float> const &o){ return new Teuchos::ArrayView<const float>(o); } ) );
		cl.def("assign", (class Teuchos::ArrayView<const float> & (Teuchos::ArrayView<const float>::*)(const class Teuchos::ArrayView<const float> &)) &Teuchos::ArrayView<const float>::operator=, "C++: Teuchos::ArrayView<const float>::operator=(const class Teuchos::ArrayView<const float> &) --> class Teuchos::ArrayView<const float> &", pybind11::return_value_policy::automatic, pybind11::arg("array"));
		cl.def("is_null", (bool (Teuchos::ArrayView<const float>::*)() const) &Teuchos::ArrayView<const float>::is_null, "C++: Teuchos::ArrayView<const float>::is_null() const --> bool");
		cl.def("size", (long (Teuchos::ArrayView<const float>::*)() const) &Teuchos::ArrayView<const float>::size, "C++: Teuchos::ArrayView<const float>::size() const --> long");
		cl.def("toString", (std::string (Teuchos::ArrayView<const float>::*)() const) &Teuchos::ArrayView<const float>::toString, "C++: Teuchos::ArrayView<const float>::toString() const --> std::string");
		cl.def("getRawPtr", (const float * (Teuchos::ArrayView<const float>::*)() const) &Teuchos::ArrayView<const float>::getRawPtr, "C++: Teuchos::ArrayView<const float>::getRawPtr() const --> const float *", pybind11::return_value_policy::automatic);
		cl.def("data", (const float * (Teuchos::ArrayView<const float>::*)() const) &Teuchos::ArrayView<const float>::data, "C++: Teuchos::ArrayView<const float>::data() const --> const float *", pybind11::return_value_policy::automatic);
		cl.def("__getitem__", (const float & (Teuchos::ArrayView<const float>::*)(long) const) &Teuchos::ArrayView<const float>::operator[], "C++: Teuchos::ArrayView<const float>::operator[](long) const --> const float &", pybind11::return_value_policy::automatic, pybind11::arg("i"));
		cl.def("front", (const float & (Teuchos::ArrayView<const float>::*)() const) &Teuchos::ArrayView<const float>::front, "C++: Teuchos::ArrayView<const float>::front() const --> const float &", pybind11::return_value_policy::automatic);
		cl.def("back", (const float & (Teuchos::ArrayView<const float>::*)() const) &Teuchos::ArrayView<const float>::back, "C++: Teuchos::ArrayView<const float>::back() const --> const float &", pybind11::return_value_policy::automatic);
		cl.def("view", (class Teuchos::ArrayView<const float> (Teuchos::ArrayView<const float>::*)(long, long) const) &Teuchos::ArrayView<const float>::view, "C++: Teuchos::ArrayView<const float>::view(long, long) const --> class Teuchos::ArrayView<const float>", pybind11::arg("offset"), pybind11::arg("size"));
		cl.def("__call__", (class Teuchos::ArrayView<const float> (Teuchos::ArrayView<const float>::*)(long, long) const) &Teuchos::ArrayView<const float>::operator(), "C++: Teuchos::ArrayView<const float>::operator()(long, long) const --> class Teuchos::ArrayView<const float>", pybind11::arg("offset"), pybind11::arg("size"));
		cl.def("__call__", (const class Teuchos::ArrayView<const float> & (Teuchos::ArrayView<const float>::*)() const) &Teuchos::ArrayView<const float>::operator(), "C++: Teuchos::ArrayView<const float>::operator()() const --> const class Teuchos::ArrayView<const float> &", pybind11::return_value_policy::automatic);
		cl.def("getConst", (class Teuchos::ArrayView<const float> (Teuchos::ArrayView<const float>::*)() const) &Teuchos::ArrayView<const float>::getConst, "C++: Teuchos::ArrayView<const float>::getConst() const --> class Teuchos::ArrayView<const float>");
		cl.def("begin", (const float * (Teuchos::ArrayView<const float>::*)() const) &Teuchos::ArrayView<const float>::begin, "C++: Teuchos::ArrayView<const float>::begin() const --> const float *", pybind11::return_value_policy::automatic);
		cl.def("end", (const float * (Teuchos::ArrayView<const float>::*)() const) &Teuchos::ArrayView<const float>::end, "C++: Teuchos::ArrayView<const float>::end() const --> const float *", pybind11::return_value_policy::automatic);
		cl.def("assert_not_null", (const class Teuchos::ArrayView<const float> & (Teuchos::ArrayView<const float>::*)() const) &Teuchos::ArrayView<const float>::assert_not_null, "C++: Teuchos::ArrayView<const float>::assert_not_null() const --> const class Teuchos::ArrayView<const float> &", pybind11::return_value_policy::automatic);
		cl.def("assert_in_range", (const class Teuchos::ArrayView<const float> & (Teuchos::ArrayView<const float>::*)(long, long) const) &Teuchos::ArrayView<const float>::assert_in_range, "C++: Teuchos::ArrayView<const float>::assert_in_range(long, long) const --> const class Teuchos::ArrayView<const float> &", pybind11::return_value_policy::automatic, pybind11::arg("offset"), pybind11::arg("size"));
		cl.def("access_private_ptr", (const float * (Teuchos::ArrayView<const float>::*)() const) &Teuchos::ArrayView<const float>::access_private_ptr, "C++: Teuchos::ArrayView<const float>::access_private_ptr() const --> const float *", pybind11::return_value_policy::automatic);

		cl.def("__str__", [](Teuchos::ArrayView<const float> const &o) -> std::string { std::ostringstream s; using namespace Teuchos; s << o; return s.str(); } );
	}
	{ // Teuchos::ArrayView file:Teuchos_ArrayViewDecl.hpp line:400
		pybind11::class_<Teuchos::ArrayView<const double>, Teuchos::RCP<Teuchos::ArrayView<const double>>> cl(M("Teuchos"), "ArrayView_const_double_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ArrayView<const double>(); } ), "doc" );
		cl.def( pybind11::init<enum Teuchos::ENull>(), pybind11::arg("null_arg") );

		cl.def( pybind11::init( [](const double * a0, long const & a1){ return new Teuchos::ArrayView<const double>(a0, a1); } ), "doc" , pybind11::arg("p"), pybind11::arg("size"));
		cl.def( pybind11::init<const double *, long, const enum Teuchos::ERCPNodeLookup>(), pybind11::arg("p"), pybind11::arg("size"), pybind11::arg("rcpNodeLookup") );

		cl.def( pybind11::init( [](Teuchos::ArrayView<const double> const &o){ return new Teuchos::ArrayView<const double>(o); } ) );
		cl.def( pybind11::init<class std::vector<double> &>(), pybind11::arg("vec") );

		cl.def( pybind11::init<const class std::vector<double> &>(), pybind11::arg("vec") );

		cl.def("assign", (class Teuchos::ArrayView<const double> & (Teuchos::ArrayView<const double>::*)(const class Teuchos::ArrayView<const double> &)) &Teuchos::ArrayView<const double>::operator=, "C++: Teuchos::ArrayView<const double>::operator=(const class Teuchos::ArrayView<const double> &) --> class Teuchos::ArrayView<const double> &", pybind11::return_value_policy::automatic, pybind11::arg("array"));
		cl.def("is_null", (bool (Teuchos::ArrayView<const double>::*)() const) &Teuchos::ArrayView<const double>::is_null, "C++: Teuchos::ArrayView<const double>::is_null() const --> bool");
		cl.def("size", (long (Teuchos::ArrayView<const double>::*)() const) &Teuchos::ArrayView<const double>::size, "C++: Teuchos::ArrayView<const double>::size() const --> long");
		cl.def("toString", (std::string (Teuchos::ArrayView<const double>::*)() const) &Teuchos::ArrayView<const double>::toString, "C++: Teuchos::ArrayView<const double>::toString() const --> std::string");
		cl.def("getRawPtr", (const double * (Teuchos::ArrayView<const double>::*)() const) &Teuchos::ArrayView<const double>::getRawPtr, "C++: Teuchos::ArrayView<const double>::getRawPtr() const --> const double *", pybind11::return_value_policy::automatic);
		cl.def("data", (const double * (Teuchos::ArrayView<const double>::*)() const) &Teuchos::ArrayView<const double>::data, "C++: Teuchos::ArrayView<const double>::data() const --> const double *", pybind11::return_value_policy::automatic);
		cl.def("__getitem__", (const double & (Teuchos::ArrayView<const double>::*)(long) const) &Teuchos::ArrayView<const double>::operator[], "C++: Teuchos::ArrayView<const double>::operator[](long) const --> const double &", pybind11::return_value_policy::automatic, pybind11::arg("i"));
		cl.def("front", (const double & (Teuchos::ArrayView<const double>::*)() const) &Teuchos::ArrayView<const double>::front, "C++: Teuchos::ArrayView<const double>::front() const --> const double &", pybind11::return_value_policy::automatic);
		cl.def("back", (const double & (Teuchos::ArrayView<const double>::*)() const) &Teuchos::ArrayView<const double>::back, "C++: Teuchos::ArrayView<const double>::back() const --> const double &", pybind11::return_value_policy::automatic);
		cl.def("view", (class Teuchos::ArrayView<const double> (Teuchos::ArrayView<const double>::*)(long, long) const) &Teuchos::ArrayView<const double>::view, "C++: Teuchos::ArrayView<const double>::view(long, long) const --> class Teuchos::ArrayView<const double>", pybind11::arg("offset"), pybind11::arg("size"));
		cl.def("__call__", (class Teuchos::ArrayView<const double> (Teuchos::ArrayView<const double>::*)(long, long) const) &Teuchos::ArrayView<const double>::operator(), "C++: Teuchos::ArrayView<const double>::operator()(long, long) const --> class Teuchos::ArrayView<const double>", pybind11::arg("offset"), pybind11::arg("size"));
		cl.def("__call__", (const class Teuchos::ArrayView<const double> & (Teuchos::ArrayView<const double>::*)() const) &Teuchos::ArrayView<const double>::operator(), "C++: Teuchos::ArrayView<const double>::operator()() const --> const class Teuchos::ArrayView<const double> &", pybind11::return_value_policy::automatic);
		cl.def("getConst", (class Teuchos::ArrayView<const double> (Teuchos::ArrayView<const double>::*)() const) &Teuchos::ArrayView<const double>::getConst, "C++: Teuchos::ArrayView<const double>::getConst() const --> class Teuchos::ArrayView<const double>");
		cl.def("begin", (const double * (Teuchos::ArrayView<const double>::*)() const) &Teuchos::ArrayView<const double>::begin, "C++: Teuchos::ArrayView<const double>::begin() const --> const double *", pybind11::return_value_policy::automatic);
		cl.def("end", (const double * (Teuchos::ArrayView<const double>::*)() const) &Teuchos::ArrayView<const double>::end, "C++: Teuchos::ArrayView<const double>::end() const --> const double *", pybind11::return_value_policy::automatic);
		cl.def("assert_not_null", (const class Teuchos::ArrayView<const double> & (Teuchos::ArrayView<const double>::*)() const) &Teuchos::ArrayView<const double>::assert_not_null, "C++: Teuchos::ArrayView<const double>::assert_not_null() const --> const class Teuchos::ArrayView<const double> &", pybind11::return_value_policy::automatic);
		cl.def("assert_in_range", (const class Teuchos::ArrayView<const double> & (Teuchos::ArrayView<const double>::*)(long, long) const) &Teuchos::ArrayView<const double>::assert_in_range, "C++: Teuchos::ArrayView<const double>::assert_in_range(long, long) const --> const class Teuchos::ArrayView<const double> &", pybind11::return_value_policy::automatic, pybind11::arg("offset"), pybind11::arg("size"));
		cl.def("access_private_ptr", (const double * (Teuchos::ArrayView<const double>::*)() const) &Teuchos::ArrayView<const double>::access_private_ptr, "C++: Teuchos::ArrayView<const double>::access_private_ptr() const --> const double *", pybind11::return_value_policy::automatic);

		cl.def("__str__", [](Teuchos::ArrayView<const double> const &o) -> std::string { std::ostringstream s; using namespace Teuchos; s << o; return s.str(); } );
	}
	// Teuchos::as(const long &) file:Teuchos_as.hpp line:255
	M("Teuchos").def("as", (int (*)(const long &)) &Teuchos::as<int,long>, "C++: Teuchos::as(const long &) --> int", pybind11::arg("t"));

	// Teuchos::as(const std::string &) file:Teuchos_as.hpp line:255
	M("Teuchos").def("as", (unsigned long (*)(const std::string &)) &Teuchos::as<unsigned long,std::string>, "C++: Teuchos::as(const std::string &) --> unsigned long", pybind11::arg("t"));

	// Teuchos::as(const unsigned long &) file:Teuchos_as.hpp line:255
	M("Teuchos").def("as", (unsigned int (*)(const unsigned long &)) &Teuchos::as<unsigned int,unsigned long>, "C++: Teuchos::as(const unsigned long &) --> unsigned int", pybind11::arg("t"));

	// Teuchos::as(const long &) file:Teuchos_as.hpp line:255
	M("Teuchos").def("as", (short (*)(const long &)) &Teuchos::as<short,long>, "C++: Teuchos::as(const long &) --> short", pybind11::arg("t"));

	// Teuchos::as(const unsigned long &) file:Teuchos_as.hpp line:255
	M("Teuchos").def("as", (unsigned short (*)(const unsigned long &)) &Teuchos::as<unsigned short,unsigned long>, "C++: Teuchos::as(const unsigned long &) --> unsigned short", pybind11::arg("t"));

	// Teuchos::as(const int &) file:Teuchos_as.hpp line:2808
	M("Teuchos").def("as", (long (*)(const int &)) &Teuchos::as<long,int>, "C++: Teuchos::as(const int &) --> long", pybind11::arg("t"));

	// Teuchos::as(const unsigned long &) file:Teuchos_as.hpp line:2808
	M("Teuchos").def("as", (int (*)(const unsigned long &)) &Teuchos::as<int,unsigned long>, "C++: Teuchos::as(const unsigned long &) --> int", pybind11::arg("t"));

	// Teuchos::asSafe(const long &) file:Teuchos_as.hpp line:324
	M("Teuchos").def("asSafe", (int (*)(const long &)) &Teuchos::asSafe<int,long>, "C++: Teuchos::asSafe(const long &) --> int", pybind11::arg("t"));

	// Teuchos::asSafe(const unsigned long &) file:Teuchos_as.hpp line:324
	M("Teuchos").def("asSafe", (unsigned int (*)(const unsigned long &)) &Teuchos::asSafe<unsigned int,unsigned long>, "C++: Teuchos::asSafe(const unsigned long &) --> unsigned int", pybind11::arg("t"));

	// Teuchos::asSafe(const long &) file:Teuchos_as.hpp line:324
	M("Teuchos").def("asSafe", (short (*)(const long &)) &Teuchos::asSafe<short,long>, "C++: Teuchos::asSafe(const long &) --> short", pybind11::arg("t"));

	// Teuchos::asSafe(const unsigned long &) file:Teuchos_as.hpp line:324
	M("Teuchos").def("asSafe", (unsigned short (*)(const unsigned long &)) &Teuchos::asSafe<unsigned short,unsigned long>, "C++: Teuchos::asSafe(const unsigned long &) --> unsigned short", pybind11::arg("t"));

	{ // Teuchos::ValueTypeConversionTraits file:Teuchos_as.hpp line:594
		pybind11::class_<Teuchos::ValueTypeConversionTraits<double,std::string>, Teuchos::RCP<Teuchos::ValueTypeConversionTraits<double,std::string>>> cl(M("Teuchos"), "ValueTypeConversionTraits_double_std_string_t", "Convert an  to a ", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ValueTypeConversionTraits<double,std::string>(); } ) );
		cl.def_static("convert", (double (*)(const std::string &)) &Teuchos::ValueTypeConversionTraits<double, std::string>::convert, "C++: Teuchos::ValueTypeConversionTraits<double, std::string>::convert(const std::string &) --> double", pybind11::arg("t"));
		cl.def_static("safeConvert", (double (*)(const std::string &)) &Teuchos::ValueTypeConversionTraits<double, std::string>::safeConvert, "C++: Teuchos::ValueTypeConversionTraits<double, std::string>::safeConvert(const std::string &) --> double", pybind11::arg("t"));
	}
	{ // Teuchos::ValueTypeConversionTraits file:Teuchos_as.hpp line:607
		pybind11::class_<Teuchos::ValueTypeConversionTraits<float,std::string>, Teuchos::RCP<Teuchos::ValueTypeConversionTraits<float,std::string>>> cl(M("Teuchos"), "ValueTypeConversionTraits_float_std_string_t", "Convert an  to a ", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ValueTypeConversionTraits<float,std::string>(); } ) );
		cl.def_static("convert", (float (*)(const std::string &)) &Teuchos::ValueTypeConversionTraits<float, std::string>::convert, "C++: Teuchos::ValueTypeConversionTraits<float, std::string>::convert(const std::string &) --> float", pybind11::arg("t"));
		cl.def_static("safeConvert", (float (*)(const std::string &)) &Teuchos::ValueTypeConversionTraits<float, std::string>::safeConvert, "C++: Teuchos::ValueTypeConversionTraits<float, std::string>::safeConvert(const std::string &) --> float", pybind11::arg("t"));
	}
	{ // Teuchos::ValueTypeConversionTraits file:Teuchos_as.hpp line:634
		pybind11::class_<Teuchos::ValueTypeConversionTraits<long double,std::string>, Teuchos::RCP<Teuchos::ValueTypeConversionTraits<long double,std::string>>> cl(M("Teuchos"), "ValueTypeConversionTraits_long_double_std_string_t", "Convert an  to a long double.", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ValueTypeConversionTraits<long double,std::string>(); } ) );
		cl.def_static("convert", (long double (*)(const std::string &)) &Teuchos::ValueTypeConversionTraits<long double, std::string>::convert, "C++: Teuchos::ValueTypeConversionTraits<long double, std::string>::convert(const std::string &) --> long double", pybind11::arg("t"));
		cl.def_static("safeConvert", (long double (*)(const std::string &)) &Teuchos::ValueTypeConversionTraits<long double, std::string>::safeConvert, "C++: Teuchos::ValueTypeConversionTraits<long double, std::string>::safeConvert(const std::string &) --> long double", pybind11::arg("t"));
	}
	{ // Teuchos::ValueTypeConversionTraits file:Teuchos_as.hpp line:660
		pybind11::class_<Teuchos::ValueTypeConversionTraits<long long,std::string>, Teuchos::RCP<Teuchos::ValueTypeConversionTraits<long long,std::string>>> cl(M("Teuchos"), "ValueTypeConversionTraits_long_long_std_string_t", "Convert an  to a long long.\n\n We assume the string stores a base-10 integer, if it stores an integer at all.", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ValueTypeConversionTraits<long long,std::string>(); } ) );
		cl.def_static("safeConvert", (long long (*)(const std::string &)) &Teuchos::ValueTypeConversionTraits<long long, std::string>::safeConvert, "Convert the given  to a long long, with checks.\n\n If the string overflows long long, this throws\n std::range_error.  If it does not contain an integer,\n this throws std::invalid_argument.\n\nC++: Teuchos::ValueTypeConversionTraits<long long, std::string>::safeConvert(const std::string &) --> long long", pybind11::arg("t"));
		cl.def_static("convert", (long long (*)(const std::string &)) &Teuchos::ValueTypeConversionTraits<long long, std::string>::convert, "Convert the given  to a long long.\n\nC++: Teuchos::ValueTypeConversionTraits<long long, std::string>::convert(const std::string &) --> long long", pybind11::arg("t"));
	}
	{ // Teuchos::ValueTypeConversionTraits file:Teuchos_as.hpp line:691
		pybind11::class_<Teuchos::ValueTypeConversionTraits<unsigned long long,std::string>, Teuchos::RCP<Teuchos::ValueTypeConversionTraits<unsigned long long,std::string>>> cl(M("Teuchos"), "ValueTypeConversionTraits_unsigned_long_long_std_string_t", "Convert an  to an unsigned long long.\n\n We assume the string stores a base-10 integer, if it stores an integer at all.", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ValueTypeConversionTraits<unsigned long long,std::string>(); } ) );
		cl.def_static("safeConvert", (unsigned long long (*)(const std::string &)) &Teuchos::ValueTypeConversionTraits<unsigned long long, std::string>::safeConvert, "Convert the given  to an unsigned long long, with checks.\n\n If the string overflows unsigned long long, this throws\n std::range_error.  If it does not contain an integer,\n this throws std::invalid_argument.\n\nC++: Teuchos::ValueTypeConversionTraits<unsigned long long, std::string>::safeConvert(const std::string &) --> unsigned long long", pybind11::arg("t"));
		cl.def_static("convert", (unsigned long long (*)(const std::string &)) &Teuchos::ValueTypeConversionTraits<unsigned long long, std::string>::convert, "Convert the given  to an unsigned long long.\n\nC++: Teuchos::ValueTypeConversionTraits<unsigned long long, std::string>::convert(const std::string &) --> unsigned long long", pybind11::arg("t"));
	}
	{ // Teuchos::ValueTypeConversionTraits file:Teuchos_as.hpp line:732
		pybind11::class_<Teuchos::ValueTypeConversionTraits<long,std::string>, Teuchos::RCP<Teuchos::ValueTypeConversionTraits<long,std::string>>> cl(M("Teuchos"), "ValueTypeConversionTraits_long_std_string_t", "Convert an  to a \n\n We assume the string stores a base-10 integer, if it stores an integer at all.", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ValueTypeConversionTraits<long,std::string>(); } ) );
		cl.def_static("safeConvert", (long (*)(const std::string &)) &Teuchos::ValueTypeConversionTraits<long, std::string>::safeConvert, "Convert the given  to a  with checks.\n\n If the string overflows long, this throws\n std::range_error.  If it does not contain an integer,\n this throws std::invalid_argument.\n\nC++: Teuchos::ValueTypeConversionTraits<long, std::string>::safeConvert(const std::string &) --> long", pybind11::arg("t"));
		cl.def_static("convert", (long (*)(const std::string &)) &Teuchos::ValueTypeConversionTraits<long, std::string>::convert, "Convert the given  to a \n\nC++: Teuchos::ValueTypeConversionTraits<long, std::string>::convert(const std::string &) --> long", pybind11::arg("t"));
	}
	{ // Teuchos::ValueTypeConversionTraits file:Teuchos_as.hpp line:754
		pybind11::class_<Teuchos::ValueTypeConversionTraits<unsigned long,std::string>, Teuchos::RCP<Teuchos::ValueTypeConversionTraits<unsigned long,std::string>>> cl(M("Teuchos"), "ValueTypeConversionTraits_unsigned_long_std_string_t", "Convert an  to an unsigned long.\n\n We assume the string stores a base-10 integer, if it stores an integer at all.", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ValueTypeConversionTraits<unsigned long,std::string>(); } ) );
		cl.def_static("safeConvert", (unsigned long (*)(const std::string &)) &Teuchos::ValueTypeConversionTraits<unsigned long, std::string>::safeConvert, "Convert the given std::string to an unsigned long, with checks.\n\n If the string overflows unsigned long, this throws\n std::range_error.  If it does not contain an integer,\n this throws std::invalid_argument.\n\nC++: Teuchos::ValueTypeConversionTraits<unsigned long, std::string>::safeConvert(const std::string &) --> unsigned long", pybind11::arg("t"));
		cl.def_static("convert", (unsigned long (*)(const std::string &)) &Teuchos::ValueTypeConversionTraits<unsigned long, std::string>::convert, "Convert the given  to an unsigned long.\n\nC++: Teuchos::ValueTypeConversionTraits<unsigned long, std::string>::convert(const std::string &) --> unsigned long", pybind11::arg("t"));
	}
	{ // Teuchos::ValueTypeConversionTraits file:Teuchos_as.hpp line:807
		pybind11::class_<Teuchos::ValueTypeConversionTraits<int,std::string>, Teuchos::RCP<Teuchos::ValueTypeConversionTraits<int,std::string>>> cl(M("Teuchos"), "ValueTypeConversionTraits_int_std_string_t", "Convert an  to an \n\n We assume the string stores a base-10 integer, if it stores an integer at all.", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ValueTypeConversionTraits<int,std::string>(); } ) );
		cl.def_static("safeConvert", (int (*)(const std::string &)) &Teuchos::ValueTypeConversionTraits<int, std::string>::safeConvert, "Convert the given  to an int, with checks.\n\n If the string overflows int, this throws\n std::range_error.  If it does not contain an integer,\n this throws std::invalid_argument.\n\nC++: Teuchos::ValueTypeConversionTraits<int, std::string>::safeConvert(const std::string &) --> int", pybind11::arg("t"));
		cl.def_static("convert", (int (*)(const std::string &)) &Teuchos::ValueTypeConversionTraits<int, std::string>::convert, "Convert the given  to an \n\nC++: Teuchos::ValueTypeConversionTraits<int, std::string>::convert(const std::string &) --> int", pybind11::arg("t"));
	}
	{ // Teuchos::ValueTypeConversionTraits file:Teuchos_as.hpp line:852
		pybind11::class_<Teuchos::ValueTypeConversionTraits<unsigned int,std::string>, Teuchos::RCP<Teuchos::ValueTypeConversionTraits<unsigned int,std::string>>> cl(M("Teuchos"), "ValueTypeConversionTraits_unsigned_int_std_string_t", "Convert an  to an unsigned int.\n\n We assume the string stores a base-10 integer, if it stores an integer at all.", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ValueTypeConversionTraits<unsigned int,std::string>(); } ) );
		cl.def_static("safeConvert", (unsigned int (*)(const std::string &)) &Teuchos::ValueTypeConversionTraits<unsigned int, std::string>::safeConvert, "Convert the given  to an unsigned int, with checks.\n\n If the string overflows unsigned int, this throws\n std::range_error.  If it does not contain an integer,\n this throws std::invalid_argument.\n\nC++: Teuchos::ValueTypeConversionTraits<unsigned int, std::string>::safeConvert(const std::string &) --> unsigned int", pybind11::arg("t"));
		cl.def_static("convert", (unsigned int (*)(const std::string &)) &Teuchos::ValueTypeConversionTraits<unsigned int, std::string>::convert, "Convert the given  to an unsigned int.\n\nC++: Teuchos::ValueTypeConversionTraits<unsigned int, std::string>::convert(const std::string &) --> unsigned int", pybind11::arg("t"));
	}
	{ // Teuchos::ValueTypeConversionTraits file:Teuchos_as.hpp line:897
		pybind11::class_<Teuchos::ValueTypeConversionTraits<short,std::string>, Teuchos::RCP<Teuchos::ValueTypeConversionTraits<short,std::string>>> cl(M("Teuchos"), "ValueTypeConversionTraits_short_std_string_t", "Convert an  to a \n\n We assume the string stores a base-10 integer, if it stores an integer at all.", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ValueTypeConversionTraits<short,std::string>(); } ) );
		cl.def_static("safeConvert", (short (*)(const std::string &)) &Teuchos::ValueTypeConversionTraits<short, std::string>::safeConvert, "Convert the given  to a short, with checks.\n\n If the string overflows short, this throws\n std::range_error.  If it does not contain an integer,\n this throws std::invalid_argument.\n\nC++: Teuchos::ValueTypeConversionTraits<short, std::string>::safeConvert(const std::string &) --> short", pybind11::arg("t"));
		cl.def_static("convert", (short (*)(const std::string &)) &Teuchos::ValueTypeConversionTraits<short, std::string>::convert, "Convert the given  to a \n\nC++: Teuchos::ValueTypeConversionTraits<short, std::string>::convert(const std::string &) --> short", pybind11::arg("t"));
	}
	{ // Teuchos::ValueTypeConversionTraits file:Teuchos_as.hpp line:942
		pybind11::class_<Teuchos::ValueTypeConversionTraits<unsigned short,std::string>, Teuchos::RCP<Teuchos::ValueTypeConversionTraits<unsigned short,std::string>>> cl(M("Teuchos"), "ValueTypeConversionTraits_unsigned_short_std_string_t", "Convert an  to an unsigned short.\n\n We assume the string stores a base-10 integer, if it stores an integer at all.", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ValueTypeConversionTraits<unsigned short,std::string>(); } ) );
		cl.def_static("safeConvert", (unsigned short (*)(const std::string &)) &Teuchos::ValueTypeConversionTraits<unsigned short, std::string>::safeConvert, "Convert the given  to an unsigned short, with checks.\n\n If the string overflows unsigned short, this throws\n std::range_error.  If it does not contain an integer,\n this throws std::invalid_argument.\n\nC++: Teuchos::ValueTypeConversionTraits<unsigned short, std::string>::safeConvert(const std::string &) --> unsigned short", pybind11::arg("t"));
		cl.def_static("convert", (unsigned short (*)(const std::string &)) &Teuchos::ValueTypeConversionTraits<unsigned short, std::string>::convert, "Convert the given  to an unsigned short.\n\nC++: Teuchos::ValueTypeConversionTraits<unsigned short, std::string>::convert(const std::string &) --> unsigned short", pybind11::arg("t"));
	}
	{ // Teuchos::ValueTypeConversionTraits file:Teuchos_as.hpp line:989
		pybind11::class_<Teuchos::ValueTypeConversionTraits<float,double>, Teuchos::RCP<Teuchos::ValueTypeConversionTraits<float,double>>> cl(M("Teuchos"), "ValueTypeConversionTraits_float_double_t", "Convert from  to ", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ValueTypeConversionTraits<float,double>(); } ) );
		cl.def_static("safeConvert", (float (*)(const double)) &Teuchos::ValueTypeConversionTraits<float, double>::safeConvert, "C++: Teuchos::ValueTypeConversionTraits<float, double>::safeConvert(const double) --> float", pybind11::arg("t"));
		cl.def_static("convert", (float (*)(const double)) &Teuchos::ValueTypeConversionTraits<float, double>::convert, "C++: Teuchos::ValueTypeConversionTraits<float, double>::convert(const double) --> float", pybind11::arg("t"));
	}
	{ // Teuchos::ValueTypeConversionTraits file:Teuchos_as.hpp line:1025
		pybind11::class_<Teuchos::ValueTypeConversionTraits<float,long double>, Teuchos::RCP<Teuchos::ValueTypeConversionTraits<float,long double>>> cl(M("Teuchos"), "ValueTypeConversionTraits_float_long_double_t", "Convert from long double to ", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ValueTypeConversionTraits<float,long double>(); } ) );
		cl.def_static("safeConvert", (float (*)(const long double)) &Teuchos::ValueTypeConversionTraits<float, long double>::safeConvert, "C++: Teuchos::ValueTypeConversionTraits<float, long double>::safeConvert(const long double) --> float", pybind11::arg("t"));
		cl.def_static("convert", (float (*)(const long double)) &Teuchos::ValueTypeConversionTraits<float, long double>::convert, "C++: Teuchos::ValueTypeConversionTraits<float, long double>::convert(const long double) --> float", pybind11::arg("t"));
	}
	{ // Teuchos::ValueTypeConversionTraits file:Teuchos_as.hpp line:1061
		pybind11::class_<Teuchos::ValueTypeConversionTraits<double,long double>, Teuchos::RCP<Teuchos::ValueTypeConversionTraits<double,long double>>> cl(M("Teuchos"), "ValueTypeConversionTraits_double_long_double_t", "Convert from long double to ", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ValueTypeConversionTraits<double,long double>(); } ) );
		cl.def_static("safeConvert", (double (*)(const long double)) &Teuchos::ValueTypeConversionTraits<double, long double>::safeConvert, "C++: Teuchos::ValueTypeConversionTraits<double, long double>::safeConvert(const long double) --> double", pybind11::arg("t"));
		cl.def_static("convert", (double (*)(const long double)) &Teuchos::ValueTypeConversionTraits<double, long double>::convert, "C++: Teuchos::ValueTypeConversionTraits<double, long double>::convert(const long double) --> double", pybind11::arg("t"));
	}
	{ // Teuchos::ValueTypeConversionTraits file:Teuchos_as.hpp line:1103
		pybind11::class_<Teuchos::ValueTypeConversionTraits<short,double>, Teuchos::RCP<Teuchos::ValueTypeConversionTraits<short,double>>> cl(M("Teuchos"), "ValueTypeConversionTraits_short_double_t", "Convert from  to ", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ValueTypeConversionTraits<short,double>(); } ) );
		cl.def_static("convert", (short (*)(const double)) &Teuchos::ValueTypeConversionTraits<short, double>::convert, "Convert the given  to a \n\n \n Double-precision floating-point values may overflow\n   short.  You should use safeConvert() if you aren't sure\n   that the given value fits in an short.\n\nC++: Teuchos::ValueTypeConversionTraits<short, double>::convert(const double) --> short", pybind11::arg("t"));
		cl.def_static("safeConvert", (short (*)(const double)) &Teuchos::ValueTypeConversionTraits<short, double>::safeConvert, "Convert the given  to a  checking for overflow first.\n\nC++: Teuchos::ValueTypeConversionTraits<short, double>::safeConvert(const double) --> short", pybind11::arg("t"));
	}
	{ // Teuchos::ValueTypeConversionTraits file:Teuchos_as.hpp line:1151
		pybind11::class_<Teuchos::ValueTypeConversionTraits<unsigned short,double>, Teuchos::RCP<Teuchos::ValueTypeConversionTraits<unsigned short,double>>> cl(M("Teuchos"), "ValueTypeConversionTraits_unsigned_short_double_t", "Convert from  to unsigned short.", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ValueTypeConversionTraits<unsigned short,double>(); } ) );
		cl.def_static("convert", (unsigned short (*)(const double)) &Teuchos::ValueTypeConversionTraits<unsigned short, double>::convert, "Convert the given  to an unsigned short.\n\nC++: Teuchos::ValueTypeConversionTraits<unsigned short, double>::convert(const double) --> unsigned short", pybind11::arg("t"));
		cl.def_static("safeConvert", (unsigned short (*)(const double)) &Teuchos::ValueTypeConversionTraits<unsigned short, double>::safeConvert, "Convert the given  to an unsigned short, checking for overflow first.\n\nC++: Teuchos::ValueTypeConversionTraits<unsigned short, double>::safeConvert(const double) --> unsigned short", pybind11::arg("t"));
	}
	{ // Teuchos::ValueTypeConversionTraits file:Teuchos_as.hpp line:1179
		pybind11::class_<Teuchos::ValueTypeConversionTraits<int,double>, Teuchos::RCP<Teuchos::ValueTypeConversionTraits<int,double>>> cl(M("Teuchos"), "ValueTypeConversionTraits_int_double_t", "Convert from  to ", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ValueTypeConversionTraits<int,double>(); } ) );
		cl.def_static("convert", (int (*)(const double)) &Teuchos::ValueTypeConversionTraits<int, double>::convert, "Convert the given  to an \n\n \n Double-precision floating-point values may overflow\n   int.  You should use safeConvert() if you aren't sure\n   that the given value fits in an int.\n\nC++: Teuchos::ValueTypeConversionTraits<int, double>::convert(const double) --> int", pybind11::arg("t"));
		cl.def_static("safeConvert", (int (*)(const double)) &Teuchos::ValueTypeConversionTraits<int, double>::safeConvert, "Convert the given  to an  checking for overflow first.\n\nC++: Teuchos::ValueTypeConversionTraits<int, double>::safeConvert(const double) --> int", pybind11::arg("t"));
	}
	{ // Teuchos::ValueTypeConversionTraits file:Teuchos_as.hpp line:1223
		pybind11::class_<Teuchos::ValueTypeConversionTraits<unsigned int,double>, Teuchos::RCP<Teuchos::ValueTypeConversionTraits<unsigned int,double>>> cl(M("Teuchos"), "ValueTypeConversionTraits_unsigned_int_double_t", "Convert from  to unsigned int.", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ValueTypeConversionTraits<unsigned int,double>(); } ) );
		cl.def_static("convert", (unsigned int (*)(const double)) &Teuchos::ValueTypeConversionTraits<unsigned int, double>::convert, "Convert the given  to an unsigned int.\n\nC++: Teuchos::ValueTypeConversionTraits<unsigned int, double>::convert(const double) --> unsigned int", pybind11::arg("t"));
		cl.def_static("safeConvert", (unsigned int (*)(const double)) &Teuchos::ValueTypeConversionTraits<unsigned int, double>::safeConvert, "Convert the given  to an unsigned int, checking for overflow first.\n\nC++: Teuchos::ValueTypeConversionTraits<unsigned int, double>::safeConvert(const double) --> unsigned int", pybind11::arg("t"));
	}
	{ // Teuchos::ValueTypeConversionTraits file:Teuchos_as.hpp line:1251
		pybind11::class_<Teuchos::ValueTypeConversionTraits<long,double>, Teuchos::RCP<Teuchos::ValueTypeConversionTraits<long,double>>> cl(M("Teuchos"), "ValueTypeConversionTraits_long_double_t", "Convert from  to ", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ValueTypeConversionTraits<long,double>(); } ) );
		cl.def_static("convert", (long (*)(const double)) &Teuchos::ValueTypeConversionTraits<long, double>::convert, "Convert the given  to \n\nC++: Teuchos::ValueTypeConversionTraits<long, double>::convert(const double) --> long", pybind11::arg("t"));
		cl.def_static("safeConvert", (long (*)(const double)) &Teuchos::ValueTypeConversionTraits<long, double>::safeConvert, "Convert the given  to  checking for overflow first.\n\nC++: Teuchos::ValueTypeConversionTraits<long, double>::safeConvert(const double) --> long", pybind11::arg("t"));
	}
	{ // Teuchos::ValueTypeConversionTraits file:Teuchos_as.hpp line:1295
		pybind11::class_<Teuchos::ValueTypeConversionTraits<unsigned long,double>, Teuchos::RCP<Teuchos::ValueTypeConversionTraits<unsigned long,double>>> cl(M("Teuchos"), "ValueTypeConversionTraits_unsigned_long_double_t", "Convert from  to unsigned long.", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ValueTypeConversionTraits<unsigned long,double>(); } ) );
		cl.def_static("convert", (unsigned long (*)(const double)) &Teuchos::ValueTypeConversionTraits<unsigned long, double>::convert, "Convert the given  to an unsigned long.\n\nC++: Teuchos::ValueTypeConversionTraits<unsigned long, double>::convert(const double) --> unsigned long", pybind11::arg("t"));
		cl.def_static("safeConvert", (unsigned long (*)(const double)) &Teuchos::ValueTypeConversionTraits<unsigned long, double>::safeConvert, "Convert the given  to an unsigned long, checking for overflow first.\n\nC++: Teuchos::ValueTypeConversionTraits<unsigned long, double>::safeConvert(const double) --> unsigned long", pybind11::arg("t"));
	}
	{ // Teuchos::ValueTypeConversionTraits file:Teuchos_as.hpp line:1322
		pybind11::class_<Teuchos::ValueTypeConversionTraits<long long,double>, Teuchos::RCP<Teuchos::ValueTypeConversionTraits<long long,double>>> cl(M("Teuchos"), "ValueTypeConversionTraits_long_long_double_t", "Convert from  to long long.", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ValueTypeConversionTraits<long long,double>(); } ) );
		cl.def_static("convert", (long long (*)(const double)) &Teuchos::ValueTypeConversionTraits<long long, double>::convert, "Convert the given  to long long.\n\nC++: Teuchos::ValueTypeConversionTraits<long long, double>::convert(const double) --> long long", pybind11::arg("t"));
		cl.def_static("safeConvert", (long long (*)(const double)) &Teuchos::ValueTypeConversionTraits<long long, double>::safeConvert, "Convert the given  to long long, checking for overflow first.\n\nC++: Teuchos::ValueTypeConversionTraits<long long, double>::safeConvert(const double) --> long long", pybind11::arg("t"));
	}
	{ // Teuchos::ValueTypeConversionTraits file:Teuchos_as.hpp line:1350
		pybind11::class_<Teuchos::ValueTypeConversionTraits<unsigned long long,double>, Teuchos::RCP<Teuchos::ValueTypeConversionTraits<unsigned long long,double>>> cl(M("Teuchos"), "ValueTypeConversionTraits_unsigned_long_long_double_t", "Convert from  to unsigned long long.", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ValueTypeConversionTraits<unsigned long long,double>(); } ) );
		cl.def_static("convert", (unsigned long long (*)(const double)) &Teuchos::ValueTypeConversionTraits<unsigned long long, double>::convert, "Convert the given  to unsigned long long.\n\nC++: Teuchos::ValueTypeConversionTraits<unsigned long long, double>::convert(const double) --> unsigned long long", pybind11::arg("t"));
		cl.def_static("safeConvert", (unsigned long long (*)(const double)) &Teuchos::ValueTypeConversionTraits<unsigned long long, double>::safeConvert, "Convert the given  to unsigned long long, checking for overflow first.\n\nC++: Teuchos::ValueTypeConversionTraits<unsigned long long, double>::safeConvert(const double) --> unsigned long long", pybind11::arg("t"));
	}
	{ // Teuchos::ValueTypeConversionTraits file:Teuchos_as.hpp line:1378
		pybind11::class_<Teuchos::ValueTypeConversionTraits<short,float>, Teuchos::RCP<Teuchos::ValueTypeConversionTraits<short,float>>> cl(M("Teuchos"), "ValueTypeConversionTraits_short_float_t", "Convert from  to ", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ValueTypeConversionTraits<short,float>(); } ) );
		cl.def_static("convert", (short (*)(const float)) &Teuchos::ValueTypeConversionTraits<short, float>::convert, "Convert the given  to a \n\n \n Single-precision floating-point values may overflow\n   short.  You should use safeConvert() if you aren't\n   sure that the given value fits in an short.\n\nC++: Teuchos::ValueTypeConversionTraits<short, float>::convert(const float) --> short", pybind11::arg("t"));
		cl.def_static("safeConvert", (short (*)(const float)) &Teuchos::ValueTypeConversionTraits<short, float>::safeConvert, "Convert the given  to a  checking for overflow first.\n\nC++: Teuchos::ValueTypeConversionTraits<short, float>::safeConvert(const float) --> short", pybind11::arg("t"));
	}
	{ // Teuchos::ValueTypeConversionTraits file:Teuchos_as.hpp line:1429
		pybind11::class_<Teuchos::ValueTypeConversionTraits<unsigned short,float>, Teuchos::RCP<Teuchos::ValueTypeConversionTraits<unsigned short,float>>> cl(M("Teuchos"), "ValueTypeConversionTraits_unsigned_short_float_t", "Convert from  to unsigned short.", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ValueTypeConversionTraits<unsigned short,float>(); } ) );
		cl.def_static("convert", (unsigned short (*)(const float)) &Teuchos::ValueTypeConversionTraits<unsigned short, float>::convert, "Convert the given  to an unsigned short.\n\nC++: Teuchos::ValueTypeConversionTraits<unsigned short, float>::convert(const float) --> unsigned short", pybind11::arg("t"));
		cl.def_static("safeConvert", (unsigned short (*)(const float)) &Teuchos::ValueTypeConversionTraits<unsigned short, float>::safeConvert, "Convert the given  to an unsigned short, checking for overflow first.\n\nC++: Teuchos::ValueTypeConversionTraits<unsigned short, float>::safeConvert(const float) --> unsigned short", pybind11::arg("t"));
	}
	{ // Teuchos::ValueTypeConversionTraits file:Teuchos_as.hpp line:1457
		pybind11::class_<Teuchos::ValueTypeConversionTraits<int,float>, Teuchos::RCP<Teuchos::ValueTypeConversionTraits<int,float>>> cl(M("Teuchos"), "ValueTypeConversionTraits_int_float_t", "Convert from  to ", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ValueTypeConversionTraits<int,float>(); } ) );
		cl.def_static("convert", (int (*)(const float)) &Teuchos::ValueTypeConversionTraits<int, float>::convert, "Convert the given  to an \n\nC++: Teuchos::ValueTypeConversionTraits<int, float>::convert(const float) --> int", pybind11::arg("t"));
		cl.def_static("safeConvert", (int (*)(const float)) &Teuchos::ValueTypeConversionTraits<int, float>::safeConvert, "Convert the given  to an \n\nC++: Teuchos::ValueTypeConversionTraits<int, float>::safeConvert(const float) --> int", pybind11::arg("t"));
	}
	{ // Teuchos::ValueTypeConversionTraits file:Teuchos_as.hpp line:1500
		pybind11::class_<Teuchos::ValueTypeConversionTraits<unsigned int,float>, Teuchos::RCP<Teuchos::ValueTypeConversionTraits<unsigned int,float>>> cl(M("Teuchos"), "ValueTypeConversionTraits_unsigned_int_float_t", "Convert from  to unsigned int.", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ValueTypeConversionTraits<unsigned int,float>(); } ) );
		cl.def_static("convert", (unsigned int (*)(const float)) &Teuchos::ValueTypeConversionTraits<unsigned int, float>::convert, "Convert the given  to an unsigned int.\n\nC++: Teuchos::ValueTypeConversionTraits<unsigned int, float>::convert(const float) --> unsigned int", pybind11::arg("t"));
		cl.def_static("safeConvert", (unsigned int (*)(const float)) &Teuchos::ValueTypeConversionTraits<unsigned int, float>::safeConvert, "Convert the given  to an unsigned int, checking first or under- or overflow.\n\nC++: Teuchos::ValueTypeConversionTraits<unsigned int, float>::safeConvert(const float) --> unsigned int", pybind11::arg("t"));
	}
	{ // Teuchos::ValueTypeConversionTraits file:Teuchos_as.hpp line:1528
		pybind11::class_<Teuchos::ValueTypeConversionTraits<long,float>, Teuchos::RCP<Teuchos::ValueTypeConversionTraits<long,float>>> cl(M("Teuchos"), "ValueTypeConversionTraits_long_float_t", "Convert from  to ", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ValueTypeConversionTraits<long,float>(); } ) );
		cl.def_static("convert", (long (*)(const float)) &Teuchos::ValueTypeConversionTraits<long, float>::convert, "Convert the given  to an \n\nC++: Teuchos::ValueTypeConversionTraits<long, float>::convert(const float) --> long", pybind11::arg("t"));
		cl.def_static("safeConvert", (long (*)(const float)) &Teuchos::ValueTypeConversionTraits<long, float>::safeConvert, "Convert the given  to an  checking first for overflow.\n\nC++: Teuchos::ValueTypeConversionTraits<long, float>::safeConvert(const float) --> long", pybind11::arg("t"));
	}
	{ // Teuchos::ValueTypeConversionTraits file:Teuchos_as.hpp line:1577
		pybind11::class_<Teuchos::ValueTypeConversionTraits<unsigned long,float>, Teuchos::RCP<Teuchos::ValueTypeConversionTraits<unsigned long,float>>> cl(M("Teuchos"), "ValueTypeConversionTraits_unsigned_long_float_t", "Convert from  to unsigned long.", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ValueTypeConversionTraits<unsigned long,float>(); } ) );
		cl.def_static("convert", (unsigned long (*)(const float)) &Teuchos::ValueTypeConversionTraits<unsigned long, float>::convert, "Convert the given  to an unsigned long.\n\nC++: Teuchos::ValueTypeConversionTraits<unsigned long, float>::convert(const float) --> unsigned long", pybind11::arg("t"));
		cl.def_static("safeConvert", (unsigned long (*)(const float)) &Teuchos::ValueTypeConversionTraits<unsigned long, float>::safeConvert, "Convert the given  to an unsigned long, checking first or under- or overflow.\n\nC++: Teuchos::ValueTypeConversionTraits<unsigned long, float>::safeConvert(const float) --> unsigned long", pybind11::arg("t"));
	}
	{ // Teuchos::ValueTypeConversionTraits file:Teuchos_as.hpp line:1604
		pybind11::class_<Teuchos::ValueTypeConversionTraits<long long,float>, Teuchos::RCP<Teuchos::ValueTypeConversionTraits<long long,float>>> cl(M("Teuchos"), "ValueTypeConversionTraits_long_long_float_t", "Convert from  to long long.", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ValueTypeConversionTraits<long long,float>(); } ) );
		cl.def_static("convert", (long long (*)(const float)) &Teuchos::ValueTypeConversionTraits<long long, float>::convert, "Convert the given  to a long long.\n\nC++: Teuchos::ValueTypeConversionTraits<long long, float>::convert(const float) --> long long", pybind11::arg("t"));
		cl.def_static("safeConvert", (long long (*)(const float)) &Teuchos::ValueTypeConversionTraits<long long, float>::safeConvert, "Convert the given  to a long long, checking first for overflow.\n\nC++: Teuchos::ValueTypeConversionTraits<long long, float>::safeConvert(const float) --> long long", pybind11::arg("t"));
	}
	{ // Teuchos::ValueTypeConversionTraits file:Teuchos_as.hpp line:1622
		pybind11::class_<Teuchos::ValueTypeConversionTraits<unsigned long long,float>, Teuchos::RCP<Teuchos::ValueTypeConversionTraits<unsigned long long,float>>> cl(M("Teuchos"), "ValueTypeConversionTraits_unsigned_long_long_float_t", "Convert from  to unsigned long long.", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ValueTypeConversionTraits<unsigned long long,float>(); } ) );
		cl.def_static("convert", (unsigned long long (*)(const float)) &Teuchos::ValueTypeConversionTraits<unsigned long long, float>::convert, "Convert the given  to an unsigned long long.\n\nC++: Teuchos::ValueTypeConversionTraits<unsigned long long, float>::convert(const float) --> unsigned long long", pybind11::arg("t"));
		cl.def_static("safeConvert", (unsigned long long (*)(const float)) &Teuchos::ValueTypeConversionTraits<unsigned long long, float>::safeConvert, "Convert the given  to an unsigned long long, checking first for overflow.\n\nC++: Teuchos::ValueTypeConversionTraits<unsigned long long, float>::safeConvert(const float) --> unsigned long long", pybind11::arg("t"));
	}
	{ // Teuchos::ValueTypeConversionTraits file:Teuchos_as.hpp line:1730
		pybind11::class_<Teuchos::ValueTypeConversionTraits<short,unsigned short>, Teuchos::RCP<Teuchos::ValueTypeConversionTraits<short,unsigned short>>> cl(M("Teuchos"), "ValueTypeConversionTraits_short_unsigned_short_t", "Convert from unsigned short to ", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ValueTypeConversionTraits<short,unsigned short>(); } ) );
		cl.def_static("convert", (short (*)(const unsigned short)) &Teuchos::ValueTypeConversionTraits<short, unsigned short>::convert, "C++: Teuchos::ValueTypeConversionTraits<short, unsigned short>::convert(const unsigned short) --> short", pybind11::arg("t"));
		cl.def_static("safeConvert", (short (*)(const unsigned short)) &Teuchos::ValueTypeConversionTraits<short, unsigned short>::safeConvert, "C++: Teuchos::ValueTypeConversionTraits<short, unsigned short>::safeConvert(const unsigned short) --> short", pybind11::arg("t"));
	}
	{ // Teuchos::ValueTypeConversionTraits file:Teuchos_as.hpp line:1744
		pybind11::class_<Teuchos::ValueTypeConversionTraits<unsigned short,short>, Teuchos::RCP<Teuchos::ValueTypeConversionTraits<unsigned short,short>>> cl(M("Teuchos"), "ValueTypeConversionTraits_unsigned_short_short_t", "Convert from short to unsigned short.", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ValueTypeConversionTraits<unsigned short,short>(); } ) );
		cl.def_static("convert", (unsigned short (*)(const short)) &Teuchos::ValueTypeConversionTraits<unsigned short, short>::convert, "C++: Teuchos::ValueTypeConversionTraits<unsigned short, short>::convert(const short) --> unsigned short", pybind11::arg("t"));
		cl.def_static("safeConvert", (unsigned short (*)(const short)) &Teuchos::ValueTypeConversionTraits<unsigned short, short>::safeConvert, "C++: Teuchos::ValueTypeConversionTraits<unsigned short, short>::safeConvert(const short) --> unsigned short", pybind11::arg("t"));
	}
	{ // Teuchos::ValueTypeConversionTraits file:Teuchos_as.hpp line:1758
		pybind11::class_<Teuchos::ValueTypeConversionTraits<int,unsigned int>, Teuchos::RCP<Teuchos::ValueTypeConversionTraits<int,unsigned int>>> cl(M("Teuchos"), "ValueTypeConversionTraits_int_unsigned_int_t", "Convert from unsigned int to ", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ValueTypeConversionTraits<int,unsigned int>(); } ) );
		cl.def_static("convert", (int (*)(const unsigned int)) &Teuchos::ValueTypeConversionTraits<int, unsigned int>::convert, "C++: Teuchos::ValueTypeConversionTraits<int, unsigned int>::convert(const unsigned int) --> int", pybind11::arg("t"));
		cl.def_static("safeConvert", (int (*)(const unsigned int)) &Teuchos::ValueTypeConversionTraits<int, unsigned int>::safeConvert, "C++: Teuchos::ValueTypeConversionTraits<int, unsigned int>::safeConvert(const unsigned int) --> int", pybind11::arg("t"));
	}
	{ // Teuchos::ValueTypeConversionTraits file:Teuchos_as.hpp line:1772
		pybind11::class_<Teuchos::ValueTypeConversionTraits<unsigned int,int>, Teuchos::RCP<Teuchos::ValueTypeConversionTraits<unsigned int,int>>> cl(M("Teuchos"), "ValueTypeConversionTraits_unsigned_int_int_t", "Convert from int to unsigned int.", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ValueTypeConversionTraits<unsigned int,int>(); } ) );
		cl.def_static("convert", (unsigned int (*)(const int)) &Teuchos::ValueTypeConversionTraits<unsigned int, int>::convert, "C++: Teuchos::ValueTypeConversionTraits<unsigned int, int>::convert(const int) --> unsigned int", pybind11::arg("t"));
		cl.def_static("safeConvert", (unsigned int (*)(const int)) &Teuchos::ValueTypeConversionTraits<unsigned int, int>::safeConvert, "C++: Teuchos::ValueTypeConversionTraits<unsigned int, int>::safeConvert(const int) --> unsigned int", pybind11::arg("t"));
	}
	{ // Teuchos::ValueTypeConversionTraits file:Teuchos_as.hpp line:1786
		pybind11::class_<Teuchos::ValueTypeConversionTraits<long,unsigned long>, Teuchos::RCP<Teuchos::ValueTypeConversionTraits<long,unsigned long>>> cl(M("Teuchos"), "ValueTypeConversionTraits_long_unsigned_long_t", "Convert from unsigned long to ", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ValueTypeConversionTraits<long,unsigned long>(); } ) );
		cl.def_static("convert", (long (*)(const unsigned long)) &Teuchos::ValueTypeConversionTraits<long, unsigned long>::convert, "C++: Teuchos::ValueTypeConversionTraits<long, unsigned long>::convert(const unsigned long) --> long", pybind11::arg("t"));
		cl.def_static("safeConvert", (long (*)(const unsigned long)) &Teuchos::ValueTypeConversionTraits<long, unsigned long>::safeConvert, "C++: Teuchos::ValueTypeConversionTraits<long, unsigned long>::safeConvert(const unsigned long) --> long", pybind11::arg("t"));
	}
	{ // Teuchos::ValueTypeConversionTraits file:Teuchos_as.hpp line:1800
		pybind11::class_<Teuchos::ValueTypeConversionTraits<unsigned long,long>, Teuchos::RCP<Teuchos::ValueTypeConversionTraits<unsigned long,long>>> cl(M("Teuchos"), "ValueTypeConversionTraits_unsigned_long_long_t", "Convert from long to unsigned long.", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ValueTypeConversionTraits<unsigned long,long>(); } ) );
		cl.def_static("convert", (unsigned long (*)(const long)) &Teuchos::ValueTypeConversionTraits<unsigned long, long>::convert, "C++: Teuchos::ValueTypeConversionTraits<unsigned long, long>::convert(const long) --> unsigned long", pybind11::arg("t"));
		cl.def_static("safeConvert", (unsigned long (*)(const long)) &Teuchos::ValueTypeConversionTraits<unsigned long, long>::safeConvert, "C++: Teuchos::ValueTypeConversionTraits<unsigned long, long>::safeConvert(const long) --> unsigned long", pybind11::arg("t"));
	}
	{ // Teuchos::ValueTypeConversionTraits file:Teuchos_as.hpp line:1814
		pybind11::class_<Teuchos::ValueTypeConversionTraits<long long,unsigned long long>, Teuchos::RCP<Teuchos::ValueTypeConversionTraits<long long,unsigned long long>>> cl(M("Teuchos"), "ValueTypeConversionTraits_long_long_unsigned_long_long_t", "Convert from unsigned long long to long long.", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ValueTypeConversionTraits<long long,unsigned long long>(); } ) );
		cl.def_static("convert", (long long (*)(const unsigned long long)) &Teuchos::ValueTypeConversionTraits<long long, unsigned long long>::convert, "C++: Teuchos::ValueTypeConversionTraits<long long, unsigned long long>::convert(const unsigned long long) --> long long", pybind11::arg("t"));
		cl.def_static("safeConvert", (long long (*)(const unsigned long long)) &Teuchos::ValueTypeConversionTraits<long long, unsigned long long>::safeConvert, "C++: Teuchos::ValueTypeConversionTraits<long long, unsigned long long>::safeConvert(const unsigned long long) --> long long", pybind11::arg("t"));
	}
	{ // Teuchos::ValueTypeConversionTraits file:Teuchos_as.hpp line:1828
		pybind11::class_<Teuchos::ValueTypeConversionTraits<unsigned long long,long long>, Teuchos::RCP<Teuchos::ValueTypeConversionTraits<unsigned long long,long long>>> cl(M("Teuchos"), "ValueTypeConversionTraits_unsigned_long_long_long_long_t", "Convert from long long to unsigned long long.", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ValueTypeConversionTraits<unsigned long long,long long>(); } ) );
		cl.def_static("convert", (unsigned long long (*)(const long long)) &Teuchos::ValueTypeConversionTraits<unsigned long long, long long>::convert, "C++: Teuchos::ValueTypeConversionTraits<unsigned long long, long long>::convert(const long long) --> unsigned long long", pybind11::arg("t"));
		cl.def_static("safeConvert", (unsigned long long (*)(const long long)) &Teuchos::ValueTypeConversionTraits<unsigned long long, long long>::safeConvert, "C++: Teuchos::ValueTypeConversionTraits<unsigned long long, long long>::safeConvert(const long long) --> unsigned long long", pybind11::arg("t"));
	}
	{ // Teuchos::ValueTypeConversionTraits file:Teuchos_as.hpp line:1846
		pybind11::class_<Teuchos::ValueTypeConversionTraits<short,int>, Teuchos::RCP<Teuchos::ValueTypeConversionTraits<short,int>>> cl(M("Teuchos"), "ValueTypeConversionTraits_short_int_t", "Convert from  to ", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ValueTypeConversionTraits<short,int>(); } ) );
		cl.def_static("convert", (short (*)(const int)) &Teuchos::ValueTypeConversionTraits<short, int>::convert, "Convert the given  to a \n\n \n  values may overflow  depending on your\n   platform.  You should use safeConvert() if you aren't sure\n   that the given  value fits in a \n\nC++: Teuchos::ValueTypeConversionTraits<short, int>::convert(const int) --> short", pybind11::arg("t"));
		cl.def_static("safeConvert", (short (*)(const int)) &Teuchos::ValueTypeConversionTraits<short, int>::safeConvert, "Convert from  to  checking for overflow first.\n\nC++: Teuchos::ValueTypeConversionTraits<short, int>::safeConvert(const int) --> short", pybind11::arg("t"));
	}
	{ // Teuchos::ValueTypeConversionTraits file:Teuchos_as.hpp line:1881
		pybind11::class_<Teuchos::ValueTypeConversionTraits<short,long>, Teuchos::RCP<Teuchos::ValueTypeConversionTraits<short,long>>> cl(M("Teuchos"), "ValueTypeConversionTraits_short_long_t", "Convert from  to ", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ValueTypeConversionTraits<short,long>(); } ) );
		cl.def_static("convert", (short (*)(const long)) &Teuchos::ValueTypeConversionTraits<short, long>::convert, "Convert the given  to a \n\n \n  integer values may overflow  depending\n   on your platform.  You should use safeConvert() if you aren't\n   sure that the given  value fits in a \n\nC++: Teuchos::ValueTypeConversionTraits<short, long>::convert(const long) --> short", pybind11::arg("t"));
		cl.def_static("safeConvert", (short (*)(const long)) &Teuchos::ValueTypeConversionTraits<short, long>::safeConvert, "Convert from  to  checking for overflow first.\n\nC++: Teuchos::ValueTypeConversionTraits<short, long>::safeConvert(const long) --> short", pybind11::arg("t"));
	}
	{ // Teuchos::ValueTypeConversionTraits file:Teuchos_as.hpp line:1916
		pybind11::class_<Teuchos::ValueTypeConversionTraits<int,long>, Teuchos::RCP<Teuchos::ValueTypeConversionTraits<int,long>>> cl(M("Teuchos"), "ValueTypeConversionTraits_int_long_t", "Convert from  to ", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ValueTypeConversionTraits<int,long>(); } ) );
		cl.def_static("convert", (int (*)(const long)) &Teuchos::ValueTypeConversionTraits<int, long>::convert, "Convert the given  to an \n\n \n  integer values may overflow  depending\n   on your platform.  You should use safeConvert() if you aren't\n   sure that the given  value fits in an \n\nC++: Teuchos::ValueTypeConversionTraits<int, long>::convert(const long) --> int", pybind11::arg("t"));
		cl.def_static("safeConvert", (int (*)(const long)) &Teuchos::ValueTypeConversionTraits<int, long>::safeConvert, "Convert from  to  checking for overflow first.\n\nC++: Teuchos::ValueTypeConversionTraits<int, long>::safeConvert(const long) --> int", pybind11::arg("t"));
	}
	{ // Teuchos::ValueTypeConversionTraits file:Teuchos_as.hpp line:1953
		pybind11::class_<Teuchos::ValueTypeConversionTraits<int,unsigned long>, Teuchos::RCP<Teuchos::ValueTypeConversionTraits<int,unsigned long>>> cl(M("Teuchos"), "ValueTypeConversionTraits_int_unsigned_long_t", "Convert from unsigned long to ", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ValueTypeConversionTraits<int,unsigned long>(); } ) );
		cl.def_static("convert", (int (*)(const unsigned long)) &Teuchos::ValueTypeConversionTraits<int, unsigned long>::convert, "Convert the given unsigned long to an \n\n \n unsigned long values may overflow\n   int, depending on your platform.  You should use\n   safeConvert() if you aren't sure that the given unsigned\n   long value fits in an int.\n\nC++: Teuchos::ValueTypeConversionTraits<int, unsigned long>::convert(const unsigned long) --> int", pybind11::arg("t"));
		cl.def_static("safeConvert", (int (*)(const unsigned long)) &Teuchos::ValueTypeConversionTraits<int, unsigned long>::safeConvert, "Convert from unsigned long to  checking for overflow first.\n\nC++: Teuchos::ValueTypeConversionTraits<int, unsigned long>::safeConvert(const unsigned long) --> int", pybind11::arg("t"));
	}
	{ // Teuchos::ValueTypeConversionTraits file:Teuchos_as.hpp line:2016
		pybind11::class_<Teuchos::ValueTypeConversionTraits<long,unsigned int>, Teuchos::RCP<Teuchos::ValueTypeConversionTraits<long,unsigned int>>> cl(M("Teuchos"), "ValueTypeConversionTraits_long_unsigned_int_t", "Convert from unsigned int to long.", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ValueTypeConversionTraits<long,unsigned int>(); } ) );
		cl.def_static("convert", (long (*)(const unsigned int)) &Teuchos::ValueTypeConversionTraits<long, unsigned int>::convert, "Convert the given unsigned int to a \n\n \n On some platforms (e.g., Windows, or any other platform\n   that implements the LLP64 model), unsigned int\n   integer values may overflow long.  You should use\n   safeConvert() if you aren't sure that the given unsigned\n   int value fits in a long.\n\nC++: Teuchos::ValueTypeConversionTraits<long, unsigned int>::convert(const unsigned int) --> long", pybind11::arg("t"));
		cl.def_static("safeConvert", (long (*)(const unsigned int)) &Teuchos::ValueTypeConversionTraits<long, unsigned int>::safeConvert, "Convert from unsigned int to  checking for overflow first.\n\nC++: Teuchos::ValueTypeConversionTraits<long, unsigned int>::safeConvert(const unsigned int) --> long", pybind11::arg("t"));
	}
	{ // Teuchos::ValueTypeConversionTraits file:Teuchos_as.hpp line:2069
		pybind11::class_<Teuchos::ValueTypeConversionTraits<unsigned int,long>, Teuchos::RCP<Teuchos::ValueTypeConversionTraits<unsigned int,long>>> cl(M("Teuchos"), "ValueTypeConversionTraits_unsigned_int_long_t", "Convert from  to unsigned int.", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ValueTypeConversionTraits<unsigned int,long>(); } ) );
		cl.def_static("convert", (unsigned int (*)(const long)) &Teuchos::ValueTypeConversionTraits<unsigned int, long>::convert, "Convert the given  to an unsigned int.\n\n \n  integer values may overflow unsigned\n   int, depending on your platform.  You should use\n   safeConvert() if you aren't sure that the given  value\n   fits in an unsigned int.\n\nC++: Teuchos::ValueTypeConversionTraits<unsigned int, long>::convert(const long) --> unsigned int", pybind11::arg("t"));
		cl.def_static("safeConvert", (unsigned int (*)(const long)) &Teuchos::ValueTypeConversionTraits<unsigned int, long>::safeConvert, "Convert from  to unsigned int, checking for underflow or overflow first.\n\nC++: Teuchos::ValueTypeConversionTraits<unsigned int, long>::safeConvert(const long) --> unsigned int", pybind11::arg("t"));
	}
	{ // Teuchos::ValueTypeConversionTraits file:Teuchos_as.hpp line:2111
		pybind11::class_<Teuchos::ValueTypeConversionTraits<unsigned int,unsigned long>, Teuchos::RCP<Teuchos::ValueTypeConversionTraits<unsigned int,unsigned long>>> cl(M("Teuchos"), "ValueTypeConversionTraits_unsigned_int_unsigned_long_t", "Convert from unsigned long to unsigned int.", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ValueTypeConversionTraits<unsigned int,unsigned long>(); } ) );
		cl.def_static("convert", (unsigned int (*)(const unsigned long)) &Teuchos::ValueTypeConversionTraits<unsigned int, unsigned long>::convert, "Convert the given unsigned long to an unsigned int.\n\n \n unsigned long integer values may overflow\n   unsigned int, depending on your platform.  You should\n   use safeConvert() if you aren't sure that the given\n   unsigned long value fits in an unsigned int.\n\nC++: Teuchos::ValueTypeConversionTraits<unsigned int, unsigned long>::convert(const unsigned long) --> unsigned int", pybind11::arg("t"));
		cl.def_static("safeConvert", (unsigned int (*)(const unsigned long)) &Teuchos::ValueTypeConversionTraits<unsigned int, unsigned long>::safeConvert, "Convert from unsigned long to unsigned int, checking for overflow first.\n\nC++: Teuchos::ValueTypeConversionTraits<unsigned int, unsigned long>::safeConvert(const unsigned long) --> unsigned int", pybind11::arg("t"));
	}
	{ // Teuchos::ValueTypeConversionTraits file:Teuchos_as.hpp line:2146
		pybind11::class_<Teuchos::ValueTypeConversionTraits<unsigned short,unsigned long>, Teuchos::RCP<Teuchos::ValueTypeConversionTraits<unsigned short,unsigned long>>> cl(M("Teuchos"), "ValueTypeConversionTraits_unsigned_short_unsigned_long_t", "Convert from unsigned long to unsigned short.", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ValueTypeConversionTraits<unsigned short,unsigned long>(); } ) );
		cl.def_static("convert", (unsigned short (*)(const unsigned long)) &Teuchos::ValueTypeConversionTraits<unsigned short, unsigned long>::convert, "Convert the given unsigned long to an unsigned short.\n\n \n unsigned long integer values may overflow\n   unsigned short, depending on your platform.  You should\n   use safeConvert() if you aren't sure that the given\n   unsigned long value fits in an unsigned short.\n\nC++: Teuchos::ValueTypeConversionTraits<unsigned short, unsigned long>::convert(const unsigned long) --> unsigned short", pybind11::arg("t"));
		cl.def_static("safeConvert", (unsigned short (*)(const unsigned long)) &Teuchos::ValueTypeConversionTraits<unsigned short, unsigned long>::safeConvert, "Convert from unsigned long to unsigned short, checking for overflow first.\n\nC++: Teuchos::ValueTypeConversionTraits<unsigned short, unsigned long>::safeConvert(const unsigned long) --> unsigned short", pybind11::arg("t"));
	}
	{ // Teuchos::ValueTypeConversionTraits file:Teuchos_as.hpp line:2181
		pybind11::class_<Teuchos::ValueTypeConversionTraits<int,long long>, Teuchos::RCP<Teuchos::ValueTypeConversionTraits<int,long long>>> cl(M("Teuchos"), "ValueTypeConversionTraits_int_long_long_t", "Convert from long long to ", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ValueTypeConversionTraits<int,long long>(); } ) );
		cl.def_static("convert", (int (*)(const long long)) &Teuchos::ValueTypeConversionTraits<int, long long>::convert, "Convert the given long long to an \n\n \n long long integer values may overflow \n   You should use safeConvert() if you aren't sure that the given\n   value fits in an \n\nC++: Teuchos::ValueTypeConversionTraits<int, long long>::convert(const long long) --> int", pybind11::arg("t"));
		cl.def_static("safeConvert", (int (*)(const long long)) &Teuchos::ValueTypeConversionTraits<int, long long>::safeConvert, "Convert from long long to int, checking for overflow first.\n\nC++: Teuchos::ValueTypeConversionTraits<int, long long>::safeConvert(const long long) --> int", pybind11::arg("t"));
	}
	{ // Teuchos::ValueTypeConversionTraits file:Teuchos_as.hpp line:2216
		pybind11::class_<Teuchos::ValueTypeConversionTraits<unsigned int,long long>, Teuchos::RCP<Teuchos::ValueTypeConversionTraits<unsigned int,long long>>> cl(M("Teuchos"), "ValueTypeConversionTraits_unsigned_int_long_long_t", "Convert from long long to unsigned int.", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ValueTypeConversionTraits<unsigned int,long long>(); } ) );
		cl.def_static("convert", (unsigned int (*)(const long long)) &Teuchos::ValueTypeConversionTraits<unsigned int, long long>::convert, "Convert the given long long to an unsigned int.\n\n \n long long integer values may overflow\n   unsigned int.  You should use safeConvert() if you\n   aren't sure that the given value fits in an unsigned\n   int.\n\nC++: Teuchos::ValueTypeConversionTraits<unsigned int, long long>::convert(const long long) --> unsigned int", pybind11::arg("t"));
		cl.def_static("safeConvert", (unsigned int (*)(const long long)) &Teuchos::ValueTypeConversionTraits<unsigned int, long long>::safeConvert, "Convert from long long to unsigned int, checking for overflow first.\n\nC++: Teuchos::ValueTypeConversionTraits<unsigned int, long long>::safeConvert(const long long) --> unsigned int", pybind11::arg("t"));
	}
	{ // Teuchos::ValueTypeConversionTraits file:Teuchos_as.hpp line:2251
		pybind11::class_<Teuchos::ValueTypeConversionTraits<int,unsigned long long>, Teuchos::RCP<Teuchos::ValueTypeConversionTraits<int,unsigned long long>>> cl(M("Teuchos"), "ValueTypeConversionTraits_int_unsigned_long_long_t", "Convert from unsigned long long to int.", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ValueTypeConversionTraits<int,unsigned long long>(); } ) );
		cl.def_static("convert", (int (*)(const unsigned long long)) &Teuchos::ValueTypeConversionTraits<int, unsigned long long>::convert, "Convert the given unsigned long long to an int.\n\n \n unsigned long long integer values may overflow\n     You should use safeConvert() if you aren't sure that\n   the given value fits in an \n\nC++: Teuchos::ValueTypeConversionTraits<int, unsigned long long>::convert(const unsigned long long) --> int", pybind11::arg("t"));
		cl.def_static("safeConvert", (int (*)(const unsigned long long)) &Teuchos::ValueTypeConversionTraits<int, unsigned long long>::safeConvert, "Convert from unsigned long long to int, checking for overflow first.\n\nC++: Teuchos::ValueTypeConversionTraits<int, unsigned long long>::safeConvert(const unsigned long long) --> int", pybind11::arg("t"));
	}
	{ // Teuchos::ValueTypeConversionTraits file:Teuchos_as.hpp line:2286
		pybind11::class_<Teuchos::ValueTypeConversionTraits<unsigned int,unsigned long long>, Teuchos::RCP<Teuchos::ValueTypeConversionTraits<unsigned int,unsigned long long>>> cl(M("Teuchos"), "ValueTypeConversionTraits_unsigned_int_unsigned_long_long_t", "Convert from unsigned long long to unsigned int.", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ValueTypeConversionTraits<unsigned int,unsigned long long>(); } ) );
		cl.def_static("convert", (unsigned int (*)(const unsigned long long)) &Teuchos::ValueTypeConversionTraits<unsigned int, unsigned long long>::convert, "Convert the given unsigned long long to an unsigned int.\n\n \n unsigned long long integer values may overflow\n   unsigned int.  You should use safeConvert() if you\n   aren't sure that the given value fits in an unsigned\n   int.\n\nC++: Teuchos::ValueTypeConversionTraits<unsigned int, unsigned long long>::convert(const unsigned long long) --> unsigned int", pybind11::arg("t"));
		cl.def_static("safeConvert", (unsigned int (*)(const unsigned long long)) &Teuchos::ValueTypeConversionTraits<unsigned int, unsigned long long>::safeConvert, "Convert from unsigned long long to unsigned int, checking for overflow first.\n\nC++: Teuchos::ValueTypeConversionTraits<unsigned int, unsigned long long>::safeConvert(const unsigned long long) --> unsigned int", pybind11::arg("t"));
	}
	{ // Teuchos::ValueTypeConversionTraits file:Teuchos_as.hpp line:2326
		pybind11::class_<Teuchos::ValueTypeConversionTraits<float,long long>, Teuchos::RCP<Teuchos::ValueTypeConversionTraits<float,long long>>> cl(M("Teuchos"), "ValueTypeConversionTraits_float_long_long_t", "Convert from long long to ", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ValueTypeConversionTraits<float,long long>(); } ) );
		cl.def_static("convert", (float (*)(const long long)) &Teuchos::ValueTypeConversionTraits<float, long long>::convert, "Convert the given long long to a \n\n \n long long integer values may overflow\n   float.  You should use safeConvert() if you aren't\n   sure that the given value fits in a float.\n\nC++: Teuchos::ValueTypeConversionTraits<float, long long>::convert(const long long) --> float", pybind11::arg("t"));
		cl.def_static("safeConvert", (float (*)(const long long)) &Teuchos::ValueTypeConversionTraits<float, long long>::safeConvert, "Convert from long long to  checking for overflow first.\n\nC++: Teuchos::ValueTypeConversionTraits<float, long long>::safeConvert(const long long) --> float", pybind11::arg("t"));
	}
	{ // Teuchos::ValueTypeConversionTraits file:Teuchos_as.hpp line:2374
		pybind11::class_<Teuchos::ValueTypeConversionTraits<float,unsigned long long>, Teuchos::RCP<Teuchos::ValueTypeConversionTraits<float,unsigned long long>>> cl(M("Teuchos"), "ValueTypeConversionTraits_float_unsigned_long_long_t", "Convert from unsigned long long to ", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ValueTypeConversionTraits<float,unsigned long long>(); } ) );
		cl.def_static("convert", (float (*)(const unsigned long long)) &Teuchos::ValueTypeConversionTraits<float, unsigned long long>::convert, "Convert the given unsigned long long to a \n\n \n unsigned long long integer values may overflow\n     You should use safeConvert() if you aren't sure\n   that the given value fits in a \n\nC++: Teuchos::ValueTypeConversionTraits<float, unsigned long long>::convert(const unsigned long long) --> float", pybind11::arg("t"));
		cl.def_static("safeConvert", (float (*)(const unsigned long long)) &Teuchos::ValueTypeConversionTraits<float, unsigned long long>::safeConvert, "Convert from unsigned long long to  checking for overflow first.\n\nC++: Teuchos::ValueTypeConversionTraits<float, unsigned long long>::safeConvert(const unsigned long long) --> float", pybind11::arg("t"));
	}
	// Teuchos::EVerbosityLevel file:Teuchos_VerbosityLevel.hpp line:31
	pybind11::enum_<Teuchos::EVerbosityLevel>(M("Teuchos"), "EVerbosityLevel", pybind11::arithmetic(), "Verbosity level.\n\n \n\n ", pybind11::module_local())
		.value("VERB_DEFAULT", Teuchos::VERB_DEFAULT)
		.value("VERB_NONE", Teuchos::VERB_NONE)
		.value("VERB_LOW", Teuchos::VERB_LOW)
		.value("VERB_MEDIUM", Teuchos::VERB_MEDIUM)
		.value("VERB_HIGH", Teuchos::VERB_HIGH)
		.value("VERB_EXTREME", Teuchos::VERB_EXTREME)
		.export_values();

;

	// Teuchos::toString(const enum Teuchos::EVerbosityLevel) file:Teuchos_VerbosityLevel.hpp line:79
	M("Teuchos").def("toString", (std::string (*)(const enum Teuchos::EVerbosityLevel)) &Teuchos::toString, "Return a std::string representation of the verbosity level.\n\n \n\n \n\nC++: Teuchos::toString(const enum Teuchos::EVerbosityLevel) --> std::string", pybind11::arg("verbLevel"));

	// Teuchos::includesVerbLevel(const enum Teuchos::EVerbosityLevel, const enum Teuchos::EVerbosityLevel, const bool) file:Teuchos_VerbosityLevel.hpp line:95
	M("Teuchos").def("includesVerbLevel", [](const enum Teuchos::EVerbosityLevel & a0, const enum Teuchos::EVerbosityLevel & a1) -> bool { return Teuchos::includesVerbLevel(a0, a1); }, "", pybind11::arg("verbLevel"), pybind11::arg("requestedVerbLevel"));
	M("Teuchos").def("includesVerbLevel", (bool (*)(const enum Teuchos::EVerbosityLevel, const enum Teuchos::EVerbosityLevel, const bool)) &Teuchos::includesVerbLevel, "Return true if the verbosity level includes the given level.\n\n \n\n           [in] The verbosity level that is in effect.\n \n\n\n           [in] The verbosity level the client is asking if\n           is included in verbLevel.\n \n\n\n           [in] Set to true if the level in\n           requestedVerbLevel is the default verbosity level.  In\n           this case, if verbLevel==VERB_DEFAULT, then this function\n           will return true.  The default value is false.\n\nC++: Teuchos::includesVerbLevel(const enum Teuchos::EVerbosityLevel, const enum Teuchos::EVerbosityLevel, const bool) --> bool", pybind11::arg("verbLevel"), pybind11::arg("requestedVerbLevel"), pybind11::arg("isDefaultLevel"));

	// Teuchos::incrVerbLevel(const enum Teuchos::EVerbosityLevel, const int) file:Teuchos_VerbosityLevel.hpp line:111
	M("Teuchos").def("incrVerbLevel", (enum Teuchos::EVerbosityLevel (*)(const enum Teuchos::EVerbosityLevel, const int)) &Teuchos::incrVerbLevel, "Return an increased or decreased verbosity level.\n\n \n\n           [in] The base verbosity level.\n \n\n\n           [in] The number of levels to increase (>0) or decrease (<0).\n\n See the function implementation for details on what it does!\n\nC++: Teuchos::incrVerbLevel(const enum Teuchos::EVerbosityLevel, const int) --> enum Teuchos::EVerbosityLevel", pybind11::arg("inputVerbLevel"), pybind11::arg("numLevels"));

	{ // Teuchos::GlobalMPISession file:Teuchos_GlobalMPISession.hpp line:81
		pybind11::class_<Teuchos::GlobalMPISession, Teuchos::RCP<Teuchos::GlobalMPISession>> cl(M("Teuchos"), "GlobalMPISession", "you would write:\n \n\n\n\n\n\n\n\n\n\n\n This saves you from needing to remember to call MPI_Init() or\n MPI_Finalize().  Also, having the GlobalMPISession object's constructor\n call MPI_Finalize() allows destructors from other objects to call MPI\n functions.  That wold never be possible if you were to directly call\n MPI_Finalize() at the end of main().\n\n This class even works if you have not built Teuchos with MPI support.  In\n that case, it behaves as if MPI_COMM_WORLD had one process, which is\n always the calling process.  Thus, you can use this class to insulate your\n code from needing to know about MPI.  You don't even have to include\n mpi.h, as long as your code doesn't directly use MPI routines or types.\n Teuchos implements wrappers for MPI communicators (see the Teuchos::Comm\n class and its subclasses in the TeuchosComm subpackage) which allow you to\n use a very very small subset of MPI functionality without needing to\n include mpi.h or depend on MPI in any way.\n\n This class also contains the most minimal of other static member functions\n that are needed for only the most simplistic of tasks needed by other\n TeuchosCore software.  For example, you can do a barrier or sum an int\n across processes.  These are needed by the most basic operations involving\n output or determining success or failure across processes for unit tests.\n\n GlobalMPISession's static functions cleverly checks whether MPI has been\n initialized already before calling any MPI functions.  Therefore, you can\n use it in your libraries without requiring that a GlobalMPISession object\n was created in main().", pybind11::module_local());
		cl.def_static("abort", (void (*)()) &Teuchos::GlobalMPISession::abort, "abort the program\n\n Calls MPI_Abort for HAVE_MPI\n Otherwise calls std::abort\n\nC++: Teuchos::GlobalMPISession::abort() --> void");
		cl.def_static("mpiIsInitialized", (bool (*)()) &Teuchos::GlobalMPISession::mpiIsInitialized, "Return whether MPI was initialized.\n\n This is always true if the constructor returned.  If the\n constructor was not called, it may or may not be true, depending\n on whether the user called MPI_Init() themselves.  If the\n constructor was called but threw an exception, then some MPI\n function returned an error code.\n\nC++: Teuchos::GlobalMPISession::mpiIsInitialized() --> bool");
		cl.def_static("mpiIsFinalized", (bool (*)()) &Teuchos::GlobalMPISession::mpiIsFinalized, "Return whether MPI was already finalized.\n\n This is always true if the destructor was called.  If the\n destructor was not called, it may or may not be true, depending\n on whether the user called MPI_Init() themselves.\n\nC++: Teuchos::GlobalMPISession::mpiIsFinalized() --> bool");
		cl.def_static("getRank", (int (*)()) &Teuchos::GlobalMPISession::getRank, "The rank of the calling process in MPI_COMM_WORLD.\n\n \n 0 if MPI has not yet been initialized, else the\n   rank of the calling process in MPI_COMM_WORLD.\n\n You may call this method even if the constructor was never\n called.  Thus, it is safe to use no matter how MPI_Init() was\n called.  However, MPI_Init() must have been called somehow in\n order for this method to return a sensible result.\n\nC++: Teuchos::GlobalMPISession::getRank() --> int");
		cl.def_static("getNProc", (int (*)()) &Teuchos::GlobalMPISession::getNProc, "The number of processes in MPI_COMM_WORLD.\n\n \n 1 if MPI has not yet been initialized, else the\n   number of processes in MPI_COMM_WORLD.\n\n You may call this method even if the constructor was never\n called.  Thus, it is safe to use no matter how MPI_Init() was\n called.  However, MPI_Init() must have been called somehow in\n order for this method to return a sensible result.\n\nC++: Teuchos::GlobalMPISession::getNProc() --> int");
		cl.def_static("barrier", (void (*)()) &Teuchos::GlobalMPISession::barrier, "Call MPI_Barrier() on MPI_COMM_WORLD.\n\n This method must be called collectively on all processes in\n MPI_COMM_WORLD.\n\n \n Users should invoke barrier through the Teuchos::Comm\n   interface.  We only expose this method for Teuchos-internal\n   functionality.\n\nC++: Teuchos::GlobalMPISession::barrier() --> void");
		cl.def_static("sum", (int (*)(int)) &Teuchos::GlobalMPISession::sum, "Sum a set of integers across processes.\n\n This performs an MPI_Allreduce() of localVal over\n MPI_COMM_WORLD, and returns the result (which is the\n same on all processes).\n\n This method must be called collectively on all processes in\n MPI_COMM_WORLD.\n\n \n [in] Value on local process to sum across processes.\n \n\n The global sum (on all processes).\n\n \n Users should invoke reductions through the Teuchos::Comm\n   interface.  We only expose this method for Teuchos-internal\n   functionality.\n\nC++: Teuchos::GlobalMPISession::sum(int) --> int", pybind11::arg("localVal"));
	}
	{ // Teuchos::basic_oblackholestream file:Teuchos_basic_oblackholestream.hpp line:27
		pybind11::class_<Teuchos::basic_oblackholestream<char,std::char_traits<char>>, Teuchos::RCP<Teuchos::basic_oblackholestream<char,std::char_traits<char>>>, std::ostream> cl(M("Teuchos"), "basic_oblackholestream_char_std_char_traits_char_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::basic_oblackholestream<char,std::char_traits<char>>(); } ) );
	}
}
