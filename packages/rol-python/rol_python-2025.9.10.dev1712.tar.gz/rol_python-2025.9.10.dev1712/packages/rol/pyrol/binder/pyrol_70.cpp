#include <ROL_BoundConstraint.hpp>
#include <ROL_Constraint.hpp>
#include <ROL_Elementwise_Function.hpp>
#include <ROL_Elementwise_Reduce.hpp>
#include <ROL_FletcherObjectiveE.hpp>
#include <ROL_Objective.hpp>
#include <ROL_PolyhedralProjection.hpp>
#include <ROL_Problem.hpp>
#include <ROL_Secant.hpp>
#include <ROL_TypeE_Algorithm.hpp>
#include <ROL_TypeE_FletcherAlgorithm.hpp>
#include <ROL_Types.hpp>
#include <ROL_UpdateType.hpp>
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

// ROL::TypeE::FletcherAlgorithm file:ROL_TypeE_FletcherAlgorithm.hpp line:26
struct PyCallBack_ROL_TypeE_FletcherAlgorithm_double_t : public ROL::TypeE::FletcherAlgorithm<double> {
	using ROL::TypeE::FletcherAlgorithm<double>::FletcherAlgorithm;

	void run(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, class ROL::Objective<double> & a2, class ROL::Constraint<double> & a3, class ROL::Vector<double> & a4, const class ROL::Vector<double> & a5, std::ostream & a6) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeE::FletcherAlgorithm<double> *>(this), "run");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4, a5, a6);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return FletcherAlgorithm::run(a0, a1, a2, a3, a4, a5, a6);
	}
	void writeHeader(std::ostream & a0) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeE::FletcherAlgorithm<double> *>(this), "writeHeader");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return FletcherAlgorithm::writeHeader(a0);
	}
	void writeName(std::ostream & a0) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeE::FletcherAlgorithm<double> *>(this), "writeName");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return FletcherAlgorithm::writeName(a0);
	}
	void writeOutput(std::ostream & a0, const bool a1) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeE::FletcherAlgorithm<double> *>(this), "writeOutput");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return FletcherAlgorithm::writeOutput(a0, a1);
	}
	void run(class ROL::Problem<double> & a0, std::ostream & a1) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeE::FletcherAlgorithm<double> *>(this), "run");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Algorithm::run(a0, a1);
	}
	void run(class ROL::Vector<double> & a0, class ROL::Objective<double> & a1, class ROL::Constraint<double> & a2, class ROL::Vector<double> & a3, std::ostream & a4) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeE::FletcherAlgorithm<double> *>(this), "run");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Algorithm::run(a0, a1, a2, a3, a4);
	}
	void run(class ROL::Vector<double> & a0, class ROL::Objective<double> & a1, class ROL::Constraint<double> & a2, class ROL::Vector<double> & a3, class ROL::Constraint<double> & a4, class ROL::Vector<double> & a5, std::ostream & a6) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeE::FletcherAlgorithm<double> *>(this), "run");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4, a5, a6);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Algorithm::run(a0, a1, a2, a3, a4, a5, a6);
	}
	void run(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, class ROL::Objective<double> & a2, class ROL::Constraint<double> & a3, class ROL::Vector<double> & a4, const class ROL::Vector<double> & a5, class ROL::Constraint<double> & a6, class ROL::Vector<double> & a7, const class ROL::Vector<double> & a8, std::ostream & a9) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeE::FletcherAlgorithm<double> *>(this), "run");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4, a5, a6, a7, a8, a9);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Algorithm::run(a0, a1, a2, a3, a4, a5, a6, a7, a8, a9);
	}
	void writeExitStatus(std::ostream & a0) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeE::FletcherAlgorithm<double> *>(this), "writeExitStatus");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Algorithm::writeExitStatus(a0);
	}
};

