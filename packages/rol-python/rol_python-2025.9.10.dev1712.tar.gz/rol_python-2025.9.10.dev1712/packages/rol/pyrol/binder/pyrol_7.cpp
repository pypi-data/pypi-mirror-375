#include <PyROL_Teuchos_Custom.hpp>
#include <ROL_AugmentedLagrangianObjective.hpp>
#include <ROL_BatchManager.hpp>
#include <ROL_BoundConstraint.hpp>
#include <ROL_Constraint.hpp>
#include <ROL_ConstraintFromObjective.hpp>
#include <ROL_Constraint_SimOpt.hpp>
#include <ROL_DynamicConstraint.hpp>
#include <ROL_ElasticObjective.hpp>
#include <ROL_Elementwise_Function.hpp>
#include <ROL_Elementwise_Reduce.hpp>
#include <ROL_Objective.hpp>
#include <ROL_ProbabilityVector.hpp>
#include <ROL_RandVarFunctional.hpp>
#include <ROL_RiskVector.hpp>
#include <ROL_StdVector.hpp>
#include <ROL_StochasticConstraint.hpp>
#include <ROL_StochasticObjective.hpp>
#include <ROL_Stream.hpp>
#include <ROL_TimeStamp.hpp>
#include <ROL_TypeB_Algorithm.hpp>
#include <ROL_TypeP_Algorithm.hpp>
#include <ROL_UpdateType.hpp>
#include <ROL_Vector.hpp>
#include <Teuchos_Array.hpp>
#include <Teuchos_ENull.hpp>
#include <Teuchos_FancyOStream.hpp>
#include <Teuchos_FilteredIterator.hpp>
#include <Teuchos_ParameterEntry.hpp>
#include <Teuchos_ParameterEntryValidator.hpp>
#include <Teuchos_ParameterList.hpp>
#include <Teuchos_ParameterListModifier.hpp>
#include <Teuchos_Ptr.hpp>
#include <Teuchos_PtrDecl.hpp>
#include <Teuchos_RCP.hpp>
#include <Teuchos_RCPDecl.hpp>
#include <Teuchos_RCPNode.hpp>
#include <Teuchos_StringIndexedOrderedValueObjectContainer.hpp>
#include <Teuchos_any.hpp>
#include <Teuchos_dyn_cast.hpp>
#include <Teuchos_toString.hpp>
#include <deque>
#include <ios>
#include <iterator>
#include <locale>
#include <memory>
#include <ostream>
#include <sstream> // __str__
#include <streambuf>
#include <string>
#include <typeinfo>
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

// Teuchos::RCPNode file:Teuchos_RCPNode.hpp line:121
struct PyCallBack_Teuchos_RCPNode : public Teuchos::RCPNode {
	using Teuchos::RCPNode::RCPNode;

	bool is_valid_ptr() const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const Teuchos::RCPNode *>(this), "is_valid_ptr");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<bool>::value) {
				static pybind11::detail::override_caster_t<bool> caster;
				return pybind11::detail::cast_ref<bool>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<bool>(std::move(o));
		}
		pybind11::pybind11_fail("Tried to call pure virtual function \"RCPNode::is_valid_ptr\"");
	}
	void delete_obj() override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const Teuchos::RCPNode *>(this), "delete_obj");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		pybind11::pybind11_fail("Tried to call pure virtual function \"RCPNode::delete_obj\"");
	}
	void throw_invalid_obj_exception(const std::string & a0, const void * a1, const class Teuchos::RCPNode * a2, const void * a3) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const Teuchos::RCPNode *>(this), "throw_invalid_obj_exception");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		pybind11::pybind11_fail("Tried to call pure virtual function \"RCPNode::throw_invalid_obj_exception\"");
	}
	const std::string get_base_obj_type_name() const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const Teuchos::RCPNode *>(this), "get_base_obj_type_name");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<const std::string>::value) {
				static pybind11::detail::override_caster_t<const std::string> caster;
				return pybind11::detail::cast_ref<const std::string>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<const std::string>(std::move(o));
		}
		pybind11::pybind11_fail("Tried to call pure virtual function \"RCPNode::get_base_obj_type_name\"");
	}
};

// Teuchos::m_bad_cast file:Teuchos_dyn_cast.hpp line:28
struct PyCallBack_Teuchos_m_bad_cast : public Teuchos::m_bad_cast {
	using Teuchos::m_bad_cast::m_bad_cast;

	const char * what() const throw() override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const Teuchos::m_bad_cast *>(this), "what");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<const char *>::value) {
				static pybind11::detail::override_caster_t<const char *> caster;
				return pybind11::detail::cast_ref<const char *>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<const char *>(std::move(o));
		}
		return m_bad_cast::what();
	}
};

void bind_pyrol_7(std::function< pybind11::module &(std::string const &namespace_) > &M)
{
	// Teuchos::ENull file:Teuchos_ENull.hpp line:22
	pybind11::enum_<Teuchos::ENull>(M("Teuchos"), "ENull", pybind11::arithmetic(), "Used to initialize a RCP object to NULL using an\n implicit conversion!\n\n \n\n ", pybind11::module_local())
		.value("null", Teuchos::null)
		.export_values();

;

	{ // Teuchos::ToStringTraits file:Teuchos_toString.hpp line:28
		pybind11::class_<Teuchos::ToStringTraits<int>, Teuchos::RCP<Teuchos::ToStringTraits<int>>> cl(M("Teuchos"), "ToStringTraits_int_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ToStringTraits<int>(); } ) );
		cl.def_static("toString", (std::string (*)(const int &)) &Teuchos::ToStringTraits<int>::toString, "C++: Teuchos::ToStringTraits<int>::toString(const int &) --> std::string", pybind11::arg("t"));
	}
	// Teuchos::toString(const double &) file:Teuchos_toString.hpp line:50
	M("Teuchos").def("toString", (std::string (*)(const double &)) &Teuchos::toString<double>, "C++: Teuchos::toString(const double &) --> std::string", pybind11::arg("t"));

	// Teuchos::toString(const int &) file:Teuchos_toString.hpp line:50
	M("Teuchos").def("toString", (std::string (*)(const int &)) &Teuchos::toString<int>, "C++: Teuchos::toString(const int &) --> std::string", pybind11::arg("t"));

	// Teuchos::toString(const bool &) file:Teuchos_toString.hpp line:50
	M("Teuchos").def("toString", (std::string (*)(const bool &)) &Teuchos::toString<bool>, "C++: Teuchos::toString(const bool &) --> std::string", pybind11::arg("t"));

	// Teuchos::toString(const std::string &) file:Teuchos_toString.hpp line:50
	M("Teuchos").def("toString", (std::string (*)(const std::string &)) &Teuchos::toString<std::string>, "C++: Teuchos::toString(const std::string &) --> std::string", pybind11::arg("t"));

	{ // Teuchos::ToStringTraits file:Teuchos_toString.hpp line:58
		pybind11::class_<Teuchos::ToStringTraits<bool>, Teuchos::RCP<Teuchos::ToStringTraits<bool>>> cl(M("Teuchos"), "ToStringTraits_bool_t", "Specialization for bool. ", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ToStringTraits<bool>(); } ) );
		cl.def_static("toString", (std::string (*)(const bool &)) &Teuchos::ToStringTraits<bool>::toString, "C++: Teuchos::ToStringTraits<bool>::toString(const bool &) --> std::string", pybind11::arg("t"));
	}
	{ // Teuchos::ToStringTraits file:Teuchos_toString.hpp line:71
		pybind11::class_<Teuchos::ToStringTraits<std::string>, Teuchos::RCP<Teuchos::ToStringTraits<std::string>>> cl(M("Teuchos"), "ToStringTraits_std_string_t", "Specialization for std::string. ", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ToStringTraits<std::string>(); } ) );
		cl.def_static("toString", (std::string (*)(const std::string &)) &Teuchos::ToStringTraits<std::string>::toString, "C++: Teuchos::ToStringTraits<std::string>::toString(const std::string &) --> std::string", pybind11::arg("t"));
	}
	{ // Teuchos::ToStringTraits file:Teuchos_toString.hpp line:81
		pybind11::class_<Teuchos::ToStringTraits<double>, Teuchos::RCP<Teuchos::ToStringTraits<double>>> cl(M("Teuchos"), "ToStringTraits_double_t", "Specialization for double. ", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ToStringTraits<double>(); } ) );
		cl.def_static("toString", (std::string (*)(const double &)) &Teuchos::ToStringTraits<double>::toString, "C++: Teuchos::ToStringTraits<double>::toString(const double &) --> std::string", pybind11::arg("t"));
	}
	{ // Teuchos::ToStringTraits file:Teuchos_toString.hpp line:117
		pybind11::class_<Teuchos::ToStringTraits<float>, Teuchos::RCP<Teuchos::ToStringTraits<float>>> cl(M("Teuchos"), "ToStringTraits_float_t", "Specialization for float. ", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ToStringTraits<float>(); } ) );
		cl.def_static("toString", (std::string (*)(const float &)) &Teuchos::ToStringTraits<float>::toString, "C++: Teuchos::ToStringTraits<float>::toString(const float &) --> std::string", pybind11::arg("t"));
	}
	// Teuchos::EPrePostDestruction file:Teuchos_RCPNode.hpp line:47
	pybind11::enum_<Teuchos::EPrePostDestruction>(M("Teuchos"), "EPrePostDestruction", pybind11::arithmetic(), "Used to specify a pre or post destruction of extra data\n\n \n\n ", pybind11::module_local())
		.value("PRE_DESTROY", Teuchos::PRE_DESTROY)
		.value("POST_DESTROY", Teuchos::POST_DESTROY)
		.export_values();

;

	// Teuchos::ERCPStrength file:Teuchos_RCPNode.hpp line:53
	pybind11::enum_<Teuchos::ERCPStrength>(M("Teuchos"), "ERCPStrength", pybind11::arithmetic(), "Used to specify if the pointer is weak or strong.\n\n \n\n ", pybind11::module_local())
		.value("RCP_STRONG", Teuchos::RCP_STRONG)
		.value("RCP_WEAK", Teuchos::RCP_WEAK)
		.export_values();

;

	// Teuchos::ERCPNodeLookup file:Teuchos_RCPNode.hpp line:59
	pybind11::enum_<Teuchos::ERCPNodeLookup>(M("Teuchos"), "ERCPNodeLookup", pybind11::arithmetic(), "Used to determine if RCPNode lookup is performed or not.\n\n \n\n ", pybind11::module_local())
		.value("RCP_ENABLE_NODE_LOOKUP", Teuchos::RCP_ENABLE_NODE_LOOKUP)
		.value("RCP_DISABLE_NODE_LOOKUP", Teuchos::RCP_DISABLE_NODE_LOOKUP)
		.export_values();

