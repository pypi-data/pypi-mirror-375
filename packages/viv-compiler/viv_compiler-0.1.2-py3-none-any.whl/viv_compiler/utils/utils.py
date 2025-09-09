"""Utility functions used by various components of the Viv DSL compiler."""

import viv_compiler.config
import viv_compiler.types
from viv_compiler.types import ExpressionDiscriminator
from typing import Any


def get_all_role_names(action_definition: viv_compiler.types.ActionDefinition) -> set[viv_compiler.types.RoleName]:
    """Return a set containing the names of all roles associated with the given action definition.

    Args:
        action_definition:

    Returns:
        A set containing the names of all roles associated with the given action definition.
    """
    return viv_compiler.config.SPECIAL_ROLE_NAMES | set(action_definition['roles'])


def get_all_referenced_roles(
    ast_chunk: Any,
    ignore_role_unpackings: bool = False,
) -> list[viv_compiler.types.RoleName]:
    """Return a list of all roles referenced in the given AST chunk.

    Args:
        ast_chunk: The full or partial AST to search for role references.
        ignore_role_unpackings: Whether to search for role references inside role unpackings.

    Returns:
        A list containing the names of all roles referenced in the given AST chunk.
    """
    roles_referenced_so_far: list[viv_compiler.types.RoleName] = []
    if isinstance(ast_chunk, list):
        for element in ast_chunk:
            roles_referenced_so_far.extend(get_all_referenced_roles(
                ast_chunk=element,
                ignore_role_unpackings=ignore_role_unpackings,
            ))
    elif isinstance(ast_chunk, dict):
        ast_chunk_type = ast_chunk.get('type')
        if ast_chunk_type in (ExpressionDiscriminator.ENTITY_REFERENCE, ExpressionDiscriminator.SYMBOL_REFERENCE):
            if not ast_chunk['value']['local']:
                if ast_chunk['value']['anchor'] != viv_compiler.config.ACTION_SELF_REFERENCE_ROLE_NAME:
                    roles_referenced_so_far.append(ast_chunk['value']['anchor'])
        elif ast_chunk_type == ExpressionDiscriminator.ROLE_UNPACKING and not ignore_role_unpackings:
            referenced_role_name = ast_chunk['value']
            roles_referenced_so_far.append(referenced_role_name)
        for value in ast_chunk.values():
            roles_referenced_so_far.extend(get_all_referenced_roles(
                ast_chunk=value,
                ignore_role_unpackings=ignore_role_unpackings,
            ))
    return list(set(roles_referenced_so_far))


def get_all_referenced_enum_names(ast_chunk: Any) -> list[viv_compiler.types.EnumName]:
    """Return a list of the names of all enums referenced in the given AST chunk.

    This list will be stored in the compiled content bundle, where it's used for
    validation purposes upon the initialization of a Viv runtime.

    Args:
        ast_chunk: The full or partial AST to search for enum references.

    Returns:
        A list containing the names of all the enums referenced in the given AST chunk.
    """
    all_enum_expressions = get_all_expressions_of_type(
        expression_type=ExpressionDiscriminator.ENUM,
        ast_chunk=ast_chunk
    )
    all_referenced_enum_names = {expression['name'] for expression in all_enum_expressions}
    return sorted(all_referenced_enum_names)


def get_all_referenced_adapter_function_names(ast_chunk: Any) -> list[viv_compiler.types.AdapterFunctionName]:
    """Return a list of the names of all adapter functions referenced in the given AST chunk.

    This list will be stored in the compiled content bundle, where it's used for
    validation purposes upon the initialization of a Viv runtime.

    Args:
        ast_chunk: The full or partial AST to search for adapter-function references.

    Returns:
        A list containing the names of all the adapter functions referenced in the given AST chunk.
    """
    all_adapter_function_references = get_all_expressions_of_type(
        expression_type=ExpressionDiscriminator.ADAPTER_FUNCTION_CALL,
        ast_chunk=ast_chunk
    )
    all_referenced_adapter_function_names = {expression['name'] for expression in all_adapter_function_references}
    return sorted(all_referenced_adapter_function_names)


