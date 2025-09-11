#include <ROL_Elementwise_Function.hpp>
#include <ROL_Elementwise_Reduce.hpp>
#include <ROL_LinearOperator.hpp>
#include <ROL_MINRES.hpp>
#include <ROL_Vector.hpp>
#include <ROL_VectorClone.hpp>
#include <Teuchos_ENull.hpp>
#include <Teuchos_RCPDecl.hpp>
#include <Teuchos_RCPNode.hpp>
#include <ios>
#include <iterator>
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

// ROL::details::MINRES file:ROL_MINRES.hpp line:29
struct PyCallBack_ROL_details_MINRES_double_t : public ROL::details::MINRES<double> {
	using ROL::details::MINRES<double>::MINRES;

	double run(class ROL::Vector<double> & a0, class ROL::LinearOperator<double> & a1, const class ROL::Vector<double> & a2, class ROL::LinearOperator<double> & a3, int & a4, int & a5) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::details::MINRES<double> *>(this), "run");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4, a5);
			if (pybind11::detail::cast_is_temporary_value_reference<double>::value) {
				static pybind11::detail::override_caster_t<double> caster;
				return pybind11::detail::cast_ref<double>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<double>(std::move(o));
		}
		return MINRES::run(a0, a1, a2, a3, a4, a5);
	}
};

