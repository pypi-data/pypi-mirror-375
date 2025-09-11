// @HEADER
// *****************************************************************************
//               Rapid Optimization Library (ROL) Package
//
// Copyright 2014 NTESS and the ROL contributors.
// SPDX-License-Identifier: BSD-3-Clause
// *****************************************************************************
// @HEADER

#ifndef HS_PROBLEM_014_HPP
#define HS_PROBLEM_014_HPP

#include "ROL_NonlinearProgram.hpp"

namespace HS {

namespace HS_014 {
template<class Real>
class Obj {
public:
  template<class ScalarT>
  ScalarT value( const std::vector<ScalarT> &x, Real &tol ) {
    ScalarT a = x[0]-2;
    ScalarT b = x[1]-1;
    return a*a+b*b; 
  }
};


template<class Real>
class EqCon {
public:
  template<class ScalarT>
  void value( std::vector<ScalarT> &c,
              const std::vector<ScalarT> &x,
              Real &tol ) {
    c[0] = x[0] - 2*x[1] + 1;
  }
};


template<class Real>
class InCon {
public:
  template<class ScalarT>
  void value( std::vector<ScalarT> &c,
              const std::vector<ScalarT> &x,
              Real &tol ) {
    c[0] = -0.25*x[0]*x[0] - x[1]*x[1] + 1;
  }
};

} // namespace HS_014



template<class Real> 
class Problem_014 : public ROL::NonlinearProgram<Real> {

  
  
  typedef ROL::Vector<Real>               V;
  typedef ROL::Objective<Real>            OBJ;
  typedef ROL::Constraint<Real>           CON;
  typedef ROL::NonlinearProgram<Real>     NP;

public:

  Problem_014() : NP( dimension_x() ) {
    NP::noBound();
  }  

  int dimension_x()  { return 2; }
  int dimension_ce() { return 1; }
  int dimension_ci() { return 1; }

  const ROL::Ptr<OBJ> getObjective() { 
    return ROL::makePtr<ROL::Sacado_StdObjective<Real,HS_014::Obj>>();
  }

  const ROL::Ptr<CON> getEqualityConstraint() {
    return ROL::makePtr<ROL::Sacado_StdConstraint<Real,HS_014::EqCon>>();
  }

  const ROL::Ptr<CON> getInequalityConstraint() {
    return ROL::makePtr<ROL::Sacado_StdConstraint<Real,HS_014::InCon>>();
  }

  const ROL::Ptr<const V> getInitialGuess() {
    Real x[] = {2,2};
    return NP::createOptVector(x);
  };
   
  bool initialGuessIsFeasible() { return false; }
  
  Real getInitialObjectiveValue() { 
    return Real(1);
  }
 
  Real getSolutionObjectiveValue() {
    return 9 - 2.875*std::sqrt(7);
  }

  ROL::Ptr<const V> getSolutionSet() {
    Real a = std::sqrt(7);
    Real x[] = {0.5*(a-1),0.25*(a+1)};
    return ROL::CreatePartitionedVector(NP::createOptVector(x));
  }
 
};

} // namespace HS

#endif // HS_PROBLEM_014_HPP
