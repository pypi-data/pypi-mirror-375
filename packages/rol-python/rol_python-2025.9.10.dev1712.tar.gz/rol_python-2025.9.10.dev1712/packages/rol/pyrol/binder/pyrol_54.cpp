#include <ROL_BatchManager.hpp>
#include <ROL_BatchStdVector.hpp>
#include <ROL_Elementwise_Function.hpp>
#include <ROL_Elementwise_Reduce.hpp>
#include <ROL_ProbabilityVector.hpp>
#include <ROL_SampledVector.hpp>
#include <ROL_StdVector.hpp>
#include <ROL_Vector.hpp>
#include <Teuchos_ENull.hpp>
#include <Teuchos_RCPDecl.hpp>
#include <Teuchos_RCPNode.hpp>
#include <Teuchos_any.hpp>
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

// ROL::BatchStdVector file:ROL_BatchStdVector.hpp line:24
struct PyCallBack_ROL_BatchStdVector_double_t : public ROL::BatchStdVector<double> {
	using ROL::BatchStdVector<double>::BatchStdVector;

	double dot(const class ROL::Vector<double> & a0) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::BatchStdVector<double> *>(this), "dot");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<double>::value) {
				static pybind11::detail::override_caster_t<double> caster;
				return pybind11::detail::cast_ref<double>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<double>(std::move(o));
		}
		return BatchStdVector::dot(a0);
	}
	class Teuchos::RCP<class ROL::Vector<double> > clone() const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::BatchStdVector<double> *>(this), "clone");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<class Teuchos::RCP<class ROL::Vector<double> >>::value) {
				static pybind11::detail::override_caster_t<class Teuchos::RCP<class ROL::Vector<double> >> caster;
				return pybind11::detail::cast_ref<class Teuchos::RCP<class ROL::Vector<double> >>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<class Teuchos::RCP<class ROL::Vector<double> >>(std::move(o));
		}
		return BatchStdVector::clone();
	}
	int dimension() const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::BatchStdVector<double> *>(this), "dimension");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<int>::value) {
				static pybind11::detail::override_caster_t<int> caster;
				return pybind11::detail::cast_ref<int>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<int>(std::move(o));
		}
		return BatchStdVector::dimension();
	}
	double reduce(const class ROL::Elementwise::ReductionOp<double> & a0) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::BatchStdVector<double> *>(this), "reduce");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<double>::value) {
				static pybind11::detail::override_caster_t<double> caster;
				return pybind11::detail::cast_ref<double>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<double>(std::move(o));
		}
		return BatchStdVector::reduce(a0);
	}
	void set(const class ROL::Vector<double> & a0) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::BatchStdVector<double> *>(this), "set");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return StdVector::set(a0);
	}
	void plus(const class ROL::Vector<double> & a0) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::BatchStdVector<double> *>(this), "plus");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return StdVector::plus(a0);
	}
	void axpy(const double a0, const class ROL::Vector<double> & a1) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::BatchStdVector<double> *>(this), "axpy");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return StdVector::axpy(a0, a1);
	}
	void scale(const double a0) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::BatchStdVector<double> *>(this), "scale");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return StdVector::scale(a0);
	}
	double norm() const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::BatchStdVector<double> *>(this), "norm");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<double>::value) {
				static pybind11::detail::override_caster_t<double> caster;
				return pybind11::detail::cast_ref<double>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<double>(std::move(o));
		}
		return StdVector::norm();
	}
	class Teuchos::RCP<class ROL::Vector<double> > basis(const int a0) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::BatchStdVector<double> *>(this), "basis");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<class Teuchos::RCP<class ROL::Vector<double> >>::value) {
				static pybind11::detail::override_caster_t<class Teuchos::RCP<class ROL::Vector<double> >> caster;
				return pybind11::detail::cast_ref<class Teuchos::RCP<class ROL::Vector<double> >>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<class Teuchos::RCP<class ROL::Vector<double> >>(std::move(o));
		}
		return StdVector::basis(a0);
	}
	void applyUnary(const class ROL::Elementwise::UnaryFunction<double> & a0) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::BatchStdVector<double> *>(this), "applyUnary");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return StdVector::applyUnary(a0);
	}
	void applyBinary(const class ROL::Elementwise::BinaryFunction<double> & a0, const class ROL::Vector<double> & a1) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::BatchStdVector<double> *>(this), "applyBinary");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return StdVector::applyBinary(a0, a1);
	}
	void setScalar(const double a0) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::BatchStdVector<double> *>(this), "setScalar");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return StdVector::setScalar(a0);
	}
	void randomize(const double a0, const double a1) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::BatchStdVector<double> *>(this), "randomize");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return StdVector::randomize(a0, a1);
	}
	void print(std::ostream & a0) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::BatchStdVector<double> *>(this), "print");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return StdVector::print(a0);
	}
	void zero() override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::BatchStdVector<double> *>(this), "zero");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Vector::zero();
	}
	const class ROL::Vector<double> & dual() const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::BatchStdVector<double> *>(this), "dual");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<const class ROL::Vector<double> &>::value) {
				static pybind11::detail::override_caster_t<const class ROL::Vector<double> &> caster;
				return pybind11::detail::cast_ref<const class ROL::Vector<double> &>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<const class ROL::Vector<double> &>(std::move(o));
		}
		return Vector::dual();
	}
	double apply(const class ROL::Vector<double> & a0) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::BatchStdVector<double> *>(this), "apply");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<double>::value) {
				static pybind11::detail::override_caster_t<double> caster;
				return pybind11::detail::cast_ref<double>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<double>(std::move(o));
		}
		return Vector::apply(a0);
	}
	class std::vector<double> checkVector(const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const bool a2, std::ostream & a3) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::BatchStdVector<double> *>(this), "checkVector");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3);
			if (pybind11::detail::cast_is_temporary_value_reference<class std::vector<double>>::value) {
				static pybind11::detail::override_caster_t<class std::vector<double>> caster;
				return pybind11::detail::cast_ref<class std::vector<double>>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<class std::vector<double>>(std::move(o));
		}
		return Vector::checkVector(a0, a1, a2, a3);
	}
};

