#include <PyROL_Teuchos_Custom.hpp>
#include <ROL_AbsoluteValue.hpp>
#include <ROL_AffineTransformConstraint.hpp>
#include <ROL_AffineTransformObjective.hpp>
#include <ROL_AlmostSureConstraint.hpp>
#include <ROL_Arcsine.hpp>
#include <ROL_AugmentedLagrangianObjective.hpp>
#include <ROL_BPOE.hpp>
#include <ROL_BackTracking_U.hpp>
#include <ROL_BarzilaiBorwein.hpp>
#include <ROL_BatchManager.hpp>
#include <ROL_BatchStdVector.hpp>
#include <ROL_Beta.hpp>
#include <ROL_BiCGSTAB.hpp>
#include <ROL_BisectionScalarMinimization.hpp>
#include <ROL_BoundConstraint.hpp>
#include <ROL_BoundConstraint_Partitioned.hpp>
#include <ROL_Bounds.hpp>
#include <ROL_Bracketing.hpp>
#include <ROL_BrentsProjection.hpp>
#include <ROL_BrentsScalarMinimization.hpp>
#include <ROL_BundleStatusTest.hpp>
#include <ROL_Bundle_U_AS.hpp>
#include <ROL_Bundle_U_TT.hpp>
#include <ROL_CVaR.hpp>
#include <ROL_Cauchy.hpp>
#include <ROL_CauchyPoint_U.hpp>
#include <ROL_ChebyshevSpectral.hpp>
#include <ROL_Chi2Divergence.hpp>
#include <ROL_CoherentEntropicRisk.hpp>
#include <ROL_CombinedStatusTest.hpp>
#include <ROL_ConjugateGradients.hpp>
#include <ROL_ConjugateResiduals.hpp>
#include <ROL_Constraint.hpp>
#include <ROL_ConstraintFromObjective.hpp>
#include <ROL_ConstraintStatusTest.hpp>
#include <ROL_Constraint_DynamicState.hpp>
#include <ROL_Constraint_Partitioned.hpp>
#include <ROL_Constraint_SimOpt.hpp>
#include <ROL_ConvexCombinationRiskMeasure.hpp>
#include <ROL_CubicInterp_U.hpp>
#include <ROL_DaiFletcherProjection.hpp>
#include <ROL_DescentDirection_U.hpp>
#include <ROL_Dirac.hpp>
#include <ROL_Distribution.hpp>
#include <ROL_DogLeg_U.hpp>
#include <ROL_DoubleDogLeg_U.hpp>
#include <ROL_DouglasRachfordProjection.hpp>
#include <ROL_DykstraProjection.hpp>
#include <ROL_DynamicConstraint.hpp>
#include <ROL_ElasticLinearConstraint.hpp>
#include <ROL_ElasticObjective.hpp>
#include <ROL_Elementwise_Function.hpp>
#include <ROL_Elementwise_Reduce.hpp>
#include <ROL_EntropicRisk.hpp>
#include <ROL_ExpectationQuad.hpp>
#include <ROL_ExpectationQuadDeviation.hpp>
#include <ROL_ExpectationQuadError.hpp>
#include <ROL_ExpectationQuadRegret.hpp>
#include <ROL_ExpectationQuadRisk.hpp>
#include <ROL_Exponential.hpp>
#include <ROL_Fejer2Quadrature.hpp>
#include <ROL_FletcherObjectiveE.hpp>
#include <ROL_GMRES.hpp>
#include <ROL_Gamma.hpp>
#include <ROL_GaussChebyshev1Quadrature.hpp>
#include <ROL_GaussChebyshev2Quadrature.hpp>
#include <ROL_GaussChebyshev3Quadrature.hpp>
#include <ROL_GaussLegendreQuadrature.hpp>
#include <ROL_Gaussian.hpp>
#include <ROL_GenMoreauYosidaCVaR.hpp>
#include <ROL_GoldenSectionScalarMinimization.hpp>
#include <ROL_Gradient_U.hpp>
#include <ROL_HMCR.hpp>
#include <ROL_IterationScaling_U.hpp>
#include <ROL_KLDivergence.hpp>
#include <ROL_Krylov.hpp>
#include <ROL_Kumaraswamy.hpp>
#include <ROL_Laplace.hpp>
#include <ROL_LineSearch_U.hpp>
#include <ROL_LinearCombinationObjective.hpp>
#include <ROL_LinearConstraint.hpp>
#include <ROL_LinearOperator.hpp>
#include <ROL_LogExponentialQuadrangle.hpp>
#include <ROL_LogQuantileQuadrangle.hpp>
#include <ROL_Logistic.hpp>
#include <ROL_MINRES.hpp>
#include <ROL_MeanDeviation.hpp>
#include <ROL_MeanDeviationFromTarget.hpp>
#include <ROL_MeanSemiDeviation.hpp>
#include <ROL_MeanSemiDeviationFromTarget.hpp>
#include <ROL_MeanValueConstraint.hpp>
#include <ROL_MeanValueObjective.hpp>
#include <ROL_MeanVariance.hpp>
#include <ROL_MeanVarianceFromTarget.hpp>
#include <ROL_MeanVarianceQuadrangle.hpp>
#include <ROL_MixedCVaR.hpp>
#include <ROL_MoreauYosidaCVaR.hpp>
#include <ROL_NewtonKrylov_U.hpp>
#include <ROL_Newton_U.hpp>
#include <ROL_NonlinearCG.hpp>
#include <ROL_NonlinearCG_U.hpp>
#include <ROL_NonlinearLeastSquaresObjective.hpp>
#include <ROL_NonlinearLeastSquaresObjective_Dynamic.hpp>
#include <ROL_NullSpaceOperator.hpp>
#include <ROL_OED_A_HetObjective.hpp>
#include <ROL_OED_A_HomObjective.hpp>
#include <ROL_OED_BilinearConstraint.hpp>
#include <ROL_OED_C_HetObjective.hpp>
#include <ROL_OED_C_HomObjective.hpp>
#include <ROL_OED_D_HetObjective.hpp>
#include <ROL_OED_D_HomObjective.hpp>
#include <ROL_OED_DoubleWellPenalty.hpp>
#include <ROL_OED_Factors.hpp>
#include <ROL_OED_I_HetObjective.hpp>
#include <ROL_OED_I_HomObjective.hpp>
#include <ROL_OED_Itrace_HetObjective.hpp>
#include <ROL_OED_Itrace_HomObjective.hpp>
#include <ROL_OED_L1Penalty.hpp>
#include <ROL_OED_LinearObjective.hpp>
#include <ROL_OED_MomentOperator.hpp>
#include <ROL_OED_Noise.hpp>
#include <ROL_OED_ProbabilityConstraint.hpp>
#include <ROL_OED_QuadraticObjective.hpp>
#include <ROL_OED_Radamacher.hpp>
#include <ROL_OED_Timer.hpp>
#include <ROL_OED_TraceSampler.hpp>
#include <ROL_Objective.hpp>
#include <ROL_Objective_FSsolver.hpp>
#include <ROL_PD_BPOE.hpp>
#include <ROL_PD_CVaR.hpp>
#include <ROL_PD_HMCR2.hpp>
#include <ROL_PD_MeanSemiDeviation.hpp>
#include <ROL_PD_MeanSemiDeviationFromTarget.hpp>
#include <ROL_PQNObjective.hpp>
#include <ROL_Parabolic.hpp>
#include <ROL_PartitionedVector.hpp>
#include <ROL_PathBasedTargetLevel_U.hpp>
#include <ROL_PlusFunction.hpp>
#include <ROL_PolyhedralProjection.hpp>
#include <ROL_PositiveFunction.hpp>
#include <ROL_ProbabilityVector.hpp>
#include <ROL_Problem.hpp>
#include <ROL_QuantileQuadrangle.hpp>
#include <ROL_QuantileRadius.hpp>
#include <ROL_QuasiNewton_U.hpp>
#include <ROL_RaisedCosine.hpp>
#include <ROL_RandVarFunctional.hpp>
#include <ROL_ReduceLinearConstraint.hpp>
#include <ROL_ReducedLinearConstraint.hpp>
#include <ROL_RiddersProjection.hpp>
#include <ROL_RiskBoundConstraint.hpp>
#include <ROL_RiskLessConstraint.hpp>
#include <ROL_RiskLessObjective.hpp>
#include <ROL_RiskNeutralConstraint.hpp>
#include <ROL_RiskNeutralObjective.hpp>
#include <ROL_RiskVector.hpp>
#include <ROL_SPGTrustRegion_U.hpp>
#include <ROL_SampleGenerator.hpp>
#include <ROL_SampledVector.hpp>
#include <ROL_ScalarController.hpp>
#include <ROL_ScalarFunction.hpp>
#include <ROL_ScalarLinearConstraint.hpp>
#include <ROL_ScalarMinimization.hpp>
#include <ROL_ScalarMinimizationLineSearch_U.hpp>
#include <ROL_ScalarMinimizationStatusTest.hpp>
#include <ROL_ScaledObjective.hpp>
#include <ROL_ScaledStdVector.hpp>
#include <ROL_Secant.hpp>
#include <ROL_SecondOrderCVaR.hpp>
#include <ROL_SemismoothNewtonProjection.hpp>
#include <ROL_SimConstraint.hpp>
#include <ROL_SimulatedBoundConstraint.hpp>
#include <ROL_SimulatedVector.hpp>
#include <ROL_SingletonVector.hpp>
#include <ROL_Sketch.hpp>
#include <ROL_SlacklessObjective.hpp>
#include <ROL_Smale.hpp>
#include <ROL_SmoothedPOE.hpp>
#include <ROL_SmoothedWorstCaseQuadrangle.hpp>
#include <ROL_Solver.hpp>
#include <ROL_SpectralRisk.hpp>
#include <ROL_StatusTest.hpp>
#include <ROL_StdBoundConstraint.hpp>
#include <ROL_StdVector.hpp>
#include <ROL_StochasticConstraint.hpp>
#include <ROL_StochasticObjective.hpp>
#include <ROL_StochasticProblem.hpp>
#include <ROL_Stream.hpp>
#include <ROL_TimeStamp.hpp>
#include <ROL_Triangle.hpp>
#include <ROL_TruncatedCG_U.hpp>
#include <ROL_TruncatedExponential.hpp>
#include <ROL_TruncatedGaussian.hpp>
#include <ROL_TruncatedMeanQuadrangle.hpp>
#include <ROL_TrustRegionModel_U.hpp>
#include <ROL_TrustRegion_U_Types.hpp>
#include <ROL_TypeB_Algorithm.hpp>
#include <ROL_TypeB_ColemanLiAlgorithm.hpp>
#include <ROL_TypeB_GradientAlgorithm.hpp>
#include <ROL_TypeB_InteriorPointAlgorithm.hpp>
#include <ROL_TypeB_KelleySachsAlgorithm.hpp>
#include <ROL_TypeB_LSecantBAlgorithm.hpp>
#include <ROL_TypeB_LinMoreAlgorithm.hpp>
#include <ROL_TypeB_MoreauYosidaAlgorithm.hpp>
#include <ROL_TypeB_NewtonKrylovAlgorithm.hpp>
#include <ROL_TypeB_PrimalDualActiveSetAlgorithm.hpp>
#include <ROL_TypeB_QuasiNewtonAlgorithm.hpp>
#include <ROL_TypeB_SpectralGradientAlgorithm.hpp>
#include <ROL_TypeB_TrustRegionSPGAlgorithm.hpp>
#include <ROL_TypeE_Algorithm.hpp>
#include <ROL_TypeE_AugmentedLagrangianAlgorithm.hpp>
#include <ROL_TypeE_CompositeStepAlgorithm.hpp>
#include <ROL_TypeE_FletcherAlgorithm.hpp>
#include <ROL_TypeE_StabilizedLCLAlgorithm.hpp>
#include <ROL_TypeG_Algorithm.hpp>
#include <ROL_TypeG_AugmentedLagrangianAlgorithm.hpp>
#include <ROL_TypeG_InteriorPointAlgorithm.hpp>
#include <ROL_TypeG_MoreauYosidaAlgorithm.hpp>
#include <ROL_TypeG_StabilizedLCLAlgorithm.hpp>
#include <ROL_TypeP_Algorithm.hpp>
#include <ROL_TypeP_InexactNewtonAlgorithm.hpp>
#include <ROL_TypeP_ProxGradientAlgorithm.hpp>
#include <ROL_TypeP_QuasiNewtonAlgorithm.hpp>
#include <ROL_TypeP_SpectralGradientAlgorithm.hpp>
#include <ROL_TypeP_TrustRegionAlgorithm.hpp>
#include <ROL_TypeP_iPianoAlgorithm.hpp>
#include <ROL_TypeU_Algorithm.hpp>
#include <ROL_TypeU_BundleAlgorithm.hpp>
#include <ROL_TypeU_LineSearchAlgorithm.hpp>
#include <ROL_TypeU_TrustRegionAlgorithm.hpp>
#include <ROL_Types.hpp>
#include <ROL_UnaryFunctions.hpp>
#include <ROL_Uniform.hpp>
#include <ROL_UpdateType.hpp>
#include <ROL_Vector.hpp>
#include <ROL_VectorController.hpp>
#include <ROL_VectorWorkspace.hpp>
#include <ROL_Vector_SimOpt.hpp>
#include <ROL_lBFGS.hpp>
#include <ROL_lDFP.hpp>
#include <ROL_lSR1.hpp>
#include <Teuchos_BLAS_types.hpp>
#include <Teuchos_DataAccess.hpp>
#include <Teuchos_ENull.hpp>
#include <Teuchos_FancyOStream.hpp>
#include <Teuchos_FilteredIterator.hpp>
#include <Teuchos_ParameterEntry.hpp>
#include <Teuchos_ParameterEntryValidator.hpp>
#include <Teuchos_ParameterList.hpp>
#include <Teuchos_ParameterListModifier.hpp>
#include <Teuchos_PtrDecl.hpp>
#include <Teuchos_RCP.hpp>
#include <Teuchos_RCPDecl.hpp>
#include <Teuchos_RCPNode.hpp>
#include <Teuchos_SerialDenseMatrix.hpp>
#include <Teuchos_SerialDenseVector.hpp>
#include <Teuchos_StringIndexedOrderedValueObjectContainer.hpp>
#include <Teuchos_any.hpp>
#include <deque>
#include <ios>
#include <iterator>
#include <locale>
#include <memory>
#include <ostream>
#include <random>
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

