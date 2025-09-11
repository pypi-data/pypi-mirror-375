#include <ROL_BatchManager.hpp>
#include <ROL_Elementwise_Function.hpp>
#include <ROL_Elementwise_Reduce.hpp>
#include <ROL_OED_Factors.hpp>
#include <ROL_OED_Factory.hpp>
#include <ROL_OED_MomentOperator.hpp>
#include <ROL_Vector.hpp>
#include <Teuchos_ENull.hpp>
#include <Teuchos_FilteredIterator.hpp>
#include <Teuchos_ParameterEntry.hpp>
#include <Teuchos_ParameterList.hpp>
#include <Teuchos_ParameterListModifier.hpp>
#include <Teuchos_RCPDecl.hpp>
#include <Teuchos_RCPNode.hpp>
#include <Teuchos_StringIndexedOrderedValueObjectContainer.hpp>
#include <deque>
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

void bind_pyrol_77(std::function< pybind11::module &(std::string const &namespace_) > &M)
{
	{ // ROL::OED::Factory file: line:77
		pybind11::class_<ROL::OED::Factory<double>, Teuchos::RCP<ROL::OED::Factory<double>>> cl(M("ROL::OED"), "Factory_double_t", "", pybind11::module_local());
		cl.def( pybind11::init<const class Teuchos::RCP<class ROL::Objective<double> > &, const class Teuchos::RCP<class ROL::SampleGenerator<double> > &, const class Teuchos::RCP<class ROL::Vector<double> > &, const class Teuchos::RCP<class ROL::OED::MomentOperator<double> > &, class Teuchos::ParameterList &>(), pybind11::arg("model"), pybind11::arg("sampler"), pybind11::arg("theta"), pybind11::arg("cov"), pybind11::arg("list") );

		cl.def( pybind11::init<const class Teuchos::RCP<class ROL::Constraint<double> > &, const class Teuchos::RCP<class ROL::SampleGenerator<double> > &, const class Teuchos::RCP<class ROL::Vector<double> > &, const class Teuchos::RCP<class ROL::Vector<double> > &, const class Teuchos::RCP<class ROL::OED::MomentOperator<double> > &, class Teuchos::ParameterList &>(), pybind11::arg("model"), pybind11::arg("sampler"), pybind11::arg("theta"), pybind11::arg("obs"), pybind11::arg("cov"), pybind11::arg("list") );

		cl.def( pybind11::init( [](ROL::OED::Factory<double> const &o){ return new ROL::OED::Factory<double>(o); } ) );
		cl.def("setBudgetConstraint", (void (ROL::OED::Factory<double>::*)(const class Teuchos::RCP<class ROL::Vector<double> > &, double)) &ROL::OED::Factory<double>::setBudgetConstraint, "C++: ROL::OED::Factory<double>::setBudgetConstraint(const class Teuchos::RCP<class ROL::Vector<double> > &, double) --> void", pybind11::arg("cost"), pybind11::arg("budget"));
		cl.def("get", (class Teuchos::RCP<class ROL::Problem<double> > (ROL::OED::Factory<double>::*)(const class Teuchos::RCP<class ROL::Vector<double> > &)) &ROL::OED::Factory<double>::get, "C++: ROL::OED::Factory<double>::get(const class Teuchos::RCP<class ROL::Vector<double> > &) --> class Teuchos::RCP<class ROL::Problem<double> >", pybind11::arg("c"));
		cl.def("get", [](ROL::OED::Factory<double> &o, class Teuchos::ParameterList & a0) -> Teuchos::RCP<class ROL::Problem<double> > { return o.get(a0); }, "", pybind11::arg("list"));
		cl.def("get", [](ROL::OED::Factory<double> &o, class Teuchos::ParameterList & a0, const class Teuchos::RCP<class ROL::SampleGenerator<double> > & a1) -> Teuchos::RCP<class ROL::Problem<double> > { return o.get(a0, a1); }, "", pybind11::arg("list"), pybind11::arg("sampler"));
		cl.def("get", (class Teuchos::RCP<class ROL::Problem<double> > (ROL::OED::Factory<double>::*)(class Teuchos::ParameterList &, const class Teuchos::RCP<class ROL::SampleGenerator<double> > &, const class Teuchos::RCP<class ROL::Objective<double> > &)) &ROL::OED::Factory<double>::get, "C++: ROL::OED::Factory<double>::get(class Teuchos::ParameterList &, const class Teuchos::RCP<class ROL::SampleGenerator<double> > &, const class Teuchos::RCP<class ROL::Objective<double> > &) --> class Teuchos::RCP<class ROL::Problem<double> >", pybind11::arg("list"), pybind11::arg("sampler"), pybind11::arg("predFun"));
		cl.def("check", [](ROL::OED::Factory<double> const &o) -> void { return o.check(); }, "");
		cl.def("check", (void (ROL::OED::Factory<double>::*)(std::ostream &) const) &ROL::OED::Factory<double>::check, "C++: ROL::OED::Factory<double>::check(std::ostream &) const --> void", pybind11::arg("stream"));
		cl.def("setDesign", (void (ROL::OED::Factory<double>::*)(double)) &ROL::OED::Factory<double>::setDesign, "C++: ROL::OED::Factory<double>::setDesign(double) --> void", pybind11::arg("val"));
		cl.def("setDesign", (void (ROL::OED::Factory<double>::*)(const class ROL::Vector<double> &)) &ROL::OED::Factory<double>::setDesign, "C++: ROL::OED::Factory<double>::setDesign(const class ROL::Vector<double> &) --> void", pybind11::arg("p"));
		cl.def("loadDesign", (int (ROL::OED::Factory<double>::*)(const std::string &, int, int)) &ROL::OED::Factory<double>::loadDesign, "C++: ROL::OED::Factory<double>::loadDesign(const std::string &, int, int) --> int", pybind11::arg("file"), pybind11::arg("dim"), pybind11::arg("n"));
		cl.def("getDesign", (const class Teuchos::RCP<const class ROL::Vector<double> > (ROL::OED::Factory<double>::*)() const) &ROL::OED::Factory<double>::getDesign, "C++: ROL::OED::Factory<double>::getDesign() const --> const class Teuchos::RCP<const class ROL::Vector<double> >");
		cl.def("getFactors", (const class Teuchos::RCP<class ROL::OED::Factors<double> > (ROL::OED::Factory<double>::*)() const) &ROL::OED::Factory<double>::getFactors, "C++: ROL::OED::Factory<double>::getFactors() const --> const class Teuchos::RCP<class ROL::OED::Factors<double> >");
		cl.def("printDesign", [](ROL::OED::Factory<double> const &o, const std::string & a0) -> void { return o.printDesign(a0); }, "", pybind11::arg("name"));
		cl.def("printDesign", (void (ROL::OED::Factory<double>::*)(const std::string &, const std::string &) const) &ROL::OED::Factory<double>::printDesign, "C++: ROL::OED::Factory<double>::printDesign(const std::string &, const std::string &) const --> void", pybind11::arg("name"), pybind11::arg("ext"));
		cl.def("printPredictionVariance", [](ROL::OED::Factory<double> const &o, const class Teuchos::RCP<class ROL::SampleGenerator<double> > & a0, const std::string & a1) -> void { return o.printPredictionVariance(a0, a1); }, "", pybind11::arg("sampler"), pybind11::arg("name"));
		cl.def("printPredictionVariance", (void (ROL::OED::Factory<double>::*)(const class Teuchos::RCP<class ROL::SampleGenerator<double> > &, const std::string &, const std::string &) const) &ROL::OED::Factory<double>::printPredictionVariance, "C++: ROL::OED::Factory<double>::printPredictionVariance(const class Teuchos::RCP<class ROL::SampleGenerator<double> > &, const std::string &, const std::string &) const --> void", pybind11::arg("sampler"), pybind11::arg("name"), pybind11::arg("ext"));
		cl.def("profile", [](ROL::OED::Factory<double> const &o, std::ostream & a0) -> void { return o.profile(a0); }, "", pybind11::arg("stream"));
		cl.def("profile", (void (ROL::OED::Factory<double>::*)(std::ostream &, const class Teuchos::RCP<class ROL::BatchManager<double> > &) const) &ROL::OED::Factory<double>::profile, "C++: ROL::OED::Factory<double>::profile(std::ostream &, const class Teuchos::RCP<class ROL::BatchManager<double> > &) const --> void", pybind11::arg("stream"), pybind11::arg("bman"));
		cl.def("reset", (void (ROL::OED::Factory<double>::*)()) &ROL::OED::Factory<double>::reset, "C++: ROL::OED::Factory<double>::reset() --> void");
	}
}
