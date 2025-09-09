#include "doxystub.h"
#include "kinematics.h"
#include <eigenpy/eigen-to-python.hpp>

using namespace reachy_mini_kinematics;
using namespace boost::python;

void expose_kinematics() {
  class__<Kinematics>("Kinematics", init<double, double>())
      .def_readwrite("motor_arm_length", &Kinematics::motor_arm_length)
      .def_readwrite("rod_length", &Kinematics::rod_length)
      .def_readwrite("fk_max_delta_linear", &Kinematics::fk_max_delta_linear)
      .def_readwrite("fk_max_delta_angular", &Kinematics::fk_max_delta_angular)
      .def("add_branch", &Kinematics::add_branch)
      .def("inverse_kinematics", &Kinematics::inverse_kinematics)
      .def("reset_forward_kinematics", &Kinematics::reset_forward_kinematics)
      .def("forward_kinematics", &Kinematics::forward_kinematics);
}