void bind_pyrol_70(std::function< pybind11::module &(std::string const &namespace_) > &M)
{
	{ // ROL::TypeE::FletcherAlgorithm file:ROL_TypeE_FletcherAlgorithm.hpp line:26
		pybind11::class_<ROL::TypeE::FletcherAlgorithm<double>, Teuchos::RCP<ROL::TypeE::FletcherAlgorithm<double>>, PyCallBack_ROL_TypeE_FletcherAlgorithm_double_t, ROL::TypeE::Algorithm<double>> cl(M("ROL::TypeE"), "FletcherAlgorithm_double_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](class Teuchos::ParameterList & a0){ return new ROL::TypeE::FletcherAlgorithm<double>(a0); }, [](class Teuchos::ParameterList & a0){ return new PyCallBack_ROL_TypeE_FletcherAlgorithm_double_t(a0); } ), "doc");
		cl.def( pybind11::init<class Teuchos::ParameterList &, const class Teuchos::RCP<class ROL::Secant<double> > &>(), pybind11::arg("list"), pybind11::arg("secant") );

		cl.def( pybind11::init( [](PyCallBack_ROL_TypeE_FletcherAlgorithm_double_t const &o){ return new PyCallBack_ROL_TypeE_FletcherAlgorithm_double_t(o); } ) );
		cl.def( pybind11::init( [](ROL::TypeE::FletcherAlgorithm<double> const &o){ return new ROL::TypeE::FletcherAlgorithm<double>(o); } ) );
		cl.def("run", [](ROL::TypeE::FletcherAlgorithm<double> &o, class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, class ROL::Objective<double> & a2, class ROL::Constraint<double> & a3, class ROL::Vector<double> & a4, const class ROL::Vector<double> & a5, class ROL::Constraint<double> & a6, class ROL::Vector<double> & a7, const class ROL::Vector<double> & a8) -> void { return o.run(a0, a1, a2, a3, a4, a5, a6, a7, a8); }, "", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("obj"), pybind11::arg("econ"), pybind11::arg("emul"), pybind11::arg("eres"), pybind11::arg("linear_econ"), pybind11::arg("linear_emul"), pybind11::arg("linear_eres"));
		cl.def("run", [](ROL::TypeE::FletcherAlgorithm<double> &o, class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, class ROL::Objective<double> & a2, class ROL::Constraint<double> & a3, class ROL::Vector<double> & a4, const class ROL::Vector<double> & a5, class ROL::Constraint<double> & a6, class ROL::Vector<double> & a7, const class ROL::Vector<double> & a8, std::ostream & a9) -> void { return o.run(a0, a1, a2, a3, a4, a5, a6, a7, a8, a9); }, "", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("obj"), pybind11::arg("econ"), pybind11::arg("emul"), pybind11::arg("eres"), pybind11::arg("linear_econ"), pybind11::arg("linear_emul"), pybind11::arg("linear_eres"), pybind11::arg("outStream"));
		cl.def("run", [](ROL::TypeE::FletcherAlgorithm<double> &o, class ROL::Vector<double> & a0, class ROL::Objective<double> & a1, class ROL::Constraint<double> & a2, class ROL::Vector<double> & a3, class ROL::Constraint<double> & a4, class ROL::Vector<double> & a5) -> void { return o.run(a0, a1, a2, a3, a4, a5); }, "", pybind11::arg("x"), pybind11::arg("obj"), pybind11::arg("econ"), pybind11::arg("emul"), pybind11::arg("linear_econ"), pybind11::arg("linear_emul"));
		cl.def("run", [](ROL::TypeE::FletcherAlgorithm<double> &o, class ROL::Vector<double> & a0, class ROL::Objective<double> & a1, class ROL::Constraint<double> & a2, class ROL::Vector<double> & a3, class ROL::Constraint<double> & a4, class ROL::Vector<double> & a5, std::ostream & a6) -> void { return o.run(a0, a1, a2, a3, a4, a5, a6); }, "", pybind11::arg("x"), pybind11::arg("obj"), pybind11::arg("econ"), pybind11::arg("emul"), pybind11::arg("linear_econ"), pybind11::arg("linear_emul"), pybind11::arg("outStream"));
		cl.def("run", [](ROL::TypeE::FletcherAlgorithm<double> &o, class ROL::Vector<double> & a0, class ROL::Objective<double> & a1, class ROL::Constraint<double> & a2, class ROL::Vector<double> & a3) -> void { return o.run(a0, a1, a2, a3); }, "", pybind11::arg("x"), pybind11::arg("obj"), pybind11::arg("econ"), pybind11::arg("emul"));
		cl.def("run", [](ROL::TypeE::FletcherAlgorithm<double> &o, class ROL::Vector<double> & a0, class ROL::Objective<double> & a1, class ROL::Constraint<double> & a2, class ROL::Vector<double> & a3, std::ostream & a4) -> void { return o.run(a0, a1, a2, a3, a4); }, "", pybind11::arg("x"), pybind11::arg("obj"), pybind11::arg("econ"), pybind11::arg("emul"), pybind11::arg("outStream"));
		cl.def("run", [](ROL::TypeE::FletcherAlgorithm<double> &o, class ROL::Problem<double> & a0) -> void { return o.run(a0); }, "", pybind11::arg("problem"));
		cl.def("run", [](ROL::TypeE::FletcherAlgorithm<double> &o, class ROL::Problem<double> & a0, std::ostream & a1) -> void { return o.run(a0, a1); }, "", pybind11::arg("problem"), pybind11::arg("outStream"));
		cl.def("initialize", (void (ROL::TypeE::FletcherAlgorithm<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::FletcherObjectiveE<double> &, class ROL::Constraint<double> &, std::ostream &)) &ROL::TypeE::FletcherAlgorithm<double>::initialize, "C++: ROL::TypeE::FletcherAlgorithm<double>::initialize(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::FletcherObjectiveE<double> &, class ROL::Constraint<double> &, std::ostream &) --> void", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("l"), pybind11::arg("c"), pybind11::arg("fobj"), pybind11::arg("con"), pybind11::arg("outStream"));
		cl.def("run", [](ROL::TypeE::FletcherAlgorithm<double> &o, class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, class ROL::Objective<double> & a2, class ROL::Constraint<double> & a3, class ROL::Vector<double> & a4, const class ROL::Vector<double> & a5) -> void { return o.run(a0, a1, a2, a3, a4, a5); }, "", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("obj"), pybind11::arg("econ"), pybind11::arg("emul"), pybind11::arg("eres"));
		cl.def("run", (void (ROL::TypeE::FletcherAlgorithm<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Constraint<double> &, class ROL::Vector<double> &, const class ROL::Vector<double> &, std::ostream &)) &ROL::TypeE::FletcherAlgorithm<double>::run, "C++: ROL::TypeE::FletcherAlgorithm<double>::run(class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Constraint<double> &, class ROL::Vector<double> &, const class ROL::Vector<double> &, std::ostream &) --> void", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("obj"), pybind11::arg("econ"), pybind11::arg("emul"), pybind11::arg("eres"), pybind11::arg("outStream"));
		cl.def("writeHeader", (void (ROL::TypeE::FletcherAlgorithm<double>::*)(std::ostream &) const) &ROL::TypeE::FletcherAlgorithm<double>::writeHeader, "C++: ROL::TypeE::FletcherAlgorithm<double>::writeHeader(std::ostream &) const --> void", pybind11::arg("os"));
		cl.def("writeName", (void (ROL::TypeE::FletcherAlgorithm<double>::*)(std::ostream &) const) &ROL::TypeE::FletcherAlgorithm<double>::writeName, "C++: ROL::TypeE::FletcherAlgorithm<double>::writeName(std::ostream &) const --> void", pybind11::arg("os"));
		cl.def("writeOutput", [](ROL::TypeE::FletcherAlgorithm<double> const &o, std::ostream & a0) -> void { return o.writeOutput(a0); }, "", pybind11::arg("os"));
		cl.def("writeOutput", (void (ROL::TypeE::FletcherAlgorithm<double>::*)(std::ostream &, const bool) const) &ROL::TypeE::FletcherAlgorithm<double>::writeOutput, "C++: ROL::TypeE::FletcherAlgorithm<double>::writeOutput(std::ostream &, const bool) const --> void", pybind11::arg("os"), pybind11::arg("print_header"));
		cl.def("setStatusTest", [](ROL::TypeE::Algorithm<double> &o, const class Teuchos::RCP<class ROL::StatusTest<double> > & a0) -> void { return o.setStatusTest(a0); }, "", pybind11::arg("status"));
		cl.def("setStatusTest", (void (ROL::TypeE::Algorithm<double>::*)(const class Teuchos::RCP<class ROL::StatusTest<double> > &, bool)) &ROL::TypeE::Algorithm<double>::setStatusTest, "C++: ROL::TypeE::Algorithm<double>::setStatusTest(const class Teuchos::RCP<class ROL::StatusTest<double> > &, bool) --> void", pybind11::arg("status"), pybind11::arg("combineStatus"));
		cl.def("run", [](ROL::TypeE::Algorithm<double> &o, class ROL::Problem<double> & a0) -> void { return o.run(a0); }, "", pybind11::arg("problem"));
		cl.def("run", (void (ROL::TypeE::Algorithm<double>::*)(class ROL::Problem<double> &, std::ostream &)) &ROL::TypeE::Algorithm<double>::run, "C++: ROL::TypeE::Algorithm<double>::run(class ROL::Problem<double> &, std::ostream &) --> void", pybind11::arg("problem"), pybind11::arg("outStream"));
		cl.def("run", [](ROL::TypeE::Algorithm<double> &o, class ROL::Vector<double> & a0, class ROL::Objective<double> & a1, class ROL::Constraint<double> & a2, class ROL::Vector<double> & a3) -> void { return o.run(a0, a1, a2, a3); }, "", pybind11::arg("x"), pybind11::arg("obj"), pybind11::arg("econ"), pybind11::arg("emul"));
		cl.def("run", (void (ROL::TypeE::Algorithm<double>::*)(class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Constraint<double> &, class ROL::Vector<double> &, std::ostream &)) &ROL::TypeE::Algorithm<double>::run, "C++: ROL::TypeE::Algorithm<double>::run(class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Constraint<double> &, class ROL::Vector<double> &, std::ostream &) --> void", pybind11::arg("x"), pybind11::arg("obj"), pybind11::arg("econ"), pybind11::arg("emul"), pybind11::arg("outStream"));
		cl.def("run", [](ROL::TypeE::Algorithm<double> &o, class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, class ROL::Objective<double> & a2, class ROL::Constraint<double> & a3, class ROL::Vector<double> & a4, const class ROL::Vector<double> & a5) -> void { return o.run(a0, a1, a2, a3, a4, a5); }, "", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("obj"), pybind11::arg("econ"), pybind11::arg("emul"), pybind11::arg("eres"));
		cl.def("run", (void (ROL::TypeE::Algorithm<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Constraint<double> &, class ROL::Vector<double> &, const class ROL::Vector<double> &, std::ostream &)) &ROL::TypeE::Algorithm<double>::run, "C++: ROL::TypeE::Algorithm<double>::run(class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Constraint<double> &, class ROL::Vector<double> &, const class ROL::Vector<double> &, std::ostream &) --> void", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("obj"), pybind11::arg("econ"), pybind11::arg("emul"), pybind11::arg("eres"), pybind11::arg("outStream"));
		cl.def("run", [](ROL::TypeE::Algorithm<double> &o, class ROL::Vector<double> & a0, class ROL::Objective<double> & a1, class ROL::Constraint<double> & a2, class ROL::Vector<double> & a3, class ROL::Constraint<double> & a4, class ROL::Vector<double> & a5) -> void { return o.run(a0, a1, a2, a3, a4, a5); }, "", pybind11::arg("x"), pybind11::arg("obj"), pybind11::arg("econ"), pybind11::arg("emul"), pybind11::arg("linear_econ"), pybind11::arg("linear_emul"));
		cl.def("run", (void (ROL::TypeE::Algorithm<double>::*)(class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Constraint<double> &, class ROL::Vector<double> &, class ROL::Constraint<double> &, class ROL::Vector<double> &, std::ostream &)) &ROL::TypeE::Algorithm<double>::run, "C++: ROL::TypeE::Algorithm<double>::run(class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Constraint<double> &, class ROL::Vector<double> &, class ROL::Constraint<double> &, class ROL::Vector<double> &, std::ostream &) --> void", pybind11::arg("x"), pybind11::arg("obj"), pybind11::arg("econ"), pybind11::arg("emul"), pybind11::arg("linear_econ"), pybind11::arg("linear_emul"), pybind11::arg("outStream"));
		cl.def("run", [](ROL::TypeE::Algorithm<double> &o, class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, class ROL::Objective<double> & a2, class ROL::Constraint<double> & a3, class ROL::Vector<double> & a4, const class ROL::Vector<double> & a5, class ROL::Constraint<double> & a6, class ROL::Vector<double> & a7, const class ROL::Vector<double> & a8) -> void { return o.run(a0, a1, a2, a3, a4, a5, a6, a7, a8); }, "", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("obj"), pybind11::arg("econ"), pybind11::arg("emul"), pybind11::arg("eres"), pybind11::arg("linear_econ"), pybind11::arg("linear_emul"), pybind11::arg("linear_eres"));
		cl.def("run", (void (ROL::TypeE::Algorithm<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Constraint<double> &, class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Constraint<double> &, class ROL::Vector<double> &, const class ROL::Vector<double> &, std::ostream &)) &ROL::TypeE::Algorithm<double>::run, "C++: ROL::TypeE::Algorithm<double>::run(class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Constraint<double> &, class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Constraint<double> &, class ROL::Vector<double> &, const class ROL::Vector<double> &, std::ostream &) --> void", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("obj"), pybind11::arg("econ"), pybind11::arg("emul"), pybind11::arg("eres"), pybind11::arg("linear_econ"), pybind11::arg("linear_emul"), pybind11::arg("linear_eres"), pybind11::arg("outStream"));
		cl.def("writeHeader", (void (ROL::TypeE::Algorithm<double>::*)(std::ostream &) const) &ROL::TypeE::Algorithm<double>::writeHeader, "C++: ROL::TypeE::Algorithm<double>::writeHeader(std::ostream &) const --> void", pybind11::arg("os"));
		cl.def("writeName", (void (ROL::TypeE::Algorithm<double>::*)(std::ostream &) const) &ROL::TypeE::Algorithm<double>::writeName, "C++: ROL::TypeE::Algorithm<double>::writeName(std::ostream &) const --> void", pybind11::arg("os"));
		cl.def("writeOutput", [](ROL::TypeE::Algorithm<double> const &o, std::ostream & a0) -> void { return o.writeOutput(a0); }, "", pybind11::arg("os"));
		cl.def("writeOutput", (void (ROL::TypeE::Algorithm<double>::*)(std::ostream &, const bool) const) &ROL::TypeE::Algorithm<double>::writeOutput, "C++: ROL::TypeE::Algorithm<double>::writeOutput(std::ostream &, const bool) const --> void", pybind11::arg("os"), pybind11::arg("write_header"));
		cl.def("writeExitStatus", (void (ROL::TypeE::Algorithm<double>::*)(std::ostream &) const) &ROL::TypeE::Algorithm<double>::writeExitStatus, "C++: ROL::TypeE::Algorithm<double>::writeExitStatus(std::ostream &) const --> void", pybind11::arg("os"));
		cl.def("getState", (class Teuchos::RCP<const struct ROL::TypeE::AlgorithmState<double> > (ROL::TypeE::Algorithm<double>::*)() const) &ROL::TypeE::Algorithm<double>::getState, "C++: ROL::TypeE::Algorithm<double>::getState() const --> class Teuchos::RCP<const struct ROL::TypeE::AlgorithmState<double> >");
		cl.def("reset", (void (ROL::TypeE::Algorithm<double>::*)()) &ROL::TypeE::Algorithm<double>::reset, "C++: ROL::TypeE::Algorithm<double>::reset() --> void");
	}
}