void bind_pyrol_22(std::function< pybind11::module &(std::string const &namespace_) > &M)
{
	{ // ROL::details::VectorClone file:ROL_VectorClone.hpp line:34
		pybind11::class_<ROL::details::VectorClone<double>, Teuchos::RCP<ROL::details::VectorClone<double>>> cl(M("ROL::details"), "VectorClone_double_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new ROL::details::VectorClone<double>(); } ) );
		cl.def( pybind11::init( [](ROL::details::VectorClone<double> const &o){ return new ROL::details::VectorClone<double>(o); } ) );
		cl.def("__call__", (class Teuchos::RCP<class ROL::Vector<double> > (ROL::details::VectorClone<double>::*)(const class ROL::Vector<double> &)) &ROL::details::VectorClone<double>::operator(), "C++: ROL::details::VectorClone<double>::operator()(const class ROL::Vector<double> &) --> class Teuchos::RCP<class ROL::Vector<double> >", pybind11::arg("x"));
		cl.def("__call__", (class Teuchos::RCP<class ROL::Vector<double> > (ROL::details::VectorClone<double>::*)(const class Teuchos::RCP<const class ROL::Vector<double> > &)) &ROL::details::VectorClone<double>::operator(), "C++: ROL::details::VectorClone<double>::operator()(const class Teuchos::RCP<const class ROL::Vector<double> > &) --> class Teuchos::RCP<class ROL::Vector<double> >", pybind11::arg("x"));
		cl.def("assign", (class ROL::details::VectorClone<double> & (ROL::details::VectorClone<double>::*)(const class ROL::details::VectorClone<double> &)) &ROL::details::VectorClone<double>::operator=, "C++: ROL::details::VectorClone<double>::operator=(const class ROL::details::VectorClone<double> &) --> class ROL::details::VectorClone<double> &", pybind11::return_value_policy::automatic, pybind11::arg(""));
	}
	{ // ROL::details::VectorCloneMap file:ROL_VectorClone.hpp line:83
		pybind11::class_<ROL::details::VectorCloneMap<double,const char *>, Teuchos::RCP<ROL::details::VectorCloneMap<double,const char *>>> cl(M("ROL::details"), "VectorCloneMap_double_const_char__star__t", "", pybind11::module_local());
		cl.def( pybind11::init( [](ROL::details::VectorCloneMap<double,const char *> const &o){ return new ROL::details::VectorCloneMap<double,const char *>(o); } ) );
		cl.def("__call__", (class Teuchos::RCP<class ROL::Vector<double> > (ROL::details::VectorCloneMap<double,const char *>::*)(const class ROL::Vector<double> &, const char *)) &ROL::details::VectorCloneMap<double>::operator(), "C++: ROL::details::VectorCloneMap<double>::operator()(const class ROL::Vector<double> &, const char *) --> class Teuchos::RCP<class ROL::Vector<double> >", pybind11::arg("x"), pybind11::arg("key"));
		cl.def("__call__", (class Teuchos::RCP<class ROL::Vector<double> > (ROL::details::VectorCloneMap<double,const char *>::*)(const class Teuchos::RCP<const class ROL::Vector<double> > &, const char *)) &ROL::details::VectorCloneMap<double>::operator(), "C++: ROL::details::VectorCloneMap<double>::operator()(const class Teuchos::RCP<const class ROL::Vector<double> > &, const char *) --> class Teuchos::RCP<class ROL::Vector<double> >", pybind11::arg("x"), pybind11::arg("key"));
		cl.def("assign", (class ROL::details::VectorCloneMap<double> & (ROL::details::VectorCloneMap<double,const char *>::*)(const class ROL::details::VectorCloneMap<double> &)) &ROL::details::VectorCloneMap<double>::operator=, "C++: ROL::details::VectorCloneMap<double>::operator=(const class ROL::details::VectorCloneMap<double> &) --> class ROL::details::VectorCloneMap<double> &", pybind11::return_value_policy::automatic, pybind11::arg(""));
	}
	{ // ROL::details::MINRES file:ROL_MINRES.hpp line:29
		pybind11::class_<ROL::details::MINRES<double>, Teuchos::RCP<ROL::details::MINRES<double>>, PyCallBack_ROL_details_MINRES_double_t, ROL::Krylov<double>> cl(M("ROL::details"), "MINRES_double_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new ROL::details::MINRES<double>(); }, [](){ return new PyCallBack_ROL_details_MINRES_double_t(); } ), "doc");
		cl.def( pybind11::init( [](double const & a0){ return new ROL::details::MINRES<double>(a0); }, [](double const & a0){ return new PyCallBack_ROL_details_MINRES_double_t(a0); } ), "doc");
		cl.def( pybind11::init( [](double const & a0, double const & a1){ return new ROL::details::MINRES<double>(a0, a1); }, [](double const & a0, double const & a1){ return new PyCallBack_ROL_details_MINRES_double_t(a0, a1); } ), "doc");
		cl.def( pybind11::init( [](double const & a0, double const & a1, unsigned int const & a2){ return new ROL::details::MINRES<double>(a0, a1, a2); }, [](double const & a0, double const & a1, unsigned int const & a2){ return new PyCallBack_ROL_details_MINRES_double_t(a0, a1, a2); } ), "doc");
		cl.def( pybind11::init<double, double, unsigned int, bool>(), pybind11::arg("absTol"), pybind11::arg("relTol"), pybind11::arg("maxit"), pybind11::arg("useInexact") );

		cl.def( pybind11::init( [](PyCallBack_ROL_details_MINRES_double_t const &o){ return new PyCallBack_ROL_details_MINRES_double_t(o); } ) );
		cl.def( pybind11::init( [](ROL::details::MINRES<double> const &o){ return new ROL::details::MINRES<double>(o); } ) );
		cl.def("run", (double (ROL::details::MINRES<double>::*)(class ROL::Vector<double> &, class ROL::LinearOperator<double> &, const class ROL::Vector<double> &, class ROL::LinearOperator<double> &, int &, int &)) &ROL::details::MINRES<double>::run, "C++: ROL::details::MINRES<double>::run(class ROL::Vector<double> &, class ROL::LinearOperator<double> &, const class ROL::Vector<double> &, class ROL::LinearOperator<double> &, int &, int &) --> double", pybind11::arg("x"), pybind11::arg("A"), pybind11::arg("b"), pybind11::arg("M"), pybind11::arg("iter"), pybind11::arg("flag"));
		cl.def("assign", (class ROL::details::MINRES<double> & (ROL::details::MINRES<double>::*)(const class ROL::details::MINRES<double> &)) &ROL::details::MINRES<double>::operator=, "C++: ROL::details::MINRES<double>::operator=(const class ROL::details::MINRES<double> &) --> class ROL::details::MINRES<double> &", pybind11::return_value_policy::automatic, pybind11::arg(""));
		cl.def("run", (double (ROL::Krylov<double>::*)(class ROL::Vector<double> &, class ROL::LinearOperator<double> &, const class ROL::Vector<double> &, class ROL::LinearOperator<double> &, int &, int &)) &ROL::Krylov<double>::run, "C++: ROL::Krylov<double>::run(class ROL::Vector<double> &, class ROL::LinearOperator<double> &, const class ROL::Vector<double> &, class ROL::LinearOperator<double> &, int &, int &) --> double", pybind11::arg("x"), pybind11::arg("A"), pybind11::arg("b"), pybind11::arg("M"), pybind11::arg("iter"), pybind11::arg("flag"));
		cl.def("resetAbsoluteTolerance", (void (ROL::Krylov<double>::*)(const double)) &ROL::Krylov<double>::resetAbsoluteTolerance, "C++: ROL::Krylov<double>::resetAbsoluteTolerance(const double) --> void", pybind11::arg("absTol"));
		cl.def("resetRelativeTolerance", (void (ROL::Krylov<double>::*)(const double)) &ROL::Krylov<double>::resetRelativeTolerance, "C++: ROL::Krylov<double>::resetRelativeTolerance(const double) --> void", pybind11::arg("relTol"));
		cl.def("resetMaximumIteration", (void (ROL::Krylov<double>::*)(const unsigned int)) &ROL::Krylov<double>::resetMaximumIteration, "C++: ROL::Krylov<double>::resetMaximumIteration(const unsigned int) --> void", pybind11::arg("maxit"));
		cl.def("getAbsoluteTolerance", (double (ROL::Krylov<double>::*)() const) &ROL::Krylov<double>::getAbsoluteTolerance, "C++: ROL::Krylov<double>::getAbsoluteTolerance() const --> double");
		cl.def("getRelativeTolerance", (double (ROL::Krylov<double>::*)() const) &ROL::Krylov<double>::getRelativeTolerance, "C++: ROL::Krylov<double>::getRelativeTolerance() const --> double");
		cl.def("getMaximumIteration", (unsigned int (ROL::Krylov<double>::*)() const) &ROL::Krylov<double>::getMaximumIteration, "C++: ROL::Krylov<double>::getMaximumIteration() const --> unsigned int");
		cl.def("assign", (class ROL::Krylov<double> & (ROL::Krylov<double>::*)(const class ROL::Krylov<double> &)) &ROL::Krylov<double>::operator=, "C++: ROL::Krylov<double>::operator=(const class ROL::Krylov<double> &) --> class ROL::Krylov<double> &", pybind11::return_value_policy::automatic, pybind11::arg(""));
	}
}
