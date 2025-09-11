"""
Expression Helper Functions
==========================

Convenience functions for creating mathematical expressions.
"""

from collections.abc import Callable

from ..quantities import FieldQnty, Quantity
from .nodes import BinaryOperation, ConditionalExpression, Expression, UnaryFunction, wrap_operand

# Type aliases for better maintainability
ExpressionOperand = Expression | FieldQnty | Quantity | int | float
ConditionalOperand = Expression | BinaryOperation


def _create_unary_function(name: str, docstring: str) -> "Callable[[ExpressionOperand], Expression | Quantity | float]":
    """Factory function for creating unary mathematical functions."""

    def func(expr: ExpressionOperand) -> Expression | Quantity | float:
        import inspect

        wrapped_expr = wrap_operand(expr)

        # For known quantities (FieldQnty with known values), check context before auto-evaluating
        if hasattr(expr, "quantity") and getattr(expr, "quantity", None) is not None:
            # Check if we're being called during Problem class definition
            # Look for Problem-related frames in the call stack
            frame = inspect.currentframe()
            try:
                while frame:
                    code = frame.f_code
                    filename = code.co_filename
                    # If we find a frame in Problem-related code or class definition,
                    # don't auto-evaluate to preserve symbolic expressions
                    if (
                        "<class" in code.co_name
                        or "problem" in filename.lower()
                        or "composition" in filename.lower()
                        or "_extract" in code.co_name.lower()
                        or "WeldedBranchConnection" in str(frame.f_locals.get("__qualname__", ""))
                    ):
                        break
                    frame = frame.f_back
                else:
                    # No Problem class context found, safe to auto-evaluate
                    try:
                        unary_func = UnaryFunction(name, wrapped_expr)
                        # Use an empty variable dict since we have the quantity directly
                        result = unary_func.evaluate({})
                        return result
                    except (ValueError, TypeError, AttributeError):
                        # Fall back to expression if evaluation fails
                        pass
            finally:
                del frame

        # For unknown variables or expressions, return the UnaryFunction
        return UnaryFunction(name, wrapped_expr)

    func.__name__ = name
    func.__doc__ = docstring
    return func


def _create_comparison_expr(expressions: tuple[ExpressionOperand, ...], comparator: str) -> Expression:
    """Create min/max expression using specified comparator."""
    if len(expressions) < 2:
        raise ValueError(f"{comparator}_expr requires at least 2 arguments")

    wrapped_expressions = [wrap_operand(expr) for expr in expressions]
    result = wrapped_expressions[0]

    for expr in wrapped_expressions[1:]:
        if comparator == "min":
            # min(a, b) = if(a < b, a, b)
            result = cond_expr(result < expr, result, expr)
        else:  # max
            # max(a, b) = if(a > b, a, b)
            result = cond_expr(result > expr, result, expr)

    return result


# Mathematical functions (generated via factory)
sin = _create_unary_function("sin", "Sine function.")
cos = _create_unary_function("cos", "Cosine function.")
tan = _create_unary_function("tan", "Tangent function.")
sqrt = _create_unary_function("sqrt", "Square root function.")
abs_expr = _create_unary_function("abs", "Absolute value function.")
ln = _create_unary_function("ln", "Natural logarithm function.")
log10 = _create_unary_function("log10", "Base-10 logarithm function.")
exp = _create_unary_function("exp", "Exponential function.")


def cond_expr(
    condition: ConditionalOperand,
    true_expr: ExpressionOperand,
    false_expr: ExpressionOperand,
) -> ConditionalExpression:
    """Conditional expression: if condition then true_expr else false_expr."""
    wrapped_condition = condition if isinstance(condition, Expression) else condition
    return ConditionalExpression(wrapped_condition, wrap_operand(true_expr), wrap_operand(false_expr))


def min_expr(*expressions: ExpressionOperand) -> Expression:
    """Minimum of multiple expressions."""
    return _create_comparison_expr(expressions, "min")


def max_expr(*expressions: ExpressionOperand) -> Expression:
    """Maximum of multiple expressions."""
    return _create_comparison_expr(expressions, "max")
