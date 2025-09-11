#include <ROL_BoundConstraint.hpp>
#include <ROL_Constraint.hpp>
#include <ROL_DescentDirection_U.hpp>
#include <ROL_Elementwise_Function.hpp>
#include <ROL_Elementwise_Reduce.hpp>
#include <ROL_LineSearch_U.hpp>
#include <ROL_Objective.hpp>
#include <ROL_PolyhedralProjection.hpp>
#include <ROL_Problem.hpp>
#include <ROL_Secant.hpp>
#include <ROL_TypeU_Algorithm.hpp>
#include <ROL_TypeU_LineSearchAlgorithm.hpp>
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

// ROL::TypeU::LineSearchAlgorithm file:ROL_TypeU_LineSearchAlgorithm.hpp line:67
struct PyCallBack_ROL_TypeU_LineSearchAlgorithm_double_t : public ROL::TypeU::LineSearchAlgorithm<double> {
	using ROL::TypeU::LineSearchAlgorithm<double>::LineSearchAlgorithm;

	void run(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, class ROL::Objective<double> & a2, std::ostream & a3) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeU::LineSearchAlgorithm<double> *>(this), "run");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return LineSearchAlgorithm::run(a0, a1, a2, a3);
	}
	void writeHeader(std::ostream & a0) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeU::LineSearchAlgorithm<double> *>(this), "writeHeader");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return LineSearchAlgorithm::writeHeader(a0);
	}
	void writeName(std::ostream & a0) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeU::LineSearchAlgorithm<double> *>(this), "writeName");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return LineSearchAlgorithm::writeName(a0);
	}
	void writeOutput(std::ostream & a0, const bool a1) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeU::LineSearchAlgorithm<double> *>(this), "writeOutput");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return LineSearchAlgorithm::writeOutput(a0, a1);
	}
	void run(class ROL::Problem<double> & a0, std::ostream & a1) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeU::LineSearchAlgorithm<double> *>(this), "run");
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
	void run(class ROL::Vector<double> & a0, class ROL::Objective<double> & a1, std::ostream & a2) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeU::LineSearchAlgorithm<double> *>(this), "run");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Algorithm::run(a0, a1, a2);
	}
	void run(class ROL::Vector<double> & a0, class ROL::Objective<double> & a1, class ROL::Constraint<double> & a2, class ROL::Vector<double> & a3, std::ostream & a4) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeU::LineSearchAlgorithm<double> *>(this), "run");
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
	void run(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, class ROL::Objective<double> & a2, class ROL::Constraint<double> & a3, class ROL::Vector<double> & a4, const class ROL::Vector<double> & a5, std::ostream & a6) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeU::LineSearchAlgorithm<double> *>(this), "run");
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
	void writeExitStatus(std::ostream & a0) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeU::LineSearchAlgorithm<double> *>(this), "writeExitStatus");
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

