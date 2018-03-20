#
# GSLNamesReferenceConverterTest.py
#
# This file is part of NEST.
#
# Copyright (C) 2004 The NEST Initiative
#
# NEST is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# NEST is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NEST.  If not, see <http://www.gnu.org/licenses/>.
import unittest

from mock import patch, Mock, MagicMock

from pynestml.codegeneration.GSLReferenceConverter import GSLReferenceConverter, UnsupportedOperationException
from pynestml.modelprocessor.ASTArithmeticOperator import ASTArithmeticOperator
from pynestml.modelprocessor.ASTFunction import ASTFunction
from pynestml.modelprocessor.ASTUnaryOperator import ASTUnaryOperator
from pynestml.modelprocessor.ASTVariable import ASTVariable
# noinspection PyTypeChecker
from pynestml.modelprocessor.PredefinedFunctions import PredefinedFunctions


# noinspection PyTypeChecker,PyMissingTypeHints
class GSLReferenceConverterTest(unittest.TestCase):
    class_under_test = None

    # noinspection PyPep8Naming
    def setUp(self):
        self.class_under_test = GSLReferenceConverter()

    def test_init_upper_bound(self):
        gsl_reference_converter = GSLReferenceConverter(True)
        self.assertTrue(gsl_reference_converter._is_upper_bound)

    @patch('pynestml.codegeneration.GSLReferenceConverter.UnitConverter')
    @patch('pynestml.codegeneration.GSLReferenceConverter.PredefinedUnits')
    def test_convert_name_reference_with_predefined_unit(self, _mock_predefined_units, _mock_unit_converter):
        with patch('pynestml.codegeneration.GSLReferenceConverter.GSLNamesConverter'):
            _mock_predefined_units.isUnit.return_value = True
            result = self.class_under_test.convert_name_reference(Mock())
            self.assertEquals(str(_mock_unit_converter.getFactor()), result)

    @patch('pynestml.codegeneration.GSLReferenceConverter.GSLNamesConverter')
    def test_convert_name_reference_with_init_value(self, _mock_gsl_names_converter):
        result = self.class_under_test.convert_name_reference(Mock())
        self.assertEqual(_mock_gsl_names_converter.name(), result)

    @patch('pynestml.codegeneration.GSLReferenceConverter.GSLNamesConverter')
    def test_convert_name_reference_with_init_buffer(self, _mock_gsl_names_converter):
        variable = Mock(ASTVariable)
        variable.getScope.return_value.resolveToSymbol.return_value.isInitValues.return_value = False
        result = self.class_under_test.convert_name_reference(variable)
        self.assertEqual('node.B_.' + _mock_gsl_names_converter.buffer_value(), result)

    @patch('pynestml.codegeneration.GSLReferenceConverter.GSLNamesConverter')
    def test_convert_name_reference_with_euler_constant(self, _mock_gsl_names_converter):
        variable = Mock(ASTVariable)
        variable.getScope.return_value.resolveToSymbol.return_value.isInitValues.return_value = False
        variable.getScope.return_value.resolveToSymbol.return_value.isBuffer.return_value = False
        _mock_gsl_names_converter.convert_to_cpp_name.return_value = 'e'
        result = self.class_under_test.convert_name_reference(variable)
        self.assertEqual('numerics::e', result)

    @patch('pynestml.codegeneration.GSLReferenceConverter.GSLNamesConverter')
    def test_convert_name_reference_with_local_variable(self, _mock_gsl_names_converter):
        variable = Mock(ASTVariable)
        variable.getScope.return_value.resolveToSymbol.return_value.isInitValues.return_value = False
        variable.getScope.return_value.resolveToSymbol.return_value.isBuffer.return_value = False
        variable.getScope.return_value.resolveToSymbol.return_value.isLocal.return_value = True
        variable.getScope.return_value.resolveToSymbol.return_value.isFunction.return_value = False
        result = self.class_under_test.convert_name_reference(variable)
        self.assertEqual(_mock_gsl_names_converter.convert_to_cpp_name.return_value, result)

    @patch('pynestml.codegeneration.GSLReferenceConverter.GSLNamesConverter')
    def test_convert_name_reference_with_function_variable(self, _mock_gsl_names_converter):
        variable = Mock(ASTVariable)
        variable.getScope.return_value.resolveToSymbol.return_value.isInitValues.return_value = False
        variable.getScope.return_value.resolveToSymbol.return_value.isBuffer.return_value = False
        variable.getScope.return_value.resolveToSymbol.return_value.isLocal.return_value = False
        variable.getScope.return_value.resolveToSymbol.return_value.isFunction.return_value = True
        result = self.class_under_test.convert_name_reference(variable)
        self.assertEqual(_mock_gsl_names_converter.convert_to_cpp_name.return_value, result)

    @patch('pynestml.codegeneration.GSLReferenceConverter.GSLNamesConverter')
    def test_convert_name_reference_with_vector_variable(self, _mock_gsl_names_converter):
        variable = Mock(ASTVariable)
        variable.getScope.return_value.resolveToSymbol.return_value.isInitValues.return_value = False
        variable.getScope.return_value.resolveToSymbol.return_value.isBuffer.return_value = False
        variable.getScope.return_value.resolveToSymbol.return_value.isLocal.return_value = False
        variable.getScope.return_value.resolveToSymbol.return_value.isFunction.return_value = False
        result = self.class_under_test.convert_name_reference(variable)
        self.assertEqual('node.get_' + _mock_gsl_names_converter.convert_to_cpp_name.return_value + '()[i]', result)

    @patch('pynestml.codegeneration.GSLReferenceConverter.GSLNamesConverter')
    def test_convert_name_reference_with_regular_variable(self, _mock_gsl_names_converter):
        variable = Mock(ASTVariable)
        variable.getScope.return_value.resolveToSymbol.return_value.isInitValues.return_value = False
        variable.getScope.return_value.resolveToSymbol.return_value.isBuffer.return_value = False
        variable.getScope.return_value.resolveToSymbol.return_value.isLocal.return_value = False
        variable.getScope.return_value.resolveToSymbol.return_value.isFunction.return_value = False
        variable.getScope.return_value.resolveToSymbol.return_value.hasVectorParameter.return_value = False
        result = self.class_under_test.convert_name_reference(variable)
        self.assertEqual('node.get_' + _mock_gsl_names_converter.convert_to_cpp_name.return_value + '()', result)

    def test_convert_function_call_name_is_resolution(self):
        func = Mock(ASTFunction)
        func.getName.return_value = 'resolution'
        result = self.class_under_test.convert_function_call(func)
        self.assertEqual('nest::Time::get_resolution().get_ms()', result)

    def test_convert_function_call_name_is_steps(self):
        func = Mock(ASTFunction)
        func.getName.return_value = 'steps'
        result = self.class_under_test.convert_function_call(func)
        self.assertEqual('nest::Time(nest::Time::ms((double) %s)).get_steps()', result)

    def test_convert_function_call_name_is_predefined_pow(self):
        func = Mock(ASTFunction)
        func.getName.return_value = PredefinedFunctions.POW
        result = self.class_under_test.convert_function_call(func)
        self.assertEqual('std::pow(%s)', result)

    def test_convert_function_call_name_is_predefined_log(self):
        func = Mock(ASTFunction)
        func.getName.return_value = PredefinedFunctions.LOG
        result = self.class_under_test.convert_function_call(func)
        self.assertEqual('std::log(%s)', result)

    def test_convert_function_call_name_is_predefined_expm1(self):
        func = Mock(ASTFunction)
        func.getName.return_value = PredefinedFunctions.EXPM1
        result = self.class_under_test.convert_function_call(func)
        self.assertEqual('numerics::expm1(%s)', result)

    def test_convert_function_call_name_is_predefined_exp_upper_bound_true(self):
        func = Mock(ASTFunction)
        func.getName.return_value = PredefinedFunctions.EXP
        self.class_under_test._is_upper_bound = True
        result = self.class_under_test.convert_function_call(func)
        self.assertEqual('std::exp(std::min(%s,' + str(self.class_under_test._maximal_exponent) + '))', result)

    def test_convert_function_call_name_is_predefined_exp_upper_bound_false(self):
        func = Mock(ASTFunction)
        func.getName.return_value = PredefinedFunctions.EXP
        self.class_under_test._is_upper_bound = False
        result = self.class_under_test.convert_function_call(func)
        self.assertEqual('std::exp(%s)', result)

    def test_convert_function_call_name_is_predefined_max(self):
        func = Mock(ASTFunction)
        func.getName.return_value = PredefinedFunctions.MAX
        result = self.class_under_test.convert_function_call(func)
        self.assertEqual('std::max(%s)', result)

    def test_convert_function_call_name_is_predefined_bounded_max(self):
        func = Mock(ASTFunction)
        func.getName.return_value = PredefinedFunctions.BOUNDED_MAX
        result = self.class_under_test.convert_function_call(func)
        self.assertEqual('std::max(%s)', result)

    def test_convert_function_call_name_is_predefined_min(self):
        func = Mock(ASTFunction)
        func.getName.return_value = PredefinedFunctions.MIN
        result = self.class_under_test.convert_function_call(func)
        self.assertEqual('std::min(%s)', result)

    def test_convert_function_call_name_is_predefined_bounded_min(self):
        func = Mock(ASTFunction)
        func.getName.return_value = PredefinedFunctions.BOUNDED_MIN
        result = self.class_under_test.convert_function_call(func)
        self.assertEqual('std::min(%s)', result)

    def test_convert_function_call_name_is_predefined_emit_spike(self):
        func = Mock(ASTFunction)
        func.getName.return_value = PredefinedFunctions.EMIT_SPIKE
        result = self.class_under_test.convert_function_call(func)
        self.assertEqual(('set_spiketime(nest::Time::step(origin.get_steps()+lag+1));\n'
                          'nest::SpikeEvent se;\n'
                          'nest::kernel().event_delivery_manager.send(*this, se, lag)'), result)

    def test_convert_function_call_name_is_not_predefined(self):
        func = Mock(ASTFunction)
        func.getName.return_value = 'foo'
        self.assertRaises(UnsupportedOperationException, self.class_under_test.convert_function_call, func)

    def test_convert_constant(self):
        constant = 'foo'
        result = self.class_under_test.convert_constant(constant)
        self.assertEqual('foo', result)

    def test_convert_unary_op(self):
        unary_op = MagicMock(ASTUnaryOperator)
        unary_op.__str__.return_value = '+'
        result = self.class_under_test.convert_unary_op(unary_op)
        self.assertEqual('+(%s)', result)

    def test_convert_binary_op_with_arithmetic_pow_op(self):
        binary_op = Mock(ASTArithmeticOperator)
        result = self.class_under_test.convert_binary_op(binary_op)
        self.assertEqual('pow(%s, %s)', result)

    def test_convert_binary_op_with_non_arithmetic_op(self):
        binary_op = Mock()
        result = self.class_under_test.convert_binary_op(binary_op)
        self.assertEqual('%s' + str(binary_op) + '%s', result)

    def test_convert_binary_op_with_arithmetic_non_pow(self):
        binary_op = MagicMock(ASTArithmeticOperator)
        binary_op.isPowOp.return_value = False
        result = self.class_under_test.convert_binary_op(binary_op)
        self.assertEqual('%s' + str(binary_op) + '%s', result)

    @patch('pynestml.codegeneration.GSLReferenceConverter.NESTReferenceConverter')
    def test_convert_logical_not(self, _mock_nest_reference_converter):
        result = self.class_under_test.convert_logical_not()
        self.assertEqual(_mock_nest_reference_converter.convert_logical_not(), result)

    @patch('pynestml.codegeneration.GSLReferenceConverter.NESTReferenceConverter')
    def test_convert_logical_op(self, _mock_nest_reference_converter):
        result = self.class_under_test.convert_logical_operator(Mock())
        self.assertEqual(_mock_nest_reference_converter.convert_logical_operator(), result)

    @patch('pynestml.codegeneration.GSLReferenceConverter.NESTReferenceConverter')
    def test_convert_comparison_op(self, _mock_nest_reference_converter):
        result = self.class_under_test.convert_comparison_operator(Mock())
        self.assertEqual(_mock_nest_reference_converter.convert_comparison_operator(), result)

    @patch('pynestml.codegeneration.GSLReferenceConverter.NESTReferenceConverter')
    def test_convert_bit_op(self, _mock_nest_reference_converter):
        result = self.class_under_test.convert_bit_operator(Mock())
        self.assertEqual(_mock_nest_reference_converter.convert_bit_operator(), result)

    @patch('pynestml.codegeneration.GSLReferenceConverter.NESTReferenceConverter')
    def test_convert_encapsulated(self, _mock_nest_reference_converter):
        result = self.class_under_test.convert_encapsulated()
        self.assertEqual(_mock_nest_reference_converter.convert_encapsulated(), result)

    @patch('pynestml.codegeneration.GSLReferenceConverter.NESTReferenceConverter')
    def test_convert_ternary_op(self, _mock_nest_reference_converter):
        result = self.class_under_test.convert_ternary_operator()
        self.assertEqual(_mock_nest_reference_converter.convert_ternary_operator(), result)

    @patch('pynestml.codegeneration.GSLReferenceConverter.NESTReferenceConverter')
    def test_convert_arithmetic_op(self, _mock_nest_reference_converter):
        result = self.class_under_test.convert_arithmetic_operator(Mock())
        self.assertEqual(_mock_nest_reference_converter.convert_arithmetic_operator(), result)
