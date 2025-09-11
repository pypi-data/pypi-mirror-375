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
#include <ROL_Ptr.hpp>
#include <ROL_RandVarFunctional.hpp>
#include <ROL_RiskVector.hpp>
#include <ROL_StdVector.hpp>
#include <ROL_StochasticConstraint.hpp>
#include <ROL_StochasticObjective.hpp>
#include <ROL_Stream.hpp>
#include <ROL_TimeStamp.hpp>
#include <ROL_TypeB_Algorithm.hpp>
#include <ROL_TypeP_Algorithm.hpp>
#include <ROL_Types.hpp>
#include <ROL_UpdateType.hpp>
#include <ROL_Vector.hpp>
#include <Teuchos_ENull.hpp>
#include <Teuchos_FilteredIterator.hpp>
#include <Teuchos_ParameterEntry.hpp>
#include <Teuchos_ParameterEntryValidator.hpp>
#include <Teuchos_ParameterList.hpp>
#include <Teuchos_ParameterListModifier.hpp>
#include <Teuchos_PtrDecl.hpp>
#include <Teuchos_RCPDecl.hpp>
#include <Teuchos_RCPNode.hpp>
#include <Teuchos_StringIndexedOrderedValueObjectContainer.hpp>
#include <Teuchos_any.hpp>
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