;

	// Teuchos::debugAssertStrength(enum Teuchos::ERCPStrength) file:Teuchos_RCPNode.hpp line:62
	M("Teuchos").def("debugAssertStrength", (void (*)(enum Teuchos::ERCPStrength)) &Teuchos::debugAssertStrength, ". \n\nC++: Teuchos::debugAssertStrength(enum Teuchos::ERCPStrength) --> void", pybind11::arg("strength"));

	{ // Teuchos::ToStringTraits file:Teuchos_RCPNode.hpp line:87
		pybind11::class_<Teuchos::ToStringTraits<Teuchos::ERCPStrength>, Teuchos::RCP<Teuchos::ToStringTraits<Teuchos::ERCPStrength>>> cl(M("Teuchos"), "ToStringTraits_Teuchos_ERCPStrength_t", "Traits class specialization for toString(...) function for\n converting from ERCPStrength to std::string.\n\n \n\n ", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ToStringTraits<Teuchos::ERCPStrength>(); } ) );
		cl.def_static("toString", (std::string (*)(const enum Teuchos::ERCPStrength &)) &Teuchos::ToStringTraits<Teuchos::ERCPStrength>::toString, "C++: Teuchos::ToStringTraits<Teuchos::ERCPStrength>::toString(const enum Teuchos::ERCPStrength &) --> std::string", pybind11::arg("t"));
	}
	{ // Teuchos::RCPNode file:Teuchos_RCPNode.hpp line:121
		pybind11::class_<Teuchos::RCPNode, Teuchos::RCP<Teuchos::RCPNode>, PyCallBack_Teuchos_RCPNode> cl(M("Teuchos"), "RCPNode", "Node class to keep track of address and the reference count for a\n reference-counted utility class and delete the object.\n\n This is not a general user-level class.  This is used in the implementation\n of all of the reference-counting utility classes.\n\n NOTE: The reference counts all start a 0 so the client (i.e. RCPNodeHandle)\n must increment them from 0 after creation.\n\n \n\n ", pybind11::module_local());
		cl.def( pybind11::init<bool>(), pybind11::arg("has_ownership_in") );

		cl.def("attemptIncrementStrongCountFromNonZeroValue", (bool (Teuchos::RCPNode::*)()) &Teuchos::RCPNode::attemptIncrementStrongCountFromNonZeroValue, "attemptIncrementStrongCountFromNonZeroValue() supports weak\n to strong conversion but this is forward looking code.\n\nC++: Teuchos::RCPNode::attemptIncrementStrongCountFromNonZeroValue() --> bool");
		cl.def("strong_count", (int (Teuchos::RCPNode::*)() const) &Teuchos::RCPNode::strong_count, ". \n\nC++: Teuchos::RCPNode::strong_count() const --> int");
		cl.def("weak_count", (int (Teuchos::RCPNode::*)() const) &Teuchos::RCPNode::weak_count, ". \n\nC++: Teuchos::RCPNode::weak_count() const --> int");
		cl.def("incr_count", (void (Teuchos::RCPNode::*)(const enum Teuchos::ERCPStrength)) &Teuchos::RCPNode::incr_count, ". \n\nC++: Teuchos::RCPNode::incr_count(const enum Teuchos::ERCPStrength) --> void", pybind11::arg("strength"));
		cl.def("deincr_count", (int (Teuchos::RCPNode::*)(const enum Teuchos::ERCPStrength)) &Teuchos::RCPNode::deincr_count, ". \n\nC++: Teuchos::RCPNode::deincr_count(const enum Teuchos::ERCPStrength) --> int", pybind11::arg("strength"));
		cl.def("has_ownership", (void (Teuchos::RCPNode::*)(bool)) &Teuchos::RCPNode::has_ownership, ". \n\nC++: Teuchos::RCPNode::has_ownership(bool) --> void", pybind11::arg("has_ownership_in"));
		cl.def("has_ownership", (bool (Teuchos::RCPNode::*)() const) &Teuchos::RCPNode::has_ownership, ". \n\nC++: Teuchos::RCPNode::has_ownership() const --> bool");
		cl.def("set_extra_data", (void (Teuchos::RCPNode::*)(const class Teuchos::any &, const std::string &, enum Teuchos::EPrePostDestruction, bool)) &Teuchos::RCPNode::set_extra_data, ". \n\nC++: Teuchos::RCPNode::set_extra_data(const class Teuchos::any &, const std::string &, enum Teuchos::EPrePostDestruction, bool) --> void", pybind11::arg("extra_data"), pybind11::arg("name"), pybind11::arg("destroy_when"), pybind11::arg("force_unique"));
		cl.def("get_extra_data", (class Teuchos::any & (Teuchos::RCPNode::*)(const std::string &, const std::string &)) &Teuchos::RCPNode::get_extra_data, ". \n\nC++: Teuchos::RCPNode::get_extra_data(const std::string &, const std::string &) --> class Teuchos::any &", pybind11::return_value_policy::automatic, pybind11::arg("type_name"), pybind11::arg("name"));
		cl.def("get_optional_extra_data", (class Teuchos::any * (Teuchos::RCPNode::*)(const std::string &, const std::string &)) &Teuchos::RCPNode::get_optional_extra_data, ". \n\nC++: Teuchos::RCPNode::get_optional_extra_data(const std::string &, const std::string &) --> class Teuchos::any *", pybind11::return_value_policy::automatic, pybind11::arg("type_name"), pybind11::arg("name"));
		cl.def("is_valid_ptr", (bool (Teuchos::RCPNode::*)() const) &Teuchos::RCPNode::is_valid_ptr, ". \n\nC++: Teuchos::RCPNode::is_valid_ptr() const --> bool");
		cl.def("delete_obj", (void (Teuchos::RCPNode::*)()) &Teuchos::RCPNode::delete_obj, ". \n\nC++: Teuchos::RCPNode::delete_obj() --> void");
		cl.def("throw_invalid_obj_exception", (void (Teuchos::RCPNode::*)(const std::string &, const void *, const class Teuchos::RCPNode *, const void *) const) &Teuchos::RCPNode::throw_invalid_obj_exception, ". \n\nC++: Teuchos::RCPNode::throw_invalid_obj_exception(const std::string &, const void *, const class Teuchos::RCPNode *, const void *) const --> void", pybind11::arg("rcp_type_name"), pybind11::arg("rcp_ptr"), pybind11::arg("rcp_node_ptr"), pybind11::arg("rcp_obj_ptr"));
		cl.def("get_base_obj_type_name", (const std::string (Teuchos::RCPNode::*)() const) &Teuchos::RCPNode::get_base_obj_type_name, ". \n\nC++: Teuchos::RCPNode::get_base_obj_type_name() const --> const std::string");
	}
	// Teuchos::throw_null_ptr_error(const std::string &) file:Teuchos_RCPNode.hpp line:302
	M("Teuchos").def("throw_null_ptr_error", (void (*)(const std::string &)) &Teuchos::throw_null_ptr_error, "Throw that a pointer passed into an RCP object is null.\n\n \n\n \n\nC++: Teuchos::throw_null_ptr_error(const std::string &) --> void", pybind11::arg("type_name"));

	{ // Teuchos::RCPNodeTracer file:Teuchos_RCPNode.hpp line:336
		pybind11::class_<Teuchos::RCPNodeTracer, Teuchos::RCP<Teuchos::RCPNodeTracer>> cl(M("Teuchos"), "RCPNodeTracer", "Debug-mode RCPNode tracing class.\n\n This is a static class that is used to trace all RCP nodes that are created\n and destroyed and to look-up RCPNodes given an an object's address.  This\n database is used for several different types of debug-mode runtime checking\n including a) the detection of cicular references, b) detecting the creation\n of duplicate owning RCPNode objects for the same reference-counted object,\n and c) to create weak RCP objects for existing RCPNode objects.\n\n This is primarily an internal implementation class but there are a few\n functions (maked as such below) that can be called by general users to turn\n on and off node tracing and to print the active RCPNode objects at any\n time.\n\n \n\n ", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::RCPNodeTracer(); } ) );
		cl.def_static("isTracingActiveRCPNodes", (bool (*)()) &Teuchos::RCPNodeTracer::isTracingActiveRCPNodes, "Return if we are tracing active nodes or not.\n\n NOTE: This will always return false when TEUCHOS_DEBUG is\n not defined.\n\nC++: Teuchos::RCPNodeTracer::isTracingActiveRCPNodes() --> bool");
		cl.def_static("numActiveRCPNodes", (int (*)()) &Teuchos::RCPNodeTracer::numActiveRCPNodes, "Print the number of active RCPNode objects currently being\n tracked.\n\nC++: Teuchos::RCPNodeTracer::numActiveRCPNodes() --> int");
		cl.def_static("getRCPNodeStatistics", (struct Teuchos::RCPNodeTracer::RCPNodeStatistics (*)()) &Teuchos::RCPNodeTracer::getRCPNodeStatistics, "Return the statistics on RCPNode allocations. \n\nC++: Teuchos::RCPNodeTracer::getRCPNodeStatistics() --> struct Teuchos::RCPNodeTracer::RCPNodeStatistics");
		cl.def_static("printRCPNodeStatistics", (void (*)(const struct Teuchos::RCPNodeTracer::RCPNodeStatistics &, std::ostream &)) &Teuchos::RCPNodeTracer::printRCPNodeStatistics, "Print the RCPNode allocation statistics. \n\nC++: Teuchos::RCPNodeTracer::printRCPNodeStatistics(const struct Teuchos::RCPNodeTracer::RCPNodeStatistics &, std::ostream &) --> void", pybind11::arg("rcpNodeStatistics"), pybind11::arg("out"));
		cl.def_static("setPrintRCPNodeStatisticsOnExit", (void (*)(bool)) &Teuchos::RCPNodeTracer::setPrintRCPNodeStatisticsOnExit, "Set if RCPNode usage statistics will be printed when the program\n ends or not.\n\nC++: Teuchos::RCPNodeTracer::setPrintRCPNodeStatisticsOnExit(bool) --> void", pybind11::arg("printRCPNodeStatisticsOnExit"));
		cl.def_static("getPrintRCPNodeStatisticsOnExit", (bool (*)()) &Teuchos::RCPNodeTracer::getPrintRCPNodeStatisticsOnExit, "Return if RCPNode usage statistics will be printed when the\n program ends or not.\n\nC++: Teuchos::RCPNodeTracer::getPrintRCPNodeStatisticsOnExit() --> bool");
		cl.def_static("setPrintActiveRcpNodesOnExit", (void (*)(bool)) &Teuchos::RCPNodeTracer::setPrintActiveRcpNodesOnExit, "Set if printActiveRCPNodes() is called on exit from the\n program.\n\nC++: Teuchos::RCPNodeTracer::setPrintActiveRcpNodesOnExit(bool) --> void", pybind11::arg("printActiveRcpNodesOnExit"));
		cl.def_static("getPrintActiveRcpNodesOnExit", (bool (*)()) &Teuchos::RCPNodeTracer::getPrintActiveRcpNodesOnExit, "Return if printActiveRCPNodes() is called on exit from the\n program.\n\nC++: Teuchos::RCPNodeTracer::getPrintActiveRcpNodesOnExit() --> bool");
		cl.def_static("printActiveRCPNodes", (void (*)(std::ostream &)) &Teuchos::RCPNodeTracer::printActiveRCPNodes, "Print the list of currently active RCP nodes.\n\n When the macro TEUCHOS_SHOW_ACTIVE_REFCOUNTPTR_NODE_TRACE is\n defined, this function will print out all of the RCP nodes that are\n currently active.  This function can be called at any time during a\n program.\n\n When the macro TEUCHOS_SHOW_ACTIVE_REFCOUNTPTR_NODE_TRACE is\n defined this function will get called automatically after the program\n ends by default and all of the local and global RCP objects have been\n destroyed.  If any RCP nodes are printed at that time, then this is an\n indication that there may be some circular references that will caused\n memory leaks.  You memory checking tool such as valgrind or purify should\n complain about this!\n\nC++: Teuchos::RCPNodeTracer::printActiveRCPNodes(std::ostream &) --> void", pybind11::arg("out"));
		cl.def_static("addNewRCPNode", (void (*)(class Teuchos::RCPNode *, const std::string &)) &Teuchos::RCPNodeTracer::addNewRCPNode, "Add new RCPNode to the global list.\n\n Only gets called when RCPNode tracing has been activated.\n\nC++: Teuchos::RCPNodeTracer::addNewRCPNode(class Teuchos::RCPNode *, const std::string &) --> void", pybind11::arg("rcp_node"), pybind11::arg("info"));
		cl.def_static("removeRCPNode", (void (*)(class Teuchos::RCPNode *)) &Teuchos::RCPNodeTracer::removeRCPNode, "Remove an RCPNode from global list.\n\n Always gets called in a debug build (TEUCHOS_DEBUG defined) when\n node tracing is enabled.\n\nC++: Teuchos::RCPNodeTracer::removeRCPNode(class Teuchos::RCPNode *) --> void", pybind11::arg("rcp_node"));
		cl.def_static("getExistingRCPNodeGivenLookupKey", (class Teuchos::RCPNode * (*)(const void *)) &Teuchos::RCPNodeTracer::getExistingRCPNodeGivenLookupKey, "Return a raw pointer to an existing owning RCPNode given its\n lookup key.\n\n \n returnVal != 0 if an owning RCPNode exists, 0\n otherwsise.\n\nC++: Teuchos::RCPNodeTracer::getExistingRCPNodeGivenLookupKey(const void *) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("lookupKey"));
		cl.def_static("getActiveRCPNodeHeaderString", (std::string (*)()) &Teuchos::RCPNodeTracer::getActiveRCPNodeHeaderString, "Header string used in printActiveRCPNodes(). \n\nC++: Teuchos::RCPNodeTracer::getActiveRCPNodeHeaderString() --> std::string");
		cl.def_static("getCommonDebugNotesString", (std::string (*)()) &Teuchos::RCPNodeTracer::getCommonDebugNotesString, "Common error message string on how to debug RCPNode problems. \n\nC++: Teuchos::RCPNodeTracer::getCommonDebugNotesString() --> std::string");

		{ // Teuchos::RCPNodeTracer::RCPNodeStatistics file:Teuchos_RCPNode.hpp line:343
			auto & enclosing_class = cl;
			pybind11::class_<Teuchos::RCPNodeTracer::RCPNodeStatistics, Teuchos::RCP<Teuchos::RCPNodeTracer::RCPNodeStatistics>> cl(enclosing_class, "RCPNodeStatistics", "RCP statistics struct. ", pybind11::module_local());
			cl.def( pybind11::init( [](){ return new Teuchos::RCPNodeTracer::RCPNodeStatistics(); } ) );
			cl.def_readwrite("maxNumRCPNodes", &Teuchos::RCPNodeTracer::RCPNodeStatistics::maxNumRCPNodes);
			cl.def_readwrite("totalNumRCPNodeAllocations", &Teuchos::RCPNodeTracer::RCPNodeStatistics::totalNumRCPNodeAllocations);
			cl.def_readwrite("totalNumRCPNodeDeletions", &Teuchos::RCPNodeTracer::RCPNodeStatistics::totalNumRCPNodeDeletions);
		}

	}
	{ // Teuchos::ActiveRCPNodesSetup file:Teuchos_RCPNode.hpp line:671
		pybind11::class_<Teuchos::ActiveRCPNodesSetup, Teuchos::RCP<Teuchos::ActiveRCPNodesSetup>> cl(M("Teuchos"), "ActiveRCPNodesSetup", "Sets up node tracing and prints remaining RCPNodes on destruction.\n\n This class is used by automataic code that sets up support for RCPNode\n tracing and for printing of remaining nodes on destruction.\n\n \n\n ", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ActiveRCPNodesSetup(); } ) );
		cl.def( pybind11::init( [](Teuchos::ActiveRCPNodesSetup const &o){ return new Teuchos::ActiveRCPNodesSetup(o); } ) );
		cl.def("foo", (void (Teuchos::ActiveRCPNodesSetup::*)()) &Teuchos::ActiveRCPNodesSetup::foo, ". \n\nC++: Teuchos::ActiveRCPNodesSetup::foo() --> void");
	}
	{ // Teuchos::RCPNodeThrowDeleter file:Teuchos_RCPNode.hpp line:1078
		pybind11::class_<Teuchos::RCPNodeThrowDeleter, Teuchos::RCP<Teuchos::RCPNodeThrowDeleter>> cl(M("Teuchos"), "RCPNodeThrowDeleter", "Deletes a (non-owning) RCPNode but not it's underlying object in\n case of a throw.\n\n This class is used in contexts where RCPNodeTracer::addNewRCPNode(...)\n might thrown an exception for a duplicate node being added.  The assumption\n is that there must already be an owning (or non-owning) RCP object that\n will delete the underlying object and therefore this class should *not*\n call delete_obj()!", pybind11::module_local());
		cl.def( pybind11::init<class Teuchos::RCPNode *>(), pybind11::arg("node") );

		cl.def("get", (class Teuchos::RCPNode * (Teuchos::RCPNodeThrowDeleter::*)() const) &Teuchos::RCPNodeThrowDeleter::get, ". \n\nC++: Teuchos::RCPNodeThrowDeleter::get() const --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic);
		cl.def("release", (void (Teuchos::RCPNodeThrowDeleter::*)()) &Teuchos::RCPNodeThrowDeleter::release, "Releaes the RCPNode pointer before the destructor is called. \n\nC++: Teuchos::RCPNodeThrowDeleter::release() --> void");
	}
	{ // Teuchos::Ptr file:Teuchos_PtrDecl.hpp line:71
		pybind11::class_<Teuchos::Ptr<const Teuchos::ParameterEntry>, Teuchos::RCP<Teuchos::Ptr<const Teuchos::ParameterEntry>>> cl(M("Teuchos"), "Ptr_const_Teuchos_ParameterEntry_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::Ptr<const Teuchos::ParameterEntry>(); } ), "doc" );
		cl.def( pybind11::init<enum Teuchos::ENull>(), pybind11::arg("null_in") );

		cl.def( pybind11::init<const class Teuchos::ParameterEntry *>(), pybind11::arg("ptr_in") );

		cl.def( pybind11::init( [](Teuchos::Ptr<const Teuchos::ParameterEntry> const &o){ return new Teuchos::Ptr<const Teuchos::ParameterEntry>(o); } ) );
		cl.def("assign", (class Teuchos::Ptr<const class Teuchos::ParameterEntry> & (Teuchos::Ptr<const Teuchos::ParameterEntry>::*)(const class Teuchos::Ptr<const class Teuchos::ParameterEntry> &)) &Teuchos::Ptr<const Teuchos::ParameterEntry>::operator=, "C++: Teuchos::Ptr<const Teuchos::ParameterEntry>::operator=(const class Teuchos::Ptr<const class Teuchos::ParameterEntry> &) --> class Teuchos::Ptr<const class Teuchos::ParameterEntry> &", pybind11::return_value_policy::automatic, pybind11::arg("ptr"));
		cl.def("arrow", (const class Teuchos::ParameterEntry * (Teuchos::Ptr<const Teuchos::ParameterEntry>::*)() const) &Teuchos::Ptr<const Teuchos::ParameterEntry>::operator->, "C++: Teuchos::Ptr<const Teuchos::ParameterEntry>::operator->() const --> const class Teuchos::ParameterEntry *", pybind11::return_value_policy::automatic);
		cl.def("dereference", (const class Teuchos::ParameterEntry & (Teuchos::Ptr<const Teuchos::ParameterEntry>::*)() const) &Teuchos::Ptr<const Teuchos::ParameterEntry>::operator*, "C++: Teuchos::Ptr<const Teuchos::ParameterEntry>::operator*() const --> const class Teuchos::ParameterEntry &", pybind11::return_value_policy::automatic);
		cl.def("get", (const class Teuchos::ParameterEntry * (Teuchos::Ptr<const Teuchos::ParameterEntry>::*)() const) &Teuchos::Ptr<const Teuchos::ParameterEntry>::get, "C++: Teuchos::Ptr<const Teuchos::ParameterEntry>::get() const --> const class Teuchos::ParameterEntry *", pybind11::return_value_policy::automatic);
		cl.def("getRawPtr", (const class Teuchos::ParameterEntry * (Teuchos::Ptr<const Teuchos::ParameterEntry>::*)() const) &Teuchos::Ptr<const Teuchos::ParameterEntry>::getRawPtr, "C++: Teuchos::Ptr<const Teuchos::ParameterEntry>::getRawPtr() const --> const class Teuchos::ParameterEntry *", pybind11::return_value_policy::automatic);
		cl.def("is_null", (bool (Teuchos::Ptr<const Teuchos::ParameterEntry>::*)() const) &Teuchos::Ptr<const Teuchos::ParameterEntry>::is_null, "C++: Teuchos::Ptr<const Teuchos::ParameterEntry>::is_null() const --> bool");
		cl.def("assert_not_null", (const class Teuchos::Ptr<const class Teuchos::ParameterEntry> & (Teuchos::Ptr<const Teuchos::ParameterEntry>::*)() const) &Teuchos::Ptr<const Teuchos::ParameterEntry>::assert_not_null, "C++: Teuchos::Ptr<const Teuchos::ParameterEntry>::assert_not_null() const --> const class Teuchos::Ptr<const class Teuchos::ParameterEntry> &", pybind11::return_value_policy::automatic);
		cl.def("ptr", (const class Teuchos::Ptr<const class Teuchos::ParameterEntry> (Teuchos::Ptr<const Teuchos::ParameterEntry>::*)() const) &Teuchos::Ptr<const Teuchos::ParameterEntry>::ptr, "C++: Teuchos::Ptr<const Teuchos::ParameterEntry>::ptr() const --> const class Teuchos::Ptr<const class Teuchos::ParameterEntry>");
		cl.def("getConst", (class Teuchos::Ptr<const class Teuchos::ParameterEntry> (Teuchos::Ptr<const Teuchos::ParameterEntry>::*)() const) &Teuchos::Ptr<const Teuchos::ParameterEntry>::getConst, "C++: Teuchos::Ptr<const Teuchos::ParameterEntry>::getConst() const --> class Teuchos::Ptr<const class Teuchos::ParameterEntry>");

		cl.def("__str__", [](Teuchos::Ptr<const Teuchos::ParameterEntry> const &o) -> std::string { std::ostringstream s; using namespace Teuchos; s << o; return s.str(); } );
	}
	{ // Teuchos::Ptr file:Teuchos_PtrDecl.hpp line:71
		pybind11::class_<Teuchos::Ptr<Teuchos::ParameterEntry>, Teuchos::RCP<Teuchos::Ptr<Teuchos::ParameterEntry>>> cl(M("Teuchos"), "Ptr_Teuchos_ParameterEntry_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::Ptr<Teuchos::ParameterEntry>(); } ), "doc" );
		cl.def( pybind11::init<enum Teuchos::ENull>(), pybind11::arg("null_in") );

		cl.def( pybind11::init<class Teuchos::ParameterEntry *>(), pybind11::arg("ptr_in") );

		cl.def( pybind11::init( [](Teuchos::Ptr<Teuchos::ParameterEntry> const &o){ return new Teuchos::Ptr<Teuchos::ParameterEntry>(o); } ) );
		cl.def("assign", (class Teuchos::Ptr<class Teuchos::ParameterEntry> & (Teuchos::Ptr<Teuchos::ParameterEntry>::*)(const class Teuchos::Ptr<class Teuchos::ParameterEntry> &)) &Teuchos::Ptr<Teuchos::ParameterEntry>::operator=, "C++: Teuchos::Ptr<Teuchos::ParameterEntry>::operator=(const class Teuchos::Ptr<class Teuchos::ParameterEntry> &) --> class Teuchos::Ptr<class Teuchos::ParameterEntry> &", pybind11::return_value_policy::automatic, pybind11::arg("ptr"));
		cl.def("arrow", (class Teuchos::ParameterEntry * (Teuchos::Ptr<Teuchos::ParameterEntry>::*)() const) &Teuchos::Ptr<Teuchos::ParameterEntry>::operator->, "C++: Teuchos::Ptr<Teuchos::ParameterEntry>::operator->() const --> class Teuchos::ParameterEntry *", pybind11::return_value_policy::automatic);
		cl.def("dereference", (class Teuchos::ParameterEntry & (Teuchos::Ptr<Teuchos::ParameterEntry>::*)() const) &Teuchos::Ptr<Teuchos::ParameterEntry>::operator*, "C++: Teuchos::Ptr<Teuchos::ParameterEntry>::operator*() const --> class Teuchos::ParameterEntry &", pybind11::return_value_policy::automatic);
		cl.def("get", (class Teuchos::ParameterEntry * (Teuchos::Ptr<Teuchos::ParameterEntry>::*)() const) &Teuchos::Ptr<Teuchos::ParameterEntry>::get, "C++: Teuchos::Ptr<Teuchos::ParameterEntry>::get() const --> class Teuchos::ParameterEntry *", pybind11::return_value_policy::automatic);
		cl.def("getRawPtr", (class Teuchos::ParameterEntry * (Teuchos::Ptr<Teuchos::ParameterEntry>::*)() const) &Teuchos::Ptr<Teuchos::ParameterEntry>::getRawPtr, "C++: Teuchos::Ptr<Teuchos::ParameterEntry>::getRawPtr() const --> class Teuchos::ParameterEntry *", pybind11::return_value_policy::automatic);
		cl.def("is_null", (bool (Teuchos::Ptr<Teuchos::ParameterEntry>::*)() const) &Teuchos::Ptr<Teuchos::ParameterEntry>::is_null, "C++: Teuchos::Ptr<Teuchos::ParameterEntry>::is_null() const --> bool");
		cl.def("assert_not_null", (const class Teuchos::Ptr<class Teuchos::ParameterEntry> & (Teuchos::Ptr<Teuchos::ParameterEntry>::*)() const) &Teuchos::Ptr<Teuchos::ParameterEntry>::assert_not_null, "C++: Teuchos::Ptr<Teuchos::ParameterEntry>::assert_not_null() const --> const class Teuchos::Ptr<class Teuchos::ParameterEntry> &", pybind11::return_value_policy::automatic);
		cl.def("ptr", (const class Teuchos::Ptr<class Teuchos::ParameterEntry> (Teuchos::Ptr<Teuchos::ParameterEntry>::*)() const) &Teuchos::Ptr<Teuchos::ParameterEntry>::ptr, "C++: Teuchos::Ptr<Teuchos::ParameterEntry>::ptr() const --> const class Teuchos::Ptr<class Teuchos::ParameterEntry>");
		cl.def("getConst", (class Teuchos::Ptr<const class Teuchos::ParameterEntry> (Teuchos::Ptr<Teuchos::ParameterEntry>::*)() const) &Teuchos::Ptr<Teuchos::ParameterEntry>::getConst, "C++: Teuchos::Ptr<Teuchos::ParameterEntry>::getConst() const --> class Teuchos::Ptr<const class Teuchos::ParameterEntry>");

		cl.def("__str__", [](Teuchos::Ptr<Teuchos::ParameterEntry> const &o) -> std::string { std::ostringstream s; using namespace Teuchos; s << o; return s.str(); } );
	}
	{ // Teuchos::Ptr file:Teuchos_PtrDecl.hpp line:71
		pybind11::class_<Teuchos::Ptr<Teuchos::ParameterList>, Teuchos::RCP<Teuchos::Ptr<Teuchos::ParameterList>>> cl(M("Teuchos"), "Ptr_Teuchos_ParameterList_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::Ptr<Teuchos::ParameterList>(); } ), "doc" );
		cl.def( pybind11::init<enum Teuchos::ENull>(), pybind11::arg("null_in") );

		cl.def( pybind11::init<class Teuchos::ParameterList *>(), pybind11::arg("ptr_in") );

		cl.def( pybind11::init( [](Teuchos::Ptr<Teuchos::ParameterList> const &o){ return new Teuchos::Ptr<Teuchos::ParameterList>(o); } ) );
		cl.def("assign", (class Teuchos::Ptr<class Teuchos::ParameterList> & (Teuchos::Ptr<Teuchos::ParameterList>::*)(const class Teuchos::Ptr<class Teuchos::ParameterList> &)) &Teuchos::Ptr<Teuchos::ParameterList>::operator=, "C++: Teuchos::Ptr<Teuchos::ParameterList>::operator=(const class Teuchos::Ptr<class Teuchos::ParameterList> &) --> class Teuchos::Ptr<class Teuchos::ParameterList> &", pybind11::return_value_policy::automatic, pybind11::arg("ptr"));
		cl.def("arrow", (class Teuchos::ParameterList * (Teuchos::Ptr<Teuchos::ParameterList>::*)() const) &Teuchos::Ptr<Teuchos::ParameterList>::operator->, "C++: Teuchos::Ptr<Teuchos::ParameterList>::operator->() const --> class Teuchos::ParameterList *", pybind11::return_value_policy::automatic);
		cl.def("dereference", (class Teuchos::ParameterList & (Teuchos::Ptr<Teuchos::ParameterList>::*)() const) &Teuchos::Ptr<Teuchos::ParameterList>::operator*, "C++: Teuchos::Ptr<Teuchos::ParameterList>::operator*() const --> class Teuchos::ParameterList &", pybind11::return_value_policy::automatic);
		cl.def("get", (class Teuchos::ParameterList * (Teuchos::Ptr<Teuchos::ParameterList>::*)() const) &Teuchos::Ptr<Teuchos::ParameterList>::get, "C++: Teuchos::Ptr<Teuchos::ParameterList>::get() const --> class Teuchos::ParameterList *", pybind11::return_value_policy::automatic);
		cl.def("getRawPtr", (class Teuchos::ParameterList * (Teuchos::Ptr<Teuchos::ParameterList>::*)() const) &Teuchos::Ptr<Teuchos::ParameterList>::getRawPtr, "C++: Teuchos::Ptr<Teuchos::ParameterList>::getRawPtr() const --> class Teuchos::ParameterList *", pybind11::return_value_policy::automatic);
		cl.def("is_null", (bool (Teuchos::Ptr<Teuchos::ParameterList>::*)() const) &Teuchos::Ptr<Teuchos::ParameterList>::is_null, "C++: Teuchos::Ptr<Teuchos::ParameterList>::is_null() const --> bool");
		cl.def("assert_not_null", (const class Teuchos::Ptr<class Teuchos::ParameterList> & (Teuchos::Ptr<Teuchos::ParameterList>::*)() const) &Teuchos::Ptr<Teuchos::ParameterList>::assert_not_null, "C++: Teuchos::Ptr<Teuchos::ParameterList>::assert_not_null() const --> const class Teuchos::Ptr<class Teuchos::ParameterList> &", pybind11::return_value_policy::automatic);
		cl.def("ptr", (const class Teuchos::Ptr<class Teuchos::ParameterList> (Teuchos::Ptr<Teuchos::ParameterList>::*)() const) &Teuchos::Ptr<Teuchos::ParameterList>::ptr, "C++: Teuchos::Ptr<Teuchos::ParameterList>::ptr() const --> const class Teuchos::Ptr<class Teuchos::ParameterList>");

		cl.def("__str__", [](Teuchos::Ptr<Teuchos::ParameterList> const &o) -> std::string { std::ostringstream s; using namespace Teuchos; s << o; return s.str(); } );
	}
	// Teuchos::ERCPWeakNoDealloc file:Teuchos_RCPDecl.hpp line:43
	pybind11::enum_<Teuchos::ERCPWeakNoDealloc>(M("Teuchos"), "ERCPWeakNoDealloc", pybind11::arithmetic(), "", pybind11::module_local())
		.value("RCP_WEAK_NO_DEALLOC", Teuchos::RCP_WEAK_NO_DEALLOC)
		.export_values();

;

	// Teuchos::ERCPUndefinedWeakNoDealloc file:Teuchos_RCPDecl.hpp line:44
	pybind11::enum_<Teuchos::ERCPUndefinedWeakNoDealloc>(M("Teuchos"), "ERCPUndefinedWeakNoDealloc", pybind11::arithmetic(), "", pybind11::module_local())
		.value("RCP_UNDEFINED_WEAK_NO_DEALLOC", Teuchos::RCP_UNDEFINED_WEAK_NO_DEALLOC)
		.export_values();

;

	// Teuchos::ERCPUndefinedWithDealloc file:Teuchos_RCPDecl.hpp line:45
	pybind11::enum_<Teuchos::ERCPUndefinedWithDealloc>(M("Teuchos"), "ERCPUndefinedWithDealloc", pybind11::arithmetic(), "", pybind11::module_local())
		.value("RCP_UNDEFINED_WITH_DEALLOC", Teuchos::RCP_UNDEFINED_WITH_DEALLOC)
		.export_values();

;

	{ // Teuchos::RCPComp file:Teuchos_RCPDecl.hpp line:923
		pybind11::class_<Teuchos::RCPComp, Teuchos::RCP<Teuchos::RCPComp>> cl(M("Teuchos"), "RCPComp", "Struct for comparing two RCPs. Simply compares\n the raw pointers contained within the RCPs", pybind11::module_local());
		cl.def( pybind11::init( [](Teuchos::RCPComp const &o){ return new Teuchos::RCPComp(o); } ) );
		cl.def( pybind11::init( [](){ return new Teuchos::RCPComp(); } ) );
		cl.def("assign", (struct Teuchos::RCPComp & (Teuchos::RCPComp::*)(const struct Teuchos::RCPComp &)) &Teuchos::RCPComp::operator=, "C++: Teuchos::RCPComp::operator=(const struct Teuchos::RCPComp &) --> struct Teuchos::RCPComp &", pybind11::return_value_policy::automatic, pybind11::arg(""));
	}
	{ // Teuchos::RCPConstComp file:Teuchos_RCPDecl.hpp line:933
		pybind11::class_<Teuchos::RCPConstComp, Teuchos::RCP<Teuchos::RCPConstComp>> cl(M("Teuchos"), "RCPConstComp", "Struct for comparing two RCPs. Simply compares\n the raw pointers contained within the RCPs", pybind11::module_local());
		cl.def( pybind11::init( [](Teuchos::RCPConstComp const &o){ return new Teuchos::RCPConstComp(o); } ) );
		cl.def( pybind11::init( [](){ return new Teuchos::RCPConstComp(); } ) );
		cl.def("__call__", (bool (Teuchos::RCPConstComp::*)(const class Teuchos::RCP<const class Teuchos::ParameterEntry>, const class Teuchos::RCP<const class Teuchos::ParameterEntry>) const) &Teuchos::RCPConstComp::operator()<Teuchos::ParameterEntry,Teuchos::ParameterEntry>, "C++: Teuchos::RCPConstComp::operator()(const class Teuchos::RCP<const class Teuchos::ParameterEntry>, const class Teuchos::RCP<const class Teuchos::ParameterEntry>) const --> bool", pybind11::arg("p1"), pybind11::arg("p2"));
		cl.def("assign", (struct Teuchos::RCPConstComp & (Teuchos::RCPConstComp::*)(const struct Teuchos::RCPConstComp &)) &Teuchos::RCPConstComp::operator=, "C++: Teuchos::RCPConstComp::operator=(const struct Teuchos::RCPConstComp &) --> struct Teuchos::RCPConstComp &", pybind11::return_value_policy::automatic, pybind11::arg(""));
	}
	{ // Teuchos::DeallocNull file:Teuchos_RCPDecl.hpp line:964
		pybind11::class_<Teuchos::DeallocNull<std::ostream>, Teuchos::RCP<Teuchos::DeallocNull<std::ostream>>> cl(M("Teuchos"), "DeallocNull_std_ostream_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::DeallocNull<std::ostream>(); } ) );
		cl.def( pybind11::init( [](Teuchos::DeallocNull<std::ostream> const &o){ return new Teuchos::DeallocNull<std::ostream>(o); } ) );
		cl.def("free", (void (Teuchos::DeallocNull<std::ostream>::*)(std::ostream *)) &Teuchos::DeallocNull<std::ostream>::free, "C++: Teuchos::DeallocNull<std::ostream>::free(std::ostream *) --> void", pybind11::arg("ptr"));
	}
	{ // Teuchos::DeallocNull file:Teuchos_RCPDecl.hpp line:964
		pybind11::class_<Teuchos::DeallocNull<Teuchos::ParameterEntry>, Teuchos::RCP<Teuchos::DeallocNull<Teuchos::ParameterEntry>>> cl(M("Teuchos"), "DeallocNull_Teuchos_ParameterEntry_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::DeallocNull<Teuchos::ParameterEntry>(); } ) );
		cl.def( pybind11::init( [](Teuchos::DeallocNull<Teuchos::ParameterEntry> const &o){ return new Teuchos::DeallocNull<Teuchos::ParameterEntry>(o); } ) );
		cl.def("free", (void (Teuchos::DeallocNull<Teuchos::ParameterEntry>::*)(class Teuchos::ParameterEntry *)) &Teuchos::DeallocNull<Teuchos::ParameterEntry>::free, "C++: Teuchos::DeallocNull<Teuchos::ParameterEntry>::free(class Teuchos::ParameterEntry *) --> void", pybind11::arg("ptr"));
	}
	{ // Teuchos::DeallocNull file:Teuchos_RCPDecl.hpp line:964
		pybind11::class_<Teuchos::DeallocNull<const Teuchos::ParameterEntry>, Teuchos::RCP<Teuchos::DeallocNull<const Teuchos::ParameterEntry>>> cl(M("Teuchos"), "DeallocNull_const_Teuchos_ParameterEntry_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::DeallocNull<const Teuchos::ParameterEntry>(); } ) );
		cl.def( pybind11::init( [](Teuchos::DeallocNull<const Teuchos::ParameterEntry> const &o){ return new Teuchos::DeallocNull<const Teuchos::ParameterEntry>(o); } ) );
		cl.def("free", (void (Teuchos::DeallocNull<const Teuchos::ParameterEntry>::*)(const class Teuchos::ParameterEntry *)) &Teuchos::DeallocNull<const Teuchos::ParameterEntry>::free, "C++: Teuchos::DeallocNull<const Teuchos::ParameterEntry>::free(const class Teuchos::ParameterEntry *) --> void", pybind11::arg("ptr"));
	}
	{ // Teuchos::DeallocNull file:Teuchos_RCPDecl.hpp line:964
		pybind11::class_<Teuchos::DeallocNull<ROL::Objective<double>>, Teuchos::RCP<Teuchos::DeallocNull<ROL::Objective<double>>>> cl(M("Teuchos"), "DeallocNull_ROL_Objective_double_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::DeallocNull<ROL::Objective<double>>(); } ) );
		cl.def( pybind11::init( [](Teuchos::DeallocNull<ROL::Objective<double>> const &o){ return new Teuchos::DeallocNull<ROL::Objective<double>>(o); } ) );
		cl.def("free", (void (Teuchos::DeallocNull<ROL::Objective<double>>::*)(class ROL::Objective<double> *)) &Teuchos::DeallocNull<ROL::Objective<double>>::free, "C++: Teuchos::DeallocNull<ROL::Objective<double>>::free(class ROL::Objective<double> *) --> void", pybind11::arg("ptr"));
	}
	{ // Teuchos::DeallocNull file:Teuchos_RCPDecl.hpp line:964
		pybind11::class_<Teuchos::DeallocNull<ROL::Constraint<double>>, Teuchos::RCP<Teuchos::DeallocNull<ROL::Constraint<double>>>> cl(M("Teuchos"), "DeallocNull_ROL_Constraint_double_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::DeallocNull<ROL::Constraint<double>>(); } ) );
		cl.def( pybind11::init( [](Teuchos::DeallocNull<ROL::Constraint<double>> const &o){ return new Teuchos::DeallocNull<ROL::Constraint<double>>(o); } ) );
		cl.def("free", (void (Teuchos::DeallocNull<ROL::Constraint<double>>::*)(class ROL::Constraint<double> *)) &Teuchos::DeallocNull<ROL::Constraint<double>>::free, "C++: Teuchos::DeallocNull<ROL::Constraint<double>>::free(class ROL::Constraint<double> *) --> void", pybind11::arg("ptr"));
	}
	{ // Teuchos::DeallocNull file:Teuchos_RCPDecl.hpp line:964
		pybind11::class_<Teuchos::DeallocNull<ROL::BoundConstraint<double>>, Teuchos::RCP<Teuchos::DeallocNull<ROL::BoundConstraint<double>>>> cl(M("Teuchos"), "DeallocNull_ROL_BoundConstraint_double_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::DeallocNull<ROL::BoundConstraint<double>>(); } ) );
		cl.def( pybind11::init( [](Teuchos::DeallocNull<ROL::BoundConstraint<double>> const &o){ return new Teuchos::DeallocNull<ROL::BoundConstraint<double>>(o); } ) );
		cl.def("free", (void (Teuchos::DeallocNull<ROL::BoundConstraint<double>>::*)(class ROL::BoundConstraint<double> *)) &Teuchos::DeallocNull<ROL::BoundConstraint<double>>::free, "C++: Teuchos::DeallocNull<ROL::BoundConstraint<double>>::free(class ROL::BoundConstraint<double> *) --> void", pybind11::arg("ptr"));
	}
	{ // Teuchos::DeallocNull file:Teuchos_RCPDecl.hpp line:964
		pybind11::class_<Teuchos::DeallocNull<ROL::Vector<double>>, Teuchos::RCP<Teuchos::DeallocNull<ROL::Vector<double>>>> cl(M("Teuchos"), "DeallocNull_ROL_Vector_double_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::DeallocNull<ROL::Vector<double>>(); } ) );
		cl.def( pybind11::init( [](Teuchos::DeallocNull<ROL::Vector<double>> const &o){ return new Teuchos::DeallocNull<ROL::Vector<double>>(o); } ) );
		cl.def("free", (void (Teuchos::DeallocNull<ROL::Vector<double>>::*)(class ROL::Vector<double> *)) &Teuchos::DeallocNull<ROL::Vector<double>>::free, "C++: Teuchos::DeallocNull<ROL::Vector<double>>::free(class ROL::Vector<double> *) --> void", pybind11::arg("ptr"));
	}
	{ // Teuchos::DeallocNull file:Teuchos_RCPDecl.hpp line:964
		pybind11::class_<Teuchos::DeallocNull<ROL::ElasticObjective<double>>, Teuchos::RCP<Teuchos::DeallocNull<ROL::ElasticObjective<double>>>> cl(M("Teuchos"), "DeallocNull_ROL_ElasticObjective_double_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::DeallocNull<ROL::ElasticObjective<double>>(); } ) );
		cl.def( pybind11::init( [](Teuchos::DeallocNull<ROL::ElasticObjective<double>> const &o){ return new Teuchos::DeallocNull<ROL::ElasticObjective<double>>(o); } ) );
		cl.def("free", (void (Teuchos::DeallocNull<ROL::ElasticObjective<double>>::*)(class ROL::ElasticObjective<double> *)) &Teuchos::DeallocNull<ROL::ElasticObjective<double>>::free, "C++: Teuchos::DeallocNull<ROL::ElasticObjective<double>>::free(class ROL::ElasticObjective<double> *) --> void", pybind11::arg("ptr"));
	}
	{ // Teuchos::DeallocNull file:Teuchos_RCPDecl.hpp line:964
		pybind11::class_<Teuchos::DeallocNull<ROL::details::basic_nullstream<char, std::char_traits<char> >>, Teuchos::RCP<Teuchos::DeallocNull<ROL::details::basic_nullstream<char, std::char_traits<char> >>>> cl(M("Teuchos"), "DeallocNull_ROL_details_basic_nullstream_char_std_char_traits_char_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::DeallocNull<ROL::details::basic_nullstream<char, std::char_traits<char> >>(); } ) );
		cl.def( pybind11::init( [](Teuchos::DeallocNull<ROL::details::basic_nullstream<char, std::char_traits<char> >> const &o){ return new Teuchos::DeallocNull<ROL::details::basic_nullstream<char, std::char_traits<char> >>(o); } ) );
		cl.def("free", (void (Teuchos::DeallocNull<ROL::details::basic_nullstream<char, std::char_traits<char> >>::*)(class ROL::details::basic_nullstream<char, struct std::char_traits<char> > *)) &Teuchos::DeallocNull<ROL::details::basic_nullstream<char, std::char_traits<char>>>::free, "C++: Teuchos::DeallocNull<ROL::details::basic_nullstream<char, std::char_traits<char>>>::free(class ROL::details::basic_nullstream<char, struct std::char_traits<char> > *) --> void", pybind11::arg("ptr"));
	}
	{ // Teuchos::DeallocNull file:Teuchos_RCPDecl.hpp line:964
		pybind11::class_<Teuchos::DeallocNull<const ROL::Vector<double>>, Teuchos::RCP<Teuchos::DeallocNull<const ROL::Vector<double>>>> cl(M("Teuchos"), "DeallocNull_const_ROL_Vector_double_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::DeallocNull<const ROL::Vector<double>>(); } ) );
		cl.def( pybind11::init( [](Teuchos::DeallocNull<const ROL::Vector<double>> const &o){ return new Teuchos::DeallocNull<const ROL::Vector<double>>(o); } ) );
		cl.def("free", (void (Teuchos::DeallocNull<const ROL::Vector<double>>::*)(const class ROL::Vector<double> *)) &Teuchos::DeallocNull<const ROL::Vector<double>>::free, "C++: Teuchos::DeallocNull<const ROL::Vector<double>>::free(const class ROL::Vector<double> *) --> void", pybind11::arg("ptr"));
	}
	{ // Teuchos::DeallocNull file:Teuchos_RCPDecl.hpp line:964
		pybind11::class_<Teuchos::DeallocNull<ROL::Constraint_SimOpt<double>>, Teuchos::RCP<Teuchos::DeallocNull<ROL::Constraint_SimOpt<double>>>> cl(M("Teuchos"), "DeallocNull_ROL_Constraint_SimOpt_double_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::DeallocNull<ROL::Constraint_SimOpt<double>>(); } ) );
		cl.def( pybind11::init( [](Teuchos::DeallocNull<ROL::Constraint_SimOpt<double>> const &o){ return new Teuchos::DeallocNull<ROL::Constraint_SimOpt<double>>(o); } ) );
		cl.def("free", (void (Teuchos::DeallocNull<ROL::Constraint_SimOpt<double>>::*)(class ROL::Constraint_SimOpt<double> *)) &Teuchos::DeallocNull<ROL::Constraint_SimOpt<double>>::free, "C++: Teuchos::DeallocNull<ROL::Constraint_SimOpt<double>>::free(class ROL::Constraint_SimOpt<double> *) --> void", pybind11::arg("ptr"));
	}
	{ // Teuchos::DeallocNull file:Teuchos_RCPDecl.hpp line:964
		pybind11::class_<Teuchos::DeallocNull<ROL::DynamicConstraint<double>>, Teuchos::RCP<Teuchos::DeallocNull<ROL::DynamicConstraint<double>>>> cl(M("Teuchos"), "DeallocNull_ROL_DynamicConstraint_double_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::DeallocNull<ROL::DynamicConstraint<double>>(); } ) );
		cl.def( pybind11::init( [](Teuchos::DeallocNull<ROL::DynamicConstraint<double>> const &o){ return new Teuchos::DeallocNull<ROL::DynamicConstraint<double>>(o); } ) );
		cl.def("free", (void (Teuchos::DeallocNull<ROL::DynamicConstraint<double>>::*)(class ROL::DynamicConstraint<double> *)) &Teuchos::DeallocNull<ROL::DynamicConstraint<double>>::free, "C++: Teuchos::DeallocNull<ROL::DynamicConstraint<double>>::free(class ROL::DynamicConstraint<double> *) --> void", pybind11::arg("ptr"));
	}
	{ // Teuchos::DeallocNull file:Teuchos_RCPDecl.hpp line:964
		pybind11::class_<Teuchos::DeallocNull<const ROL::TimeStamp<double>>, Teuchos::RCP<Teuchos::DeallocNull<const ROL::TimeStamp<double>>>> cl(M("Teuchos"), "DeallocNull_const_ROL_TimeStamp_double_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::DeallocNull<const ROL::TimeStamp<double>>(); } ) );
		cl.def( pybind11::init( [](Teuchos::DeallocNull<const ROL::TimeStamp<double>> const &o){ return new Teuchos::DeallocNull<const ROL::TimeStamp<double>>(o); } ) );
		cl.def("free", (void (Teuchos::DeallocNull<const ROL::TimeStamp<double>>::*)(const struct ROL::TimeStamp<double> *)) &Teuchos::DeallocNull<const ROL::TimeStamp<double>>::free, "C++: Teuchos::DeallocNull<const ROL::TimeStamp<double>>::free(const struct ROL::TimeStamp<double> *) --> void", pybind11::arg("ptr"));
	}
	{ // Teuchos::DeallocNull file:Teuchos_RCPDecl.hpp line:964
		pybind11::class_<Teuchos::DeallocNull<Teuchos::ParameterList>, Teuchos::RCP<Teuchos::DeallocNull<Teuchos::ParameterList>>> cl(M("Teuchos"), "DeallocNull_Teuchos_ParameterList_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::DeallocNull<Teuchos::ParameterList>(); } ) );
		cl.def( pybind11::init( [](Teuchos::DeallocNull<Teuchos::ParameterList> const &o){ return new Teuchos::DeallocNull<Teuchos::ParameterList>(o); } ) );
		cl.def("free", (void (Teuchos::DeallocNull<Teuchos::ParameterList>::*)(class Teuchos::ParameterList *)) &Teuchos::DeallocNull<Teuchos::ParameterList>::free, "C++: Teuchos::DeallocNull<Teuchos::ParameterList>::free(class Teuchos::ParameterList *) --> void", pybind11::arg("ptr"));
	}
	{ // Teuchos::DeallocNull file:Teuchos_RCPDecl.hpp line:964
		pybind11::class_<Teuchos::DeallocNull<std::vector<double>>, Teuchos::RCP<Teuchos::DeallocNull<std::vector<double>>>> cl(M("Teuchos"), "DeallocNull_std_vector_double_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::DeallocNull<std::vector<double>>(); } ) );
		cl.def( pybind11::init( [](Teuchos::DeallocNull<std::vector<double>> const &o){ return new Teuchos::DeallocNull<std::vector<double>>(o); } ) );
		cl.def("free", (void (Teuchos::DeallocNull<std::vector<double>>::*)(class std::vector<double> *)) &Teuchos::DeallocNull<std::vector<double>>::free, "C++: Teuchos::DeallocNull<std::vector<double>>::free(class std::vector<double> *) --> void", pybind11::arg("ptr"));
	}
	{ // Teuchos::DeallocNull file:Teuchos_RCPDecl.hpp line:964
		pybind11::class_<Teuchos::DeallocNull<const ROL::ProbabilityVector<double>>, Teuchos::RCP<Teuchos::DeallocNull<const ROL::ProbabilityVector<double>>>> cl(M("Teuchos"), "DeallocNull_const_ROL_ProbabilityVector_double_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::DeallocNull<const ROL::ProbabilityVector<double>>(); } ) );
		cl.def( pybind11::init( [](Teuchos::DeallocNull<const ROL::ProbabilityVector<double>> const &o){ return new Teuchos::DeallocNull<const ROL::ProbabilityVector<double>>(o); } ) );
		cl.def("free", (void (Teuchos::DeallocNull<const ROL::ProbabilityVector<double>>::*)(const class ROL::ProbabilityVector<double> *)) &Teuchos::DeallocNull<const ROL::ProbabilityVector<double>>::free, "C++: Teuchos::DeallocNull<const ROL::ProbabilityVector<double>>::free(const class ROL::ProbabilityVector<double> *) --> void", pybind11::arg("ptr"));
	}
	// Teuchos::rcpFromRef(std::ostream &) file:Teuchos_RCP.hpp line:616
	M("Teuchos").def("rcpFromRef", (class Teuchos::RCP<std::ostream > (*)(std::ostream &)) &Teuchos::rcpFromRef<std::ostream>, "C++: Teuchos::rcpFromRef(std::ostream &) --> class Teuchos::RCP<std::ostream >", pybind11::arg("r"));

	// Teuchos::rcpFromRef(class Teuchos::ParameterEntry &) file:Teuchos_RCPDecl.hpp line:1265
	M("Teuchos").def("rcpFromRef", (class Teuchos::RCP<class Teuchos::ParameterEntry> (*)(class Teuchos::ParameterEntry &)) &Teuchos::rcpFromRef<Teuchos::ParameterEntry>, "C++: Teuchos::rcpFromRef(class Teuchos::ParameterEntry &) --> class Teuchos::RCP<class Teuchos::ParameterEntry>", pybind11::arg("r"));

	// Teuchos::rcpFromRef(const class Teuchos::ParameterEntry &) file:Teuchos_RCPDecl.hpp line:1265
	M("Teuchos").def("rcpFromRef", (class Teuchos::RCP<const class Teuchos::ParameterEntry> (*)(const class Teuchos::ParameterEntry &)) &Teuchos::rcpFromRef<const Teuchos::ParameterEntry>, "C++: Teuchos::rcpFromRef(const class Teuchos::ParameterEntry &) --> class Teuchos::RCP<const class Teuchos::ParameterEntry>", pybind11::arg("r"));

	// Teuchos::rcpFromRef(class ROL::Objective<double> &) file:Teuchos_RCP.hpp line:616
	M("Teuchos").def("rcpFromRef", (class Teuchos::RCP<class ROL::Objective<double> > (*)(class ROL::Objective<double> &)) &Teuchos::rcpFromRef<ROL::Objective<double>>, "C++: Teuchos::rcpFromRef(class ROL::Objective<double> &) --> class Teuchos::RCP<class ROL::Objective<double> >", pybind11::arg("r"));

	// Teuchos::rcpFromRef(class ROL::Constraint<double> &) file:Teuchos_RCP.hpp line:616
	M("Teuchos").def("rcpFromRef", (class Teuchos::RCP<class ROL::Constraint<double> > (*)(class ROL::Constraint<double> &)) &Teuchos::rcpFromRef<ROL::Constraint<double>>, "C++: Teuchos::rcpFromRef(class ROL::Constraint<double> &) --> class Teuchos::RCP<class ROL::Constraint<double> >", pybind11::arg("r"));

	// Teuchos::rcpFromRef(class ROL::BoundConstraint<double> &) file:Teuchos_RCP.hpp line:616
	M("Teuchos").def("rcpFromRef", (class Teuchos::RCP<class ROL::BoundConstraint<double> > (*)(class ROL::BoundConstraint<double> &)) &Teuchos::rcpFromRef<ROL::BoundConstraint<double>>, "C++: Teuchos::rcpFromRef(class ROL::BoundConstraint<double> &) --> class Teuchos::RCP<class ROL::BoundConstraint<double> >", pybind11::arg("r"));

	// Teuchos::rcpFromRef(class ROL::Vector<double> &) file:Teuchos_RCP.hpp line:616
	M("Teuchos").def("rcpFromRef", (class Teuchos::RCP<class ROL::Vector<double> > (*)(class ROL::Vector<double> &)) &Teuchos::rcpFromRef<ROL::Vector<double>>, "C++: Teuchos::rcpFromRef(class ROL::Vector<double> &) --> class Teuchos::RCP<class ROL::Vector<double> >", pybind11::arg("r"));

	// Teuchos::rcpFromRef(class ROL::ElasticObjective<double> &) file:Teuchos_RCP.hpp line:616
	M("Teuchos").def("rcpFromRef", (class Teuchos::RCP<class ROL::ElasticObjective<double> > (*)(class ROL::ElasticObjective<double> &)) &Teuchos::rcpFromRef<ROL::ElasticObjective<double>>, "C++: Teuchos::rcpFromRef(class ROL::ElasticObjective<double> &) --> class Teuchos::RCP<class ROL::ElasticObjective<double> >", pybind11::arg("r"));

	// Teuchos::rcpFromRef(class ROL::details::basic_nullstream<char, struct std::char_traits<char> > &) file:Teuchos_RCP.hpp line:616
	M("Teuchos").def("rcpFromRef", (class Teuchos::RCP<class ROL::details::basic_nullstream<char, struct std::char_traits<char> > > (*)(class ROL::details::basic_nullstream<char, struct std::char_traits<char> > &)) &Teuchos::rcpFromRef<ROL::details::basic_nullstream<char, std::char_traits<char> >>, "C++: Teuchos::rcpFromRef(class ROL::details::basic_nullstream<char, struct std::char_traits<char> > &) --> class Teuchos::RCP<class ROL::details::basic_nullstream<char, struct std::char_traits<char> > >", pybind11::arg("r"));

	// Teuchos::rcpFromRef(const class ROL::Vector<double> &) file:Teuchos_RCP.hpp line:616
	M("Teuchos").def("rcpFromRef", (class Teuchos::RCP<const class ROL::Vector<double> > (*)(const class ROL::Vector<double> &)) &Teuchos::rcpFromRef<const ROL::Vector<double>>, "C++: Teuchos::rcpFromRef(const class ROL::Vector<double> &) --> class Teuchos::RCP<const class ROL::Vector<double> >", pybind11::arg("r"));

	// Teuchos::rcpFromRef(class ROL::Constraint_SimOpt<double> &) file:Teuchos_RCP.hpp line:616
	M("Teuchos").def("rcpFromRef", (class Teuchos::RCP<class ROL::Constraint_SimOpt<double> > (*)(class ROL::Constraint_SimOpt<double> &)) &Teuchos::rcpFromRef<ROL::Constraint_SimOpt<double>>, "C++: Teuchos::rcpFromRef(class ROL::Constraint_SimOpt<double> &) --> class Teuchos::RCP<class ROL::Constraint_SimOpt<double> >", pybind11::arg("r"));

	// Teuchos::rcpFromRef(class ROL::DynamicConstraint<double> &) file:Teuchos_RCP.hpp line:616
	M("Teuchos").def("rcpFromRef", (class Teuchos::RCP<class ROL::DynamicConstraint<double> > (*)(class ROL::DynamicConstraint<double> &)) &Teuchos::rcpFromRef<ROL::DynamicConstraint<double>>, "C++: Teuchos::rcpFromRef(class ROL::DynamicConstraint<double> &) --> class Teuchos::RCP<class ROL::DynamicConstraint<double> >", pybind11::arg("r"));

	// Teuchos::rcpFromRef(const struct ROL::TimeStamp<double> &) file:Teuchos_RCP.hpp line:616
	M("Teuchos").def("rcpFromRef", (class Teuchos::RCP<const struct ROL::TimeStamp<double> > (*)(const struct ROL::TimeStamp<double> &)) &Teuchos::rcpFromRef<const ROL::TimeStamp<double>>, "C++: Teuchos::rcpFromRef(const struct ROL::TimeStamp<double> &) --> class Teuchos::RCP<const struct ROL::TimeStamp<double> >", pybind11::arg("r"));

	// Teuchos::rcpFromRef(class Teuchos::ParameterList &) file:Teuchos_RCP.hpp line:616
	M("Teuchos").def("rcpFromRef", (class Teuchos::RCP<class Teuchos::ParameterList> (*)(class Teuchos::ParameterList &)) &Teuchos::rcpFromRef<Teuchos::ParameterList>, "C++: Teuchos::rcpFromRef(class Teuchos::ParameterList &) --> class Teuchos::RCP<class Teuchos::ParameterList>", pybind11::arg("r"));

	// Teuchos::rcpFromRef(class std::vector<double> &) file:Teuchos_RCP.hpp line:616
	M("Teuchos").def("rcpFromRef", (class Teuchos::RCP<class std::vector<double> > (*)(class std::vector<double> &)) &Teuchos::rcpFromRef<std::vector<double>>, "C++: Teuchos::rcpFromRef(class std::vector<double> &) --> class Teuchos::RCP<class std::vector<double> >", pybind11::arg("r"));

	// Teuchos::rcpFromRef(const class ROL::ProbabilityVector<double> &) file:Teuchos_RCP.hpp line:616
	M("Teuchos").def("rcpFromRef", (class Teuchos::RCP<const class ROL::ProbabilityVector<double> > (*)(const class ROL::ProbabilityVector<double> &)) &Teuchos::rcpFromRef<const ROL::ProbabilityVector<double>>, "C++: Teuchos::rcpFromRef(const class ROL::ProbabilityVector<double> &) --> class Teuchos::RCP<const class ROL::ProbabilityVector<double> >", pybind11::arg("r"));

	// Teuchos::rcpWithEmbeddedObjPostDestroy(class Teuchos::ParameterList *, const class Teuchos::RCP<class Teuchos::ParameterList> &, bool) file:Teuchos_RCP.hpp line:644
	M("Teuchos").def("rcpWithEmbeddedObjPostDestroy", [](class Teuchos::ParameterList * a0, const class Teuchos::RCP<class Teuchos::ParameterList> & a1) -> Teuchos::RCP<class Teuchos::ParameterList> { return Teuchos::rcpWithEmbeddedObjPostDestroy(a0, a1); }, "", pybind11::arg("p"), pybind11::arg("embedded"));
	M("Teuchos").def("rcpWithEmbeddedObjPostDestroy", (class Teuchos::RCP<class Teuchos::ParameterList> (*)(class Teuchos::ParameterList *, const class Teuchos::RCP<class Teuchos::ParameterList> &, bool)) &Teuchos::rcpWithEmbeddedObjPostDestroy<Teuchos::ParameterList,Teuchos::RCP<Teuchos::ParameterList>>, "C++: Teuchos::rcpWithEmbeddedObjPostDestroy(class Teuchos::ParameterList *, const class Teuchos::RCP<class Teuchos::ParameterList> &, bool) --> class Teuchos::RCP<class Teuchos::ParameterList>", pybind11::arg("p"), pybind11::arg("embedded"), pybind11::arg("owns_mem"));

	// Teuchos::rcpWithEmbeddedObjPostDestroy(const class Teuchos::ParameterList *, const class Teuchos::RCP<const class Teuchos::ParameterList> &, bool) file:Teuchos_RCP.hpp line:644
	M("Teuchos").def("rcpWithEmbeddedObjPostDestroy", [](const class Teuchos::ParameterList * a0, const class Teuchos::RCP<const class Teuchos::ParameterList> & a1) -> Teuchos::RCP<const class Teuchos::ParameterList> { return Teuchos::rcpWithEmbeddedObjPostDestroy(a0, a1); }, "", pybind11::arg("p"), pybind11::arg("embedded"));
	M("Teuchos").def("rcpWithEmbeddedObjPostDestroy", (class Teuchos::RCP<const class Teuchos::ParameterList> (*)(const class Teuchos::ParameterList *, const class Teuchos::RCP<const class Teuchos::ParameterList> &, bool)) &Teuchos::rcpWithEmbeddedObjPostDestroy<const Teuchos::ParameterList,Teuchos::RCP<const Teuchos::ParameterList>>, "C++: Teuchos::rcpWithEmbeddedObjPostDestroy(const class Teuchos::ParameterList *, const class Teuchos::RCP<const class Teuchos::ParameterList> &, bool) --> class Teuchos::RCP<const class Teuchos::ParameterList>", pybind11::arg("p"), pybind11::arg("embedded"), pybind11::arg("owns_mem"));

	// Teuchos::nonnull(const class Teuchos::RCP<std::ostream > &) file:Teuchos_RCP.hpp line:691
	M("Teuchos").def("nonnull", (bool (*)(const class Teuchos::RCP<std::ostream > &)) &Teuchos::nonnull<std::ostream>, "C++: Teuchos::nonnull(const class Teuchos::RCP<std::ostream > &) --> bool", pybind11::arg("p"));

	// Teuchos::nonnull(const class Teuchos::RCP<class Teuchos::basic_FancyOStream<char> > &) file:Teuchos_RCP.hpp line:691
	M("Teuchos").def("nonnull", (bool (*)(const class Teuchos::RCP<class Teuchos::basic_FancyOStream<char> > &)) &Teuchos::nonnull<Teuchos::basic_FancyOStream<char>>, "C++: Teuchos::nonnull(const class Teuchos::RCP<class Teuchos::basic_FancyOStream<char> > &) --> bool", pybind11::arg("p"));

	// Teuchos::nonnull(const class Teuchos::RCP<const class Teuchos::ParameterEntryValidator> &) file:Teuchos_RCP.hpp line:691
	M("Teuchos").def("nonnull", (bool (*)(const class Teuchos::RCP<const class Teuchos::ParameterEntryValidator> &)) &Teuchos::nonnull<const Teuchos::ParameterEntryValidator>, "C++: Teuchos::nonnull(const class Teuchos::RCP<const class Teuchos::ParameterEntryValidator> &) --> bool", pybind11::arg("p"));

	// Teuchos::rcp_static_cast(const class Teuchos::RCP<const struct ROL::TypeP::AlgorithmState<double> > &) file:Teuchos_RCP.hpp line:743
	M("Teuchos").def("rcp_static_cast", (class Teuchos::RCP<const struct ROL::TypeP::AlgorithmState<double> > (*)(const class Teuchos::RCP<const struct ROL::TypeP::AlgorithmState<double> > &)) &Teuchos::rcp_static_cast<const ROL::TypeP::AlgorithmState<double>,const ROL::TypeP::AlgorithmState<double>>, "C++: Teuchos::rcp_static_cast(const class Teuchos::RCP<const struct ROL::TypeP::AlgorithmState<double> > &) --> class Teuchos::RCP<const struct ROL::TypeP::AlgorithmState<double> >", pybind11::arg("p1"));

	// Teuchos::rcp_static_cast(const class Teuchos::RCP<const struct ROL::TypeB::AlgorithmState<double> > &) file:Teuchos_RCP.hpp line:743
	M("Teuchos").def("rcp_static_cast", (class Teuchos::RCP<const struct ROL::TypeB::AlgorithmState<double> > (*)(const class Teuchos::RCP<const struct ROL::TypeB::AlgorithmState<double> > &)) &Teuchos::rcp_static_cast<const ROL::TypeB::AlgorithmState<double>,const ROL::TypeB::AlgorithmState<double>>, "C++: Teuchos::rcp_static_cast(const class Teuchos::RCP<const struct ROL::TypeB::AlgorithmState<double> > &) --> class Teuchos::RCP<const struct ROL::TypeB::AlgorithmState<double> >", pybind11::arg("p1"));

	// Teuchos::rcp_static_cast(const class Teuchos::RCP<class ROL::Vector<double> > &) file:Teuchos_RCP.hpp line:743
	M("Teuchos").def("rcp_static_cast", (class Teuchos::RCP<class ROL::StdVector<double> > (*)(const class Teuchos::RCP<class ROL::Vector<double> > &)) &Teuchos::rcp_static_cast<ROL::StdVector<double>,ROL::Vector<double>>, "C++: Teuchos::rcp_static_cast(const class Teuchos::RCP<class ROL::Vector<double> > &) --> class Teuchos::RCP<class ROL::StdVector<double> >", pybind11::arg("p1"));

	// Teuchos::rcp_const_cast(const class Teuchos::RCP<const class ROL::Vector<double> > &) file:Teuchos_RCP.hpp line:754
	M("Teuchos").def("rcp_const_cast", (class Teuchos::RCP<class ROL::Vector<double> > (*)(const class Teuchos::RCP<const class ROL::Vector<double> > &)) &Teuchos::rcp_const_cast<ROL::Vector<double>,const ROL::Vector<double>>, "C++: Teuchos::rcp_const_cast(const class Teuchos::RCP<const class ROL::Vector<double> > &) --> class Teuchos::RCP<class ROL::Vector<double> >", pybind11::arg("p1"));

	{ // Teuchos::m_bad_cast file:Teuchos_dyn_cast.hpp line:28
		pybind11::class_<Teuchos::m_bad_cast, Teuchos::RCP<Teuchos::m_bad_cast>, PyCallBack_Teuchos_m_bad_cast> cl(M("Teuchos"), "m_bad_cast", "Exception class for bad cast.\n\n\nWe create this class so that we may throw a bad_cast when appropriate and\nstill use the TEUCHOS_TEST_FOR_EXCEPTION macro.  We recommend users try to catch a\nbad_cast.", pybind11::module_local());
		cl.def( pybind11::init<const std::string &>(), pybind11::arg("what_arg") );

		cl.def( pybind11::init( [](PyCallBack_Teuchos_m_bad_cast const &o){ return new PyCallBack_Teuchos_m_bad_cast(o); } ) );
		cl.def( pybind11::init( [](Teuchos::m_bad_cast const &o){ return new Teuchos::m_bad_cast(o); } ) );
		cl.def("what", (const char * (Teuchos::m_bad_cast::*)() const) &Teuchos::m_bad_cast::what, "C++: Teuchos::m_bad_cast::what() const --> const char *", pybind11::return_value_policy::automatic);
		cl.def("assign", (class Teuchos::m_bad_cast & (Teuchos::m_bad_cast::*)(const class Teuchos::m_bad_cast &)) &Teuchos::m_bad_cast::operator=, "C++: Teuchos::m_bad_cast::operator=(const class Teuchos::m_bad_cast &) --> class Teuchos::m_bad_cast &", pybind11::return_value_policy::automatic, pybind11::arg(""));
	}
	// Teuchos::dyn_cast_throw_exception(const std::string &, const std::string &, const std::string &) file:Teuchos_dyn_cast.hpp line:38
	M("Teuchos").def("dyn_cast_throw_exception", (void (*)(const std::string &, const std::string &, const std::string &)) &Teuchos::dyn_cast_throw_exception, "C++: Teuchos::dyn_cast_throw_exception(const std::string &, const std::string &, const std::string &) --> void", pybind11::arg("T_from"), pybind11::arg("T_from_concr"), pybind11::arg("T_to"));

	// Teuchos::dyn_cast(std::ostream &) file:Teuchos_dyn_cast.hpp line:141
	M("Teuchos").def("dyn_cast", (class Teuchos::basic_FancyOStream<char> & (*)(std::ostream &)) &Teuchos::dyn_cast<Teuchos::basic_FancyOStream<char>,std::ostream>, "C++: Teuchos::dyn_cast(std::ostream &) --> class Teuchos::basic_FancyOStream<char> &", pybind11::return_value_policy::automatic, pybind11::arg("from"));

	// Teuchos::dyn_cast(class ROL::RiskVector<double> &) file:Teuchos_dyn_cast.hpp line:141
	M("Teuchos").def("dyn_cast", (class ROL::RiskVector<double> & (*)(class ROL::RiskVector<double> &)) &Teuchos::dyn_cast<ROL::RiskVector<double>,ROL::RiskVector<double>>, "C++: Teuchos::dyn_cast(class ROL::RiskVector<double> &) --> class ROL::RiskVector<double> &", pybind11::return_value_policy::automatic, pybind11::arg("from"));

	// Teuchos::dyn_cast(class ROL::Vector<double> &) file:Teuchos_dyn_cast.hpp line:141
	M("Teuchos").def("dyn_cast", (class ROL::RiskVector<double> & (*)(class ROL::Vector<double> &)) &Teuchos::dyn_cast<ROL::RiskVector<double>,ROL::Vector<double>>, "C++: Teuchos::dyn_cast(class ROL::Vector<double> &) --> class ROL::RiskVector<double> &", pybind11::return_value_policy::automatic, pybind11::arg("from"));

	// Teuchos::dyn_cast(class ROL::Constraint<double> &) file:Teuchos_dyn_cast.hpp line:141
	M("Teuchos").def("dyn_cast", (class ROL::ConstraintFromObjective<double> & (*)(class ROL::Constraint<double> &)) &Teuchos::dyn_cast<ROL::ConstraintFromObjective<double>,ROL::Constraint<double>>, "C++: Teuchos::dyn_cast(class ROL::Constraint<double> &) --> class ROL::ConstraintFromObjective<double> &", pybind11::return_value_policy::automatic, pybind11::arg("from"));

	// Teuchos::dyn_cast(class ROL::Objective<double> &) file:Teuchos_dyn_cast.hpp line:141
	M("Teuchos").def("dyn_cast", (class ROL::StochasticObjective<double> & (*)(class ROL::Objective<double> &)) &Teuchos::dyn_cast<ROL::StochasticObjective<double>,ROL::Objective<double>>, "C++: Teuchos::dyn_cast(class ROL::Objective<double> &) --> class ROL::StochasticObjective<double> &", pybind11::return_value_policy::automatic, pybind11::arg("from"));

	// Teuchos::dyn_cast(class ROL::Constraint<double> &) file:Teuchos_dyn_cast.hpp line:141
	M("Teuchos").def("dyn_cast", (class ROL::StochasticConstraint<double> & (*)(class ROL::Constraint<double> &)) &Teuchos::dyn_cast<ROL::StochasticConstraint<double>,ROL::Constraint<double>>, "C++: Teuchos::dyn_cast(class ROL::Constraint<double> &) --> class ROL::StochasticConstraint<double> &", pybind11::return_value_policy::automatic, pybind11::arg("from"));

	// Teuchos::dyn_cast(class ROL::Vector<double> &) file:Teuchos_dyn_cast.hpp line:141
	M("Teuchos").def("dyn_cast", (class ROL::ProbabilityVector<double> & (*)(class ROL::Vector<double> &)) &Teuchos::dyn_cast<ROL::ProbabilityVector<double>,ROL::Vector<double>>, "C++: Teuchos::dyn_cast(class ROL::Vector<double> &) --> class ROL::ProbabilityVector<double> &", pybind11::return_value_policy::automatic, pybind11::arg("from"));

	// Teuchos::ptrFromRef(class Teuchos::ParameterEntry &) file:Teuchos_PtrDecl.hpp line:265
	M("Teuchos").def("ptrFromRef", (class Teuchos::Ptr<class Teuchos::ParameterEntry> (*)(class Teuchos::ParameterEntry &)) &Teuchos::ptrFromRef<Teuchos::ParameterEntry>, "C++: Teuchos::ptrFromRef(class Teuchos::ParameterEntry &) --> class Teuchos::Ptr<class Teuchos::ParameterEntry>", pybind11::arg("arg"));

	// Teuchos::ptrFromRef(const class Teuchos::ParameterEntry &) file:Teuchos_PtrDecl.hpp line:265
	M("Teuchos").def("ptrFromRef", (class Teuchos::Ptr<const class Teuchos::ParameterEntry> (*)(const class Teuchos::ParameterEntry &)) &Teuchos::ptrFromRef<const Teuchos::ParameterEntry>, "C++: Teuchos::ptrFromRef(const class Teuchos::ParameterEntry &) --> class Teuchos::Ptr<const class Teuchos::ParameterEntry>", pybind11::arg("arg"));

	// Teuchos::rcpFromPtr(const class Teuchos::Ptr<class Teuchos::ParameterEntry> &) file:Teuchos_PtrDecl.hpp line:276
	M("Teuchos").def("rcpFromPtr", (class Teuchos::RCP<class Teuchos::ParameterEntry> (*)(const class Teuchos::Ptr<class Teuchos::ParameterEntry> &)) &Teuchos::rcpFromPtr<Teuchos::ParameterEntry>, "C++: Teuchos::rcpFromPtr(const class Teuchos::Ptr<class Teuchos::ParameterEntry> &) --> class Teuchos::RCP<class Teuchos::ParameterEntry>", pybind11::arg("ptr"));

	// Teuchos::rcpFromPtr(const class Teuchos::Ptr<const class Teuchos::ParameterEntry> &) file:Teuchos_PtrDecl.hpp line:276
	M("Teuchos").def("rcpFromPtr", (class Teuchos::RCP<const class Teuchos::ParameterEntry> (*)(const class Teuchos::Ptr<const class Teuchos::ParameterEntry> &)) &Teuchos::rcpFromPtr<const Teuchos::ParameterEntry>, "C++: Teuchos::rcpFromPtr(const class Teuchos::Ptr<const class Teuchos::ParameterEntry> &) --> class Teuchos::RCP<const class Teuchos::ParameterEntry>", pybind11::arg("ptr"));

}
