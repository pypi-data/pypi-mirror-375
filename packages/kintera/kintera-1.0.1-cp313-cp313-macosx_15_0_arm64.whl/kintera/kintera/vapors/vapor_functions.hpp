#pragma once

// C/C++
#include <cmath>

// base
#include <configure.h>

// kintera
#include <kintera/utils/func1.hpp>

#define VAPOR_FUNCTION(name, var)                   \
  DISPATCH_MACRO double name(double);               \
  static Func1Registrar logsvp_##name(#name, name); \
  DISPATCH_MACRO double name(double var)

DISPATCH_MACRO
inline double logsvp_ideal(double t, double beta, double gamma) {
  return (1. - 1. / t) * beta - gamma * log(t);
}

DISPATCH_MACRO
inline double logsvp_ideal_ddT(double t, double beta, double gamma) {
  return beta / (t * t) - gamma / t;
}

DISPATCH_MACRO
inline double logsvp_antoine(double T, double A, double B, double C) {
  return log(1.E5) + (A - B / (T + C)) * log(10.);
}

DISPATCH_MACRO
inline double logsvp_antoine_ddT(double T, double B, double C) {
  return B * log(10.) / ((T + C) * (T + C));
}
