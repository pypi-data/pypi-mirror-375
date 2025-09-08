#include <pybind11/pybind11.h>
#include <pybind11/eigen.h>
#include <pybind11/stl.h>
#include "condreg/condreg.hpp"
#include "condreg/utils.hpp"

namespace py = pybind11;

PYBIND11_MODULE(condreg_cpp, m) {
    m.doc() = "C++ implementation of condition number regularization";
    
    // Expose utility functions
    m.def("kgrid", &condreg::kgrid, 
          "Generate a vector of grid of penalties for cross-validation",
          py::arg("gridmax"), py::arg("numpts"));
    
    m.def("pfweights", &condreg::pfweights,
          "Compute optimal portfolio weights",
          py::arg("sigma"));
    
    m.def("transcost", &condreg::transcost,
          "Compute transaction cost of rebalancing portfolio",
          py::arg("wnew"), py::arg("wold"), py::arg("lastearnings"), 
          py::arg("reltc"), py::arg("wealth"));
    
    // Expose condreg core functions
    m.def("condreg", [](const Eigen::MatrixXd& data_in, double kmax) {
        condreg::CondregResult result = condreg::condreg(data_in, kmax);
        return py::make_tuple(result.S, result.invS);
    }, "Compute condition number regularized covariance matrix",
       py::arg("data_in"), py::arg("kmax"));
    
    m.def("select_condreg", [](const Eigen::MatrixXd& X, const Eigen::VectorXd& k, int folds) {
        condreg::CondregResult result = condreg::select_condreg(X, k, folds);
        return py::make_tuple(result.S, result.invS);
    }, "Compute condition number regularized covariance using cross-validation",
       py::arg("X"), py::arg("k"), py::arg("folds") = 0);
    
    m.def("select_kmax", [](const Eigen::MatrixXd& X, const Eigen::VectorXd& k, int folds) {
        condreg::SelectKmaxResult result = condreg::select_kmax(X, k, folds);
        return py::make_tuple(result.kmax, result.negL);
    }, "Selection of penalty parameter based on cross-validation",
       py::arg("X"), py::arg("k"), py::arg("folds") = 0);
}