// ROL::ProbabilityVector file:ROL_ProbabilityVector.hpp line:29
struct PyCallBack_ROL_ProbabilityVector_double_t : public ROL::ProbabilityVector<double> {
	using ROL::ProbabilityVector<double>::ProbabilityVector;

	class Teuchos::RCP<class ROL::Vector<double> > clone() const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ProbabilityVector<double> *>(this), "clone");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<class Teuchos::RCP<class ROL::Vector<double> >>::value) {
				static pybind11::detail::override_caster_t<class Teuchos::RCP<class ROL::Vector<double> >> caster;
				return pybind11::detail::cast_ref<class Teuchos::RCP<class ROL::Vector<double> >>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<class Teuchos::RCP<class ROL::Vector<double> >>(std::move(o));
		}
		return ProbabilityVector::clone();
	}
	double dot(const class ROL::Vector<double> & a0) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ProbabilityVector<double> *>(this), "dot");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<double>::value) {
				static pybind11::detail::override_caster_t<double> caster;
				return pybind11::detail::cast_ref<double>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<double>(std::move(o));
		}
		return BatchStdVector::dot(a0);
	}
	int dimension() const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ProbabilityVector<double> *>(this), "dimension");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<int>::value) {
				static pybind11::detail::override_caster_t<int> caster;
				return pybind11::detail::cast_ref<int>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<int>(std::move(o));
		}
		return BatchStdVector::dimension();
	}
	double reduce(const class ROL::Elementwise::ReductionOp<double> & a0) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ProbabilityVector<double> *>(this), "reduce");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<double>::value) {
				static pybind11::detail::override_caster_t<double> caster;
				return pybind11::detail::cast_ref<double>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<double>(std::move(o));
		}
		return BatchStdVector::reduce(a0);
	}
	void set(const class ROL::Vector<double> & a0) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ProbabilityVector<double> *>(this), "set");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return StdVector::set(a0);
	}
	void plus(const class ROL::Vector<double> & a0) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ProbabilityVector<double> *>(this), "plus");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return StdVector::plus(a0);
	}
	void axpy(const double a0, const class ROL::Vector<double> & a1) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ProbabilityVector<double> *>(this), "axpy");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return StdVector::axpy(a0, a1);
	}
	void scale(const double a0) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ProbabilityVector<double> *>(this), "scale");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return StdVector::scale(a0);
	}
	double norm() const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ProbabilityVector<double> *>(this), "norm");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<double>::value) {
				static pybind11::detail::override_caster_t<double> caster;
				return pybind11::detail::cast_ref<double>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<double>(std::move(o));
		}
		return StdVector::norm();
	}
	class Teuchos::RCP<class ROL::Vector<double> > basis(const int a0) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ProbabilityVector<double> *>(this), "basis");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<class Teuchos::RCP<class ROL::Vector<double> >>::value) {
				static pybind11::detail::override_caster_t<class Teuchos::RCP<class ROL::Vector<double> >> caster;
				return pybind11::detail::cast_ref<class Teuchos::RCP<class ROL::Vector<double> >>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<class Teuchos::RCP<class ROL::Vector<double> >>(std::move(o));
		}
		return StdVector::basis(a0);
	}
	void applyUnary(const class ROL::Elementwise::UnaryFunction<double> & a0) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ProbabilityVector<double> *>(this), "applyUnary");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return StdVector::applyUnary(a0);
	}
	void applyBinary(const class ROL::Elementwise::BinaryFunction<double> & a0, const class ROL::Vector<double> & a1) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ProbabilityVector<double> *>(this), "applyBinary");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return StdVector::applyBinary(a0, a1);
	}
	void setScalar(const double a0) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ProbabilityVector<double> *>(this), "setScalar");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return StdVector::setScalar(a0);
	}
	void randomize(const double a0, const double a1) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ProbabilityVector<double> *>(this), "randomize");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return StdVector::randomize(a0, a1);
	}
	void print(std::ostream & a0) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ProbabilityVector<double> *>(this), "print");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return StdVector::print(a0);
	}
	void zero() override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ProbabilityVector<double> *>(this), "zero");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Vector::zero();
	}
	const class ROL::Vector<double> & dual() const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ProbabilityVector<double> *>(this), "dual");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<const class ROL::Vector<double> &>::value) {
				static pybind11::detail::override_caster_t<const class ROL::Vector<double> &> caster;
				return pybind11::detail::cast_ref<const class ROL::Vector<double> &>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<const class ROL::Vector<double> &>(std::move(o));
		}
		return Vector::dual();
	}
	double apply(const class ROL::Vector<double> & a0) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ProbabilityVector<double> *>(this), "apply");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<double>::value) {
				static pybind11::detail::override_caster_t<double> caster;
				return pybind11::detail::cast_ref<double>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<double>(std::move(o));
		}
		return Vector::apply(a0);
	}
	class std::vector<double> checkVector(const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const bool a2, std::ostream & a3) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ProbabilityVector<double> *>(this), "checkVector");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3);
			if (pybind11::detail::cast_is_temporary_value_reference<class std::vector<double>>::value) {
				static pybind11::detail::override_caster_t<class std::vector<double>> caster;
				return pybind11::detail::cast_ref<class std::vector<double>>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<class std::vector<double>>(std::move(o));
		}
		return Vector::checkVector(a0, a1, a2, a3);
	}
};