void bind_pyrol_10(std::function< pybind11::module &(std::string const &namespace_) > &M)
{
	// ROL::makePtrFromRef(std::ostream &) file:ROL_Ptr.hpp line:54
	M("ROL").def("makePtrFromRef", (class Teuchos::RCP<std::ostream > (*)(std::ostream &)) &ROL::makePtrFromRef<std::ostream>, "C++: ROL::makePtrFromRef(std::ostream &) --> class Teuchos::RCP<std::ostream >", pybind11::arg("obj"));

	// ROL::makePtrFromRef(class ROL::details::basic_nullstream<char, struct std::char_traits<char> > &) file:ROL_Ptr.hpp line:54
	M("ROL").def("makePtrFromRef", (class Teuchos::RCP<class ROL::details::basic_nullstream<char, struct std::char_traits<char> > > (*)(class ROL::details::basic_nullstream<char, struct std::char_traits<char> > &)) &ROL::makePtrFromRef<ROL::details::basic_nullstream<char, std::char_traits<char> >>, "C++: ROL::makePtrFromRef(class ROL::details::basic_nullstream<char, struct std::char_traits<char> > &) --> class Teuchos::RCP<class ROL::details::basic_nullstream<char, struct std::char_traits<char> > >", pybind11::arg("obj"));

	// ROL::makePtrFromRef(class Teuchos::ParameterList &) file:ROL_Ptr.hpp line:54
	M("ROL").def("makePtrFromRef", (class Teuchos::RCP<class Teuchos::ParameterList> (*)(class Teuchos::ParameterList &)) &ROL::makePtrFromRef<Teuchos::ParameterList>, "C++: ROL::makePtrFromRef(class Teuchos::ParameterList &) --> class Teuchos::RCP<class Teuchos::ParameterList>", pybind11::arg("obj"));

	// ROL::makePtrFromRef(const class ROL::Vector<double> &) file:ROL_Ptr.hpp line:54
	M("ROL").def("makePtrFromRef", (class Teuchos::RCP<const class ROL::Vector<double> > (*)(const class ROL::Vector<double> &)) &ROL::makePtrFromRef<const ROL::Vector<double>>, "C++: ROL::makePtrFromRef(const class ROL::Vector<double> &) --> class Teuchos::RCP<const class ROL::Vector<double> >", pybind11::arg("obj"));

	// ROL::makePtrFromRef(class ROL::Objective<double> &) file:ROL_Ptr.hpp line:54
	M("ROL").def("makePtrFromRef", (class Teuchos::RCP<class ROL::Objective<double> > (*)(class ROL::Objective<double> &)) &ROL::makePtrFromRef<ROL::Objective<double>>, "C++: ROL::makePtrFromRef(class ROL::Objective<double> &) --> class Teuchos::RCP<class ROL::Objective<double> >", pybind11::arg("obj"));

	// ROL::makePtrFromRef(class ROL::Constraint<double> &) file:ROL_Ptr.hpp line:54
	M("ROL").def("makePtrFromRef", (class Teuchos::RCP<class ROL::Constraint<double> > (*)(class ROL::Constraint<double> &)) &ROL::makePtrFromRef<ROL::Constraint<double>>, "C++: ROL::makePtrFromRef(class ROL::Constraint<double> &) --> class Teuchos::RCP<class ROL::Constraint<double> >", pybind11::arg("obj"));

	// ROL::makePtrFromRef(class ROL::BoundConstraint<double> &) file:ROL_Ptr.hpp line:54
	M("ROL").def("makePtrFromRef", (class Teuchos::RCP<class ROL::BoundConstraint<double> > (*)(class ROL::BoundConstraint<double> &)) &ROL::makePtrFromRef<ROL::BoundConstraint<double>>, "C++: ROL::makePtrFromRef(class ROL::BoundConstraint<double> &) --> class Teuchos::RCP<class ROL::BoundConstraint<double> >", pybind11::arg("obj"));

	// ROL::makePtrFromRef(class ROL::Vector<double> &) file:ROL_Ptr.hpp line:54
	M("ROL").def("makePtrFromRef", (class Teuchos::RCP<class ROL::Vector<double> > (*)(class ROL::Vector<double> &)) &ROL::makePtrFromRef<ROL::Vector<double>>, "C++: ROL::makePtrFromRef(class ROL::Vector<double> &) --> class Teuchos::RCP<class ROL::Vector<double> >", pybind11::arg("obj"));

	// ROL::makePtrFromRef(class ROL::ElasticObjective<double> &) file:ROL_Ptr.hpp line:54
	M("ROL").def("makePtrFromRef", (class Teuchos::RCP<class ROL::ElasticObjective<double> > (*)(class ROL::ElasticObjective<double> &)) &ROL::makePtrFromRef<ROL::ElasticObjective<double>>, "C++: ROL::makePtrFromRef(class ROL::ElasticObjective<double> &) --> class Teuchos::RCP<class ROL::ElasticObjective<double> >", pybind11::arg("obj"));

	// ROL::makePtrFromRef(class ROL::Constraint_SimOpt<double> &) file:ROL_Ptr.hpp line:54
	M("ROL").def("makePtrFromRef", (class Teuchos::RCP<class ROL::Constraint_SimOpt<double> > (*)(class ROL::Constraint_SimOpt<double> &)) &ROL::makePtrFromRef<ROL::Constraint_SimOpt<double>>, "C++: ROL::makePtrFromRef(class ROL::Constraint_SimOpt<double> &) --> class Teuchos::RCP<class ROL::Constraint_SimOpt<double> >", pybind11::arg("obj"));

	// ROL::makePtrFromRef(class ROL::DynamicConstraint<double> &) file:ROL_Ptr.hpp line:54
	M("ROL").def("makePtrFromRef", (class Teuchos::RCP<class ROL::DynamicConstraint<double> > (*)(class ROL::DynamicConstraint<double> &)) &ROL::makePtrFromRef<ROL::DynamicConstraint<double>>, "C++: ROL::makePtrFromRef(class ROL::DynamicConstraint<double> &) --> class Teuchos::RCP<class ROL::DynamicConstraint<double> >", pybind11::arg("obj"));

	// ROL::makePtrFromRef(const struct ROL::TimeStamp<double> &) file:ROL_Ptr.hpp line:54
	M("ROL").def("makePtrFromRef", (class Teuchos::RCP<const struct ROL::TimeStamp<double> > (*)(const struct ROL::TimeStamp<double> &)) &ROL::makePtrFromRef<const ROL::TimeStamp<double>>, "C++: ROL::makePtrFromRef(const struct ROL::TimeStamp<double> &) --> class Teuchos::RCP<const struct ROL::TimeStamp<double> >", pybind11::arg("obj"));

	// ROL::makePtrFromRef(class std::vector<double> &) file:ROL_Ptr.hpp line:54
	M("ROL").def("makePtrFromRef", (class Teuchos::RCP<class std::vector<double> > (*)(class std::vector<double> &)) &ROL::makePtrFromRef<std::vector<double>>, "C++: ROL::makePtrFromRef(class std::vector<double> &) --> class Teuchos::RCP<class std::vector<double> >", pybind11::arg("obj"));

	// ROL::makePtrFromRef(const class ROL::ProbabilityVector<double> &) file:ROL_Ptr.hpp line:54
	M("ROL").def("makePtrFromRef", (class Teuchos::RCP<const class ROL::ProbabilityVector<double> > (*)(const class ROL::ProbabilityVector<double> &)) &ROL::makePtrFromRef<const ROL::ProbabilityVector<double>>, "C++: ROL::makePtrFromRef(const class ROL::ProbabilityVector<double> &) --> class Teuchos::RCP<const class ROL::ProbabilityVector<double> >", pybind11::arg("obj"));

	// ROL::staticPtrCast(const class Teuchos::RCP<const struct ROL::TypeP::AlgorithmState<double> > &) file:ROL_Ptr.hpp line:60
	M("ROL").def("staticPtrCast", (class Teuchos::RCP<const struct ROL::TypeP::AlgorithmState<double> > (*)(const class Teuchos::RCP<const struct ROL::TypeP::AlgorithmState<double> > &)) &ROL::staticPtrCast<const ROL::TypeP::AlgorithmState<double>,const ROL::TypeP::AlgorithmState<double>>, "C++: ROL::staticPtrCast(const class Teuchos::RCP<const struct ROL::TypeP::AlgorithmState<double> > &) --> class Teuchos::RCP<const struct ROL::TypeP::AlgorithmState<double> >", pybind11::arg("r"));

	// ROL::staticPtrCast(const class Teuchos::RCP<const struct ROL::TypeB::AlgorithmState<double> > &) file:ROL_Ptr.hpp line:60
	M("ROL").def("staticPtrCast", (class Teuchos::RCP<const struct ROL::TypeB::AlgorithmState<double> > (*)(const class Teuchos::RCP<const struct ROL::TypeB::AlgorithmState<double> > &)) &ROL::staticPtrCast<const ROL::TypeB::AlgorithmState<double>,const ROL::TypeB::AlgorithmState<double>>, "C++: ROL::staticPtrCast(const class Teuchos::RCP<const struct ROL::TypeB::AlgorithmState<double> > &) --> class Teuchos::RCP<const struct ROL::TypeB::AlgorithmState<double> >", pybind11::arg("r"));

	// ROL::staticPtrCast(const class Teuchos::RCP<class ROL::Vector<double> > &) file:ROL_Ptr.hpp line:60
	M("ROL").def("staticPtrCast", (class Teuchos::RCP<class ROL::StdVector<double> > (*)(const class Teuchos::RCP<class ROL::Vector<double> > &)) &ROL::staticPtrCast<ROL::StdVector<double>,ROL::Vector<double>>, "C++: ROL::staticPtrCast(const class Teuchos::RCP<class ROL::Vector<double> > &) --> class Teuchos::RCP<class ROL::StdVector<double> >", pybind11::arg("r"));

	// ROL::constPtrCast(const class Teuchos::RCP<const class ROL::Vector<double> > &) file:ROL_Ptr.hpp line:66
	M("ROL").def("constPtrCast", (class Teuchos::RCP<class ROL::Vector<double> > (*)(const class Teuchos::RCP<const class ROL::Vector<double> > &)) &ROL::constPtrCast<ROL::Vector<double>,const ROL::Vector<double>>, "C++: ROL::constPtrCast(const class Teuchos::RCP<const class ROL::Vector<double> > &) --> class Teuchos::RCP<class ROL::Vector<double> >", pybind11::arg("r"));

	// ROL::dynamicPtrCast(const class Teuchos::RCP<class ROL::Vector<double> > &) file:ROL_Ptr.hpp line:72
	M("ROL").def("dynamicPtrCast", (class Teuchos::RCP<class ROL::RiskVector<double> > (*)(const class Teuchos::RCP<class ROL::Vector<double> > &)) &ROL::dynamicPtrCast<ROL::RiskVector<double>,ROL::Vector<double>>, "C++: ROL::dynamicPtrCast(const class Teuchos::RCP<class ROL::Vector<double> > &) --> class Teuchos::RCP<class ROL::RiskVector<double> >", pybind11::arg("r"));

	// ROL::dynamicPtrCast(const class Teuchos::RCP<class ROL::Objective<double> > &) file:ROL_Ptr.hpp line:72
	M("ROL").def("dynamicPtrCast", (class Teuchos::RCP<class ROL::StochasticObjective<double> > (*)(const class Teuchos::RCP<class ROL::Objective<double> > &)) &ROL::dynamicPtrCast<ROL::StochasticObjective<double>,ROL::Objective<double>>, "C++: ROL::dynamicPtrCast(const class Teuchos::RCP<class ROL::Objective<double> > &) --> class Teuchos::RCP<class ROL::StochasticObjective<double> >", pybind11::arg("r"));

	// ROL::dynamicPtrCast(const class Teuchos::RCP<class ROL::Constraint<double> > &) file:ROL_Ptr.hpp line:72
	M("ROL").def("dynamicPtrCast", (class Teuchos::RCP<class ROL::StochasticConstraint<double> > (*)(const class Teuchos::RCP<class ROL::Constraint<double> > &)) &ROL::dynamicPtrCast<ROL::StochasticConstraint<double>,ROL::Constraint<double>>, "C++: ROL::dynamicPtrCast(const class Teuchos::RCP<class ROL::Constraint<double> > &) --> class Teuchos::RCP<class ROL::StochasticConstraint<double> >", pybind11::arg("r"));

	// ROL::dynamicPtrCast(const class Teuchos::RCP<class ROL::Vector<double> > &) file:ROL_Ptr.hpp line:72
	M("ROL").def("dynamicPtrCast", (class Teuchos::RCP<class ROL::ProbabilityVector<double> > (*)(const class Teuchos::RCP<class ROL::Vector<double> > &)) &ROL::dynamicPtrCast<ROL::ProbabilityVector<double>,ROL::Vector<double>>, "C++: ROL::dynamicPtrCast(const class Teuchos::RCP<class ROL::Vector<double> > &) --> class Teuchos::RCP<class ROL::ProbabilityVector<double> >", pybind11::arg("r"));

	// ROL::dynamicPtrCast(const class Teuchos::RCP<class ROL::RiskVector<double> > &) file:ROL_Ptr.hpp line:72
	M("ROL").def("dynamicPtrCast", (class Teuchos::RCP<class ROL::RiskVector<double> > (*)(const class Teuchos::RCP<class ROL::RiskVector<double> > &)) &ROL::dynamicPtrCast<ROL::RiskVector<double>,ROL::RiskVector<double>>, "C++: ROL::dynamicPtrCast(const class Teuchos::RCP<class ROL::RiskVector<double> > &) --> class Teuchos::RCP<class ROL::RiskVector<double> >", pybind11::arg("r"));

	// ROL::dynamicPtrCast(const class Teuchos::RCP<class ROL::Constraint<double> > &) file:ROL_Ptr.hpp line:72
	M("ROL").def("dynamicPtrCast", (class Teuchos::RCP<class ROL::ConstraintFromObjective<double> > (*)(const class Teuchos::RCP<class ROL::Constraint<double> > &)) &ROL::dynamicPtrCast<ROL::ConstraintFromObjective<double>,ROL::Constraint<double>>, "C++: ROL::dynamicPtrCast(const class Teuchos::RCP<class ROL::Constraint<double> > &) --> class Teuchos::RCP<class ROL::ConstraintFromObjective<double> >", pybind11::arg("r"));

	// ROL::getCount(const class Teuchos::RCP<class ROL::Vector<double> > &) file:ROL_Ptr.hpp line:90
	M("ROL").def("getCount", (int (*)(const class Teuchos::RCP<class ROL::Vector<double> > &)) &ROL::getCount<ROL::Vector<double>>, "C++: ROL::getCount(const class Teuchos::RCP<class ROL::Vector<double> > &) --> int", pybind11::arg("x"));

	// ROL::NumberToString(int) file:ROL_Types.hpp line:47
	M("ROL").def("NumberToString", (std::string (*)(int)) &ROL::NumberToString<int>, "C++: ROL::NumberToString(int) --> std::string", pybind11::arg("Number"));

	// ROL::ROL_EPSILON() file:ROL_Types.hpp line:57
	M("ROL").def("ROL_EPSILON", (double (*)()) &ROL::ROL_EPSILON<double>, "C++: ROL::ROL_EPSILON() --> double");

	// ROL::ROL_OVERFLOW() file:ROL_Types.hpp line:68
	M("ROL").def("ROL_OVERFLOW", (double (*)()) &ROL::ROL_OVERFLOW<double>, "C++: ROL::ROL_OVERFLOW() --> double");

	// ROL::ROL_INF() file:ROL_Types.hpp line:71
	M("ROL").def("ROL_INF", (double (*)()) &ROL::ROL_INF<double>, "C++: ROL::ROL_INF() --> double");

	// ROL::ROL_NINF() file:ROL_Types.hpp line:74
	M("ROL").def("ROL_NINF", (double (*)()) &ROL::ROL_NINF<double>, "C++: ROL::ROL_NINF() --> double");

	// ROL::ROL_UNDERFLOW() file:ROL_Types.hpp line:79
	M("ROL").def("ROL_UNDERFLOW", (double (*)()) &ROL::ROL_UNDERFLOW<double>, "C++: ROL::ROL_UNDERFLOW() --> double");

	// ROL::EExitStatus file:ROL_Types.hpp line:83
	pybind11::enum_<ROL::EExitStatus>(M("ROL"), "EExitStatus", pybind11::arithmetic(), "Enum for algorithm termination.", pybind11::module_local())
		.value("EXITSTATUS_CONVERGED", ROL::EXITSTATUS_CONVERGED)
		.value("EXITSTATUS_MAXITER", ROL::EXITSTATUS_MAXITER)
		.value("EXITSTATUS_STEPTOL", ROL::EXITSTATUS_STEPTOL)
		.value("EXITSTATUS_NAN", ROL::EXITSTATUS_NAN)
		.value("EXITSTATUS_USERDEFINED", ROL::EXITSTATUS_USERDEFINED)
		.value("EXITSTATUS_LAST", ROL::EXITSTATUS_LAST)
		.export_values();

;

	// ROL::EExitStatusToString(enum ROL::EExitStatus) file:ROL_Types.hpp line:92
	M("ROL").def("EExitStatusToString", (std::string (*)(enum ROL::EExitStatus)) &ROL::EExitStatusToString, "C++: ROL::EExitStatusToString(enum ROL::EExitStatus) --> std::string", pybind11::arg("tr"));

	{ // ROL::AlgorithmState file:ROL_Types.hpp line:109
		pybind11::class_<ROL::AlgorithmState<double>, Teuchos::RCP<ROL::AlgorithmState<double>>> cl(M("ROL"), "AlgorithmState_double_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new ROL::AlgorithmState<double>(); } ) );
		cl.def( pybind11::init( [](ROL::AlgorithmState<double> const &o){ return new ROL::AlgorithmState<double>(o); } ) );
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
	{ // ROL::removeSpecialCharacters file:ROL_Types.hpp line:209
		pybind11::class_<ROL::removeSpecialCharacters, Teuchos::RCP<ROL::removeSpecialCharacters>> cl(M("ROL"), "removeSpecialCharacters", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new ROL::removeSpecialCharacters(); } ) );
		cl.def( pybind11::init( [](ROL::removeSpecialCharacters const &o){ return new ROL::removeSpecialCharacters(o); } ) );
		cl.def("__call__", (bool (ROL::removeSpecialCharacters::*)(char)) &ROL::removeSpecialCharacters::operator(), "C++: ROL::removeSpecialCharacters::operator()(char) --> bool", pybind11::arg("c"));
	}
	// ROL::removeStringFormat(std::string) file:ROL_Types.hpp line:215
	M("ROL").def("removeStringFormat", (std::string (*)(std::string)) &ROL::removeStringFormat, "C++: ROL::removeStringFormat(std::string) --> std::string", pybind11::arg("s"));

	// ROL::EProblem file:ROL_Types.hpp line:223
	pybind11::enum_<ROL::EProblem>(M("ROL"), "EProblem", pybind11::arithmetic(), "", pybind11::module_local())
		.value("TYPE_U", ROL::TYPE_U)
		.value("TYPE_P", ROL::TYPE_P)
		.value("TYPE_B", ROL::TYPE_B)
		.value("TYPE_E", ROL::TYPE_E)
		.value("TYPE_EB", ROL::TYPE_EB)
		.value("TYPE_LAST", ROL::TYPE_LAST)
		.export_values();

;

	// ROL::EStep file:ROL_Types.hpp line:243
	pybind11::enum_<ROL::EStep>(M("ROL"), "EStep", pybind11::arithmetic(), "Enumeration of step types.\n\n      \n    AUGMENTEDLAGRANGIAN     describe\n      \n\n    BUNDLE                  describe\n      \n\n    COMPOSITESTEP           describe\n      \n\n    LINESEARCH              describe\n      \n\n    MOREAUYOSIDAPENALTY     describe\n      \n\n    PRIMALDUALACTIVESET     describe\n      \n\n    TRUSTREGION             describe", pybind11::module_local())
		.value("STEP_AUGMENTEDLAGRANGIAN", ROL::STEP_AUGMENTEDLAGRANGIAN)
		.value("STEP_BUNDLE", ROL::STEP_BUNDLE)
		.value("STEP_COMPOSITESTEP", ROL::STEP_COMPOSITESTEP)
		.value("STEP_LINESEARCH", ROL::STEP_LINESEARCH)
		.value("STEP_MOREAUYOSIDAPENALTY", ROL::STEP_MOREAUYOSIDAPENALTY)
		.value("STEP_PRIMALDUALACTIVESET", ROL::STEP_PRIMALDUALACTIVESET)
		.value("STEP_TRUSTREGION", ROL::STEP_TRUSTREGION)
		.value("STEP_INTERIORPOINT", ROL::STEP_INTERIORPOINT)
		.value("STEP_FLETCHER", ROL::STEP_FLETCHER)
		.value("STEP_LAST", ROL::STEP_LAST)
		.export_values();

;

	// ROL::EStepToString(enum ROL::EStep) file:ROL_Types.hpp line:256
	M("ROL").def("EStepToString", (std::string (*)(enum ROL::EStep)) &ROL::EStepToString, "C++: ROL::EStepToString(enum ROL::EStep) --> std::string", pybind11::arg("tr"));

	// ROL::isCompatibleStep(enum ROL::EProblem, enum ROL::EStep) file:ROL_Types.hpp line:274
	M("ROL").def("isCompatibleStep", (bool (*)(enum ROL::EProblem, enum ROL::EStep)) &ROL::isCompatibleStep, "C++: ROL::isCompatibleStep(enum ROL::EProblem, enum ROL::EStep) --> bool", pybind11::arg("p"), pybind11::arg("s"));

	// ROL::EProblemToString(enum ROL::EProblem) file:ROL_Types.hpp line:309
	M("ROL").def("EProblemToString", (std::string (*)(enum ROL::EProblem)) &ROL::EProblemToString, "C++: ROL::EProblemToString(enum ROL::EProblem) --> std::string", pybind11::arg("p"));

	// ROL::isValidStep(enum ROL::EStep) file:ROL_Types.hpp line:329
	M("ROL").def("isValidStep", (int (*)(enum ROL::EStep)) &ROL::isValidStep, "Verifies validity of a TrustRegion enum.\n\n      \n  [in]  - enum of the TrustRegion\n      \n\n 1 if the argument is a valid TrustRegion; 0 otherwise.\n\nC++: ROL::isValidStep(enum ROL::EStep) --> int", pybind11::arg("ls"));

	// ROL::StringToEStep(std::string) file:ROL_Types.hpp line:361
	M("ROL").def("StringToEStep", (enum ROL::EStep (*)(std::string)) &ROL::StringToEStep, "C++: ROL::StringToEStep(std::string) --> enum ROL::EStep", pybind11::arg("s"));

	// ROL::EDescent file:ROL_Types.hpp line:381
	pybind11::enum_<ROL::EDescent>(M("ROL"), "EDescent", pybind11::arithmetic(), "Enumeration of descent direction types.\n\n      \n    STEEPEST        describe\n      \n\n    NONLINEARCG     describe\n      \n\n    SECANT          describe\n      \n\n    NEWTON          describe \n      \n\n    NEWTONKRYLOV    describe\n      \n\n    SECANTPRECOND   describe", pybind11::module_local())
		.value("DESCENT_STEEPEST", ROL::DESCENT_STEEPEST)
		.value("DESCENT_NONLINEARCG", ROL::DESCENT_NONLINEARCG)
		.value("DESCENT_SECANT", ROL::DESCENT_SECANT)
		.value("DESCENT_NEWTON", ROL::DESCENT_NEWTON)
		.value("DESCENT_NEWTONKRYLOV", ROL::DESCENT_NEWTONKRYLOV)
		.value("DESCENT_LAST", ROL::DESCENT_LAST)
		.export_values();

;

	// ROL::EDescentToString(enum ROL::EDescent) file:ROL_Types.hpp line:390
	M("ROL").def("EDescentToString", (std::string (*)(enum ROL::EDescent)) &ROL::EDescentToString, "C++: ROL::EDescentToString(enum ROL::EDescent) --> std::string", pybind11::arg("tr"));

	// ROL::isValidDescent(enum ROL::EDescent) file:ROL_Types.hpp line:409
	M("ROL").def("isValidDescent", (int (*)(enum ROL::EDescent)) &ROL::isValidDescent, "Verifies validity of a Secant enum.\n\n      \n  [in]  - enum of the Secant\n      \n\n 1 if the argument is a valid Secant; 0 otherwise.\n\nC++: ROL::isValidDescent(enum ROL::EDescent) --> int", pybind11::arg("d"));

	// ROL::StringToEDescent(std::string) file:ROL_Types.hpp line:438
	M("ROL").def("StringToEDescent", (enum ROL::EDescent (*)(std::string)) &ROL::StringToEDescent, "C++: ROL::StringToEDescent(std::string) --> enum ROL::EDescent", pybind11::arg("s"));

	// ROL::ESecant file:ROL_Types.hpp line:456
	pybind11::enum_<ROL::ESecant>(M("ROL"), "ESecant", pybind11::arithmetic(), "Enumeration of secant update algorithms.\n\n      \n    LBFGS           describe\n      \n\n    LDFP            describe\n      \n\n    LSR1            describe \n      \n\n    BARZILAIBORWEIN describe", pybind11::module_local())
		.value("SECANT_LBFGS", ROL::SECANT_LBFGS)
		.value("SECANT_LDFP", ROL::SECANT_LDFP)
		.value("SECANT_LSR1", ROL::SECANT_LSR1)
		.value("SECANT_BARZILAIBORWEIN", ROL::SECANT_BARZILAIBORWEIN)
		.value("SECANT_USERDEFINED", ROL::SECANT_USERDEFINED)
		.value("SECANT_LAST", ROL::SECANT_LAST)
		.export_values();

;

	// ROL::ESecantToString(enum ROL::ESecant) file:ROL_Types.hpp line:465
	M("ROL").def("ESecantToString", (std::string (*)(enum ROL::ESecant)) &ROL::ESecantToString, "C++: ROL::ESecantToString(enum ROL::ESecant) --> std::string", pybind11::arg("tr"));

	// ROL::isValidSecant(enum ROL::ESecant) file:ROL_Types.hpp line:484
	M("ROL").def("isValidSecant", (int (*)(enum ROL::ESecant)) &ROL::isValidSecant, "Verifies validity of a Secant enum.\n\n      \n  [in]  - enum of the Secant\n      \n\n 1 if the argument is a valid Secant; 0 otherwise.\n\nC++: ROL::isValidSecant(enum ROL::ESecant) --> int", pybind11::arg("s"));

	// ROL::StringToESecant(std::string) file:ROL_Types.hpp line:513
	M("ROL").def("StringToESecant", (enum ROL::ESecant (*)(std::string)) &ROL::StringToESecant, "C++: ROL::StringToESecant(std::string) --> enum ROL::ESecant", pybind11::arg("s"));

	// ROL::ENonlinearCG file:ROL_Types.hpp line:536
	pybind11::enum_<ROL::ENonlinearCG>(M("ROL"), "ENonlinearCG", pybind11::arithmetic(), "Enumeration of nonlinear CG algorithms.\n\n      \n    HESTENES_STIEFEL   \n\n      \n    FLETCHER_REEVES    \n\n      \n    DANIEL             \n\n      \n    POLAK_RIBIERE      \n\n      \n    FLETCHER_CONJDESC  \n\n      \n    LIU_STOREY         \n\n      \n    DAI_YUAN           \n\n      \n    HAGER_ZHANG        \n\n      \n    OREN_LUENBERGER    \n ", pybind11::module_local())
		.value("NONLINEARCG_HESTENES_STIEFEL", ROL::NONLINEARCG_HESTENES_STIEFEL)
		.value("NONLINEARCG_FLETCHER_REEVES", ROL::NONLINEARCG_FLETCHER_REEVES)
		.value("NONLINEARCG_DANIEL", ROL::NONLINEARCG_DANIEL)
		.value("NONLINEARCG_POLAK_RIBIERE", ROL::NONLINEARCG_POLAK_RIBIERE)
		.value("NONLINEARCG_FLETCHER_CONJDESC", ROL::NONLINEARCG_FLETCHER_CONJDESC)
		.value("NONLINEARCG_LIU_STOREY", ROL::NONLINEARCG_LIU_STOREY)
		.value("NONLINEARCG_DAI_YUAN", ROL::NONLINEARCG_DAI_YUAN)
		.value("NONLINEARCG_HAGER_ZHANG", ROL::NONLINEARCG_HAGER_ZHANG)
		.value("NONLINEARCG_OREN_LUENBERGER", ROL::NONLINEARCG_OREN_LUENBERGER)
		.value("NONLINEARCG_USERDEFINED", ROL::NONLINEARCG_USERDEFINED)
		.value("NONLINEARCG_LAST", ROL::NONLINEARCG_LAST)
		.export_values();

;

	// ROL::ENonlinearCGToString(enum ROL::ENonlinearCG) file:ROL_Types.hpp line:550
	M("ROL").def("ENonlinearCGToString", (std::string (*)(enum ROL::ENonlinearCG)) &ROL::ENonlinearCGToString, "C++: ROL::ENonlinearCGToString(enum ROL::ENonlinearCG) --> std::string", pybind11::arg("tr"));

	// ROL::isValidNonlinearCG(enum ROL::ENonlinearCG) file:ROL_Types.hpp line:574
	M("ROL").def("isValidNonlinearCG", (int (*)(enum ROL::ENonlinearCG)) &ROL::isValidNonlinearCG, "Verifies validity of a NonlinearCG enum.\n\n      \n  [in]  - enum of the NonlinearCG\n      \n\n 1 if the argument is a valid NonlinearCG; 0 otherwise.\n\nC++: ROL::isValidNonlinearCG(enum ROL::ENonlinearCG) --> int", pybind11::arg("s"));

	// ROL::StringToENonlinearCG(std::string) file:ROL_Types.hpp line:608
	M("ROL").def("StringToENonlinearCG", (enum ROL::ENonlinearCG (*)(std::string)) &ROL::StringToENonlinearCG, "C++: ROL::StringToENonlinearCG(std::string) --> enum ROL::ENonlinearCG", pybind11::arg("s"));

	// ROL::ELineSearch file:ROL_Types.hpp line:628
	pybind11::enum_<ROL::ELineSearch>(M("ROL"), "ELineSearch", pybind11::arithmetic(), "Enumeration of line-search types.\n\n      \n    BACKTRACKING    describe\n      \n\n    BISECTION       describe\n      \n\n    GOLDENSECTION   describe\n      \n\n    CUBICINTERP     describe\n      \n\n    BRENTS          describe\n      \n\n    USERDEFINED     describe", pybind11::module_local())
		.value("LINESEARCH_ITERATIONSCALING", ROL::LINESEARCH_ITERATIONSCALING)
		.value("LINESEARCH_PATHBASEDTARGETLEVEL", ROL::LINESEARCH_PATHBASEDTARGETLEVEL)
		.value("LINESEARCH_BACKTRACKING", ROL::LINESEARCH_BACKTRACKING)
		.value("LINESEARCH_BISECTION", ROL::LINESEARCH_BISECTION)
		.value("LINESEARCH_GOLDENSECTION", ROL::LINESEARCH_GOLDENSECTION)
		.value("LINESEARCH_CUBICINTERP", ROL::LINESEARCH_CUBICINTERP)
		.value("LINESEARCH_BRENTS", ROL::LINESEARCH_BRENTS)
		.value("LINESEARCH_USERDEFINED", ROL::LINESEARCH_USERDEFINED)
		.value("LINESEARCH_LAST", ROL::LINESEARCH_LAST)
		.export_values();

;

	// ROL::ELineSearchToString(enum ROL::ELineSearch) file:ROL_Types.hpp line:640
	M("ROL").def("ELineSearchToString", (std::string (*)(enum ROL::ELineSearch)) &ROL::ELineSearchToString, "C++: ROL::ELineSearchToString(enum ROL::ELineSearch) --> std::string", pybind11::arg("ls"));

	// ROL::isValidLineSearch(enum ROL::ELineSearch) file:ROL_Types.hpp line:662
	M("ROL").def("isValidLineSearch", (int (*)(enum ROL::ELineSearch)) &ROL::isValidLineSearch, "Verifies validity of a LineSearch enum.\n\n      \n  [in]  - enum of the linesearch\n      \n\n 1 if the argument is a valid linesearch; 0 otherwise.\n\nC++: ROL::isValidLineSearch(enum ROL::ELineSearch) --> int", pybind11::arg("ls"));

	// ROL::StringToELineSearch(std::string) file:ROL_Types.hpp line:694
	M("ROL").def("StringToELineSearch", (enum ROL::ELineSearch (*)(std::string)) &ROL::StringToELineSearch, "C++: ROL::StringToELineSearch(std::string) --> enum ROL::ELineSearch", pybind11::arg("s"));

	// ROL::ECurvatureCondition file:ROL_Types.hpp line:711
	pybind11::enum_<ROL::ECurvatureCondition>(M("ROL"), "ECurvatureCondition", pybind11::arithmetic(), "Enumeration of line-search curvature conditions.\n\n      \n    WOLFE           describe\n      \n\n    STRONGWOLFE     describe\n      \n\n    GOLDSTEIN       describe", pybind11::module_local())
		.value("CURVATURECONDITION_WOLFE", ROL::CURVATURECONDITION_WOLFE)
		.value("CURVATURECONDITION_STRONGWOLFE", ROL::CURVATURECONDITION_STRONGWOLFE)
		.value("CURVATURECONDITION_GENERALIZEDWOLFE", ROL::CURVATURECONDITION_GENERALIZEDWOLFE)
		.value("CURVATURECONDITION_APPROXIMATEWOLFE", ROL::CURVATURECONDITION_APPROXIMATEWOLFE)
		.value("CURVATURECONDITION_GOLDSTEIN", ROL::CURVATURECONDITION_GOLDSTEIN)
		.value("CURVATURECONDITION_NULL", ROL::CURVATURECONDITION_NULL)
		.value("CURVATURECONDITION_LAST", ROL::CURVATURECONDITION_LAST)
		.export_values();

;

	// ROL::ECurvatureConditionToString(enum ROL::ECurvatureCondition) file:ROL_Types.hpp line:721
	M("ROL").def("ECurvatureConditionToString", (std::string (*)(enum ROL::ECurvatureCondition)) &ROL::ECurvatureConditionToString, "C++: ROL::ECurvatureConditionToString(enum ROL::ECurvatureCondition) --> std::string", pybind11::arg("ls"));

	// ROL::isValidCurvatureCondition(enum ROL::ECurvatureCondition) file:ROL_Types.hpp line:741
	M("ROL").def("isValidCurvatureCondition", (int (*)(enum ROL::ECurvatureCondition)) &ROL::isValidCurvatureCondition, "Verifies validity of a CurvatureCondition enum.\n\n      \n  [in]  - enum of the Curvature Conditions\n      \n\n 1 if the argument is a valid curvature condition; 0 otherwise.\n\nC++: ROL::isValidCurvatureCondition(enum ROL::ECurvatureCondition) --> int", pybind11::arg("ls"));

	// ROL::StringToECurvatureCondition(std::string) file:ROL_Types.hpp line:771
	M("ROL").def("StringToECurvatureCondition", (enum ROL::ECurvatureCondition (*)(std::string)) &ROL::StringToECurvatureCondition, "C++: ROL::StringToECurvatureCondition(std::string) --> enum ROL::ECurvatureCondition", pybind11::arg("s"));

	// ROL::ECGFlag file:ROL_Types.hpp line:791
	pybind11::enum_<ROL::ECGFlag>(M("ROL"), "ECGFlag", pybind11::arithmetic(), "Enumation of flags used by conjugate gradient methods.\n\n    \n CG_FLAG_SUCCESS     Residual Tolerance Met\n    \n\n CG_FLAG_ITEREXCEED  Iteration Limit Exceeded\n    \n\n CG_FLAG_NEGCURVE    Negative Curvature Detected\n    \n\n CG_FLAG_TRRADEX     Trust-Region Radius Exceeded\n    \n\n CG_FLAG_ZERORHS     Initiali Right Hand Side is Zero\n\n  ", pybind11::module_local())
		.value("CG_FLAG_SUCCESS", ROL::CG_FLAG_SUCCESS)
		.value("CG_FLAG_ITEREXCEED", ROL::CG_FLAG_ITEREXCEED)
		.value("CG_FLAG_NEGCURVE", ROL::CG_FLAG_NEGCURVE)
		.value("CG_FLAG_TRRADEX", ROL::CG_FLAG_TRRADEX)
		.value("CG_FLAG_ZERORHS", ROL::CG_FLAG_ZERORHS)
		.value("CG_FLAG_UNDEFINED", ROL::CG_FLAG_UNDEFINED)
		.export_values();

;

	// ROL::ECGFlagToString(enum ROL::ECGFlag) file:ROL_Types.hpp line:801
	M("ROL").def("ECGFlagToString", (std::string (*)(enum ROL::ECGFlag)) &ROL::ECGFlagToString, "C++: ROL::ECGFlagToString(enum ROL::ECGFlag) --> std::string", pybind11::arg("cgf"));

	{ // ROL::TypeCaster file:ROL_Types.hpp line:865
		pybind11::class_<ROL::TypeCaster<double,float>, Teuchos::RCP<ROL::TypeCaster<double,float>>> cl(M("ROL"), "TypeCaster_double_float_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new ROL::TypeCaster<double,float>(); } ) );
		cl.def_static("ElementToReal", (double (*)(const float &)) &ROL::TypeCaster<double, float>::ElementToReal, "C++: ROL::TypeCaster<double, float>::ElementToReal(const float &) --> double", pybind11::arg("val"));
	}
}
