#include <ROL_DynamicConstraint.hpp>
#include <ROL_DynamicConstraint_CheckInterface.hpp>
#include <ROL_Elementwise_Function.hpp>
#include <ROL_Elementwise_Reduce.hpp>
#include <ROL_TimeStamp.hpp>
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
#include <functional>
#include <iterator>
#include <memory>
#include <ostream>
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

void bind_pyrol_45(std::function< pybind11::module &(std::string const &namespace_) > &M)
{
	// ROL::make_check(class ROL::DynamicConstraint<double> &) file:ROL_DynamicConstraint_CheckInterface.hpp line:226
	M("ROL").def("make_check", (class ROL::details::DynamicConstraint_CheckInterface<double> (*)(class ROL::DynamicConstraint<double> &)) &ROL::make_check<double>, "C++: ROL::make_check(class ROL::DynamicConstraint<double> &) --> class ROL::details::DynamicConstraint_CheckInterface<double>", pybind11::arg("con"));

	// ROL::make_check(class ROL::DynamicConstraint<double> &, struct ROL::TimeStamp<double> &) file:ROL_DynamicConstraint_CheckInterface.hpp line:231
	M("ROL").def("make_check", (class ROL::details::DynamicConstraint_CheckInterface<double> (*)(class ROL::DynamicConstraint<double> &, struct ROL::TimeStamp<double> &)) &ROL::make_check<double>, "C++: ROL::make_check(class ROL::DynamicConstraint<double> &, struct ROL::TimeStamp<double> &) --> class ROL::details::DynamicConstraint_CheckInterface<double>", pybind11::arg("con"), pybind11::arg("timeStamp"));

}