void bind_pyrol_54(std::function< pybind11::module &(std::string const &namespace_) > &M)
{
	{ // ROL::BatchStdVector file:ROL_BatchStdVector.hpp line:24
		pybind11::class_<ROL::BatchStdVector<double>, Teuchos::RCP<ROL::BatchStdVector<double>>, PyCallBack_ROL_BatchStdVector_double_t, ROL::StdVector<double,double>> cl(M("ROL"), "BatchStdVector_double_t", "", pybind11::module_local());
		cl.def( pybind11::init<const class Teuchos::RCP<class std::vector<double> > &, const class Teuchos::RCP<class ROL::BatchManager<double> > &>(), pybind11::arg("vec"), pybind11::arg("bman") );

		cl.def( pybind11::init( [](PyCallBack_ROL_BatchStdVector_double_t const &o){ return new PyCallBack_ROL_BatchStdVector_double_t(o); } ) );
		cl.def( pybind11::init( [](ROL::BatchStdVector<double> const &o){ return new ROL::BatchStdVector<double>(o); } ) );
		cl.def("dot", (double (ROL::BatchStdVector<double>::*)(const class ROL::Vector<double> &) const) &ROL::BatchStdVector<double>::dot, "C++: ROL::BatchStdVector<double>::dot(const class ROL::Vector<double> &) const --> double", pybind11::arg("x"));
		cl.def("clone", (class Teuchos::RCP<class ROL::Vector<double> > (ROL::BatchStdVector<double>::*)() const) &ROL::BatchStdVector<double>::clone, "C++: ROL::BatchStdVector<double>::clone() const --> class Teuchos::RCP<class ROL::Vector<double> >");
		cl.def("dimension", (int (ROL::BatchStdVector<double>::*)() const) &ROL::BatchStdVector<double>::dimension, "C++: ROL::BatchStdVector<double>::dimension() const --> int");
		cl.def("reduce", (double (ROL::BatchStdVector<double>::*)(const class ROL::Elementwise::ReductionOp<double> &) const) &ROL::BatchStdVector<double>::reduce, "C++: ROL::BatchStdVector<double>::reduce(const class ROL::Elementwise::ReductionOp<double> &) const --> double", pybind11::arg("r"));
		cl.def("getBatchManager", (const class Teuchos::RCP<class ROL::BatchManager<double> > (ROL::BatchStdVector<double>::*)() const) &ROL::BatchStdVector<double>::getBatchManager, "C++: ROL::BatchStdVector<double>::getBatchManager() const --> const class Teuchos::RCP<class ROL::BatchManager<double> >");
		cl.def("__getitem__", (double & (ROL::StdVector<double,double>::*)(int)) &ROL::StdVector<double>::operator[], "C++: ROL::StdVector<double>::operator[](int) --> double &", pybind11::return_value_policy::automatic, pybind11::arg("i"));
		cl.def("set", (void (ROL::StdVector<double,double>::*)(const class ROL::Vector<double> &)) &ROL::StdVector<double>::set, "C++: ROL::StdVector<double>::set(const class ROL::Vector<double> &) --> void", pybind11::arg("x"));
		cl.def("plus", (void (ROL::StdVector<double,double>::*)(const class ROL::Vector<double> &)) &ROL::StdVector<double>::plus, "C++: ROL::StdVector<double>::plus(const class ROL::Vector<double> &) --> void", pybind11::arg("x"));
		cl.def("axpy", (void (ROL::StdVector<double,double>::*)(const double, const class ROL::Vector<double> &)) &ROL::StdVector<double>::axpy, "C++: ROL::StdVector<double>::axpy(const double, const class ROL::Vector<double> &) --> void", pybind11::arg("alpha"), pybind11::arg("x"));
		cl.def("scale", (void (ROL::StdVector<double,double>::*)(const double)) &ROL::StdVector<double>::scale, "C++: ROL::StdVector<double>::scale(const double) --> void", pybind11::arg("alpha"));
		cl.def("dot", (double (ROL::StdVector<double,double>::*)(const class ROL::Vector<double> &) const) &ROL::StdVector<double>::dot, "C++: ROL::StdVector<double>::dot(const class ROL::Vector<double> &) const --> double", pybind11::arg("x"));
		cl.def("norm", (double (ROL::StdVector<double,double>::*)() const) &ROL::StdVector<double>::norm, "C++: ROL::StdVector<double>::norm() const --> double");
		cl.def("clone", (class Teuchos::RCP<class ROL::Vector<double> > (ROL::StdVector<double,double>::*)() const) &ROL::StdVector<double>::clone, "C++: ROL::StdVector<double>::clone() const --> class Teuchos::RCP<class ROL::Vector<double> >");
		cl.def("getVector", (class Teuchos::RCP<class std::vector<double> > (ROL::StdVector<double,double>::*)()) &ROL::StdVector<double>::getVector, "C++: ROL::StdVector<double>::getVector() --> class Teuchos::RCP<class std::vector<double> >");
		cl.def("basis", (class Teuchos::RCP<class ROL::Vector<double> > (ROL::StdVector<double,double>::*)(const int) const) &ROL::StdVector<double>::basis, "C++: ROL::StdVector<double>::basis(const int) const --> class Teuchos::RCP<class ROL::Vector<double> >", pybind11::arg("i"));
		cl.def("dimension", (int (ROL::StdVector<double,double>::*)() const) &ROL::StdVector<double>::dimension, "C++: ROL::StdVector<double>::dimension() const --> int");
		cl.def("applyUnary", (void (ROL::StdVector<double,double>::*)(const class ROL::Elementwise::UnaryFunction<double> &)) &ROL::StdVector<double>::applyUnary, "C++: ROL::StdVector<double>::applyUnary(const class ROL::Elementwise::UnaryFunction<double> &) --> void", pybind11::arg("f"));
		cl.def("applyBinary", (void (ROL::StdVector<double,double>::*)(const class ROL::Elementwise::BinaryFunction<double> &, const class ROL::Vector<double> &)) &ROL::StdVector<double>::applyBinary, "C++: ROL::StdVector<double>::applyBinary(const class ROL::Elementwise::BinaryFunction<double> &, const class ROL::Vector<double> &) --> void", pybind11::arg("f"), pybind11::arg("x"));
		cl.def("reduce", (double (ROL::StdVector<double,double>::*)(const class ROL::Elementwise::ReductionOp<double> &) const) &ROL::StdVector<double>::reduce, "C++: ROL::StdVector<double>::reduce(const class ROL::Elementwise::ReductionOp<double> &) const --> double", pybind11::arg("r"));
		cl.def("setScalar", (void (ROL::StdVector<double,double>::*)(const double)) &ROL::StdVector<double>::setScalar, "C++: ROL::StdVector<double>::setScalar(const double) --> void", pybind11::arg("C"));
		cl.def("randomize", [](ROL::StdVector<double,double> &o) -> void { return o.randomize(); }, "");
		cl.def("randomize", [](ROL::StdVector<double,double> &o, const double & a0) -> void { return o.randomize(a0); }, "", pybind11::arg("l"));
		cl.def("randomize", (void (ROL::StdVector<double,double>::*)(const double, const double)) &ROL::StdVector<double>::randomize, "C++: ROL::StdVector<double>::randomize(const double, const double) --> void", pybind11::arg("l"), pybind11::arg("u"));
		cl.def("print", (void (ROL::StdVector<double,double>::*)(std::ostream &) const) &ROL::StdVector<double>::print, "C++: ROL::StdVector<double>::print(std::ostream &) const --> void", pybind11::arg("outStream"));
		cl.def("assign", (class ROL::StdVector<double> & (ROL::StdVector<double,double>::*)(const class ROL::StdVector<double> &)) &ROL::StdVector<double>::operator=, "C++: ROL::StdVector<double>::operator=(const class ROL::StdVector<double> &) --> class ROL::StdVector<double> &", pybind11::return_value_policy::automatic, pybind11::arg(""));
		cl.def("plus", (void (ROL::Vector<double>::*)(const class ROL::Vector<double> &)) &ROL::Vector<double>::plus, "C++: ROL::Vector<double>::plus(const class ROL::Vector<double> &) --> void", pybind11::arg("x"));
		cl.def("scale", (void (ROL::Vector<double>::*)(const double)) &ROL::Vector<double>::scale, "C++: ROL::Vector<double>::scale(const double) --> void", pybind11::arg("alpha"));
		cl.def("dot", (double (ROL::Vector<double>::*)(const class ROL::Vector<double> &) const) &ROL::Vector<double>::dot, "C++: ROL::Vector<double>::dot(const class ROL::Vector<double> &) const --> double", pybind11::arg("x"));
		cl.def("norm", (double (ROL::Vector<double>::*)() const) &ROL::Vector<double>::norm, "C++: ROL::Vector<double>::norm() const --> double");
		cl.def("clone", (class Teuchos::RCP<class ROL::Vector<double> > (ROL::Vector<double>::*)() const) &ROL::Vector<double>::clone, "C++: ROL::Vector<double>::clone() const --> class Teuchos::RCP<class ROL::Vector<double> >");
		cl.def("axpy", (void (ROL::Vector<double>::*)(const double, const class ROL::Vector<double> &)) &ROL::Vector<double>::axpy, "Compute \n where \n.\n\n             \n is the scaling of \n             \n\n     is a vector.\n\n             On return \n.\n             Uses #clone, #set, #scale and #plus for the computation.\n             Please overload if a more efficient implementation is needed.\n\n             ---\n\nC++: ROL::Vector<double>::axpy(const double, const class ROL::Vector<double> &) --> void", pybind11::arg("alpha"), pybind11::arg("x"));
		cl.def("zero", (void (ROL::Vector<double>::*)()) &ROL::Vector<double>::zero, "Set to zero vector.\n\n             Uses #scale by zero for the computation.\n             Please overload if a more efficient implementation is needed.\n\n             ---\n\nC++: ROL::Vector<double>::zero() --> void");
		cl.def("basis", (class Teuchos::RCP<class ROL::Vector<double> > (ROL::Vector<double>::*)(const int) const) &ROL::Vector<double>::basis, "Return i-th basis vector.\n\n             \n is the index of the basis function.\n             \n\n A reference-counted pointer to the basis vector with index \n\n             Overloading the basis is only required if the default gradient implementation\n             is used, which computes a finite-difference approximation.\n\n             ---\n\nC++: ROL::Vector<double>::basis(const int) const --> class Teuchos::RCP<class ROL::Vector<double> >", pybind11::arg("i"));
		cl.def("dimension", (int (ROL::Vector<double>::*)() const) &ROL::Vector<double>::dimension, "Return dimension of the vector space.\n\n             \n The dimension of the vector space, i.e., the total number of basis vectors.\n\n             Overload if the basis is overloaded.\n\n             ---\n\nC++: ROL::Vector<double>::dimension() const --> int");
		cl.def("set", (void (ROL::Vector<double>::*)(const class ROL::Vector<double> &)) &ROL::Vector<double>::set, "Set \n where \n.\n\n             \n     is a vector.\n\n             On return \n.\n             Uses #zero and #plus methods for the computation.\n             Please overload if a more efficient implementation is needed.\n\n             ---\n\nC++: ROL::Vector<double>::set(const class ROL::Vector<double> &) --> void", pybind11::arg("x"));
		cl.def("dual", (const class ROL::Vector<double> & (ROL::Vector<double>::*)() const) &ROL::Vector<double>::dual, "Return dual representation of \n, for example,\n             the result of applying a Riesz map, or change of basis, or\n             change of memory layout.\n\n             \n         A const reference to dual representation.\n\n             By default, returns the current object.\n             Please overload if you need a dual representation.\n\n             ---\n\nC++: ROL::Vector<double>::dual() const --> const class ROL::Vector<double> &", pybind11::return_value_policy::automatic);
		cl.def("apply", (double (ROL::Vector<double>::*)(const class ROL::Vector<double> &) const) &ROL::Vector<double>::apply, "Apply \n to a dual vector.  This is equivalent\n             to the call \n\n.\n\n             \n      is a vector\n             \n\n         The number equal to \n.\n\n             ---\n\nC++: ROL::Vector<double>::apply(const class ROL::Vector<double> &) const --> double", pybind11::arg("x"));
		cl.def("applyUnary", (void (ROL::Vector<double>::*)(const class ROL::Elementwise::UnaryFunction<double> &)) &ROL::Vector<double>::applyUnary, "C++: ROL::Vector<double>::applyUnary(const class ROL::Elementwise::UnaryFunction<double> &) --> void", pybind11::arg("f"));
		cl.def("applyBinary", (void (ROL::Vector<double>::*)(const class ROL::Elementwise::BinaryFunction<double> &, const class ROL::Vector<double> &)) &ROL::Vector<double>::applyBinary, "C++: ROL::Vector<double>::applyBinary(const class ROL::Elementwise::BinaryFunction<double> &, const class ROL::Vector<double> &) --> void", pybind11::arg("f"), pybind11::arg("x"));
		cl.def("reduce", (double (ROL::Vector<double>::*)(const class ROL::Elementwise::ReductionOp<double> &) const) &ROL::Vector<double>::reduce, "C++: ROL::Vector<double>::reduce(const class ROL::Elementwise::ReductionOp<double> &) const --> double", pybind11::arg("r"));
		cl.def("print", (void (ROL::Vector<double>::*)(std::ostream &) const) &ROL::Vector<double>::print, "C++: ROL::Vector<double>::print(std::ostream &) const --> void", pybind11::arg("outStream"));
		cl.def("setScalar", (void (ROL::Vector<double>::*)(const double)) &ROL::Vector<double>::setScalar, "Set \n where \n.\n\n             \n     is a scalar.\n\n             On return \n.\n             Uses #applyUnary methods for the computation.\n             Please overload if a more efficient implementation is needed.\n\n             ---\n\nC++: ROL::Vector<double>::setScalar(const double) --> void", pybind11::arg("C"));
		cl.def("randomize", [](ROL::Vector<double> &o) -> void { return o.randomize(); }, "");
		cl.def("randomize", [](ROL::Vector<double> &o, const double & a0) -> void { return o.randomize(a0); }, "", pybind11::arg("l"));
		cl.def("randomize", (void (ROL::Vector<double>::*)(const double, const double)) &ROL::Vector<double>::randomize, "Set vector to be uniform random between [l,u].\n\n             \n     is a the lower bound.\n             \n\n     is a the upper bound.\n\n             On return the components of \n are uniform\n             random numbers on the interval \n\n.\n       	     The default implementation uses #applyUnary methods for the\n       	     computation. Please overload if a more efficient implementation is\n             needed.\n\n             ---\n\nC++: ROL::Vector<double>::randomize(const double, const double) --> void", pybind11::arg("l"), pybind11::arg("u"));
		cl.def("checkVector", [](ROL::Vector<double> const &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1) -> std::vector<double> { return o.checkVector(a0, a1); }, "", pybind11::arg("x"), pybind11::arg("y"));
		cl.def("checkVector", [](ROL::Vector<double> const &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const bool & a2) -> std::vector<double> { return o.checkVector(a0, a1, a2); }, "", pybind11::arg("x"), pybind11::arg("y"), pybind11::arg("printToStream"));
		cl.def("checkVector", (class std::vector<double> (ROL::Vector<double>::*)(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const bool, std::ostream &) const) &ROL::Vector<double>::checkVector, "Verify vector-space methods.\n\n             \n     is a vector.\n             \n\n     is a vector.\n\n             Returns a vector of Reals, all of which should be close to zero.\n             They represent consistency errors in the vector space properties,\n             as follows:\n\n             - Commutativity of addition: \n.\n             - Associativity of addition: \n\n.\n             - Identity element of addition: \n\n.\n             - Inverse elements of addition: \n\n.\n             - Identity element of scalar multiplication: \n\n.\n             - Consistency of scalar multiplication with field multiplication: \n\n.\n             - Distributivity of scalar multiplication with respect to field addition: \n\n.\n             - Distributivity of scalar multiplication with respect to vector addition: \n\n.\n             - Commutativity of dot (inner) product over the field of reals: \n\n.\n             - Additivity of dot (inner) product: \n\n.\n             - Consistency of scalar multiplication and norm: \n\n.\n             - Reflexivity: \n\n .\n             - Consistency of apply and dual: \n\n.\n\n             The consistency errors are defined as the norms or absolute values of the differences between the left-hand\n             side and the right-hand side terms in the above equalities.\n\n             ---\n\nC++: ROL::Vector<double>::checkVector(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const bool, std::ostream &) const --> class std::vector<double>", pybind11::arg("x"), pybind11::arg("y"), pybind11::arg("printToStream"), pybind11::arg("outStream"));
		cl.def("assign", (class ROL::Vector<double> & (ROL::Vector<double>::*)(const class ROL::Vector<double> &)) &ROL::Vector<double>::operator=, "C++: ROL::Vector<double>::operator=(const class ROL::Vector<double> &) --> class ROL::Vector<double> &", pybind11::return_value_policy::automatic, pybind11::arg(""));
	}
	{ // ROL::ProbabilityVector file:ROL_ProbabilityVector.hpp line:29
		pybind11::class_<ROL::ProbabilityVector<double>, Teuchos::RCP<ROL::ProbabilityVector<double>>, PyCallBack_ROL_ProbabilityVector_double_t, ROL::BatchStdVector<double>> cl(M("ROL"), "ProbabilityVector_double_t", "", pybind11::module_local());
		cl.def( pybind11::init<const class Teuchos::RCP<class std::vector<double> > &, const class Teuchos::RCP<class ROL::BatchManager<double> > &>(), pybind11::arg("vec"), pybind11::arg("bman") );

		cl.def( pybind11::init( [](PyCallBack_ROL_ProbabilityVector_double_t const &o){ return new PyCallBack_ROL_ProbabilityVector_double_t(o); } ) );
		cl.def( pybind11::init( [](ROL::ProbabilityVector<double> const &o){ return new ROL::ProbabilityVector<double>(o); } ) );
		cl.def("getProbability", (const double (ROL::ProbabilityVector<double>::*)(const int) const) &ROL::ProbabilityVector<double>::getProbability, "C++: ROL::ProbabilityVector<double>::getProbability(const int) const --> const double", pybind11::arg("i"));
		cl.def("setProbability", (void (ROL::ProbabilityVector<double>::*)(const int, const double)) &ROL::ProbabilityVector<double>::setProbability, "C++: ROL::ProbabilityVector<double>::setProbability(const int, const double) --> void", pybind11::arg("i"), pybind11::arg("wt"));
		cl.def("getNumMyAtoms", (int (ROL::ProbabilityVector<double>::*)() const) &ROL::ProbabilityVector<double>::getNumMyAtoms, "C++: ROL::ProbabilityVector<double>::getNumMyAtoms() const --> int");
		cl.def("clone", (class Teuchos::RCP<class ROL::Vector<double> > (ROL::ProbabilityVector<double>::*)() const) &ROL::ProbabilityVector<double>::clone, "C++: ROL::ProbabilityVector<double>::clone() const --> class Teuchos::RCP<class ROL::Vector<double> >");
		cl.def("dot", (double (ROL::BatchStdVector<double>::*)(const class ROL::Vector<double> &) const) &ROL::BatchStdVector<double>::dot, "C++: ROL::BatchStdVector<double>::dot(const class ROL::Vector<double> &) const --> double", pybind11::arg("x"));
		cl.def("clone", (class Teuchos::RCP<class ROL::Vector<double> > (ROL::BatchStdVector<double>::*)() const) &ROL::BatchStdVector<double>::clone, "C++: ROL::BatchStdVector<double>::clone() const --> class Teuchos::RCP<class ROL::Vector<double> >");
		cl.def("dimension", (int (ROL::BatchStdVector<double>::*)() const) &ROL::BatchStdVector<double>::dimension, "C++: ROL::BatchStdVector<double>::dimension() const --> int");
		cl.def("reduce", (double (ROL::BatchStdVector<double>::*)(const class ROL::Elementwise::ReductionOp<double> &) const) &ROL::BatchStdVector<double>::reduce, "C++: ROL::BatchStdVector<double>::reduce(const class ROL::Elementwise::ReductionOp<double> &) const --> double", pybind11::arg("r"));
		cl.def("getBatchManager", (const class Teuchos::RCP<class ROL::BatchManager<double> > (ROL::BatchStdVector<double>::*)() const) &ROL::BatchStdVector<double>::getBatchManager, "C++: ROL::BatchStdVector<double>::getBatchManager() const --> const class Teuchos::RCP<class ROL::BatchManager<double> >");
		cl.def("__getitem__", (double & (ROL::StdVector<double,double>::*)(int)) &ROL::StdVector<double>::operator[], "C++: ROL::StdVector<double>::operator[](int) --> double &", pybind11::return_value_policy::automatic, pybind11::arg("i"));
		cl.def("set", (void (ROL::StdVector<double,double>::*)(const class ROL::Vector<double> &)) &ROL::StdVector<double>::set, "C++: ROL::StdVector<double>::set(const class ROL::Vector<double> &) --> void", pybind11::arg("x"));
		cl.def("plus", (void (ROL::StdVector<double,double>::*)(const class ROL::Vector<double> &)) &ROL::StdVector<double>::plus, "C++: ROL::StdVector<double>::plus(const class ROL::Vector<double> &) --> void", pybind11::arg("x"));
		cl.def("axpy", (void (ROL::StdVector<double,double>::*)(const double, const class ROL::Vector<double> &)) &ROL::StdVector<double>::axpy, "C++: ROL::StdVector<double>::axpy(const double, const class ROL::Vector<double> &) --> void", pybind11::arg("alpha"), pybind11::arg("x"));
		cl.def("scale", (void (ROL::StdVector<double,double>::*)(const double)) &ROL::StdVector<double>::scale, "C++: ROL::StdVector<double>::scale(const double) --> void", pybind11::arg("alpha"));
		cl.def("dot", (double (ROL::StdVector<double,double>::*)(const class ROL::Vector<double> &) const) &ROL::StdVector<double>::dot, "C++: ROL::StdVector<double>::dot(const class ROL::Vector<double> &) const --> double", pybind11::arg("x"));
		cl.def("norm", (double (ROL::StdVector<double,double>::*)() const) &ROL::StdVector<double>::norm, "C++: ROL::StdVector<double>::norm() const --> double");
		cl.def("clone", (class Teuchos::RCP<class ROL::Vector<double> > (ROL::StdVector<double,double>::*)() const) &ROL::StdVector<double>::clone, "C++: ROL::StdVector<double>::clone() const --> class Teuchos::RCP<class ROL::Vector<double> >");
		cl.def("getVector", (class Teuchos::RCP<class std::vector<double> > (ROL::StdVector<double,double>::*)()) &ROL::StdVector<double>::getVector, "C++: ROL::StdVector<double>::getVector() --> class Teuchos::RCP<class std::vector<double> >");
		cl.def("basis", (class Teuchos::RCP<class ROL::Vector<double> > (ROL::StdVector<double,double>::*)(const int) const) &ROL::StdVector<double>::basis, "C++: ROL::StdVector<double>::basis(const int) const --> class Teuchos::RCP<class ROL::Vector<double> >", pybind11::arg("i"));
		cl.def("dimension", (int (ROL::StdVector<double,double>::*)() const) &ROL::StdVector<double>::dimension, "C++: ROL::StdVector<double>::dimension() const --> int");
		cl.def("applyUnary", (void (ROL::StdVector<double,double>::*)(const class ROL::Elementwise::UnaryFunction<double> &)) &ROL::StdVector<double>::applyUnary, "C++: ROL::StdVector<double>::applyUnary(const class ROL::Elementwise::UnaryFunction<double> &) --> void", pybind11::arg("f"));
		cl.def("applyBinary", (void (ROL::StdVector<double,double>::*)(const class ROL::Elementwise::BinaryFunction<double> &, const class ROL::Vector<double> &)) &ROL::StdVector<double>::applyBinary, "C++: ROL::StdVector<double>::applyBinary(const class ROL::Elementwise::BinaryFunction<double> &, const class ROL::Vector<double> &) --> void", pybind11::arg("f"), pybind11::arg("x"));
		cl.def("reduce", (double (ROL::StdVector<double,double>::*)(const class ROL::Elementwise::ReductionOp<double> &) const) &ROL::StdVector<double>::reduce, "C++: ROL::StdVector<double>::reduce(const class ROL::Elementwise::ReductionOp<double> &) const --> double", pybind11::arg("r"));
		cl.def("setScalar", (void (ROL::StdVector<double,double>::*)(const double)) &ROL::StdVector<double>::setScalar, "C++: ROL::StdVector<double>::setScalar(const double) --> void", pybind11::arg("C"));
		cl.def("randomize", [](ROL::StdVector<double,double> &o) -> void { return o.randomize(); }, "");
		cl.def("randomize", [](ROL::StdVector<double,double> &o, const double & a0) -> void { return o.randomize(a0); }, "", pybind11::arg("l"));
		cl.def("randomize", (void (ROL::StdVector<double,double>::*)(const double, const double)) &ROL::StdVector<double>::randomize, "C++: ROL::StdVector<double>::randomize(const double, const double) --> void", pybind11::arg("l"), pybind11::arg("u"));
		cl.def("print", (void (ROL::StdVector<double,double>::*)(std::ostream &) const) &ROL::StdVector<double>::print, "C++: ROL::StdVector<double>::print(std::ostream &) const --> void", pybind11::arg("outStream"));
		cl.def("assign", (class ROL::StdVector<double> & (ROL::StdVector<double,double>::*)(const class ROL::StdVector<double> &)) &ROL::StdVector<double>::operator=, "C++: ROL::StdVector<double>::operator=(const class ROL::StdVector<double> &) --> class ROL::StdVector<double> &", pybind11::return_value_policy::automatic, pybind11::arg(""));
		cl.def("plus", (void (ROL::Vector<double>::*)(const class ROL::Vector<double> &)) &ROL::Vector<double>::plus, "C++: ROL::Vector<double>::plus(const class ROL::Vector<double> &) --> void", pybind11::arg("x"));
		cl.def("scale", (void (ROL::Vector<double>::*)(const double)) &ROL::Vector<double>::scale, "C++: ROL::Vector<double>::scale(const double) --> void", pybind11::arg("alpha"));
		cl.def("dot", (double (ROL::Vector<double>::*)(const class ROL::Vector<double> &) const) &ROL::Vector<double>::dot, "C++: ROL::Vector<double>::dot(const class ROL::Vector<double> &) const --> double", pybind11::arg("x"));
		cl.def("norm", (double (ROL::Vector<double>::*)() const) &ROL::Vector<double>::norm, "C++: ROL::Vector<double>::norm() const --> double");
		cl.def("clone", (class Teuchos::RCP<class ROL::Vector<double> > (ROL::Vector<double>::*)() const) &ROL::Vector<double>::clone, "C++: ROL::Vector<double>::clone() const --> class Teuchos::RCP<class ROL::Vector<double> >");
		cl.def("axpy", (void (ROL::Vector<double>::*)(const double, const class ROL::Vector<double> &)) &ROL::Vector<double>::axpy, "Compute \n where \n.\n\n             \n is the scaling of \n             \n\n     is a vector.\n\n             On return \n.\n             Uses #clone, #set, #scale and #plus for the computation.\n             Please overload if a more efficient implementation is needed.\n\n             ---\n\nC++: ROL::Vector<double>::axpy(const double, const class ROL::Vector<double> &) --> void", pybind11::arg("alpha"), pybind11::arg("x"));
		cl.def("zero", (void (ROL::Vector<double>::*)()) &ROL::Vector<double>::zero, "Set to zero vector.\n\n             Uses #scale by zero for the computation.\n             Please overload if a more efficient implementation is needed.\n\n             ---\n\nC++: ROL::Vector<double>::zero() --> void");
		cl.def("basis", (class Teuchos::RCP<class ROL::Vector<double> > (ROL::Vector<double>::*)(const int) const) &ROL::Vector<double>::basis, "Return i-th basis vector.\n\n             \n is the index of the basis function.\n             \n\n A reference-counted pointer to the basis vector with index \n\n             Overloading the basis is only required if the default gradient implementation\n             is used, which computes a finite-difference approximation.\n\n             ---\n\nC++: ROL::Vector<double>::basis(const int) const --> class Teuchos::RCP<class ROL::Vector<double> >", pybind11::arg("i"));
		cl.def("dimension", (int (ROL::Vector<double>::*)() const) &ROL::Vector<double>::dimension, "Return dimension of the vector space.\n\n             \n The dimension of the vector space, i.e., the total number of basis vectors.\n\n             Overload if the basis is overloaded.\n\n             ---\n\nC++: ROL::Vector<double>::dimension() const --> int");
		cl.def("set", (void (ROL::Vector<double>::*)(const class ROL::Vector<double> &)) &ROL::Vector<double>::set, "Set \n where \n.\n\n             \n     is a vector.\n\n             On return \n.\n             Uses #zero and #plus methods for the computation.\n             Please overload if a more efficient implementation is needed.\n\n             ---\n\nC++: ROL::Vector<double>::set(const class ROL::Vector<double> &) --> void", pybind11::arg("x"));
		cl.def("dual", (const class ROL::Vector<double> & (ROL::Vector<double>::*)() const) &ROL::Vector<double>::dual, "Return dual representation of \n, for example,\n             the result of applying a Riesz map, or change of basis, or\n             change of memory layout.\n\n             \n         A const reference to dual representation.\n\n             By default, returns the current object.\n             Please overload if you need a dual representation.\n\n             ---\n\nC++: ROL::Vector<double>::dual() const --> const class ROL::Vector<double> &", pybind11::return_value_policy::automatic);
		cl.def("apply", (double (ROL::Vector<double>::*)(const class ROL::Vector<double> &) const) &ROL::Vector<double>::apply, "Apply \n to a dual vector.  This is equivalent\n             to the call \n\n.\n\n             \n      is a vector\n             \n\n         The number equal to \n.\n\n             ---\n\nC++: ROL::Vector<double>::apply(const class ROL::Vector<double> &) const --> double", pybind11::arg("x"));
		cl.def("applyUnary", (void (ROL::Vector<double>::*)(const class ROL::Elementwise::UnaryFunction<double> &)) &ROL::Vector<double>::applyUnary, "C++: ROL::Vector<double>::applyUnary(const class ROL::Elementwise::UnaryFunction<double> &) --> void", pybind11::arg("f"));
		cl.def("applyBinary", (void (ROL::Vector<double>::*)(const class ROL::Elementwise::BinaryFunction<double> &, const class ROL::Vector<double> &)) &ROL::Vector<double>::applyBinary, "C++: ROL::Vector<double>::applyBinary(const class ROL::Elementwise::BinaryFunction<double> &, const class ROL::Vector<double> &) --> void", pybind11::arg("f"), pybind11::arg("x"));
		cl.def("reduce", (double (ROL::Vector<double>::*)(const class ROL::Elementwise::ReductionOp<double> &) const) &ROL::Vector<double>::reduce, "C++: ROL::Vector<double>::reduce(const class ROL::Elementwise::ReductionOp<double> &) const --> double", pybind11::arg("r"));
		cl.def("print", (void (ROL::Vector<double>::*)(std::ostream &) const) &ROL::Vector<double>::print, "C++: ROL::Vector<double>::print(std::ostream &) const --> void", pybind11::arg("outStream"));
		cl.def("setScalar", (void (ROL::Vector<double>::*)(const double)) &ROL::Vector<double>::setScalar, "Set \n where \n.\n\n             \n     is a scalar.\n\n             On return \n.\n             Uses #applyUnary methods for the computation.\n             Please overload if a more efficient implementation is needed.\n\n             ---\n\nC++: ROL::Vector<double>::setScalar(const double) --> void", pybind11::arg("C"));
		cl.def("randomize", [](ROL::Vector<double> &o) -> void { return o.randomize(); }, "");
		cl.def("randomize", [](ROL::Vector<double> &o, const double & a0) -> void { return o.randomize(a0); }, "", pybind11::arg("l"));
		cl.def("randomize", (void (ROL::Vector<double>::*)(const double, const double)) &ROL::Vector<double>::randomize, "Set vector to be uniform random between [l,u].\n\n             \n     is a the lower bound.\n             \n\n     is a the upper bound.\n\n             On return the components of \n are uniform\n             random numbers on the interval \n\n.\n       	     The default implementation uses #applyUnary methods for the\n       	     computation. Please overload if a more efficient implementation is\n             needed.\n\n             ---\n\nC++: ROL::Vector<double>::randomize(const double, const double) --> void", pybind11::arg("l"), pybind11::arg("u"));
		cl.def("checkVector", [](ROL::Vector<double> const &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1) -> std::vector<double> { return o.checkVector(a0, a1); }, "", pybind11::arg("x"), pybind11::arg("y"));
		cl.def("checkVector", [](ROL::Vector<double> const &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const bool & a2) -> std::vector<double> { return o.checkVector(a0, a1, a2); }, "", pybind11::arg("x"), pybind11::arg("y"), pybind11::arg("printToStream"));
		cl.def("checkVector", (class std::vector<double> (ROL::Vector<double>::*)(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const bool, std::ostream &) const) &ROL::Vector<double>::checkVector, "Verify vector-space methods.\n\n             \n     is a vector.\n             \n\n     is a vector.\n\n             Returns a vector of Reals, all of which should be close to zero.\n             They represent consistency errors in the vector space properties,\n             as follows:\n\n             - Commutativity of addition: \n.\n             - Associativity of addition: \n\n.\n             - Identity element of addition: \n\n.\n             - Inverse elements of addition: \n\n.\n             - Identity element of scalar multiplication: \n\n.\n             - Consistency of scalar multiplication with field multiplication: \n\n.\n             - Distributivity of scalar multiplication with respect to field addition: \n\n.\n             - Distributivity of scalar multiplication with respect to vector addition: \n\n.\n             - Commutativity of dot (inner) product over the field of reals: \n\n.\n             - Additivity of dot (inner) product: \n\n.\n             - Consistency of scalar multiplication and norm: \n\n.\n             - Reflexivity: \n\n .\n             - Consistency of apply and dual: \n\n.\n\n             The consistency errors are defined as the norms or absolute values of the differences between the left-hand\n             side and the right-hand side terms in the above equalities.\n\n             ---\n\nC++: ROL::Vector<double>::checkVector(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const bool, std::ostream &) const --> class std::vector<double>", pybind11::arg("x"), pybind11::arg("y"), pybind11::arg("printToStream"), pybind11::arg("outStream"));
		cl.def("assign", (class ROL::Vector<double> & (ROL::Vector<double>::*)(const class ROL::Vector<double> &)) &ROL::Vector<double>::operator=, "C++: ROL::Vector<double>::operator=(const class ROL::Vector<double> &) --> class ROL::Vector<double> &", pybind11::return_value_policy::automatic, pybind11::arg(""));
	}
	{ // ROL::SampledVector file:ROL_SampledVector.hpp line:16
		pybind11::class_<ROL::SampledVector<double,std::vector<double>>, Teuchos::RCP<ROL::SampledVector<double,std::vector<double>>>> cl(M("ROL"), "SampledVector_double_std_vector_double_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new ROL::SampledVector<double,std::vector<double>>(); } ) );
		cl.def( pybind11::init( [](ROL::SampledVector<double,std::vector<double>> const &o){ return new ROL::SampledVector<double,std::vector<double>>(o); } ) );
		cl.def("update", [](ROL::SampledVector<double,std::vector<double>> &o) -> void { return o.update(); }, "");
		cl.def("update", (void (ROL::SampledVector<double,std::vector<double>>::*)(const bool)) &ROL::SampledVector<double>::update, "C++: ROL::SampledVector<double>::update(const bool) --> void", pybind11::arg("flag"));
		cl.def("get", (bool (ROL::SampledVector<double,std::vector<double>>::*)(class ROL::Vector<double> &, const class std::vector<double> &)) &ROL::SampledVector<double>::get, "C++: ROL::SampledVector<double>::get(class ROL::Vector<double> &, const class std::vector<double> &) --> bool", pybind11::arg("x"), pybind11::arg("param"));
		cl.def("set", (void (ROL::SampledVector<double,std::vector<double>>::*)(const class ROL::Vector<double> &, const class std::vector<double> &)) &ROL::SampledVector<double>::set, "C++: ROL::SampledVector<double>::set(const class ROL::Vector<double> &, const class std::vector<double> &) --> void", pybind11::arg("x"), pybind11::arg("param"));
		cl.def("assign", (class ROL::SampledVector<double> & (ROL::SampledVector<double,std::vector<double>>::*)(const class ROL::SampledVector<double> &)) &ROL::SampledVector<double>::operator=, "C++: ROL::SampledVector<double>::operator=(const class ROL::SampledVector<double> &) --> class ROL::SampledVector<double> &", pybind11::return_value_policy::automatic, pybind11::arg(""));
	}
}