def get_all_assigned_scratch_variable_names(ast_chunk: Any) -> list[viv_compiler.types.VariableName]:
    """Return a list of the names of all scratch variables that are assigned anywhere in the given AST chunk.

    Args:
        ast_chunk: The full or partial AST to search for scratch variables being assigned.

    Returns:
        A list containing the names of all scratch variables that are assigned anywhere in the given AST chunk.
    """
    all_assigned_scratch_variable_names = set()
    all_assignments = get_all_expressions_of_type(
        expression_type=ExpressionDiscriminator.ASSIGNMENT,
        ast_chunk=ast_chunk
    )
    for assignment in all_assignments:
        # Move on if the effective prefix is not `@this.scratch.`
        lhs = assignment['left']
        if lhs['type'] != ExpressionDiscriminator.ENTITY_REFERENCE:
            continue
        if lhs['value']['local']:
            continue
        if lhs['value']['anchor'] != viv_compiler.config.SCRATCH_VARIABLE_REFERENCE_ANCHOR:
            continue
        if lhs['value']['path'][0] != viv_compiler.config.SCRATCH_VARIABLE_REFERENCE_PATH_PREFIX[0]:
            continue
        # Now determine if the LHS of the assignment is a bare scratch variable, i.e., an effective `@this.scratch.var`
        head, *tail = lhs['value']['path'][1:]
        if tail:
            continue
        if 'name' not in head:
            # Move on if we somehow have a pointer or lookup after an effective `@this.scratch` (not idiomatic)
            continue
        all_assigned_scratch_variable_names.add(head['name'])
    return sorted(all_assigned_scratch_variable_names)


def get_all_referenced_scratch_variable_names(ast_chunk: Any) -> list[viv_compiler.types.VariableName]:
    """Return a list of the names of all scratch variables that are referenced anywhere in the given AST chunk.

    Args:
        ast_chunk: The full or partial AST to search for scratch variables being referenced.

    Returns:
        A list containing the names of all scratch variables that are referenced anywhere in the given AST chunk.
    """
    all_referenced_scratch_variable_names = set()
    all_entity_references = get_all_expressions_of_type(
        expression_type=ExpressionDiscriminator.ENTITY_REFERENCE,
        ast_chunk=ast_chunk
    )
    for entity_reference in all_entity_references:
        # Move on if the effective prefix is not `@this.scratch.`
        if entity_reference['local']:
            continue
        if entity_reference['anchor'] != viv_compiler.config.SCRATCH_VARIABLE_REFERENCE_ANCHOR:
            continue
        if entity_reference['path'][0] != viv_compiler.config.SCRATCH_VARIABLE_REFERENCE_PATH_PREFIX[0]:
            continue
        # Now determine if the LHS of the assignment is a bare scratch variable, i.e., an effective `@this.scratch.var`
        head, *_ = entity_reference['path'][1:]
        if 'name' not in head:
            # Move on if we somehow have a pointer or lookup after an effective `@this.scratch` (not idiomatic)
            continue
        all_referenced_scratch_variable_names.add(head['name'])
    return sorted(all_referenced_scratch_variable_names)


def get_all_expressions_of_type(expression_type: str, ast_chunk: Any) -> list[Any]:
    """Return a list containing values for all expressions of the given type that are nested in the given AST chunk.

    Args:
        expression_type: String indicating the type of Viv expression to search for.
        ast_chunk: The AST chunk to search for expressions of the given type.

    Returns:
        A list containing all the Viv expressions of the given type in the given AST chunk.
    """
    expressions = []
    if isinstance(ast_chunk, list):
        for element in ast_chunk:
            expressions.extend(get_all_expressions_of_type(expression_type=expression_type, ast_chunk=element))
    elif isinstance(ast_chunk, dict):
        if 'type' in ast_chunk and ast_chunk['type'] == expression_type:
            expression_of_type = ast_chunk['value']
            expressions.append(expression_of_type)
        else:
            for key, value in ast_chunk.items():
                expressions.extend(get_all_expressions_of_type(expression_type=expression_type, ast_chunk=value))
    return expressions


def get_all_negated_expressions(ast_chunk: Any) -> list[viv_compiler.types.Expression]:
    """
    Return every negated expression in the given AST chunk.

    Args:
        ast_chunk: The full or partial AST to search for negated expressions.

    Returns:
        A list containing all the negated Viv expressions in the given AST chunk.
    """
    negated_expressions = []
    if isinstance(ast_chunk, list):
        for element in ast_chunk:
            negated_expressions.extend(get_all_negated_expressions(ast_chunk=element))
    elif isinstance(ast_chunk, dict):
        if ast_chunk.get("negated"):
            negated_expressions.append(ast_chunk)
        for value in ast_chunk.values():
            negated_expressions.extend(get_all_negated_expressions(ast_chunk=value))
    return negated_expressions


def contains_eval_fail_safe_operator(ast_chunk: Any) -> bool:
    """Return whether the given AST chunk contains an eval fail-safe operator.

    Args:
        ast_chunk: The full or partial AST to search for expressions of the given type.

    Returns:
        True if the given AST chunk contains an eval fail-safe operator, else False.
    """
    if isinstance(ast_chunk, list):
        for element in ast_chunk:
            if contains_eval_fail_safe_operator(ast_chunk=element):
                return True
    elif isinstance(ast_chunk, dict):
        if 'type' in ast_chunk and ast_chunk['type'] == ExpressionDiscriminator.EVAL_FAIL_SAFE:
            return True
        else:
            for key, value in ast_chunk.items():
                if contains_eval_fail_safe_operator(ast_chunk=value):
                    return True
    return False
