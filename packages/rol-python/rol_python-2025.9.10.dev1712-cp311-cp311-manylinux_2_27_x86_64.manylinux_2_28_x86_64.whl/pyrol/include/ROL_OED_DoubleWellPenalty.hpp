// @HEADER
// *****************************************************************************
//               Rapid Optimization Library (ROL) Package
//
// Copyright 2014 NTESS and the ROL contributors.
// SPDX-License-Identifier: BSD-3-Clause
// *****************************************************************************
// @HEADER

#ifndef ROL_OED_DOUBLE_WELL_PENALTY_HPP
#define ROL_OED_DOUBLE_WELL_PENALTY_HPP

#include "ROL_Objective.hpp"
#include "ROL_ProbabilityVector.hpp"
#include "ROL_OED_ProfiledClass.hpp"

namespace ROL {
namespace OED {

template<typename Real>
class DoubleWellPenalty : public Objective<Real>, public ProfiledClass<Real,std::string> {
private:

  std::vector<Real>& getData(Vector<Real> &x) const;
  const std::vector<Real>& getConstData(const Vector<Real> &x) const;
  void sumAll(Real *input, Real *output, int size, const Vector<Real> &x) const;

  using ProfiledClass<Real,std::string>::startTimer;
  using ProfiledClass<Real,std::string>::stopTimer;

public:
  DoubleWellPenalty();

  Real value( const Vector<Real> &x, Real &tol ) override;
  void gradient( Vector<Real> &g, const Vector<Real> &x, Real &tol ) override;
  void hessVec( Vector<Real> &hv, const Vector<Real> &v, const Vector<Real> &x, Real &tol ) override;

}; // class DoubleWellPenalty

} // End OED Namespace
} // End ROL Namespace

#include "ROL_OED_DoubleWellPenalty_Def.hpp"

#endif