void bind_pyrol_9(std::function< pybind11::module &(std::string const &namespace_) > &M)
{
	// Teuchos::RCP_createNewRCPNodeRawPtrNonowned(std::ostream *) file:Teuchos_RCP.hpp line:43
	M("Teuchos").def("RCP_createNewRCPNodeRawPtrNonowned", (class Teuchos::RCPNode * (*)(std::ostream *)) &Teuchos::RCP_createNewRCPNodeRawPtrNonowned<std::ostream>, "C++: Teuchos::RCP_createNewRCPNodeRawPtrNonowned(std::ostream *) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"));

	// Teuchos::RCP_createNewRCPNodeRawPtrNonowned(class Teuchos::ParameterEntry *) file:Teuchos_RCP.hpp line:43
	M("Teuchos").def("RCP_createNewRCPNodeRawPtrNonowned", (class Teuchos::RCPNode * (*)(class Teuchos::ParameterEntry *)) &Teuchos::RCP_createNewRCPNodeRawPtrNonowned<Teuchos::ParameterEntry>, "C++: Teuchos::RCP_createNewRCPNodeRawPtrNonowned(class Teuchos::ParameterEntry *) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"));

	// Teuchos::RCP_createNewRCPNodeRawPtrNonowned(const class Teuchos::ParameterEntry *) file:Teuchos_RCP.hpp line:43
	M("Teuchos").def("RCP_createNewRCPNodeRawPtrNonowned", (class Teuchos::RCPNode * (*)(const class Teuchos::ParameterEntry *)) &Teuchos::RCP_createNewRCPNodeRawPtrNonowned<const Teuchos::ParameterEntry>, "C++: Teuchos::RCP_createNewRCPNodeRawPtrNonowned(const class Teuchos::ParameterEntry *) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"));

	// Teuchos::RCP_createNewRCPNodeRawPtrNonowned(class ROL::Objective<double> *) file:Teuchos_RCP.hpp line:43
	M("Teuchos").def("RCP_createNewRCPNodeRawPtrNonowned", (class Teuchos::RCPNode * (*)(class ROL::Objective<double> *)) &Teuchos::RCP_createNewRCPNodeRawPtrNonowned<ROL::Objective<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtrNonowned(class ROL::Objective<double> *) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"));

	// Teuchos::RCP_createNewRCPNodeRawPtrNonowned(class ROL::Constraint<double> *) file:Teuchos_RCP.hpp line:43
	M("Teuchos").def("RCP_createNewRCPNodeRawPtrNonowned", (class Teuchos::RCPNode * (*)(class ROL::Constraint<double> *)) &Teuchos::RCP_createNewRCPNodeRawPtrNonowned<ROL::Constraint<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtrNonowned(class ROL::Constraint<double> *) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"));

	// Teuchos::RCP_createNewRCPNodeRawPtrNonowned(class ROL::BoundConstraint<double> *) file:Teuchos_RCP.hpp line:43
	M("Teuchos").def("RCP_createNewRCPNodeRawPtrNonowned", (class Teuchos::RCPNode * (*)(class ROL::BoundConstraint<double> *)) &Teuchos::RCP_createNewRCPNodeRawPtrNonowned<ROL::BoundConstraint<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtrNonowned(class ROL::BoundConstraint<double> *) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"));

	// Teuchos::RCP_createNewRCPNodeRawPtrNonowned(class ROL::Vector<double> *) file:Teuchos_RCP.hpp line:43
	M("Teuchos").def("RCP_createNewRCPNodeRawPtrNonowned", (class Teuchos::RCPNode * (*)(class ROL::Vector<double> *)) &Teuchos::RCP_createNewRCPNodeRawPtrNonowned<ROL::Vector<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtrNonowned(class ROL::Vector<double> *) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"));

	// Teuchos::RCP_createNewRCPNodeRawPtrNonowned(class ROL::ElasticObjective<double> *) file:Teuchos_RCP.hpp line:43
	M("Teuchos").def("RCP_createNewRCPNodeRawPtrNonowned", (class Teuchos::RCPNode * (*)(class ROL::ElasticObjective<double> *)) &Teuchos::RCP_createNewRCPNodeRawPtrNonowned<ROL::ElasticObjective<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtrNonowned(class ROL::ElasticObjective<double> *) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"));

	// Teuchos::RCP_createNewRCPNodeRawPtrNonowned(class ROL::details::basic_nullstream<char, struct std::char_traits<char> > *) file:Teuchos_RCP.hpp line:43
	M("Teuchos").def("RCP_createNewRCPNodeRawPtrNonowned", (class Teuchos::RCPNode * (*)(class ROL::details::basic_nullstream<char, struct std::char_traits<char> > *)) &Teuchos::RCP_createNewRCPNodeRawPtrNonowned<ROL::details::basic_nullstream<char, std::char_traits<char> >>, "C++: Teuchos::RCP_createNewRCPNodeRawPtrNonowned(class ROL::details::basic_nullstream<char, struct std::char_traits<char> > *) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"));

	// Teuchos::RCP_createNewRCPNodeRawPtrNonowned(const class ROL::Vector<double> *) file:Teuchos_RCP.hpp line:43
	M("Teuchos").def("RCP_createNewRCPNodeRawPtrNonowned", (class Teuchos::RCPNode * (*)(const class ROL::Vector<double> *)) &Teuchos::RCP_createNewRCPNodeRawPtrNonowned<const ROL::Vector<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtrNonowned(const class ROL::Vector<double> *) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"));

	// Teuchos::RCP_createNewRCPNodeRawPtrNonowned(class ROL::Constraint_SimOpt<double> *) file:Teuchos_RCP.hpp line:43
	M("Teuchos").def("RCP_createNewRCPNodeRawPtrNonowned", (class Teuchos::RCPNode * (*)(class ROL::Constraint_SimOpt<double> *)) &Teuchos::RCP_createNewRCPNodeRawPtrNonowned<ROL::Constraint_SimOpt<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtrNonowned(class ROL::Constraint_SimOpt<double> *) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"));

	// Teuchos::RCP_createNewRCPNodeRawPtrNonowned(class ROL::DynamicConstraint<double> *) file:Teuchos_RCP.hpp line:43
	M("Teuchos").def("RCP_createNewRCPNodeRawPtrNonowned", (class Teuchos::RCPNode * (*)(class ROL::DynamicConstraint<double> *)) &Teuchos::RCP_createNewRCPNodeRawPtrNonowned<ROL::DynamicConstraint<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtrNonowned(class ROL::DynamicConstraint<double> *) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"));

	// Teuchos::RCP_createNewRCPNodeRawPtrNonowned(const struct ROL::TimeStamp<double> *) file:Teuchos_RCP.hpp line:43
	M("Teuchos").def("RCP_createNewRCPNodeRawPtrNonowned", (class Teuchos::RCPNode * (*)(const struct ROL::TimeStamp<double> *)) &Teuchos::RCP_createNewRCPNodeRawPtrNonowned<const ROL::TimeStamp<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtrNonowned(const struct ROL::TimeStamp<double> *) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"));

	// Teuchos::RCP_createNewRCPNodeRawPtrNonowned(class Teuchos::ParameterList *) file:Teuchos_RCP.hpp line:43
	M("Teuchos").def("RCP_createNewRCPNodeRawPtrNonowned", (class Teuchos::RCPNode * (*)(class Teuchos::ParameterList *)) &Teuchos::RCP_createNewRCPNodeRawPtrNonowned<Teuchos::ParameterList>, "C++: Teuchos::RCP_createNewRCPNodeRawPtrNonowned(class Teuchos::ParameterList *) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"));

	// Teuchos::RCP_createNewRCPNodeRawPtrNonowned(class std::vector<double> *) file:Teuchos_RCP.hpp line:43
	M("Teuchos").def("RCP_createNewRCPNodeRawPtrNonowned", (class Teuchos::RCPNode * (*)(class std::vector<double> *)) &Teuchos::RCP_createNewRCPNodeRawPtrNonowned<std::vector<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtrNonowned(class std::vector<double> *) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"));

	// Teuchos::RCP_createNewRCPNodeRawPtrNonowned(const class ROL::ProbabilityVector<double> *) file:Teuchos_RCP.hpp line:43
	M("Teuchos").def("RCP_createNewRCPNodeRawPtrNonowned", (class Teuchos::RCPNode * (*)(const class ROL::ProbabilityVector<double> *)) &Teuchos::RCP_createNewRCPNodeRawPtrNonowned<const ROL::ProbabilityVector<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtrNonowned(const class ROL::ProbabilityVector<double> *) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::details::basic_nullstream<char, struct std::char_traits<char> > *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::details::basic_nullstream<char, struct std::char_traits<char> > *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::details::basic_nullstream<char, std::char_traits<char> >>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::details::basic_nullstream<char, struct std::char_traits<char> > *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class Teuchos::basic_FancyOStream<char> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class Teuchos::basic_FancyOStream<char> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<Teuchos::basic_FancyOStream<char>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class Teuchos::basic_FancyOStream<char> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(std::ostream *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(std::ostream *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<std::ostream>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(std::ostream *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class Teuchos::ParameterList *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class Teuchos::ParameterList *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<Teuchos::ParameterList>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class Teuchos::ParameterList *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::BoundConstraint<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::BoundConstraint<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::BoundConstraint<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::BoundConstraint<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Constraint_Partitioned<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::Constraint_Partitioned<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::Constraint_Partitioned<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Constraint_Partitioned<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::PartitionedVector<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::PartitionedVector<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::PartitionedVector<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::PartitionedVector<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::BoundConstraint_Partitioned<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::BoundConstraint_Partitioned<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::BoundConstraint_Partitioned<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::BoundConstraint_Partitioned<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::SlacklessObjective<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::SlacklessObjective<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::SlacklessObjective<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::SlacklessObjective<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::NullSpaceOperator<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::NullSpaceOperator<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::NullSpaceOperator<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::NullSpaceOperator<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::ReduceLinearConstraint<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::ReduceLinearConstraint<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::ReduceLinearConstraint<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::ReduceLinearConstraint<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::LinearConstraint<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::LinearConstraint<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::LinearConstraint<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::LinearConstraint<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::AffineTransformObjective<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::AffineTransformObjective<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::AffineTransformObjective<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::AffineTransformObjective<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::AffineTransformConstraint<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::AffineTransformConstraint<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::AffineTransformConstraint<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::AffineTransformConstraint<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::DaiFletcherProjection<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::DaiFletcherProjection<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::DaiFletcherProjection<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::DaiFletcherProjection<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::DykstraProjection<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::DykstraProjection<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::DykstraProjection<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::DykstraProjection<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::DouglasRachfordProjection<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::DouglasRachfordProjection<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::DouglasRachfordProjection<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::DouglasRachfordProjection<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::ConjugateResiduals<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::ConjugateResiduals<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::ConjugateResiduals<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::ConjugateResiduals<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::ConjugateGradients<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::ConjugateGradients<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::ConjugateGradients<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::ConjugateGradients<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class Teuchos::SerialDenseMatrix<int, double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class Teuchos::SerialDenseMatrix<int, double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<Teuchos::SerialDenseMatrix<int, double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class Teuchos::SerialDenseMatrix<int, double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class Teuchos::SerialDenseVector<int, double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class Teuchos::SerialDenseVector<int, double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<Teuchos::SerialDenseVector<int, double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class Teuchos::SerialDenseVector<int, double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class std::vector<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class std::vector<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<std::vector<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class std::vector<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::GMRES<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::GMRES<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::GMRES<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::GMRES<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::details::MINRES<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::details::MINRES<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::details::MINRES<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::details::MINRES<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::BiCGSTAB<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::BiCGSTAB<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::BiCGSTAB<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::BiCGSTAB<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::SemismoothNewtonProjection<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::SemismoothNewtonProjection<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::SemismoothNewtonProjection<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::SemismoothNewtonProjection<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::RiddersProjection<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::RiddersProjection<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::RiddersProjection<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::RiddersProjection<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::BrentsProjection<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::BrentsProjection<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::BrentsProjection<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::BrentsProjection<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::CombinedStatusTest<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::CombinedStatusTest<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::CombinedStatusTest<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::CombinedStatusTest<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(struct ROL::TypeU::AlgorithmState<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(struct ROL::TypeU::AlgorithmState<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::TypeU::AlgorithmState<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(struct ROL::TypeU::AlgorithmState<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::StatusTest<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::StatusTest<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::StatusTest<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::StatusTest<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::BundleStatusTest<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::BundleStatusTest<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::BundleStatusTest<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::BundleStatusTest<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Bundle_U_TT<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::Bundle_U_TT<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::Bundle_U_TT<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Bundle_U_TT<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Bundle_U_AS<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::Bundle_U_AS<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::Bundle_U_AS<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Bundle_U_AS<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::IterationScaling_U<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::IterationScaling_U<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::IterationScaling_U<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::IterationScaling_U<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::PathBasedTargetLevel_U<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::PathBasedTargetLevel_U<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::PathBasedTargetLevel_U<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::PathBasedTargetLevel_U<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::BackTracking_U<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::BackTracking_U<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::BackTracking_U<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::BackTracking_U<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::CubicInterp_U<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::CubicInterp_U<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::CubicInterp_U<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::CubicInterp_U<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Bracketing<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::Bracketing<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::Bracketing<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Bracketing<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::BrentsScalarMinimization<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::BrentsScalarMinimization<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::BrentsScalarMinimization<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::BrentsScalarMinimization<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::BisectionScalarMinimization<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::BisectionScalarMinimization<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::BisectionScalarMinimization<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::BisectionScalarMinimization<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::GoldenSectionScalarMinimization<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::GoldenSectionScalarMinimization<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::GoldenSectionScalarMinimization<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::GoldenSectionScalarMinimization<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::ScalarMinimizationLineSearch_U<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::ScalarMinimizationLineSearch_U<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::ScalarMinimizationLineSearch_U<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::ScalarMinimizationLineSearch_U<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeU::BundleAlgorithm<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::TypeU::BundleAlgorithm<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::TypeU::BundleAlgorithm<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeU::BundleAlgorithm<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Gradient_U<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::Gradient_U<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::Gradient_U<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Gradient_U<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(struct ROL::NonlinearCGState<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(struct ROL::NonlinearCGState<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::NonlinearCGState<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(struct ROL::NonlinearCGState<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::NonlinearCG<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::NonlinearCG<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::NonlinearCG<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::NonlinearCG<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::NonlinearCG_U<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::NonlinearCG_U<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::NonlinearCG_U<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::NonlinearCG_U<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(struct ROL::SecantState<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(struct ROL::SecantState<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::SecantState<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(struct ROL::SecantState<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::lBFGS<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::lBFGS<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::lBFGS<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::lBFGS<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::lDFP<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::lDFP<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::lDFP<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::lDFP<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::lSR1<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::lSR1<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::lSR1<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::lSR1<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::BarzilaiBorwein<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::BarzilaiBorwein<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::BarzilaiBorwein<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::BarzilaiBorwein<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::QuasiNewton_U<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::QuasiNewton_U<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::QuasiNewton_U<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::QuasiNewton_U<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Newton_U<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::Newton_U<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::Newton_U<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Newton_U<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::NewtonKrylov_U<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::NewtonKrylov_U<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::NewtonKrylov_U<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::NewtonKrylov_U<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeU::LineSearchAlgorithm<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::TypeU::LineSearchAlgorithm<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::TypeU::LineSearchAlgorithm<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeU::LineSearchAlgorithm<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::CauchyPoint_U<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::CauchyPoint_U<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::CauchyPoint_U<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::CauchyPoint_U<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::DogLeg_U<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::DogLeg_U<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::DogLeg_U<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::DogLeg_U<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::DoubleDogLeg_U<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::DoubleDogLeg_U<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::DoubleDogLeg_U<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::DoubleDogLeg_U<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TruncatedCG_U<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::TruncatedCG_U<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::TruncatedCG_U<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TruncatedCG_U<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::SPGTrustRegion_U<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::SPGTrustRegion_U<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::SPGTrustRegion_U<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::SPGTrustRegion_U<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TrustRegionModel_U<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::TrustRegionModel_U<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::TrustRegionModel_U<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TrustRegionModel_U<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeU::TrustRegionAlgorithm<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::TypeU::TrustRegionAlgorithm<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::TypeU::TrustRegionAlgorithm<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeU::TrustRegionAlgorithm<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(struct ROL::TypeP::AlgorithmState<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(struct ROL::TypeP::AlgorithmState<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::TypeP::AlgorithmState<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(struct ROL::TypeP::AlgorithmState<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeP::TrustRegionAlgorithm<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::TypeP::TrustRegionAlgorithm<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::TypeP::TrustRegionAlgorithm<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeP::TrustRegionAlgorithm<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeP::InexactNewtonAlgorithm<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::TypeP::InexactNewtonAlgorithm<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::TypeP::InexactNewtonAlgorithm<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeP::InexactNewtonAlgorithm<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::PQNObjective<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::PQNObjective<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::PQNObjective<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::PQNObjective<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeP::QuasiNewtonAlgorithm<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::TypeP::QuasiNewtonAlgorithm<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::TypeP::QuasiNewtonAlgorithm<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeP::QuasiNewtonAlgorithm<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeP::ProxGradientAlgorithm<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::TypeP::ProxGradientAlgorithm<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::TypeP::ProxGradientAlgorithm<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeP::ProxGradientAlgorithm<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeP::SpectralGradientAlgorithm<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::TypeP::SpectralGradientAlgorithm<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::TypeP::SpectralGradientAlgorithm<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeP::SpectralGradientAlgorithm<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeP::iPianoAlgorithm<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::TypeP::iPianoAlgorithm<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::TypeP::iPianoAlgorithm<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeP::iPianoAlgorithm<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(struct ROL::TypeB::AlgorithmState<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(struct ROL::TypeB::AlgorithmState<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::TypeB::AlgorithmState<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(struct ROL::TypeB::AlgorithmState<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::PolyhedralProjection<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::PolyhedralProjection<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::PolyhedralProjection<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::PolyhedralProjection<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeB::NewtonKrylovAlgorithm<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::TypeB::NewtonKrylovAlgorithm<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::TypeB::NewtonKrylovAlgorithm<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeB::NewtonKrylovAlgorithm<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::ReducedLinearConstraint<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::ReducedLinearConstraint<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::ReducedLinearConstraint<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::ReducedLinearConstraint<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeB::LSecantBAlgorithm<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::TypeB::LSecantBAlgorithm<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::TypeB::LSecantBAlgorithm<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeB::LSecantBAlgorithm<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Problem<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::Problem<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::Problem<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Problem<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeB::LinMoreAlgorithm<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::TypeB::LinMoreAlgorithm<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::TypeB::LinMoreAlgorithm<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeB::LinMoreAlgorithm<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeB::PrimalDualActiveSetAlgorithm<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::TypeB::PrimalDualActiveSetAlgorithm<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::TypeB::PrimalDualActiveSetAlgorithm<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeB::PrimalDualActiveSetAlgorithm<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::ScalarController<double, int> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::ScalarController<double, int> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::ScalarController<double, int>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::ScalarController<double, int> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::VectorController<double, int> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::VectorController<double, int> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::VectorController<double, int>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::VectorController<double, int> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::SingletonVector<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::SingletonVector<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::SingletonVector<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::SingletonVector<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeB::MoreauYosidaAlgorithm<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::TypeB::MoreauYosidaAlgorithm<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::TypeB::MoreauYosidaAlgorithm<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeB::MoreauYosidaAlgorithm<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeB::InteriorPointAlgorithm<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::TypeB::InteriorPointAlgorithm<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::TypeB::InteriorPointAlgorithm<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeB::InteriorPointAlgorithm<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeB::QuasiNewtonAlgorithm<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::TypeB::QuasiNewtonAlgorithm<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::TypeB::QuasiNewtonAlgorithm<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeB::QuasiNewtonAlgorithm<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeB::GradientAlgorithm<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::TypeB::GradientAlgorithm<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::TypeB::GradientAlgorithm<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeB::GradientAlgorithm<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeB::KelleySachsAlgorithm<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::TypeB::KelleySachsAlgorithm<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::TypeB::KelleySachsAlgorithm<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeB::KelleySachsAlgorithm<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeB::TrustRegionSPGAlgorithm<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::TypeB::TrustRegionSPGAlgorithm<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::TypeB::TrustRegionSPGAlgorithm<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeB::TrustRegionSPGAlgorithm<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeB::ColemanLiAlgorithm<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::TypeB::ColemanLiAlgorithm<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::TypeB::ColemanLiAlgorithm<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeB::ColemanLiAlgorithm<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeB::SpectralGradientAlgorithm<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::TypeB::SpectralGradientAlgorithm<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::TypeB::SpectralGradientAlgorithm<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeB::SpectralGradientAlgorithm<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(struct ROL::TypeE::AlgorithmState<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(struct ROL::TypeE::AlgorithmState<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::TypeE::AlgorithmState<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(struct ROL::TypeE::AlgorithmState<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::ConstraintStatusTest<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::ConstraintStatusTest<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::ConstraintStatusTest<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::ConstraintStatusTest<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeE::AugmentedLagrangianAlgorithm<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::TypeE::AugmentedLagrangianAlgorithm<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::TypeE::AugmentedLagrangianAlgorithm<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeE::AugmentedLagrangianAlgorithm<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeE::FletcherAlgorithm<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::TypeE::FletcherAlgorithm<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::TypeE::FletcherAlgorithm<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeE::FletcherAlgorithm<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeE::CompositeStepAlgorithm<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::TypeE::CompositeStepAlgorithm<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::TypeE::CompositeStepAlgorithm<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeE::CompositeStepAlgorithm<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::AugmentedLagrangianObjective<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::AugmentedLagrangianObjective<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::AugmentedLagrangianObjective<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::AugmentedLagrangianObjective<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::ElasticLinearConstraint<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::ElasticLinearConstraint<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::ElasticLinearConstraint<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::ElasticLinearConstraint<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Bounds<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::Bounds<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::Bounds<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Bounds<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeE::StabilizedLCLAlgorithm<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::TypeE::StabilizedLCLAlgorithm<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::TypeE::StabilizedLCLAlgorithm<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeE::StabilizedLCLAlgorithm<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(struct ROL::TypeG::AlgorithmState<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(struct ROL::TypeG::AlgorithmState<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::TypeG::AlgorithmState<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(struct ROL::TypeG::AlgorithmState<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeG::AugmentedLagrangianAlgorithm<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::TypeG::AugmentedLagrangianAlgorithm<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::TypeG::AugmentedLagrangianAlgorithm<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeG::AugmentedLagrangianAlgorithm<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeG::MoreauYosidaAlgorithm<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::TypeG::MoreauYosidaAlgorithm<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::TypeG::MoreauYosidaAlgorithm<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeG::MoreauYosidaAlgorithm<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeG::InteriorPointAlgorithm<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::TypeG::InteriorPointAlgorithm<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::TypeG::InteriorPointAlgorithm<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeG::InteriorPointAlgorithm<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeG::StabilizedLCLAlgorithm<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::TypeG::StabilizedLCLAlgorithm<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::TypeG::StabilizedLCLAlgorithm<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TypeG::StabilizedLCLAlgorithm<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Vector_SimOpt<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::Vector_SimOpt<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::Vector_SimOpt<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Vector_SimOpt<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::VectorController<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::VectorController<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::VectorController<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::VectorController<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::SimConstraint<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::SimConstraint<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::SimConstraint<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::SimConstraint<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::NonlinearLeastSquaresObjective<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::NonlinearLeastSquaresObjective<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::NonlinearLeastSquaresObjective<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::NonlinearLeastSquaresObjective<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Objective_FSsolver<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::Objective_FSsolver<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::Objective_FSsolver<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Objective_FSsolver<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class std::normal_distribution<> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class std::normal_distribution<> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<std::normal_distribution<>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class std::normal_distribution<> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Elementwise::NormalRandom<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::Elementwise::NormalRandom<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::Elementwise::NormalRandom<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Elementwise::NormalRandom<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class std::mersenne_twister_engine<unsigned long, 64, 312, 156, 31, 13043109905998158313, 29, 6148914691236517205, 17, 8202884508482404352, 37, 18444473444759240704, 43, 6364136223846793005> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class std::mersenne_twister_engine<unsigned long, 64, 312, 156, 31, 13043109905998158313, 29, 6148914691236517205, 17, 8202884508482404352, 37, 18444473444759240704, 43, 6364136223846793005> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<std::mersenne_twister_engine<unsigned long, 64, 312, 156, 31, 13043109905998158313, 29, 6148914691236517205, 17, 8202884508482404352, 37, 18444473444759240704, 43, 6364136223846793005>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class std::mersenne_twister_engine<unsigned long, 64, 312, 156, 31, 13043109905998158313, 29, 6148914691236517205, 17, 8202884508482404352, 37, 18444473444759240704, 43, 6364136223846793005> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Sketch<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::Sketch<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::Sketch<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Sketch<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::NonlinearLeastSquaresObjective_Dynamic<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::NonlinearLeastSquaresObjective_Dynamic<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::NonlinearLeastSquaresObjective_Dynamic<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::NonlinearLeastSquaresObjective_Dynamic<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Constraint_DynamicState<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::Constraint_DynamicState<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::Constraint_DynamicState<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Constraint_DynamicState<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::PD_CVaR<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::PD_CVaR<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::PD_CVaR<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::PD_CVaR<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::PD_MeanSemiDeviation<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::PD_MeanSemiDeviation<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::PD_MeanSemiDeviation<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::PD_MeanSemiDeviation<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::PD_MeanSemiDeviationFromTarget<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::PD_MeanSemiDeviationFromTarget<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::PD_MeanSemiDeviationFromTarget<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::PD_MeanSemiDeviationFromTarget<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::PD_HMCR2<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::PD_HMCR2<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::PD_HMCR2<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::PD_HMCR2<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::PD_BPOE<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::PD_BPOE<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::PD_BPOE<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::PD_BPOE<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::StdVector<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::StdVector<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::StdVector<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::StdVector<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::RiskVector<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::RiskVector<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::RiskVector<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::RiskVector<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(const class std::vector<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(const class std::vector<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<const std::vector<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(const class std::vector<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::StochasticObjective<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::StochasticObjective<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::StochasticObjective<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::StochasticObjective<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::StdBoundConstraint<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::StdBoundConstraint<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::StdBoundConstraint<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::StdBoundConstraint<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::RiskBoundConstraint<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::RiskBoundConstraint<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::RiskBoundConstraint<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::RiskBoundConstraint<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::RiskLessConstraint<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::RiskLessConstraint<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::RiskLessConstraint<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::RiskLessConstraint<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Solver<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::Solver<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::Solver<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Solver<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::ScalarController<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::ScalarController<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::ScalarController<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::ScalarController<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::RiskNeutralObjective<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::RiskNeutralObjective<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::RiskNeutralObjective<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::RiskNeutralObjective<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Arcsine<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::Arcsine<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::Arcsine<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Arcsine<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Beta<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::Beta<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::Beta<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Beta<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Cauchy<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::Cauchy<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::Cauchy<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Cauchy<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Dirac<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::Dirac<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::Dirac<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Dirac<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Exponential<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::Exponential<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::Exponential<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Exponential<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Gamma<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::Gamma<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::Gamma<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Gamma<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Gaussian<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::Gaussian<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::Gaussian<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Gaussian<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Kumaraswamy<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::Kumaraswamy<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::Kumaraswamy<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Kumaraswamy<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Laplace<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::Laplace<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::Laplace<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Laplace<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Logistic<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::Logistic<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::Logistic<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Logistic<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Parabolic<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::Parabolic<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::Parabolic<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Parabolic<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::RaisedCosine<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::RaisedCosine<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::RaisedCosine<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::RaisedCosine<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Smale<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::Smale<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::Smale<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Smale<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Triangle<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::Triangle<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::Triangle<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Triangle<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TruncatedExponential<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::TruncatedExponential<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::TruncatedExponential<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TruncatedExponential<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TruncatedGaussian<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::TruncatedGaussian<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::TruncatedGaussian<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TruncatedGaussian<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Uniform<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::Uniform<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::Uniform<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Uniform<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::PlusFunction<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::PlusFunction<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::PlusFunction<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::PlusFunction<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::CVaR<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::CVaR<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::CVaR<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::CVaR<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::MoreauYosidaCVaR<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::MoreauYosidaCVaR<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::MoreauYosidaCVaR<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::MoreauYosidaCVaR<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::ExpectationQuadRisk<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::ExpectationQuadRisk<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::ExpectationQuadRisk<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::ExpectationQuadRisk<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::GenMoreauYosidaCVaR<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::GenMoreauYosidaCVaR<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::GenMoreauYosidaCVaR<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::GenMoreauYosidaCVaR<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::MixedCVaR<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::MixedCVaR<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::MixedCVaR<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::MixedCVaR<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::SpectralRisk<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::SpectralRisk<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::SpectralRisk<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::SpectralRisk<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::GaussLegendreQuadrature<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::GaussLegendreQuadrature<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::GaussLegendreQuadrature<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::GaussLegendreQuadrature<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Fejer2Quadrature<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::Fejer2Quadrature<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::Fejer2Quadrature<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Fejer2Quadrature<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::SecondOrderCVaR<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::SecondOrderCVaR<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::SecondOrderCVaR<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::SecondOrderCVaR<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::GaussChebyshev1Quadrature<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::GaussChebyshev1Quadrature<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::GaussChebyshev1Quadrature<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::GaussChebyshev1Quadrature<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::GaussChebyshev2Quadrature<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::GaussChebyshev2Quadrature<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::GaussChebyshev2Quadrature<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::GaussChebyshev2Quadrature<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::GaussChebyshev3Quadrature<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::GaussChebyshev3Quadrature<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::GaussChebyshev3Quadrature<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::GaussChebyshev3Quadrature<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::ChebyshevSpectral<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::ChebyshevSpectral<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::ChebyshevSpectral<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::ChebyshevSpectral<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::QuantileRadius<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::QuantileRadius<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::QuantileRadius<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::QuantileRadius<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::HMCR<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::HMCR<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::HMCR<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::HMCR<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::EntropicRisk<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::EntropicRisk<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::EntropicRisk<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::EntropicRisk<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::CoherentEntropicRisk<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::CoherentEntropicRisk<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::CoherentEntropicRisk<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::CoherentEntropicRisk<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::MeanSemiDeviation<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::MeanSemiDeviation<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::MeanSemiDeviation<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::MeanSemiDeviation<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::MeanSemiDeviationFromTarget<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::MeanSemiDeviationFromTarget<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::MeanSemiDeviationFromTarget<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::MeanSemiDeviationFromTarget<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::AbsoluteValue<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::AbsoluteValue<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::AbsoluteValue<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::AbsoluteValue<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::MeanDeviationFromTarget<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::MeanDeviationFromTarget<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::MeanDeviationFromTarget<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::MeanDeviationFromTarget<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::MeanDeviation<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::MeanDeviation<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::MeanDeviation<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::MeanDeviation<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::MeanVarianceFromTarget<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::MeanVarianceFromTarget<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::MeanVarianceFromTarget<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::MeanVarianceFromTarget<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::MeanVariance<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::MeanVariance<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::MeanVariance<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::MeanVariance<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TruncatedMeanQuadrangle<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::TruncatedMeanQuadrangle<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::TruncatedMeanQuadrangle<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::TruncatedMeanQuadrangle<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::LogQuantileQuadrangle<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::LogQuantileQuadrangle<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::LogQuantileQuadrangle<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::LogQuantileQuadrangle<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::SmoothedWorstCaseQuadrangle<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::SmoothedWorstCaseQuadrangle<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::SmoothedWorstCaseQuadrangle<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::SmoothedWorstCaseQuadrangle<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::LogExponentialQuadrangle<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::LogExponentialQuadrangle<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::LogExponentialQuadrangle<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::LogExponentialQuadrangle<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::MeanVarianceQuadrangle<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::MeanVarianceQuadrangle<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::MeanVarianceQuadrangle<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::MeanVarianceQuadrangle<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Chi2Divergence<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::Chi2Divergence<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::Chi2Divergence<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::Chi2Divergence<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::KLDivergence<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::KLDivergence<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::KLDivergence<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::KLDivergence<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::ConvexCombinationRiskMeasure<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::ConvexCombinationRiskMeasure<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::ConvexCombinationRiskMeasure<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::ConvexCombinationRiskMeasure<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::ExpectationQuadDeviation<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::ExpectationQuadDeviation<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::ExpectationQuadDeviation<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::ExpectationQuadDeviation<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::QuantileQuadrangle<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::QuantileQuadrangle<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::QuantileQuadrangle<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::QuantileQuadrangle<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::ExpectationQuadError<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::ExpectationQuadError<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::ExpectationQuadError<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::ExpectationQuadError<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::ExpectationQuadRegret<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::ExpectationQuadRegret<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::ExpectationQuadRegret<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::ExpectationQuadRegret<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::BPOE<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::BPOE<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::BPOE<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::BPOE<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::SmoothedPOE<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::SmoothedPOE<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::SmoothedPOE<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::SmoothedPOE<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::MeanValueObjective<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::MeanValueObjective<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::MeanValueObjective<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::MeanValueObjective<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::RiskNeutralConstraint<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::RiskNeutralConstraint<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::RiskNeutralConstraint<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::RiskNeutralConstraint<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::AlmostSureConstraint<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::AlmostSureConstraint<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::AlmostSureConstraint<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::AlmostSureConstraint<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::SimulatedVector<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::SimulatedVector<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::SimulatedVector<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::SimulatedVector<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::PrimalSimulatedVector<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::PrimalSimulatedVector<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::PrimalSimulatedVector<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::PrimalSimulatedVector<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::DualSimulatedVector<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::DualSimulatedVector<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::DualSimulatedVector<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::DualSimulatedVector<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::SimulatedBoundConstraint<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::SimulatedBoundConstraint<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::SimulatedBoundConstraint<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::SimulatedBoundConstraint<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::ConstraintFromObjective<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::ConstraintFromObjective<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::ConstraintFromObjective<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::ConstraintFromObjective<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::StochasticConstraint<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::StochasticConstraint<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::StochasticConstraint<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::StochasticConstraint<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::MeanValueConstraint<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::MeanValueConstraint<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::MeanValueConstraint<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::MeanValueConstraint<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::RiskLessObjective<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::RiskLessObjective<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::RiskLessObjective<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::RiskLessObjective<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::details::VectorWorkspace<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::details::VectorWorkspace<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::details::VectorWorkspace<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::details::VectorWorkspace<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::OED::Timer<double, std::string > *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::OED::Timer<double, std::string > *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::OED::Timer<double, std::string >>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::OED::Timer<double, std::string > *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::OED::Factors<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::OED::Factors<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::OED::Factors<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::OED::Factors<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::OED::MomentOperator<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::OED::MomentOperator<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::OED::MomentOperator<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::OED::MomentOperator<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::BatchStdVector<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::BatchStdVector<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::BatchStdVector<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::BatchStdVector<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::ProbabilityVector<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::ProbabilityVector<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::ProbabilityVector<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::ProbabilityVector<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::OED::L1Penalty<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::OED::L1Penalty<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::OED::L1Penalty<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::OED::L1Penalty<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::OED::DoubleWellPenalty<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::OED::DoubleWellPenalty<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::OED::DoubleWellPenalty<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::OED::DoubleWellPenalty<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::LinearCombinationObjective<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::LinearCombinationObjective<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::LinearCombinationObjective<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::LinearCombinationObjective<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::StochasticProblem<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::StochasticProblem<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::StochasticProblem<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::StochasticProblem<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::OED::TraceSampler<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::OED::TraceSampler<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::OED::TraceSampler<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::OED::TraceSampler<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::OED::BilinearConstraint<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::OED::BilinearConstraint<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::OED::BilinearConstraint<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::OED::BilinearConstraint<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::OED::LinearObjective<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::OED::LinearObjective<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::OED::LinearObjective<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::OED::LinearObjective<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::OED::Hom::I_Objective<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::OED::Hom::I_Objective<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::OED::Hom::I_Objective<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::OED::Hom::I_Objective<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::OED::QuadraticObjective<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::OED::QuadraticObjective<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::OED::QuadraticObjective<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::OED::QuadraticObjective<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::OED::Het::I_Objective<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::OED::Het::I_Objective<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::OED::Het::I_Objective<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::OED::Het::I_Objective<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::SampledVector<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::SampledVector<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::SampledVector<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::SampledVector<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::OED::Hom::C_Objective<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::OED::Hom::C_Objective<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::OED::Hom::C_Objective<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::OED::Hom::C_Objective<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::OED::Hom::D_Objective<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::OED::Hom::D_Objective<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::OED::Hom::D_Objective<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::OED::Hom::D_Objective<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::OED::Radamacher<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::OED::Radamacher<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::OED::Radamacher<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::OED::Radamacher<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::OED::Hom::A_Objective<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::OED::Hom::A_Objective<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::OED::Hom::A_Objective<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::OED::Hom::A_Objective<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::OED::Hom::Itrace_Objective<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::OED::Hom::Itrace_Objective<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::OED::Hom::Itrace_Objective<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::OED::Hom::Itrace_Objective<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::ScaledObjective<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::ScaledObjective<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::ScaledObjective<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::ScaledObjective<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::OED::Het::C_Objective<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::OED::Het::C_Objective<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::OED::Het::C_Objective<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::OED::Het::C_Objective<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::OED::Het::D_Objective<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::OED::Het::D_Objective<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::OED::Het::D_Objective<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::OED::Het::D_Objective<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::OED::Het::A_Objective<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::OED::Het::A_Objective<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::OED::Het::A_Objective<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::OED::Het::A_Objective<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::OED::Het::Itrace_Objective<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::OED::Het::Itrace_Objective<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::OED::Het::Itrace_Objective<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::OED::Het::Itrace_Objective<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::OED::ProbabilityConstraint<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::OED::ProbabilityConstraint<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::OED::ProbabilityConstraint<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::OED::ProbabilityConstraint<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::PrimalScaledStdVector<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::PrimalScaledStdVector<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::PrimalScaledStdVector<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::PrimalScaledStdVector<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::DualScaledStdVector<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::DualScaledStdVector<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::DualScaledStdVector<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::DualScaledStdVector<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

	// Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::ScalarLinearConstraint<double> *, bool) file:Teuchos_RCP.hpp line:59
	M("Teuchos").def("RCP_createNewRCPNodeRawPtr", (class Teuchos::RCPNode * (*)(class ROL::ScalarLinearConstraint<double> *, bool)) &Teuchos::RCP_createNewRCPNodeRawPtr<ROL::ScalarLinearConstraint<double>>, "C++: Teuchos::RCP_createNewRCPNodeRawPtr(class ROL::ScalarLinearConstraint<double> *, bool) --> class Teuchos::RCPNode *", pybind11::return_value_policy::automatic, pybind11::arg("p"), pybind11::arg("has_ownership_in"));

}
