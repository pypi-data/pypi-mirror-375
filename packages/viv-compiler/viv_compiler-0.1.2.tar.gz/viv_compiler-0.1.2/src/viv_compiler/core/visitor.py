"""Visitor component of the Viv DSL compiler.

Defines a single `Visitor` class that traverses and modifies a Viv AST, in
accordance with the structure prescribed by Arpeggio, our PEG parser solution.
"""

import math
import copy
import arpeggio
import viv_compiler.config
import viv_compiler.types
from viv_compiler.types import ExpressionDiscriminator, ReferencePathComponentDiscriminator, LocalVariable
from typing import Any, Optional


class Visitor(arpeggio.PTNodeVisitor):
    """A visitor for Viv abstract syntax trees (AST), following the visitor pattern in parsing."""

    @staticmethod
    def visit_file(_, children: Any) -> viv_compiler.types.AST:
        """Visit the <file> node, i.e., the root of the parse tree."""
        ast = {"_includes": [], "tropes": [], "actions": []}
        for child in children:
            if child["_type"] == 'include':
                ast['_includes'].append(child['value'])
            elif child["_type"] == 'action':
                ast['actions'].append(child['value'])
            elif child["_type"] == 'trope':
                ast['tropes'].append(child['value'])
        return ast

    @staticmethod
    def visit_include(_, children: Any) -> dict[str, Any]:
        """Visit an <include> node."""
        return {"_type": "include", "value": children[0]}

    @staticmethod
    def visit_filename(_, children: Any) -> str:
        """Visit a <filename> node."""
        return ''.join(children)

    @staticmethod
    def visit_trope(_, children: Any) -> dict[str, Any]:
        """Visit a <trope> node."""
        if len(children) == 3:
            name, params, conditions = children
        else:
            name, conditions = children
            params = []
        trope_definition = {"name": name, "params": params, "conditions": conditions}
        return {"_type": "trope", "value": trope_definition}

    @staticmethod
    def visit_trope_params(_, children: Any) -> list[str]:
        """Visit a <trope_params> node."""
        return children

    @staticmethod
    def visit_trope_param(_, children: Any) -> viv_compiler.types.TropeParam:
        """Visit a <trope_param> node."""
        role_type, name = children
        component = {"name": name, "isEntityParam": role_type["_is_entity"]}
        return component

    @staticmethod
    def visit_action(_, children: Any) -> dict[str, Any]:
        """Visit an <action> node."""
        action_definition = {"special": False, "parent": None}
        header, body = children
        action_definition.update(header)
        action_definition.update(body)
        return {"_type": "action", "value": action_definition}

    @staticmethod
    def visit_action_header(_, children: Any) -> dict[str, Any]:
        """Visit a <action_header> node."""
        component = {"special": False}
        for child in children:
            if isinstance(child, str):
                component['name'] = child
            else:
                component.update(child)
        return component

    @staticmethod
    def visit_special_action_tag(_, __: Any) -> dict[str, bool]:
        """Visit a <special_action_tag> node."""
        return {"special": True}

    @staticmethod
    def visit_parent_action_declaration(_, children: Any) -> dict[str, str]:
        """Visit a <parent_action_declaration> node."""
        return {"parent": children[0]}

    @staticmethod
    def visit_action_body(_, children: Any) -> dict[str, Any]:
        """Visit a <action_body> node."""
        # Prepare with base data including optional fields
        component = {}
        for child in children:
            component.update(child)
        return component

    @staticmethod
    def visit_gloss(
        _, children: Any
    ) -> dict[str, viv_compiler.types.TemplateStringField | viv_compiler.types.StringField]:
        """Visit a <gloss> node."""
        gloss = children[0]
        return {"gloss": gloss}

    @staticmethod
    def visit_report(_, children: Any) -> dict[str, viv_compiler.types.TemplateStringField]:
        """Visit a <report> node."""
        report = children[0]
        return {"report": report}

    @staticmethod
    def visit_templated_text(_, children: Any) -> viv_compiler.types.TemplateStringField:
        """Visit a <templated_text> node."""
        template = []
        for child in children:
            if isinstance(child, dict):
                template.append(child)
            else:
                template.append({"type": "string", "value": child})
        component = {"type": ExpressionDiscriminator.TEMPLATE_STRING, "value": template}
        return component

    @staticmethod
    def visit_template_frame_component_double_quote(node: Any, _) -> str:
        """Visit a <template_frame_component_double_quote> node."""
        return str(node)

    @staticmethod
    def visit_template_frame_component_single_quote(node: Any, _) -> str:
        """Visit a <template_frame_component_single_quote> node."""
        return str(node)

    @staticmethod
    def visit_template_gap(_, children: Any) -> viv_compiler.types.Expression:
        """Visit a <template_gap> node."""
        return children[0]

    @staticmethod
    def visit_tags_field(_, children: Any) -> dict[str, Any]:
        """Visit a <tags_field> node."""
        if len(children) == 2:
            component = {"tags": children[1], "_join_tags": True}
        else:
            component = {"tags": children[0]}
        return component

    @staticmethod
    def visit_tags(_, children: Any) -> viv_compiler.types.ListField:
        """Visit a <tags> node."""
        component = {"type": ExpressionDiscriminator.LIST, "value": children}
        return component

    @staticmethod
    def visit_tag(_, children: Any) -> viv_compiler.types.StringField:
        """Visit a <tag> node."""
        component = {"type": ExpressionDiscriminator.STRING, "value": children[0]}
        return component

    @staticmethod
    def visit_roles(_, children: Any) -> dict[str, Any]:
        """Visit a <roles> node."""
        if children[0] == "join":
            component = {"roles": children[1:], "_join_roles": True}
        else:
            component = {"roles": children}
        return component

    @staticmethod
    def visit_role(_, children: Any) -> viv_compiler.types.RoleDefinition:
        """Visit a <role> node."""
        if "_role_renaming" in children[0]:
            return children[0]
        component = {
            "min": 1,
            "max": 1,
            "chance": None,
            "mean": None,
            "sd": None,
            "pool": None,
            "parent": None,
            "children": [],
            "character": False,
            "item": False,
            "action": False,
            "location": False,
            "symbol": False,
            "initiator": False,
            "partner": False,
            "recipient": False,
            "bystander": False,
            "absent": False,
            "precast": False,
            "build": False,
        }
        marked_entity_role = False
        for child in children:
            if "_is_entity" in child:
                marked_entity_role = child["_is_entity"]
            elif "min" in child:
                component['min'] = child['min']['value']
                component['max'] = child['max']['value']
            else:
                component.update(child)
        if marked_entity_role and component['symbol']:
            raise ValueError(f"Role '@{component['name']}' has entity prefix but is marked symbol")
        if not marked_entity_role and not component['symbol']:
            raise ValueError(f"Role '&{component['name']}' has symbol prefix but is not marked symbol")
        if not (component['item'] or component['action'] or component['location'] or component['symbol']):
            component['character'] = True
        if component['mean'] is not None:
            # Some initial experimentation has shown that taking the log of max - min produces a solid
            # standard deviation (for a normal distribution centered on the author-supplied mean), but
            # only for smaller values. Once the span eclipses 20 or so, we need a bigger SD to allow
            # for the tails to get better coverage (since otherwise the min and max are effectively
            # ignored). Empirically, it appears that dividing the span by 7 works for bigger spans.
            span = component['max'] - component['min']
            if span != 0:
                sd = max(math.log(span), span / 7)
            else:
                sd = 0
            component['sd'] = round(sd, 2)
        return component

    @staticmethod
    def visit_role_renaming(_, children: Any) -> dict[str, Any]:
        """Visit a <role_renaming> node."""
        component = {"_role_renaming": True, "_source_name": children[1]['name'], "_target_name": children[0]['name']}
        return component

    @staticmethod
    def visit_number_range(_, children: Any) -> dict[str, Any]:
        """Visit a <number_range> node."""
        if len(children) == 1:
            return {"min": children[0], "max": children[0]}
        return {"min": children[0], "max": children[1]}

    @staticmethod
    def visit_binding_type(_, children: Any) -> dict[str, bool]:
        """Visit a <binding_type> node."""
        return {"_is_entity": children[0] == "@"}

    @staticmethod
    def visit_role_name(_, children: Any) -> dict[str, str]:
        """Visit a <role_name> node."""
        name = children[0]
        return {"name": name}

    @staticmethod
    def visit_binding_pool_directive(_, children: Any) -> dict[str, Any]:
        """Visit a <binding_pool_directive> node."""
        return children[0]

    @staticmethod
    def visit_binding_pool_from_directive(_, children: Any) -> dict[str, Any]:
        """Visit a <binding_pool_from_directive> node."""
        component = {"pool": {"body": children[0]}}
        return component

    @staticmethod
    def visit_binding_pool_is_directive(_, children: Any) -> dict[str, Any]:
        """Visit a <binding_pool_is_directive> node."""
        binding_pool = {"type": ExpressionDiscriminator.LIST, "value": [children[0]]}
        component = {"pool": {"body": binding_pool}}
        return component

    @staticmethod
    def visit_role_labels(_, children: Any) -> dict[str, Any]:
        """Visit a <role_labels> node."""
        role_labels = []
        entity_recipe = None
        for role_label in children:
            if isinstance(role_label, dict):  # Build directive
                role_labels.append("build")
                entity_recipe = role_label["build"]
            else:
                role_labels.append(role_label)
        role_labels_component = {tag: True for tag in role_labels}
        if entity_recipe:
            role_labels_component["entityRecipe"] = entity_recipe
        return role_labels_component

    @staticmethod
    def visit_build_directive(_, children: Any) -> dict[str, Any]:
        """Visit a <build_directive> node."""
        return {"build": children[0]}

    @staticmethod
    def visit_build_directive_entity_recipe(_, children: Any) -> Any:
        """Visit a <build_directive_entity_recipe> node."""
        return children[0]

    @staticmethod
    def visit_binding_rate_directive(_, children: Any) -> Any:
        """Visit a <binding_rate_directive> node."""
        return children[0]

    @staticmethod
    def visit_chance_directive(_, children: Any) -> dict[str, float]:
        """Visit a <chance_directive> node."""
        # Children are the numeric tokens only (the `%` is a literal in the grammar)
        number = ''.join(str(child) for child in children)
        # Guard against empty or degenerate number strings
        if number in ('', '-', '.', '-.'):
            chance = -1.0  # There's no number preceding the `%`, so just trigger an error reliably
        else:
            try:
                chance = float(number) / 100.0
            except ValueError:
                chance = -1.0  # Same idea here
        # Preserve any negative we just created for the validator, and otherwise clamp tiny positives for stability
        if chance > 0:
            chance = max(round(chance, 3), 0.001)
        return {"chance": chance}

    @staticmethod
    def visit_mean_directive(_, children: Any) -> dict[str, float]:
        """Visit a <mean_directive> node."""
        # Children are the numeric tokens only (the `~` is a literal in the grammar)
        number = ''.join(str(child) for child in children)
        # Guard against empty or degenerate number strings
        if number in ('', '-', '.', '-.'):
            mean = -1.0  # There's no number succeeding the `~`, so just trigger an error reliably
        else:
            try:
                mean = float(number)
            except ValueError:
                mean = -1.0  # Same idea here
        mean = round(mean, 2)
        return {"mean": mean}

    @staticmethod
    def visit_preconditions(_, children: Any) -> dict[str, Any]:
        """Visit a <preconditions> node."""
        if len(children) == 2:
            component = {"preconditions": children[1], "_join_preconditions": True}
        else:
            component = {"preconditions": children[0]}
        return component

    @staticmethod
    def visit_child_join_operator(node: Any, __: Any) -> Any:
        """Visit a <child_join_operator> node."""
        return node

    @staticmethod
    def visit_scratch(_, children: Any) -> dict[str, Any]:
        """Visit a <scratch> node."""
        if len(children) == 2:
            component = {"scratch": children[1], "_join_scratch": True}
        else:
            component = {"scratch": children[0]}
        return component

    @staticmethod
    def visit_effects(_, children: Any) -> dict[str, Any]:
        """Visit a <effects> node."""
        if len(children) == 2:
            component = {"effects": children[1], "_join_effects": True}
        else:
            component = {"effects": children[0]}
        return component

    @staticmethod
    def visit_reactions(_, children: Any) -> dict[str, Any]:
        """Visit a <reactions> node."""
        if children[0] == "join":
            component = {"reactions": children[1:], "_join_reactions": True}
        else:
            component = {"reactions": children}
        return component

    @staticmethod
    def visit_reaction(_, children: Any):
        """Visit a <reaction> node."""
        # Prepare default reaction settings
        reaction_object = {
            "options": copy.deepcopy(viv_compiler.config.REACTION_FIELD_DEFAULT_OPTIONS),
        }
        for child in children:
            reaction_object.update(child)
        # Move the 'bindings' field from the options component to the top level of the reaction value
        reaction_object['bindings'] = reaction_object['options']['bindings']
        del reaction_object['options']['bindings']
        # Package up the component and return it
        reaction_value: viv_compiler.types.ReactionValue = reaction_object  # type: ignore[assignment]
        component: viv_compiler.types.Reaction = {"type": ExpressionDiscriminator.REACTION, "value": reaction_value}
        return component

    @staticmethod
    def visit_reaction_action_name(_, children: Any) -> dict[str, Any]:
        """Visit a <reaction_action_name> node."""
        return {"actionName": children[0]}

    @staticmethod
    def visit_bindings(_, children: Any) -> dict[str, Any]:
        """Visit a <bindings> node."""
        return {"bindings": children}

    @staticmethod
    def visit_binding(_, children: Any) -> viv_compiler.types.ReactionRoleBindings:
        """Visit a <binding> node."""
        role_type, role_name, candidate_expression = children
        component = {
            "role": role_name,
            "isEntityRole": role_type["_is_entity"],
            "candidates": candidate_expression,
        }
        return component

    @staticmethod
    def visit_reaction_options(_, children: Any) -> dict[str, Any]:
        """Visit a <reaction_options> node."""
        component = {"options": copy.deepcopy(viv_compiler.config.REACTION_FIELD_DEFAULT_OPTIONS)}
        for child in children:
            component['options'].update(child)
        return component

    @staticmethod
    def visit_urgent(_, children: Any) -> dict[str, Any]:
        """Visit a <urgent> node."""
        component = {"urgent": children[0]}
        return component

    @staticmethod
    def visit_priority(_, children: Any) -> dict[str, Any]:
        """Visit a <priority> node."""
        component = {"priority": children[0]}
        return component

    @staticmethod
    def visit_kill_code(_, children: Any) -> dict[str, Any]:
        """Visit a <kill_code> node."""
        component = {"killCode": children[0]}
        return component

    @staticmethod
    def visit_where(_, children: Any) -> dict[str, Any]:
        """Visit a <where> node."""
        component = {"where": children[0]}
        return component

    @staticmethod
    def visit_when(_, children: Any) -> dict[str, viv_compiler.types.TemporalConstraints]:
        """Visit a <when> node."""
        when_value = {}
        for child in children:
            when_value.update(child)
        component = {"when": when_value}
        return component

    @staticmethod
    def visit_when_action_timestamp_anchor(_, __: Any) -> dict[str, bool]:
        """Visit a <when_action_timestamp_anchor> node."""
        component = {"useActionTimestamp": True}
        return component

    @staticmethod
    def visit_when_hearing_timestamp_anchor(_, __: Any) -> dict[str, bool]:
        """Visit a <when_hearing_timestamp_anchor> node."""
        component = {"useActionTimestamp": False}
        return component

    @staticmethod
    def visit_time_expression(_, children: Any) -> viv_compiler.types.TemporalConstraints:
        """Visit a <time_expression> node."""
        time_constraints: dict[str, Optional[dict[str, Any]]] = {"timePeriod": None, "timeOfDay": None}
        for child in children:
            if child["operator"] == "between":
                if child["open"]["type"] == "timePeriod":
                    time_constraints["timePeriod"] = {
                        "open": {"amount": child["open"]["amount"], "unit": child["open"]["unit"]},
                        "close": {"amount": child["close"]["amount"], "unit": child["close"]["unit"]},
                    }
                else:  # child["open"]["type"] == "time"
                    time_constraints["timeOfDay"] = {
                        "open": {"hour": child["open"]["hour"], "minute": child["open"]["minute"]},
                        "close": {"hour": child["close"]["hour"], "minute": child["close"]["minute"]},
                    }
            elif child["operator"] == "before":
                anchor = child["anchor"]
                if anchor["type"] == "timePeriod":
                    time_constraints["timePeriod"] = {
                        "open": None,
                        "close": {"amount": anchor["amount"], "unit": anchor["unit"]},
                    }
                else:  # anchor["type"] == "time"
                    time_constraints["timeOfDay"] = {
                        "open": None,
                        "close": {"hour": anchor["hour"], "minute": anchor["minute"]}
                    }
            else:  # operator == "after":
                anchor = child["anchor"]
                if anchor["type"] == "timePeriod":
                    time_constraints["timePeriod"] = {
                        "open": {"amount": anchor["amount"], "unit": anchor["unit"]},
                        "close": None,
                    }
                else:  # anchor["type"] == "time"
                    time_constraints["timeOfDay"] = {
                        "open": {"hour": anchor["hour"], "minute": anchor["minute"]},
                        "close": None,
                    }
        return time_constraints

    @staticmethod
    def visit_time_statement(_, children: Any) -> dict[str, Any]:
        """Visit a <time_statement> node."""
        return children[0]

    @staticmethod
    def visit_before_time_statement(_, children: Any) -> dict[str, Any]:
        """Visit a <before_time_statement> node."""
        return {"operator": "before", "anchor": children[0]}

    @staticmethod
    def visit_after_time_statement(_, children: Any) -> dict[str, Any]:
        """Visit a <after_time_statement> node."""
        return {"operator": "after", "anchor": children[0]}

    @staticmethod
    def visit_between_time_statement(_, children: Any) -> dict[str, Any]:
        """Visit a <between_time_statement> node."""
        return {"operator": "between", "open": children[0], "close": children[1]}

    @staticmethod
    def visit_time_period(_, children: Any) -> dict[str, Any]:
        """Visit a <time_period> node."""
        number = children[0]['value']
        unit = children[1] + 's' if children[1][-1] != 's' else children[1]
        component = {"type": "timePeriod", "amount": number, "unit": unit}
        return component

    @staticmethod
    def visit_time(_, children: Any) -> dict[str, Any]:
        """Visit a <time> node."""
        raw_hour = int(children[0])
        minute = int(children[1]) if len(children) > 1 and children[1].isdigit() else 0
        if children[-1].upper() in ("AM", "PM"):  # 12-hour form
            period = children[-1].upper()
            if not 1 <= raw_hour <= 12:
                raise ValueError(f"Invalid hour in 12-hour time: {raw_hour}")
            hour = (raw_hour % 12) + (12 if period == "PM" else 0)
        else:  # 24-hour form
            if not 0 <= raw_hour <= 23:
                raise ValueError(f"Invalid hour in 24-hour time: {raw_hour}")
            hour = raw_hour
        if not 0 <= minute <= 59:
            raise ValueError(f"Invalid minute in time: {minute}")
        component = {"type": "time", "hour": hour, "minute": minute}
        return component

    @staticmethod
    def visit_digits(_, children: Any) -> str:
        """Visit a <digits> node."""
        return ''.join(children)

    @staticmethod
    def visit_abandonment_conditions(_, children: Any) -> dict[str, list[viv_compiler.types.Expression]]:
        """Visit a <abandonment_conditions> node."""
        component = {"abandonmentConditions": children}
        return component

    @staticmethod
    def visit_saliences(_, children: Any) -> dict[str, Any]:
        """Visit a <saliences> node."""
        join_saliences = False
        if children[0] == "join":
            join_saliences = True
            children = children[1:]
        local_variable, body = None, []
        if len(children) == 1:  # Default only
            default_value_expression = children[0]
        else:
            local_variable, default_value_expression, body = children
        component = {
            "saliences": {
                "default": default_value_expression,
                "variable": local_variable,
                "body": body,
            }
        }
        if join_saliences:
            component["_join_saliences"] = True
        return component

    @staticmethod
    def visit_saliences_default_value(_, children: Any) -> viv_compiler.types.Expression:
        """Visit a <saliences_default_value> node."""
        return children[0]

    @staticmethod
    def visit_saliences_body(_, children: Any) -> list[viv_compiler.types.Expression]:
        """Visit a <saliences_body> node."""
        return children

    @staticmethod
    def visit_associations(_, children: Any) -> dict[str, Any]:
        """Visit an <associations> node."""
        join_associations = False
        if children[0] == "join":
            join_associations = True
            children = children[1:]
        local_variable, body = None, []
        if len(children) == 1:  # Default only
            default_value_expression = children[0]
        else:
            local_variable, default_value_expression, body = children
        component = {
            "associations": {
                "default": default_value_expression,
                "variable": local_variable,
                "body": body,
            }
        }
        if join_associations:
            component["_join_associations"] = True
        return component

    @staticmethod
    def visit_associations_default_value(_, children: Any) -> viv_compiler.types.Expression:
        """Visit a <associations_default_value> node."""
        return children[0]

    @staticmethod
    def visit_associations_body(_, children: Any) -> list[viv_compiler.types.Expression]:
        """Visit a <associations_body> node."""
        return children[0]

    @staticmethod
    def visit_associations_statements(_, children: Any) -> list[viv_compiler.types.Expression]:
        """Visit a <associations_statements> node."""
        return children

    @staticmethod
    def visit_associations_statement(_, children: Any) -> list[viv_compiler.types.Expression]:
        """Visit a <associations_statement> node."""
        return children[0]

    @staticmethod
    def visit_associations_loop(_, children: Any) -> viv_compiler.types.Loop:
        """Visit a <associations_loop> node."""
        iterable_reference, variable_name, loop_body = children
        component = {
            "type": ExpressionDiscriminator.LOOP,
            "value": {"iterable": iterable_reference, "variable": variable_name['name'], "body": loop_body}
        }
        return component

    @staticmethod
    def visit_associations_conditional(_, children: Any) -> viv_compiler.types.Conditional:
        """Visit a <associations_conditional> node."""
        conditional_object = {"type": ExpressionDiscriminator.CONDITIONAL, "value": {}}
        for child in children:
            conditional_object['value'].update(child)
        return conditional_object

    @staticmethod
    def visit_associations_conditional_branches(_, children: Any) -> dict[str, viv_compiler.types.Expression]:
        """Visit a <associations_conditional_branches> node."""
        return {"branches": children}

    @staticmethod
    def visit_associations_conditional_branch(_, children: Any) -> dict[str, viv_compiler.types.Expression]:
        """Visit a <associations_conditional_branch> node."""
        component = {}
        for child in children:
            component.update(child)
        return component

    @staticmethod
    def visit_associations_conditional_consequent(_, children: Any) -> dict[str, list[viv_compiler.types.Expression]]:
        """Visit a <associations_conditional_consequent> node."""
        return {"consequent": children[0]}

    @staticmethod
    def visit_associations_conditional_alternative(_, children: Any) -> dict[str, list[viv_compiler.types.Expression]]:
        """Visit a <associations_conditional_alternative> node."""
        return {"alternative": children[0]}

    @staticmethod
    def visit_associations_scoped_statements(_, children: Any) -> list[viv_compiler.types.Expression]:
        """Visit a <associations_scoped_statements> node."""
        return children

    @staticmethod
    def visit_associations_scoped_statement(_, children: Any) -> list[viv_compiler.types.Expression]:
        """Visit a <associations_scoped_statement> node."""
        return children[0]

    @staticmethod
    def visit_embargoes(_, children: Any) -> dict[str, Any]:
        """Visit an <embargoes> node."""
        if children[0] == "join":
            component = {"embargoes": children[1:], "_join_embargoes": True}
        else:
            component = {"embargoes": children}
        return component

    @staticmethod
    def visit_embargo(_, children: Any) -> dict[str, Any]:
        """Visit an <embargo> node."""
        # Prepare default values that we'll override below or in post-processing
        component = {"roles": None, "permanent": False, "period": None, "here": False}
        for child in children:
            component.update(child)
        return component

    @staticmethod
    def visit_embargo_roles(_, children: Any) -> dict[str, list[str]]:
        """Visit an <embargo_roles> node."""
        component = {"roles": [child['name'] for child in children]}
        return component

    @staticmethod
    def visit_embargo_time_period(_, children: Any) -> dict[str, Any]:
        """Visit an <embargo_time_period> node."""
        if children == ["forever"]:
            component = {"permanent": True, "period": None}
        else:
            component = {
                "permanent": False,
                "period": {
                    "amount": children[0]["amount"],
                    "unit": children[0]["unit"]
                }
            }
        return component

    @staticmethod
    def visit_embargo_location(_, __: Any) -> dict[str, bool]:
        """Visit an <embargo_location> node."""
        component = {"here": True}
        return component

    @staticmethod
    def visit_conditional(_, children: Any) -> viv_compiler.types.Conditional:
        """Visit a <conditional> node."""
        component = {"type": ExpressionDiscriminator.CONDITIONAL, "value": {}}
        for child in children:
            component['value'].update(child)
        return component

    @staticmethod
    def visit_conditional_branches(_, children: Any) -> dict[str, viv_compiler.types.Expression]:
        """Visit a <conditional_branches> node."""
        return {"branches": children}

    @staticmethod
    def visit_conditional_branch(_, children: Any) -> dict[str, viv_compiler.types.Expression]:
        """Visit a <conditional_branch> node."""
        component = {}
        for child in children:
            component.update(child)
        return component

    @staticmethod
    def visit_condition(_, children: Any) -> dict[str, viv_compiler.types.Expression]:
        """Visit a <condition> node."""
        return {"condition": children[0]}

    @staticmethod
    def visit_consequent(_, children: Any) -> dict[str, list[viv_compiler.types.Expression]]:
        """Visit a <condition> node."""
        return {"consequent": children[0]}

    @staticmethod
    def visit_alternative(_, children: Any) -> dict[str, list[viv_compiler.types.Expression]]:
        """Visit a <condition> node."""
        return {"alternative": children[0]}

    @staticmethod
    def visit_loop(_, children: Any) -> viv_compiler.types.Loop:
        """Visit a <loop> node."""
        iterable_reference, loop_variable, loop_body = children
        component = {
            "type": ExpressionDiscriminator.LOOP,
            "value": {"iterable": iterable_reference, "variable": loop_variable, "body": loop_body}
        }
        return component

    @staticmethod
    def visit_local_variable(_, children: Any) -> LocalVariable:
        """Visit a <local_variable> node."""
        _, binding_type, name = children
        component = {
            "name": name,
            "isEntityVariable": binding_type["_is_entity"]
        }
        return component

    @staticmethod
    def visit_statements(_, children: Any) -> list[viv_compiler.types.Expression]:
        """Visit a <statement> node."""
        return children

    @staticmethod
    def visit_statement(_, children: Any) -> viv_compiler.types.Expression:
        """Visit a <statement> node."""
        return children[0]

    @staticmethod
    def visit_scoped_statements(_, children: Any) -> list[viv_compiler.types.Expression]:
        """Visit a <scoped_statements> node."""
        return children

    @staticmethod
    def visit_expression(_, children: Any) -> viv_compiler.types.Expression:
        """Visit an <expression> node."""
        return children[0]

    @staticmethod
    def visit_logical_expression(_, children: Any) -> viv_compiler.types.Expression:
        """Visit a <logical_expression> node."""
        # The <logical_expression> nonterminal is just a wrapper around disjunction,
        # and in any event all the work to package up the expression will have already
        # been done by the time it gets to here, so we simply return the sole child.
        return children[0]

    @staticmethod
    def visit_disjunction(_, children: Any) -> viv_compiler.types.Expression:
        """Visit a <disjunction> node."""
        # The elimination of left recursion in the grammar allows for a child expression to
        # work its way up to here, in which case we just want to return that, since it's
        # not a true disjunction.
        if len(children) == 1:
            return children[0]
        negated = False
        if children[0] == "!":
            negated = True
            children = children[1:]
        component = {"type": ExpressionDiscriminator.DISJUNCTION, "value": {"operands": children}}
        if negated:
            component["negated"] = True
        return component

    @staticmethod
    def visit_conjunction(_, children: Any) -> viv_compiler.types.Expression:
        """Visit a <conjunction> node."""
        # The elimination of left recursion in the grammar allows for a child expression to
        # work its way up to here, in which case we just want to return that, since it's
        # not a true conjunction.
        if len(children) == 1:
            return children[0]
        negated = False
        if children[0] == "!":
            negated = True
            children = children[1:]
        component = {"type": ExpressionDiscriminator.CONJUNCTION, "value": {"operands": children}}
        if negated:
            component["negated"] = True
        return component

    @staticmethod
    def visit_relational_expression(_, children: Any) -> viv_compiler.types.Expression:
        """Visit a <relational_expression> node."""
        # The elimination of left recursion in the grammar allows for a child expression to
        # work its way up to here, in which case we just want to return that, since it's
        # not a true comparison.
        if len(children) == 1:
            return children[0]
        negated = False
        if children[0] == "!":
            negated = True
            children = children[1:]
        left, operator, right = children
        component = {
            "type": ExpressionDiscriminator.MEMBERSHIP_TEST if operator == "in" else ExpressionDiscriminator.COMPARISON,
            "value": {
                "left": left,
                "operator": operator,
                "right": right
            }
        }
        if negated:
            component["negated"] = True
        return component

    @staticmethod
    def visit_assignment_expression(_, children: Any) -> viv_compiler.types.Assignment:
        """Visit an <assignment_expression> node."""
        left, operator, right = children
        component = {
            "type": ExpressionDiscriminator.ASSIGNMENT,
            "value": {
                "left": left,
                "operator": operator,
                "right": right
            }
        }
        return component

    @staticmethod
    def visit_assignment_lvalue(_, children: Any) -> dict[str, Any]:
        """Visit an <assignment_lvalue> node."""
        return children[0]

    @staticmethod
    def visit_arithmetic_expression(_, children: Any) -> viv_compiler.types.ArithmeticExpression:
        """Visit an <arithmetic_expression> node."""
        left, operator, right = children
        component = {
            "type": ExpressionDiscriminator.ARITHMETIC_EXPRESSION,
            "value": {
                "left": left,
                "operator": operator,
                "right": right
            }
        }
        return component

    @staticmethod
    def visit_unary_expression(_, children: Any) -> viv_compiler.types.Expression:
        """Visit a <unary_expression> node."""
        component = children[-1]
        if len(children) > 1:
            component['negated'] = True
        return component

    @staticmethod
    def visit_object(_, children: Any) -> viv_compiler.types.ObjectField:
        """Visit a <object> node."""
        component = {"type": ExpressionDiscriminator.OBJECT, "value": {}}
        for child in children:
            component['value'].update(child)
        return component

    @staticmethod
    def visit_key_value_pair(_, children: Any) -> dict[str, viv_compiler.types.Expression]:
        """Visit a <key_value_pair> node."""
        key, value = children
        if isinstance(key, dict):  # The author formatted the key as a string
            key = key['value']
        return {key: value}

    @staticmethod
    def visit_adapter_function_call(_, children: Any) -> viv_compiler.types.AdapterFunctionCall:
        """Visit a <adapter_function_call> node."""
        function_result_fail_safe = False
        if children[-1] == {"type": ExpressionDiscriminator.EVAL_FAIL_SAFE}:
            function_result_fail_safe = True
            children = children[:-1]
        try:
            function_name, function_args = children
        except ValueError:  # No arguments passed in the function call, which is syntactically fine
            function_name = children[0]
            function_args = []
        function_call_object = {
            "type": ExpressionDiscriminator.ADAPTER_FUNCTION_CALL,
            "value": {
                "name": function_name,
                "args": function_args,
            }
        }
        if function_result_fail_safe:
            function_call_object["value"]["resultFailSafe"] = True
        return function_call_object

    @staticmethod
    def visit_args(_, children: Any) -> list[viv_compiler.types.Expression]:
        """Visit a <args> node."""
        return children

    @staticmethod
    def visit_reference(_, children: Any) -> viv_compiler.types.EntityReference | viv_compiler.types.SymbolReference:
        """Visit a <reference> node."""
        is_symbol_reference = False
        anchor_is_local_variable = False
        if children[0] == "$":
            # If the reference is anchored in a scratch variable, expand the `$` anchor. `$` is really
            # just syntactic sugar for `@this.scratch.`, which means any reference anchored in a scratch
            # variable is in fact an entity reference anchored in a role name.
            children = children[1:]
            if children[0] == "&":
                # We will ignore the symbol sigil here, because ultimately that refers to the type of
                # the scratch variable, not the anchor, which is always entity data.
                pass
            children = children[1:]
            anchor = viv_compiler.config.SCRATCH_VARIABLE_REFERENCE_ANCHOR
            path = [
                *viv_compiler.config.SCRATCH_VARIABLE_REFERENCE_PATH_PREFIX,
                {
                    "type": ReferencePathComponentDiscriminator.REFERENCE_PATH_COMPONENT_PROPERTY_NAME,
                    "name": children[0],
                }
            ]
            path += children[1] if len(children) > 1 else []
        elif children[0] == "_":
            anchor_is_local_variable = True
            children = children[1:]
            if children[0] == "&":
                is_symbol_reference = True
            children = children[1:]
            anchor = children[0]
            path = children[1] if len(children) > 1 else []
        else:  # Bare reference to a role, e.g., `@foo` or `&bar`
            if children[0] == "&":
                is_symbol_reference = True
            children = children[1:]
            anchor = children[0]
            path = children[1] if len(children) > 1 else []
        if is_symbol_reference:
            component_type = ExpressionDiscriminator.SYMBOL_REFERENCE
        else:
            component_type = ExpressionDiscriminator.ENTITY_REFERENCE
        component = {
            "type": component_type,
            "value": {
                "local": anchor_is_local_variable,
                "anchor": anchor,
                "path": path,
            }
        }
        return component

    @staticmethod
    def visit_entity_sigil(node: Any, _) -> Any:
        """Visit an <entity_sigil> node."""
        return node

    @staticmethod
    def visit_symbol_sigil(node: Any, _) -> Any:
        """Visit a <symbol_sigil> node."""
        return node

    @staticmethod
    def visit_scratch_variable_sigil(node: Any, _) -> Any:
        """Visit a <scratch_variable_sigil> node."""
        return node

    @staticmethod
    def visit_local_variable_sigil(node: Any, _) -> Any:
        """Visit a <local_variable_sigil> node."""
        return node

    @staticmethod
    def visit_reference_path(_, children: Any) -> list[viv_compiler.types.ReferencePathComponent]:
        """Visit a <reference_path> node."""
        return children

    @staticmethod
    def visit_reference_path_property_name(_, children: Any) -> viv_compiler.types.ReferencePathComponentPropertyName:
        """Visit a <reference_path_property_name> node."""
        property_name = children[0]
        component = {
            "type": ReferencePathComponentDiscriminator.REFERENCE_PATH_COMPONENT_PROPERTY_NAME,
            "name": property_name,
        }
        if len(children) > 1:
            component["failSafe"] = True
        return component

    @staticmethod
    def visit_reference_path_pointer(_, children: Any) -> viv_compiler.types.ReferencePathComponentPointer:
        """Visit a <reference_path_pointer> node."""
        property_name = children[0]
        component = {
            "type": ReferencePathComponentDiscriminator.REFERENCE_PATH_COMPONENT_POINTER,
            "propertyName": property_name,
        }
        if len(children) > 1:
            component["failSafe"] = True
        return component

    @staticmethod
    def visit_reference_path_lookup(_, children: Any) -> viv_compiler.types.ReferencePathComponentLookup:
        """Visit a <reference_path_lookup> node."""
        key = children[0]
        component = {
            "type": ReferencePathComponentDiscriminator.REFERENCE_PATH_COMPONENT_LOOKUP,
            "key": key,
        }
        if len(children) > 1:
            component["failSafe"] = True
        return component

    @staticmethod
    def visit_role_unpacking(_, children: Any) -> viv_compiler.types.RoleUnpacking:
        """Visit a <role_unpacking> node."""
        component = {"type": ExpressionDiscriminator.ROLE_UNPACKING, "value": children[0]}
        return component

    @staticmethod
    def visit_relational_operator(_, children: Any) -> str:
        """Visit a <relational_operator> node."""
        return children[0]

    @staticmethod
    def visit_assignment_operator(_, children: Any) -> str:
        """Visit a <assignment_operator> node."""
        return children[0]

    @staticmethod
    def visit_negation(_, __: Any) -> str:
        """Visit a <negation> node."""
        return "!"

    @staticmethod
    def visit_list(_, children: Any) -> viv_compiler.types.ListField:
        """Visit a <list> node."""
        component = {"type": ExpressionDiscriminator.LIST, "value": children}
        return component

    @staticmethod
    def visit_chance_expression(_, children: Any) -> viv_compiler.types.ChanceExpression:
        """Visit a <chance_expression> node."""
        # Children may include a leading '-' and the numeric fragments; '%' is a literal in the grammar
        chance_str = ''.join(str(tok) for tok in children if tok != '%')
        if not chance_str or chance_str == '-':
            chance = -1  # signal for later validation
        else:
            chance = float(chance_str) / 100
        component = {"type": ExpressionDiscriminator.CHANCE_EXPRESSION, "value": chance}
        return component

    @staticmethod
    def visit_literal(_, children: Any) -> viv_compiler.types.Expression:
        """Visit a <literal> node."""
        return children[0]

    @staticmethod
    def visit_enum(_, children: Any) -> viv_compiler.types.Enum:
        """Visit an <enum> node."""
        additive_inverse_present = False
        if len(children) > 1:
            additive_inverse_present = children[0] == "-"
        token = children[-1]
        unscaled = token[:2] == "##"  # As opposed to '#', which yields a scaled enum
        name = token.lstrip('#')
        component = {
            "type": ExpressionDiscriminator.ENUM,
            "value": {
                "name": name,
                "scaled": not unscaled,
                "minus": additive_inverse_present
            }
        }
        return component

    @staticmethod
    def visit_string(_, children: Any) -> viv_compiler.types.TemplateStringField | viv_compiler.types.StringField:
        """Visit a <string> node."""
        string = []  # A mix of strings and string-producing references
        injected_string = False
        partial_string = ""
        for child in children:
            if isinstance(child, str):
                partial_string += child
            else:  # A reference, making this an injected string
                injected_string = True
                if partial_string:
                    string.append(partial_string)
                partial_string = " "  # Needed because the parser gobbles whitespace between nonterminals
                string.append(child)
        if partial_string.strip():
            string.append(partial_string)
        if injected_string:
            component = {"type": ExpressionDiscriminator.TEMPLATE_STRING, "value": string}
        else:
            component = {"type": ExpressionDiscriminator.STRING, "value": partial_string}
        return component

    @staticmethod
    def visit_character(node: Any, _) -> str:
        """Visit a <character> node."""
        return str(node)

    @staticmethod
    def visit_space(node: Any, _) -> str:
        """Visit a <space> node."""
        return str(node)

    @staticmethod
    def visit_number(_, children: Any) -> viv_compiler.types.FloatField | viv_compiler.types.IntField:
        """Visit a <number> node."""
        number_str = ''.join(children)
        if any(child for child in children if child == '.'):
            component = {"type": ExpressionDiscriminator.FLOAT, "value": float(number_str)}
        else:
            component = {"type": ExpressionDiscriminator.INT, "value": int(number_str)}
        return component

    @staticmethod
    def visit_number_word(_, children: Any) -> viv_compiler.types.IntField:
        """Visit a <number_word> node."""
        number_word_to_value = {
            "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
            "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
        }
        component = {"type": ExpressionDiscriminator.INT, "value": number_word_to_value[children[0]]}
        return component

    @staticmethod
    def visit_boolean(node: Any, __: Any) -> viv_compiler.types.BoolField:
        """Visit a <boolean> node."""
        component = {"type": ExpressionDiscriminator.BOOL, "value": True if node.value == "true" else False}
        return component

    @staticmethod
    def visit_null_type(_, __: Any) -> viv_compiler.types.NullField:
        """Visit a <null_type> node."""
        component = {"type": ExpressionDiscriminator.NULL_TYPE, "value": None}
        return component

    @staticmethod
    def visit_eval_fail_safe_marker(_, __: Any) -> viv_compiler.types.EvalFailSafeField:
        """Visit an <eval_fail_safe_marker> node."""
        component = {"type": ExpressionDiscriminator.EVAL_FAIL_SAFE}
        return component

    @staticmethod
    def visit_trope_fit_expression(_, children: Any) -> viv_compiler.types.TropeFitExpression:
        """Visit a <trope_fit_expression> node."""
        arguments, trope_name = children
        component = {
            "type": ExpressionDiscriminator.TROPE_FIT_EXPRESSION,
            "value": {
                "tropeName": trope_name,
                "args": arguments
            }
        }
        return component

    @staticmethod
    def visit_trope_fit_expression_args(_, children: Any) -> list[viv_compiler.types.Expression]:
        """Visit a <trope_fit_expression_args> node."""
        return children