void bind_pyrol_35(std::function< pybind11::module &(std::string const &namespace_) > &M)
{
	{ // ROL::TypeU::LineSearchAlgorithm file:ROL_TypeU_LineSearchAlgorithm.hpp line:67
		pybind11::class_<ROL::TypeU::LineSearchAlgorithm<double>, Teuchos::RCP<ROL::TypeU::LineSearchAlgorithm<double>>, PyCallBack_ROL_TypeU_LineSearchAlgorithm_double_t, ROL::TypeU::Algorithm<double>> cl(M("ROL::TypeU"), "LineSearchAlgorithm_double_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](class Teuchos::ParameterList & a0){ return new ROL::TypeU::LineSearchAlgorithm<double>(a0); }, [](class Teuchos::ParameterList & a0){ return new PyCallBack_ROL_TypeU_LineSearchAlgorithm_double_t(a0); } ), "doc");
		cl.def( pybind11::init( [](class Teuchos::ParameterList & a0, const class Teuchos::RCP<class ROL::Secant<double> > & a1){ return new ROL::TypeU::LineSearchAlgorithm<double>(a0, a1); }, [](class Teuchos::ParameterList & a0, const class Teuchos::RCP<class ROL::Secant<double> > & a1){ return new PyCallBack_ROL_TypeU_LineSearchAlgorithm_double_t(a0, a1); } ), "doc");
		cl.def( pybind11::init( [](class Teuchos::ParameterList & a0, const class Teuchos::RCP<class ROL::Secant<double> > & a1, const class Teuchos::RCP<class ROL::DescentDirection_U<double> > & a2){ return new ROL::TypeU::LineSearchAlgorithm<double>(a0, a1, a2); }, [](class Teuchos::ParameterList & a0, const class Teuchos::RCP<class ROL::Secant<double> > & a1, const class Teuchos::RCP<class ROL::DescentDirection_U<double> > & a2){ return new PyCallBack_ROL_TypeU_LineSearchAlgorithm_double_t(a0, a1, a2); } ), "doc");
		cl.def( pybind11::init<class Teuchos::ParameterList &, const class Teuchos::RCP<class ROL::Secant<double> > &, const class Teuchos::RCP<class ROL::DescentDirection_U<double> > &, const class Teuchos::RCP<class ROL::LineSearch_U<double> > &>(), pybind11::arg("parlist"), pybind11::arg("secant"), pybind11::arg("descent"), pybind11::arg("lineSearch") );

		cl.def( pybind11::init( [](PyCallBack_ROL_TypeU_LineSearchAlgorithm_double_t const &o){ return new PyCallBack_ROL_TypeU_LineSearchAlgorithm_double_t(o); } ) );
		cl.def( pybind11::init( [](ROL::TypeU::LineSearchAlgorithm<double> const &o){ return new ROL::TypeU::LineSearchAlgorithm<double>(o); } ) );
		cl.def("run", [](ROL::TypeU::LineSearchAlgorithm<double> &o, class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, class ROL::Objective<double> & a2, class ROL::Constraint<double> & a3, class ROL::Vector<double> & a4, const class ROL::Vector<double> & a5) -> void { return o.run(a0, a1, a2, a3, a4, a5); }, "", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("obj"), pybind11::arg("linear_con"), pybind11::arg("linear_mul"), pybind11::arg("linear_c"));
		cl.def("run", [](ROL::TypeU::LineSearchAlgorithm<double> &o, class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, class ROL::Objective<double> & a2, class ROL::Constraint<double> & a3, class ROL::Vector<double> & a4, const class ROL::Vector<double> & a5, std::ostream & a6) -> void { return o.run(a0, a1, a2, a3, a4, a5, a6); }, "", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("obj"), pybind11::arg("linear_con"), pybind11::arg("linear_mul"), pybind11::arg("linear_c"), pybind11::arg("outStream"));
		cl.def("run", [](ROL::TypeU::LineSearchAlgorithm<double> &o, class ROL::Vector<double> & a0, class ROL::Objective<double> & a1, class ROL::Constraint<double> & a2, class ROL::Vector<double> & a3) -> void { return o.run(a0, a1, a2, a3); }, "", pybind11::arg("x"), pybind11::arg("obj"), pybind11::arg("linear_con"), pybind11::arg("linear_mul"));
		cl.def("run", [](ROL::TypeU::LineSearchAlgorithm<double> &o, class ROL::Vector<double> & a0, class ROL::Objective<double> & a1, class ROL::Constraint<double> & a2, class ROL::Vector<double> & a3, std::ostream & a4) -> void { return o.run(a0, a1, a2, a3, a4); }, "", pybind11::arg("x"), pybind11::arg("obj"), pybind11::arg("linear_con"), pybind11::arg("linear_mul"), pybind11::arg("outStream"));
		cl.def("run", [](ROL::TypeU::LineSearchAlgorithm<double> &o, class ROL::Vector<double> & a0, class ROL::Objective<double> & a1) -> void { return o.run(a0, a1); }, "", pybind11::arg("x"), pybind11::arg("obj"));
		cl.def("run", [](ROL::TypeU::LineSearchAlgorithm<double> &o, class ROL::Vector<double> & a0, class ROL::Objective<double> & a1, std::ostream & a2) -> void { return o.run(a0, a1, a2); }, "", pybind11::arg("x"), pybind11::arg("obj"), pybind11::arg("outStream"));
		cl.def("run", [](ROL::TypeU::LineSearchAlgorithm<double> &o, class ROL::Problem<double> & a0) -> void { return o.run(a0); }, "", pybind11::arg("problem"));
		cl.def("run", [](ROL::TypeU::LineSearchAlgorithm<double> &o, class ROL::Problem<double> & a0, std::ostream & a1) -> void { return o.run(a0, a1); }, "", pybind11::arg("problem"), pybind11::arg("outStream"));
		cl.def("initialize", [](ROL::TypeU::LineSearchAlgorithm<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, class ROL::Objective<double> & a2) -> void { return o.initialize(a0, a1, a2); }, "", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("obj"));
		cl.def("initialize", (void (ROL::TypeU::LineSearchAlgorithm<double>::*)(const class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &, std::ostream &)) &ROL::TypeU::LineSearchAlgorithm<double>::initialize, "C++: ROL::TypeU::LineSearchAlgorithm<double>::initialize(const class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &, std::ostream &) --> void", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("obj"), pybind11::arg("outStream"));
		cl.def("run", [](ROL::TypeU::LineSearchAlgorithm<double> &o, class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, class ROL::Objective<double> & a2) -> void { return o.run(a0, a1, a2); }, "", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("obj"));
		cl.def("run", (void (ROL::TypeU::LineSearchAlgorithm<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &, std::ostream &)) &ROL::TypeU::LineSearchAlgorithm<double>::run, "C++: ROL::TypeU::LineSearchAlgorithm<double>::run(class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &, std::ostream &) --> void", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("obj"), pybind11::arg("outStream"));
		cl.def("writeHeader", (void (ROL::TypeU::LineSearchAlgorithm<double>::*)(std::ostream &) const) &ROL::TypeU::LineSearchAlgorithm<double>::writeHeader, "C++: ROL::TypeU::LineSearchAlgorithm<double>::writeHeader(std::ostream &) const --> void", pybind11::arg("os"));
		cl.def("writeName", (void (ROL::TypeU::LineSearchAlgorithm<double>::*)(std::ostream &) const) &ROL::TypeU::LineSearchAlgorithm<double>::writeName, "C++: ROL::TypeU::LineSearchAlgorithm<double>::writeName(std::ostream &) const --> void", pybind11::arg("os"));
		cl.def("writeOutput", [](ROL::TypeU::LineSearchAlgorithm<double> const &o, std::ostream & a0) -> void { return o.writeOutput(a0); }, "", pybind11::arg("os"));
		cl.def("writeOutput", (void (ROL::TypeU::LineSearchAlgorithm<double>::*)(std::ostream &, const bool) const) &ROL::TypeU::LineSearchAlgorithm<double>::writeOutput, "C++: ROL::TypeU::LineSearchAlgorithm<double>::writeOutput(std::ostream &, const bool) const --> void", pybind11::arg("os"), pybind11::arg("print_header"));
		cl.def("setStatusTest", [](ROL::TypeU::Algorithm<double> &o, const class Teuchos::RCP<class ROL::StatusTest<double> > & a0) -> void { return o.setStatusTest(a0); }, "", pybind11::arg("status"));
		cl.def("setStatusTest", (void (ROL::TypeU::Algorithm<double>::*)(const class Teuchos::RCP<class ROL::StatusTest<double> > &, bool)) &ROL::TypeU::Algorithm<double>::setStatusTest, "C++: ROL::TypeU::Algorithm<double>::setStatusTest(const class Teuchos::RCP<class ROL::StatusTest<double> > &, bool) --> void", pybind11::arg("status"), pybind11::arg("combineStatus"));
		cl.def("run", [](ROL::TypeU::Algorithm<double> &o, class ROL::Problem<double> & a0) -> void { return o.run(a0); }, "", pybind11::arg("problem"));
		cl.def("run", (void (ROL::TypeU::Algorithm<double>::*)(class ROL::Problem<double> &, std::ostream &)) &ROL::TypeU::Algorithm<double>::run, "C++: ROL::TypeU::Algorithm<double>::run(class ROL::Problem<double> &, std::ostream &) --> void", pybind11::arg("problem"), pybind11::arg("outStream"));
		cl.def("run", [](ROL::TypeU::Algorithm<double> &o, class ROL::Vector<double> & a0, class ROL::Objective<double> & a1) -> void { return o.run(a0, a1); }, "", pybind11::arg("x"), pybind11::arg("obj"));
		cl.def("run", (void (ROL::TypeU::Algorithm<double>::*)(class ROL::Vector<double> &, class ROL::Objective<double> &, std::ostream &)) &ROL::TypeU::Algorithm<double>::run, "C++: ROL::TypeU::Algorithm<double>::run(class ROL::Vector<double> &, class ROL::Objective<double> &, std::ostream &) --> void", pybind11::arg("x"), pybind11::arg("obj"), pybind11::arg("outStream"));
		cl.def("run", [](ROL::TypeU::Algorithm<double> &o, class ROL::Vector<double> & a0, class ROL::Objective<double> & a1, class ROL::Constraint<double> & a2, class ROL::Vector<double> & a3) -> void { return o.run(a0, a1, a2, a3); }, "", pybind11::arg("x"), pybind11::arg("obj"), pybind11::arg("linear_con"), pybind11::arg("linear_mul"));
		cl.def("run", (void (ROL::TypeU::Algorithm<double>::*)(class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Constraint<double> &, class ROL::Vector<double> &, std::ostream &)) &ROL::TypeU::Algorithm<double>::run, "C++: ROL::TypeU::Algorithm<double>::run(class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Constraint<double> &, class ROL::Vector<double> &, std::ostream &) --> void", pybind11::arg("x"), pybind11::arg("obj"), pybind11::arg("linear_con"), pybind11::arg("linear_mul"), pybind11::arg("outStream"));
		cl.def("run", [](ROL::TypeU::Algorithm<double> &o, class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, class ROL::Objective<double> & a2, class ROL::Constraint<double> & a3, class ROL::Vector<double> & a4, const class ROL::Vector<double> & a5) -> void { return o.run(a0, a1, a2, a3, a4, a5); }, "", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("obj"), pybind11::arg("linear_con"), pybind11::arg("linear_mul"), pybind11::arg("linear_c"));
		cl.def("run", (void (ROL::TypeU::Algorithm<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Constraint<double> &, class ROL::Vector<double> &, const class ROL::Vector<double> &, std::ostream &)) &ROL::TypeU::Algorithm<double>::run, "C++: ROL::TypeU::Algorithm<double>::run(class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Constraint<double> &, class ROL::Vector<double> &, const class ROL::Vector<double> &, std::ostream &) --> void", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("obj"), pybind11::arg("linear_con"), pybind11::arg("linear_mul"), pybind11::arg("linear_c"), pybind11::arg("outStream"));
		cl.def("run", [](ROL::TypeU::Algorithm<double> &o, class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, class ROL::Objective<double> & a2) -> void { return o.run(a0, a1, a2); }, "", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("obj"));
		cl.def("run", (void (ROL::TypeU::Algorithm<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &, std::ostream &)) &ROL::TypeU::Algorithm<double>::run, "C++: ROL::TypeU::Algorithm<double>::run(class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &, std::ostream &) --> void", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("obj"), pybind11::arg("outStream"));
		cl.def("writeHeader", (void (ROL::TypeU::Algorithm<double>::*)(std::ostream &) const) &ROL::TypeU::Algorithm<double>::writeHeader, "C++: ROL::TypeU::Algorithm<double>::writeHeader(std::ostream &) const --> void", pybind11::arg("os"));
		cl.def("writeName", (void (ROL::TypeU::Algorithm<double>::*)(std::ostream &) const) &ROL::TypeU::Algorithm<double>::writeName, "C++: ROL::TypeU::Algorithm<double>::writeName(std::ostream &) const --> void", pybind11::arg("os"));
		cl.def("writeOutput", [](ROL::TypeU::Algorithm<double> const &o, std::ostream & a0) -> void { return o.writeOutput(a0); }, "", pybind11::arg("os"));
		cl.def("writeOutput", (void (ROL::TypeU::Algorithm<double>::*)(std::ostream &, const bool) const) &ROL::TypeU::Algorithm<double>::writeOutput, "C++: ROL::TypeU::Algorithm<double>::writeOutput(std::ostream &, const bool) const --> void", pybind11::arg("os"), pybind11::arg("write_header"));
		cl.def("writeExitStatus", (void (ROL::TypeU::Algorithm<double>::*)(std::ostream &) const) &ROL::TypeU::Algorithm<double>::writeExitStatus, "C++: ROL::TypeU::Algorithm<double>::writeExitStatus(std::ostream &) const --> void", pybind11::arg("os"));
		cl.def("getState", (class Teuchos::RCP<const struct ROL::TypeU::AlgorithmState<double> > (ROL::TypeU::Algorithm<double>::*)() const) &ROL::TypeU::Algorithm<double>::getState, "C++: ROL::TypeU::Algorithm<double>::getState() const --> class Teuchos::RCP<const struct ROL::TypeU::AlgorithmState<double> >");
		cl.def("reset", (void (ROL::TypeU::Algorithm<double>::*)()) &ROL::TypeU::Algorithm<double>::reset, "C++: ROL::TypeU::Algorithm<double>::reset() --> void");
	}
}
