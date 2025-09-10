#pragma once

// torch
#include <ATen/TensorIterator.h>
#include <ATen/native/DispatchStub.h>

// kintera
#include <kintera/utils/func1.hpp>
#include <kintera/utils/func2.hpp>
#include <kintera/utils/func3.hpp>

namespace at::native {

using fn1iter = void (*)(at::TensorIterator &iter,
                         std::vector<std::string> const &funcs);
using fn2iter = void (*)(at::TensorIterator &iter,
                         std::vector<std::string> const &funcs);
using fn3iter = void (*)(at::TensorIterator &iter,
                         std::vector<std::string> const &funcs);

DECLARE_DISPATCH(fn1iter, call_func1);
DECLARE_DISPATCH(fn2iter, call_func2);
DECLARE_DISPATCH(fn3iter, call_func3);

}  // namespace at::native
