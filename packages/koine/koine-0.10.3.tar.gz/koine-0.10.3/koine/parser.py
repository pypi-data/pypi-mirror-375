import re
from bisect import bisect_right
import json
from dataclasses import dataclass
from typing import Optional
from copy import deepcopy
from contextlib import contextmanager
from functools import reduce
from operator import getitem
from pathlib import Path
import yaml
from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor
from parsimonious.expressions import Literal, Quantifier, Lookahead, Regex, Expression
from parsimonious.exceptions import ParseError, IncompleteParseError, LeftRecursionError, VisitationError, BadGrammar, UndefinedLabel

def sanitize_to_json_data(obj): return json.loads(json.dumps(obj))

def flatten(items):
    if items is None or items == []: return []
    stack = list(reversed(items if isinstance(items, list) else [items]))
    out = []
    while stack:
        x = stack.pop()
        if x is None or x == []: continue
        if isinstance(x, list):
            stack.extend(reversed(x))
        else:
            out.append(x)
    return out

def apply_type(text, type_name):
    if type_name == 'number':
        val = float(text)
        return int(val) if val.is_integer() else val
    if type_name == 'bool':
        return str(text).lower() == 'true'
    if type_name == 'null':
        return None
    return text

# ==============================================================================
# 0. LEXER
# ==============================================================================
@dataclass
class Token:
    type: str
    value: str
    line: int
    col: int
    def __repr__(self):
        return f"Token({self.type}, '{self.value}', L{self.line}:C{self.col})"

class StatefulLexer:
    """
    A stateful lexer that handles tokenizing text, including indentation-based
    syntax.
    """
    def __init__(self, lexer_config: dict, tab_width=8):
        self.token_specs = lexer_config.get('tokens', [])
        self.tab_width = tab_width
        # Compile regexes for efficiency
        self.compiled_specs = []
        for spec in self.token_specs:
            self.compiled_specs.append(
                (re.compile(spec['regex']), spec.get('action'), spec.get('token'))
            )
        self.handles_indentation = any(
            spec.get('action') == 'handle_indent' for spec in self.token_specs
        )

    def tokenize(self, text: str) -> list[Token]:
        # The caller is responsible for stripping any unwanted leading/trailing whitespace.
        # Normalize Windows/Mac newlines to '\n' for consistent indentation handling.
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        text = text.expandtabs(self.tab_width)
        tokens = []
        indent_stack = [0]
        line_num = 1
        line_start = 0
        pos = 0

        while pos < len(text):
            longest_match, best_spec = None, None
            for regex, action, token_type in self.compiled_specs:
                match = regex.match(text, pos)
                if match and (longest_match is None or len(match.group(0)) > len(longest_match.group(0))):
                    longest_match, best_spec = match, (action, token_type)

            if longest_match:
                value = longest_match.group(0)
                action, token_type = best_spec
                
                col = pos - line_start + 1

                if action == 'handle_indent':
                    # value is like "\n[ \t]*"
                    indent_level = len(value) - 1  # whitespace after '\n'
                    # Detect if the next line is blank or whitespace-only. If so, do not
                    # emit INDENT/DEDENT for this newline; indentation should be decided
                    # by the next non-blank line.
                    j = longest_match.end()
                    while j < len(text) and text[j] in (' ', '\t'):
                        j += 1
                    blank_line = (j >= len(text)) or (text[j] == '\n')

                    if not blank_line:
                        if indent_level > indent_stack[-1]:
                            indent_stack.append(indent_level)
                            tokens.append(Token('INDENT', '', line_num + 1, 1))

                        while indent_level < indent_stack[-1]:
                            indent_stack.pop()
                            tokens.append(Token('DEDENT', '', line_num + 1, 1))

                        if indent_level != indent_stack[-1]:
                            raise IndentationError(f"Indentation error in input text at L{line_num+1}:C1")
                
                elif action != 'skip':
                    tokens.append(Token(token_type, value, line_num, col))
                
                # Update line and column counters
                newlines = value.count('\n')
                if newlines > 0:
                    line_num += newlines
                    line_start = pos + value.rfind('\n') + 1
                
                pos = longest_match.end()
            else:
                col = pos - line_start + 1
                raise SyntaxError(f"Unexpected character in input text at L{line_num}:C{col}: '{text[pos]}'")

        # At end of file, dedent all remaining levels
        if self.handles_indentation:
            while len(indent_stack) > 1:
                indent_stack.pop()
                tokens.append(Token('DEDENT', '', line_num, 1))
            
        return tokens

# ==============================================================================
# 1. GRAMMAR-TO-STRING TRANSPILER
# ==============================================================================

def transpile_rule(rule_definition, is_token_grammar=False, rule_name=None):
    """Recursively transpiles a single rule dictionary into a Parsimonious grammar string component."""
    if not isinstance(rule_definition, dict):
        error_msg = f"Rule definition must be a dictionary, but got {type(rule_definition).__name__}: {rule_definition!r}"
        if rule_name:
            user_facing_rule_name = rule_name.split('__')[0]
            error_msg += f" (in rule '{user_facing_rule_name}')"
        raise ValueError(error_msg)

    rule_keys = {
        'literal', 'regex', 'rule', 'choice', 'sequence',
        'zero_or_more', 'one_or_more', 'optional', 'token',
        'positive_lookahead', 'negative_lookahead'
    }
    # This is a Koine-specific key that should be resolved before transpilation.
    # If it's still present, it means we're in a structural-only build where
    # it acts as a placeholder that should have been replaced. We treat it as
    # a rule that can match an empty string, which is a safe default.
    if 'subgrammar' in rule_definition:
        return '("")?'

    found_keys = [key for key in rule_definition if key in rule_keys]

    if len(found_keys) != 1:
        raise ValueError(f"Rule must have exactly one key from {rule_keys}, found {found_keys} in {rule_definition}")

    rule_type, value = found_keys[0], rule_definition[found_keys[0]]

    if rule_type == 'token':
        return value
    elif rule_type in ['literal', 'regex'] and is_token_grammar:
        raise ValueError(f"'{rule_type}' is not supported when a lexer is defined. Use 'token' instead.")
    elif rule_type == 'literal':
        escaped_value = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped_value}"'
    elif rule_type == 'regex':
        # To embed a regex in a parsimonious ~r"..." string, any double quotes
        # within the regex itself must be escaped.
        escaped_value = value.replace('"', '\\"')
        return f'~r"{escaped_value}"'
    elif rule_type == 'rule':
        # If a rule reference has its own AST config, it's not a simple alias.
        # We must prevent Parsimonious from optimizing it away, which would
        # cause the AST config to be ignored. We force it to be a sequence
        # of one, which is not optimized. An 'ast' block that ONLY contains
        # 'name' is for structuring the parent and does not count.
        ast_config = rule_definition.get('ast', {})
        ast_keys = list(ast_config.keys())
        is_just_a_name = len(ast_keys) == 1 and 'name' in ast_keys
        if 'ast' in rule_definition and not is_just_a_name:
            return f'({value} ("")?)'
        return value
    elif rule_type in ['choice', 'sequence']:
        if not value:
            return '("")?' if rule_type == 'sequence' else (_ for _ in ()).throw(ValueError("Choice cannot be empty"))
        parts = [transpile_rule(part, is_token_grammar, rule_name=rule_name) for part in value]
        joiner = " / " if rule_type == 'choice' else " "
        joined_parts = joiner.join(parts)
        # For a sequence of one item, Parsimonious optimizes `(foo)` to just `foo`.
        # This breaks AST construction, as the sequence rule's AST config is ignored.
        # We add a no-op (`("")?`) to prevent this optimization.
        if rule_type == 'sequence' and len(parts) == 1:
            return f'({joined_parts} ("")?)'
        return f'({joined_parts})'
    else:  # Quantifiers and lookaheads
        # Postfix operators
        if rule_type in ['zero_or_more', 'one_or_more', 'optional']:
            op_map = {'zero_or_more': '*', 'one_or_more': '+', 'optional': '?'}
            return f"({transpile_rule(value, is_token_grammar, rule_name=rule_name)}){op_map[rule_type]}"
        # Prefix operators
        else:  # positive_lookahead, negative_lookahead
            op_map = {'positive_lookahead': '&', 'negative_lookahead': '!'}
            return f"{op_map[rule_type]}({transpile_rule(value, is_token_grammar, rule_name=rule_name)})"

def transpile_grammar(grammar_dict):
    """Takes a full grammar dictionary and transpiles it into a single grammar string."""
    if 'rules' not in grammar_dict:
        raise ValueError("Grammar definition must have a 'rules' key.")
    
    is_token_grammar = 'lexer' in grammar_dict
    grammar_lines = [f"{name} = {transpile_rule(rule, is_token_grammar, rule_name=name)}" for name, rule in grammar_dict['rules'].items()]
    
    if is_token_grammar:
        token_types = {spec['token'] for spec in grammar_dict['lexer']['tokens'] if 'token' in spec}
        token_types.update(['INDENT', 'DEDENT'])
        for token_type in sorted(token_types):
            # Match the token name and consume any trailing whitespace that separates it
            grammar_lines.append(f'{token_type} = ~r"{token_type}\\s*"')

    return "\n".join(grammar_lines)

# ==============================================================================
# 2. POSITION FINDER UTILITY
# ==============================================================================

class LineColumnFinder:
    """A utility to find the line and column of a character offset in a text."""
    def __init__(self, text: str):
        self.text = text
        self.line_starts = [0]
        for i, char in enumerate(text):
            if char == '\n':
                self.line_starts.append(i + 1)

    def find(self, offset: int) -> tuple[int, int]:
        """Returns (line, column) for a given character offset."""
        if offset < 0:
            offset = 0
        if offset > len(self.text):
            offset = len(self.text)

        line_num = bisect_right(self.line_starts, offset)
        # line_num is 1-based. self.line_starts is 0-indexed.
        col_num = offset - self.line_starts[line_num - 1] + 1
        return line_num, col_num


# ==============================================================================
# 3. PARSE-TREE-TO-AST VISITOR
# ==============================================================================
def is_wrapped_leaf(rule_def):
    """
    Checks if a rule is a sequence of one item that is a literal or regex,
    and the item has no ast config of its own. This is a pattern used to
    prevent optimization of leaf-like rules that were normalized from inline
    definitions.
    """
    if 'sequence' in rule_def and len(rule_def['sequence']) == 1:
        child = rule_def['sequence'][0]
        if isinstance(child, dict) and ('literal' in child or 'regex' in child) and 'ast' not in child:
            return True
    return False

class AstBuilderVisitor(NodeVisitor):
    def __init__(self, grammar_dict: dict, finder: LineColumnFinder, tokens: list[Token] = None):
        self.grammar_dict = grammar_dict
        self.grammar_rules = grammar_dict['rules']
        self.finder = finder
        self.tokens = tokens
        self.token_idx = 0
        self.token_rule_names = set()
        if self.tokens:
            lexer_tokens = {spec['token'] for spec in grammar_dict['lexer']['tokens'] if 'token' in spec}
            lexer_tokens.update(['INDENT', 'DEDENT'])
            self.token_rule_names = lexer_tokens

    def get_pos(self, node, children):
        if self.tokens:
            if children:
                for child in children:
                    if isinstance(child, dict) and 'line' in child: return child['line'], child['col']
            return 1, 1
        return self.finder.find(node.start)

    def generic_visit(self, node, visited_children):
        rule_name = node.expr_name

        if self.tokens and rule_name in self.token_rule_names:
            if self.token_idx < len(self.tokens):
                token = self.tokens[self.token_idx]
                if token.type != rule_name:
                    raise ValueError(
                        f"Internal lexer/parser mismatch: expected token '{rule_name}' "
                        f"but got '{token.type}' at L{token.line}:C{token.col}"
                    )
                self.token_idx += 1

                spec_ast = {}
                for spec in self.grammar_dict.get('lexer', {}).get('tokens', []):
                    if spec.get('token') == token.type:
                        spec_ast = spec.get('ast', {})
                        break
                # If the token's own spec says to discard, skip it.
                if spec_ast.get('discard'):
                    return None

                base_node = {"tag": token.type,
                             "text": token.value,
                             "line": token.line,
                             "col": token.col}

                spec_type = spec_ast.get('type')
                if spec_type in ('number', 'bool', 'null'):
                    base_node['value'] = apply_type(token.value, spec_type)
                else:
                    base_node['value'] = token.value
                return base_node
            return None

        if rule_name not in self.grammar_rules:
            if isinstance(node.expr, Lookahead) or (not node.text and not visited_children): return None
            if isinstance(node.expr, Quantifier) and node.expr.max == 1:
                return visited_children[0] if visited_children else None
            if (isinstance(node.expr, Literal) or isinstance(node.expr, Regex)) and not self.tokens:
                tag = "literal" if isinstance(node.expr, Literal) else "regex"
                line, col = self.finder.find(node.start)
                return {"tag": tag, "text": node.text, "line": line, "col": col} if node.text else None
            return [c for c in visited_children if c is not None]

        rule_def = self.grammar_rules.get(rule_name, {})
        ast_config = rule_def.get('ast', {})
        if ast_config.get('discard'): return None
        
        children = [c for c in visited_children if c is not None]

        is_leaf_rule = ast_config.get('leaf') or \
                       (not self.tokens and ('literal' in rule_def or 'regex' in rule_def)) or \
                       is_wrapped_leaf(rule_def)

        if is_leaf_rule:
            line, col = self.get_pos(node, children)
            leaf_text = node.text
            if self.tokens and children:
                texts = [c['text'] for c in flatten(children) if isinstance(c, dict) and 'text' in c]
                if texts:
                    leaf_text = "".join(texts)
            base_node = {"tag": ast_config.get('tag', rule_name), "text": leaf_text, "line": line, "col": col}
            if 'type' in ast_config:
                base_node['value'] = apply_type(leaf_text, ast_config['type'])
            return base_node

        if ast_config.get('promote'):
            if isinstance(children, list):
                children = flatten(children)

            # Determine what to promote. Could be a single node, a list, or None.
            promoted_node = None
            if len(children) == 3 and \
               isinstance(children[0], dict) and children[0].get('tag') == 'literal' and \
               isinstance(children[2], dict) and children[2].get('tag') == 'literal':
                # This is a special case for `( expression )` style rules.
                promoted_node = children[1]
            else:
                is_sequence = 'sequence' in rule_def
                is_quantifier = 'one_or_more' in rule_def or 'zero_or_more' in rule_def or 'optional' in rule_def

                if is_sequence or is_quantifier:
                    # Promoted sequences and quantifiers always result in a list of children.
                    promoted_node = children
                elif not children:
                    promoted_node = None
                elif len(children) == 1:
                    # A choice or rule reference that results in one child.
                    promoted_node = children[0]
                else:
                    # A sequence that resulted in multiple children.
                    promoted_node = children

            if promoted_node is None:
                return None

            # Apply parent directives to the promoted result.
            if isinstance(promoted_node, dict):
                if 'tag' in ast_config:
                    promoted_node['tag'] = ast_config['tag']

                if ast_config.get('leaf') is True:
                    if 'children' in promoted_node:
                        del promoted_node['children']
                
                if 'type' in ast_config:
                    new_type = ast_config['type']
                    text = promoted_node.get('text')
                    try:
                        promoted_node['value'] = apply_type(text, new_type)
                    except (ValueError, TypeError):
                        promoted_node['value'] = text
                
                return promoted_node
            
            if isinstance(promoted_node, list):
                # If the parent has a tag, wrap the promoted list in a new node.
                # Other directives like `type` or `leaf` are not applicable to lists.
                if 'tag' in ast_config:
                    line, col = self.get_pos(node, children)
                    return {
                        "tag": ast_config['tag'],
                        "text": node.text,
                        "line": line,
                        "col": col,
                        "children": promoted_node
                    }

            return promoted_node

        structure_config = ast_config.get('structure')
        if isinstance(structure_config, str):
            if structure_config == 'left_associative_op':
                left = children[0]
                if len(children) < 2:
                    return left
                for group in children[1]:
                    clean_group = [item for item in group if item is not None]
                    if not clean_group: continue
                    op, right = clean_group[0], clean_group[1]
                    new_node = {"tag": "binary_op", "op": op, "left": left, "right": right, "line": op['line'], "col": op['col']}
                    left = new_node
                return left
            elif structure_config == 'right_associative_op':
                left = children[0]
                if len(children) < 2 or not children[1]: return left
                op_and_right_list = [item for item in children[1] if item is not None]
                if not op_and_right_list: return left
                op, right = op_and_right_list[0], op_and_right_list[1]
                new_node = {"tag": "binary_op", "op": op, "left": left, "right": right, "line": op['line'], "col": op['col']}
                return new_node
        elif isinstance(structure_config, dict):
            line, col = self.get_pos(node, children)
            new_node = {
                "tag": structure_config.get('tag', rule_name),
                "text": node.text,
                "line": line,
                "col": col,
                "children": {}
            }
            map_children_config = structure_config.get('map_children', {})
            # The direct children from the sequence are in a nested list.
            # Only unwrap **when it is the single element**, otherwise keep the
            # full list so we don't accidentally drop siblings that follow.
            child_nodes = visited_children[0] if len(visited_children) == 1 and isinstance(visited_children[0], list) else visited_children
            # A filtered view that omits placeholders such as None or empty lists.
            filtered_nodes = [c for c in child_nodes if c not in (None, [])]

            for name, mapping in map_children_config.items():
                idx = mapping['from_child']

                # Try to pick the element at the same ordinal position, but
                # fall-forward until we hit the next real node.  This makes
                # the mapping robust when optional / discarded parts are
                # omitted, so the remaining children “collapse” leftward.
                selected = None
                scan_idx = idx
                while scan_idx < len(child_nodes):
                    cand = child_nodes[scan_idx]
                    if cand not in (None, []):
                        selected = cand
                        break
                    scan_idx += 1

                if selected not in (None, []):
                    new_node['children'][name] = selected
            return new_node

        # Default node creation
        line, col = self.get_pos(node, children)
        base_node = {"tag": ast_config.get('tag', rule_name), "text": node.text, "line": line, "col": col}
        
        named_children = {}
        sequence_def = rule_def.get('sequence', [])
        
        child_producing_parts = []
        for part in sequence_def:
            is_lookahead = 'positive_lookahead' in part or 'negative_lookahead' in part
            if is_lookahead:
                continue

            is_discarded = False
            if 'ast' in part and part['ast'].get('discard'):
                is_discarded = True
            elif 'rule' in part:
                # If it's a rule reference, we must look up that rule's definition.
                ref_rule_def = self.grammar_rules.get(part['rule'], {})
                if ref_rule_def.get('ast', {}).get('discard'):
                    is_discarded = True

            if not is_discarded:
                child_producing_parts.append(part)

        # `children` is a list of the results from visiting each part of the sequence.
        # This list is parallel to the `child_producing_parts` list.
        for i, part in enumerate(child_producing_parts):
            if 'ast' in part and 'name' in part['ast']:
                child_name = part['ast']['name']
                # The i-th result in `children` corresponds to the i-th non-discarded rule.
                # If that result is a list (from a promoted rule), it's assigned as a list.
                if i < len(children):
                    named_children[child_name] = children[i]
                else: # Handle optional named children that didn't match
                    named_children[child_name] = []
        
        if named_children:
             base_node['children'] = named_children
        else:
             # This logic is for unnamed children, which should be flattened.
             unwrapped_children = children[0] if (children and isinstance(children[0], list) and len(children) == 1) else children
             if unwrapped_children is None or not unwrapped_children:
                base_node['children'] = []
             else:
                nodes_to_process = unwrapped_children if isinstance(unwrapped_children, list) else [unwrapped_children]
                base_node['children'] = flatten(nodes_to_process)

        return base_node

# ==============================================================================
# 4. AST-TO-STRING TRANSPILER
# ==============================================================================
class Transpiler:
    def __init__(self, transpile_grammar: dict = None):
        if transpile_grammar is None:
            transpile_grammar = {}
        transpiler_config = transpile_grammar.get('transpiler', {})
        self.transpile_rules = transpile_grammar.get('rules', {})
        self.indent_str = transpiler_config.get('indent', '    ')
        self.indent_level = 0
        self.state = {}

    @contextmanager
    def _indented(self, flag):
        if flag:
            self.indent_level += 1
        try:
            yield
        finally:
            if flag:
                self.indent_level -= 1

    def _get_path(self, path: str):
        try:
            return reduce(getitem, path.split('.'), self.state)
        except (KeyError, TypeError):
            return None

    def _set_path(self, path: str, value):
        keys = path.split('.')
        d = self.state
        for key in keys[:-1]:
            d = d.setdefault(key, {})
        d[keys[-1]] = value

    def _resolve_path_in_context(self, path: str, context: dict):
        """Resolves a dot-notation path against a context dictionary."""
        try:
            return reduce(getitem, path.split('.'), context)
        except (KeyError, TypeError, AttributeError):
            return None

    def _evaluate_condition(self, condition_dict: dict, context: dict) -> bool:
        """Evaluates a condition defined as a dictionary."""
        if 'path' not in condition_dict:
            raise ValueError(f"Condition must have a 'path' key: {condition_dict}")

        path_template = condition_dict['path']
        path = path_template.format(**context)
        actual_val = self._resolve_path_in_context(path, context)

        result = False
        if 'equals' in condition_dict:
            # Equality check
            expected_val = condition_dict['equals']
            result = str(actual_val) == str(expected_val)
        else:
            # Existence check
            result = bool(actual_val)

        if condition_dict.get('negate', False):
            return not result
        return result

    def transpile(self, node: dict) -> str:
        if not isinstance(node, dict) or 'tag' not in node:
            raise ValueError("Transpilation must start from a valid AST node.")
        self.indent_level = 0
        self.state = {}
        out = self._transpile_node(node)
        return out

    def _transpile_node(self, node):
        if isinstance(node, list):
            return " ".join(self._transpile_node(n) for n in node if n not in (None, []))

        if not isinstance(node, dict):
            return str(node or "")
        
        transpile_config = self.transpile_rules.get(node.get('tag'), {})
        
        output = ""
        with self._indented(transpile_config.get('indent')):
            current_indent = self.indent_str * self.indent_level

            # Prepare substitutions once for use in conditions, templates, and state_set
            subs = {}
            children = node.get('children', [])
            if isinstance(children, dict):
                for name, child in children.items():
                    subs[name] = self._transpile_node(child)
            elif isinstance(children, list):
                joiner = transpile_config.get('join_children_with', ' ')
                if '\n' in joiner:
                    joiner = joiner.replace('\n', '\n' + current_indent)
                child_strings = [self._transpile_node(c) for c in children]
                child_strings = [s for s in child_strings if s]  # drop blanks
                joined = joiner.join(child_strings)
                if transpile_config.get('indent') and joined:
                    joined = current_indent + joined
                subs['children'] = joined
            
            if 'op' in node: subs['op'] = self._transpile_node(node['op'])
            if 'left' in node: subs['left'] = self._transpile_node(node['left'])
            if 'right' in node: subs['right'] = self._transpile_node(node['right'])

            template = None
            # Check for the new 'cases' structure first.
            if 'cases' in transpile_config:
                # The full context for evaluation has access to the raw node, state, and transpiled children
                context = {'node': node, 'state': self.state, **subs}
                
                for case in transpile_config['cases']:
                    if 'if' in case:
                        if self._evaluate_condition(case['if'], context):
                            template = case['then']
                            break
                    elif 'default' in case:
                        template = case['default']
                        break
            elif 'template' in transpile_config:
                template = transpile_config['template']
            
            if template is not None:
                try:
                    output = template.format(**subs)
                except KeyError as ke:
                    raise ValueError(f"Missing placeholder '{ke.args[0]}' in template for tag '{node.get('tag')}'")
            elif transpile_config.get('use') == 'value':
                output = str(node.get('value', ''))
            elif transpile_config.get('use') == 'text':
                output = node['text']
            elif 'value' in transpile_config:
                output = transpile_config['value']
            else:
                if 'value' in node:
                    output = str(node['value'])
                elif 'text' in node:
                    output = node['text']
                else:
                    raise ValueError(f"Don't know how to transpile node: {node}")
            
            # After producing output, update state for subsequent nodes.
            if 'state_set' in transpile_config:
                for key_template, value in transpile_config['state_set'].items():
                    try:
                        final_key = key_template.format(**subs)
                    except KeyError as ke:
                        raise ValueError(f"Missing placeholder '{ke.args[0]}' in state_set key for tag '{node.get('tag')}'")
                    final_value = value
                    if isinstance(value, str):
                        try:
                            final_value = value.format(**subs)
                        except KeyError as ke:
                            raise ValueError(f"Missing placeholder '{ke.args[0]}' in state_set value for tag '{node.get('tag')}'")
                    self._set_path(final_key, final_value)
            return output

# ==============================================================================
# 5. MAIN PARSER CLASS
# ==============================================================================

# ==============================================================================
# 5. PARSER CORE & IMPLEMENTATIONS
# ==============================================================================

class _ParserCore:
    """
    A base class containing common logic for parsing, grammar compilation,
    and linting. Not intended for direct use.
    """
    def _compile_grammar_from_dict(self, grammar_dict, lint=True):
        config = {}
        config['grammar_dict'] = self._normalize_grammar(grammar_dict)
        external_refs = config['grammar_dict'].pop('_external_refs', [])
        config['is_token_grammar'] = 'lexer' in config['grammar_dict']
        if lint:
            self._lint_grammar(config['grammar_dict'], external_refs=external_refs)
        
        if config['is_token_grammar']:
            config['lexer'] = StatefulLexer(config['grammar_dict']['lexer'])
        
        config['grammar_string'] = transpile_grammar(config['grammar_dict'])
        try:
            config['grammar'] = Grammar(config['grammar_string'])
        except LeftRecursionError as e:
            raise ValueError(f"Left-recursion detected in grammar. Parsimonious error: {e}") from e
        except UndefinedLabel as e:
            label_match = re.search(r'The label "([^"]+)"', str(e))
            missing_rule = label_match.group(1) if label_match else "unknown"
            raise ValueError(f"Rule '{missing_rule}' is not defined in grammar.") from e
        except VisitationError as e:
            # Check for circular reference, which parsimonious reports as BadGrammar
            if isinstance(e.__cause__, BadGrammar) and "Circular Reference" in str(e.__cause__):
                raise ValueError(f"Left-recursion detected in grammar. Parsimonious error: {e}") from e
            
            if isinstance(e.__cause__, KeyError):
                missing_rule = e.__cause__.args[0]
                raise ValueError(f"Rule '{missing_rule}' is not defined in grammar.") from e
            
            raise ValueError(f"Error during grammar compilation. Parsimonious error: {e}") from e
        config['start_rule'] = config['grammar_dict'].get('start_rule', 'start')
        
        return config

    def _get_expected_from_error(self, error, grammar_config):
        """Builds a set of human-readable expected things from a ParseError."""
        expected_things = set()
        # Normalize across Parsimonious versions: prefer error.exprs, then error.expr, then error.expressions
        exprs = []
        if hasattr(error, 'exprs') and error.exprs:
            exprs = list(error.exprs)
        elif hasattr(error, 'expr') and error.expr:
            exprs = [error.expr]
        elif hasattr(error, 'expressions') and error.expressions:
            exprs = list(error.expressions)
        if not exprs:
            return expected_things

        grammar = grammar_config['grammar']
        is_token_grammar = grammar_config.get('is_token_grammar', False)
        
        # Build a reverse map from Parsimonious expression objects to our rule names
        expression_map = {v: k for k, v in grammar.items()}

        visited = set()

        def _collect_expected(expr):
            # Avoid revisiting the same expression node
            if expr in visited:
                return
            visited.add(expr)

            if not is_token_grammar:
                # Literal leaf
                if isinstance(expr, Literal) and getattr(expr, 'literal', None):
                    expected_things.add(f'literal "{expr.literal}"')

                # Regex leaf (handle different parsimonious internals)
                elif isinstance(expr, Regex):
                    pattern = getattr(expr, 'pattern', None)
                    if not pattern:
                        re_obj = getattr(expr, 're', None)
                        if hasattr(re_obj, 'pattern'):
                            pattern = re_obj.pattern
                    if not pattern:
                        pattern = getattr(expr, 'regexp', None)
                    if pattern:
                        expected_things.add(f'regex matching r"{pattern}"')

            # Recurse into common composite expression containers
            members = getattr(expr, 'members', None)
            if members:
                for m in members:
                    _collect_expected(m)

            # Also attempt common single-child attributes used by parsimonious nodes
            for attr in ('element', 'member', 'expr', 'expression', 'term'):
                child = getattr(expr, attr, None)
                if child is not None and child is not expr:
                    _collect_expected(child)

            # Generic deep crawl: inspect attributes that are expressions or containers of expressions
            try:
                for v in vars(expr).values():
                    if v is None:
                        continue
                    if isinstance(v, Expression):
                        _collect_expected(v)
                    elif isinstance(v, (list, tuple, set)):
                        for item in v:
                            if isinstance(item, Expression):
                                _collect_expected(item)
            except Exception:
                # Some parsimonious nodes may not expose __dict__ or may raise during vars()
                pass

        for expr in exprs:
            if expr in expression_map:
                rule_name = expression_map[expr]
                # Don't show internal, normalized rule names to the user
                if "__" not in rule_name:
                    expected_things.add(rule_name)
            # Always descend to find nested literal/regex expectations
            _collect_expected(expr)
        
        return expected_things

    def _lint_grammar(self, grammar_dict, external_refs=None):
        """
        Performs static analysis on the grammar to find common issues like
        unreachable rules.
        """
        self._check_for_unreachable_rules(grammar_dict, external_refs=external_refs or [])
        self._check_for_always_empty_rules(grammar_dict)


        for rule_name, rule_def in grammar_dict.get('rules', {}).items():
            ast_config = rule_def.get('ast', {})
            if not isinstance(ast_config, dict): continue

            has_promote = ast_config.get('promote', False)
            has_structure = 'structure' in ast_config
            has_discard = ast_config.get('discard', False)

            if has_promote and has_structure:
                raise ValueError(f"In rule '{rule_name}': 'promote' and 'structure' directives are mutually exclusive.")
            
            if has_promote and has_discard:
                raise ValueError(f"In rule '{rule_name}': 'promote: true' is redundant when 'discard: true' is also present.")

    def _lint_leaf_subgrammar_conflict(self, grammar_dict):
        """
        Checks for the mutually exclusive combination of `leaf: true` and
        the `subgrammar` directive within a rule. This check must be run
        before subgrammars are resolved and replaced.
        """
        for rule_name, rule_def in grammar_dict.get('rules', {}).items():
            ast_config = rule_def.get('ast', {})
            if not isinstance(ast_config, dict): continue

            is_leaf = ast_config.get('leaf', False)
            if is_leaf:
                # Helper to find subgrammar directives recursively
                def has_subgrammar_directive(node):
                    if isinstance(node, dict):
                        if 'subgrammar' in node:
                            return True
                        for key, value in node.items():
                            if key != 'ast' and has_subgrammar_directive(value):
                                return True
                    elif isinstance(node, list):
                        for item in node:
                            if has_subgrammar_directive(item):
                                return True
                    return False
                
                if has_subgrammar_directive(rule_def):
                    raise ValueError(f"Rule '{rule_name}' is defined as a 'leaf' node but contains a 'subgrammar' directive. These are mutually exclusive.")

    def _check_for_unreachable_rules(self, grammar_dict, external_refs=None):
        """
        Checks for rules that are defined in the grammar but can never be
        reached from the start_rule.
        """
        if external_refs is None:
            external_refs = []

        all_rules = set(grammar_dict['rules'].keys())
        start_rule = grammar_dict.get('start_rule', 'start')
        if start_rule not in all_rules:
            # This will be caught later by parsimonious, but it prevents
            # the linter from running on an invalid start_rule.
            return

        def find_references(rule_def):
            """Recursively find all rule references in a definition."""
            refs = set()
            if isinstance(rule_def, dict):
                if 'rule' in rule_def:
                    refs.add(rule_def['rule'])
                for value in rule_def.values():
                    refs.update(find_references(value))
            elif isinstance(rule_def, list):
                for item in rule_def:
                    refs.update(find_references(item))
            return refs

        reachable = set()
        queue = [start_rule] + external_refs
        
        while queue:
            current_rule = queue.pop(0)
            if current_rule in reachable:
                continue
            
            reachable.add(current_rule)
            
            if current_rule not in grammar_dict['rules']:
                # This indicates a reference to a non-existent rule.
                # Parsimonious will catch this with a better error message, so we
                # can abort the unreachability check and let that error surface.
                return

            rule_definition = grammar_dict['rules'][current_rule]
            references = find_references(rule_definition)
            
            for ref in references:
                if ref not in reachable:
                    queue.append(ref)
        
        unreachable = all_rules - reachable
        # Filter out internal, normalized rules from the final report
        unreachable = {rule for rule in unreachable if "__" not in rule}

        if unreachable:
            raise ValueError(f"Unreachable rules detected: {', '.join(sorted(list(unreachable)))}")

    def _is_def_always_empty(self, rule_def, memo, grammar_dict):
        if not isinstance(rule_def, dict):
            return False

        ast_config = rule_def.get('ast', {})
        if ast_config.get('discard'): return True
        if 'structure' in ast_config: return False

        if 'rule' in rule_def: return self._is_rule_always_empty(rule_def['rule'], memo, grammar_dict)
        
        if grammar_dict.get('lexer') and 'token' in rule_def:
            token_type = rule_def['token']
            for spec in grammar_dict.get('lexer', {}).get('tokens', []):
                if spec.get('token') == token_type:
                    return spec.get('action') == 'skip' or spec.get('ast', {}).get('discard', False)
            return False

        if 'literal' in rule_def or 'regex' in rule_def or ast_config.get('leaf'):
            return False

        if 'positive_lookahead' in rule_def or 'negative_lookahead' in rule_def:
            return True
        
        if 'choice' in rule_def:
            return all(self._is_def_always_empty(alt, memo, grammar_dict) for alt in rule_def['choice'])

        if 'sequence' in rule_def:
            if any(isinstance(part, dict) and 'name' in part.get('ast', {}) for part in rule_def['sequence']):
                return False
            return all(self._is_def_always_empty(part, memo, grammar_dict) for part in rule_def['sequence'])

        for quantifier in ['one_or_more', 'zero_or_more', 'optional']:
            if quantifier in rule_def:
                return self._is_def_always_empty(rule_def[quantifier], memo, grammar_dict)

        return False

    def _is_rule_always_empty(self, rule_name, memo, grammar_dict):
        if rule_name in memo:
            return memo[rule_name]
        
        if rule_name not in grammar_dict['rules']:
            return False

        memo[rule_name] = False
        
        rule_def = grammar_dict['rules'][rule_name]
        is_empty = self._is_def_always_empty(rule_def, memo, grammar_dict)
        
        memo[rule_name] = is_empty
        return is_empty

    def _check_for_always_empty_rules(self, grammar_dict):
        """
        Checks for rules that are not explicitly 'discard' but will always
        produce an empty AST node due to their structure.
        """
        memo = {}
        implicitly_empty_rules = []
        for rule_name, rule_def in grammar_dict['rules'].items():
            if rule_def.get('ast', {}).get('discard'):
                continue
            
            is_lookahead_rule = 'positive_lookahead' in rule_def or 'negative_lookahead' in rule_def
            if is_lookahead_rule:
                continue
            
            if self._is_rule_always_empty(rule_name, memo, grammar_dict):
                implicitly_empty_rules.append(rule_name)
        
        if implicitly_empty_rules:
            raise ValueError(
                "The following rules will always produce an empty AST node, which may be unintentional. "
                "If this is intended, add `ast: { discard: true }` to the rule definition. "
                f"Rules: {', '.join(sorted(implicitly_empty_rules))}"
            )

    def _normalize_grammar(self, grammar_dict: dict):
        """
        Recursively walks the grammar and gives names to any anonymous
        (inline) rule definitions that have an `ast` block. This is
        necessary so that the AstBuilderVisitor can find the `ast` config
        for these rules by name.
        """
        # Deep copy to avoid modifying the user's original dict
        new_grammar = deepcopy(grammar_dict)
        rules = new_grammar.get('rules', {})

        def is_inline_def_with_ast(d):
            if not isinstance(d, dict) or 'ast' not in d:
                return False

            # An inline definition that ONLY specifies a name is for structuring the parent,
            # not for creating a new named anonymous rule.
            if list(d['ast'].keys()) == ['name']:
                return False
            
            # An inline definition cannot be a rule reference.
            if 'rule' in d:
                return False

            rule_keys = {
                'literal', 'regex', 'choice', 'sequence', 'zero_or_more', 
                'one_or_more', 'optional', 'positive_lookahead', 'negative_lookahead',
                'token'            # allow inline token defs with their own ast block
            }
            # It must contain one of the core grammar keys.
            return any(key in d for key in rule_keys)

        def walker(node, base_name, counter):
            if isinstance(node, list):
                for i, item in enumerate(node):
                    if is_inline_def_with_ast(item):
                        counter[0] += 1
                        new_rule_name = f"{base_name}__{counter[0]}"
                        ast_config = item.pop('ast')
                        rules[new_rule_name] = {
                            'ast': ast_config,
                            'sequence': [item]
                        }
                        node[i] = {'rule': new_rule_name}
                    else:
                        walker(item, base_name, counter)
            elif isinstance(node, dict):
                # Hoist inline ast from a single-item sequence onto the parent rule, if parent has no ast
                if 'sequence' in node and isinstance(node['sequence'], list) and len(node['sequence']) == 1:
                    only = node['sequence'][0]
                    if is_inline_def_with_ast(only) and 'ast' not in node:
                        ast_config = only.pop('ast')
                        node['ast'] = ast_config

                for key, value in list(node.items()):
                    if key in ['ast', 'transpile']:
                        continue

                    if is_inline_def_with_ast(value):
                        counter[0] += 1
                        new_rule_name = f"{base_name}__{counter[0]}"
                        ast_config = value.pop('ast')
                        rules[new_rule_name] = {
                            'ast': ast_config,
                            'sequence': [value]
                        }
                        node[key] = {'rule': new_rule_name}
                    else:
                        walker(value, base_name, counter)

        # Start walking from inside each of the top-level rule definitions
        rules_map = new_grammar.get('rules', {})
        processed_rules = set()

        while True:
            # Find rules that haven't been processed yet.
            # This is necessary because the walker can add new rules to the map.
            rules_to_process = {name: rule for name, rule in rules_map.items() if name not in processed_rules}
            if not rules_to_process:
                break # No new rules to process, we are done.

            for name, rule_def in rules_to_process.items():
                # Use a mutable list for the counter to pass by reference
                walker(rule_def, name, [0])
                processed_rules.add(name)
        return new_grammar

    def _cleanup_ast(self, node):
        """
        A post-processing step to recursively remove any internal nodes (`__` in tag)
        that may have been incorrectly generated. Returns a cleaned version of the node.
        """
        if isinstance(node, dict):
            # Fast-path: leaf AST node without children and not an internal tag
            if 'tag' in node and 'children' not in node and '__' not in node.get('tag', ''):
                return node
        if isinstance(node, list):
            # Build a new list containing cleaned children.
            new_list = []
            for item in node:
                # If the item itself has an internal tag, filter it out.
                if isinstance(item, dict) and '__' in item.get('tag', ''):
                    continue
                # Otherwise, clean the item and add it to the new list.
                new_list.append(self._cleanup_ast(item))
            return new_list

        if isinstance(node, dict):
            # If the node is an AST node (has a 'tag'), clean its children.
            if 'tag' in node:
                new_node = node.copy()
                if 'children' in new_node:
                    new_node['children'] = self._cleanup_ast(new_node['children'])
                return new_node
            # Otherwise, it's a dictionary of named children. Clean its values.
            else:
                new_dict = {}
                for key, value in node.items():
                    if isinstance(value, dict) and '__' in value.get('tag', ''):
                        continue
                    new_dict[key] = self._cleanup_ast(value)
                return new_dict

        # Primitive values are returned as-is.
        return node

    def _parse_internal(self, text: str, grammar_config: dict, start_rule: str):
        config = grammar_config
        start_rule = start_rule if start_rule is not None else config['start_rule']
        finder = LineColumnFinder(text)
        tokens = None
        
        try:
            if config.get('is_token_grammar'):
                tokens = config['lexer'].tokenize(text)
                token_string = " ".join([t.type for t in tokens])
                visitor = AstBuilderVisitor(config['grammar_dict'], finder, tokens)
                tree = config['grammar'][start_rule].parse(token_string)
            else:
                visitor = AstBuilderVisitor(config['grammar_dict'], finder)
                tree = config['grammar'][start_rule].parse(text)
            
            ast = visitor.visit(tree)
            ast = self._cleanup_ast(ast)
            return {"status": "success", "ast": ast}

        except (ParseError, IncompleteParseError, SyntaxError, IndentationError) as e:
            if isinstance(e, (ParseError, IncompleteParseError)) and config.get('is_token_grammar'):
                # Find the token corresponding to the error position in the token string
                if tokens is None:
                    # This can happen if the lexer fails before tokenization is complete
                    return {"status": "error", "message": str(e)}
                
                error_token = None
                
                # Recalculate token_string as it's not available in this scope
                token_string = " ".join([t.type for t in tokens])
                # The number of spaces before the error position corresponds to the token index.
                # This is more robust than splitting the string.
                error_token_idx = token_string[:e.pos].count(' ')
                
                if error_token_idx < len(tokens):
                    error_token = tokens[error_token_idx]
                    line, col = error_token.line, error_token.col
                    message = f"Syntax error in input text at L{line}:C{col}. Unexpected token '{error_token.type}' ('{error_token.value}') while parsing rule '{start_rule}'"
                else:  # Error at end of input
                    if tokens:
                        last_token = tokens[-1]
                        line, col = last_token.line, last_token.col + len(last_token.value)
                    else:
                        # No tokens were produced. The error is at the end of the text.
                        line, col = finder.find(len(text))
                    message = f"Syntax error in input text at L{line}:C{col}. Unexpected end of input while parsing rule '{start_rule}'"
                
                expected_things = self._get_expected_from_error(e, config)
                if expected_things:
                    message += f" Expected one of: {', '.join(sorted(list(expected_things)))}"
                
                return {"status": "error", "message": message}
            elif isinstance(e, (ParseError, IncompleteParseError)):
                line, col = finder.find(e.pos)
                
                if isinstance(e, IncompleteParseError):
                    snippet = text[e.pos:e.pos+20].split('\n')[0]
                    message = f"Parse Error in input text at L{line}:C{col}. Rule '{start_rule}' parsed successfully, but failed to consume the entire input. Unconsumed text begins with: '{snippet}...'"
                else: # It's a ParseError
                    snippet = text[e.pos:e.pos+20].split('\n')[0]
                    message = f"Syntax error in input text at L{line}:C{col} while parsing rule '{start_rule}'"
                    
                    expected_things = self._get_expected_from_error(e, config)

                    if snippet == "":
                        contextual_text = text if len(text) < 40 else text[:37] + "..."
                        message += f". Unexpected end of input while parsing '{contextual_text}'"
                    else:
                        if expected_things:
                            message += f". Expected one of: {', '.join(sorted(list(expected_things)))}"
                            message += f", but found text starting with: '{snippet}...'"
                        else:
                            message += f" near text: '{snippet}...'"

                return {"status": "error", "message": message}
            else: # SyntaxError or IndentationError from our lexer
                 return {"status": "error", "message": str(e)}

    def _replace_subgrammars_with_placeholders(self, node):
        """
        Recursively walks a grammar tree and replaces any `subgrammar`
        definitions with their `placeholder` content.
        """
        visited_nodes = set()
        def placeholder_walker(node):
            node_id = id(node)
            if node_id in visited_nodes: return
            visited_nodes.add(node_id)

            if isinstance(node, list):
                for i, item in enumerate(node):
                    if isinstance(item, dict) and 'subgrammar' in item:
                        subgrammar_config = item['subgrammar']
                        placeholder_def = subgrammar_config.get('placeholder', {'sequence': []})
                        new_item = item.copy()
                        del new_item['subgrammar']
                        new_item.update(placeholder_def)
                        node[i] = new_item
                    else:
                        placeholder_walker(item)
            elif isinstance(node, dict):
                if 'subgrammar' in node:
                    subgrammar_config = node['subgrammar']
                    placeholder_def = subgrammar_config.get('placeholder', {'sequence': []})
                    del node['subgrammar']
                    node.update(placeholder_def)
                    return

                for key, value in node.items():
                    if key in ('ast', 'transpile'): continue
                    placeholder_walker(value)
        
        placeholder_walker(node)



class PlaceholderParser(_ParserCore):
    """
    A parser that operates on a single grammar definition, replacing any
    `subgrammar` directives with their specified placeholders. It does not
    load or process any `includes` or `subgrammar` files.

    This is useful for structurally validating or testing a single grammar
    file in isolation without its dependencies.
    """
    @classmethod
    def from_file(cls, filepath: str):
        """Loads a grammar from a YAML file for placeholder parsing."""
        with open(filepath, 'r') as f:
            raw = yaml.safe_load(f) or {}
            grammar_dict = sanitize_to_json_data(raw)
        return cls(grammar_dict)

    def __init__(self, grammar_dict: dict):
        """
        Initializes the placeholder parser with a grammar dictionary.
        """
        grammar_dict = sanitize_to_json_data(grammar_dict)
        config_dict = deepcopy(grammar_dict)

        # In placeholder mode, we do not process subgrammars from files.
        
        # Replace subgrammar directives with their placeholders
        rules = config_dict.get('rules', {})
        self._replace_subgrammars_with_placeholders(rules)

        # Linting is disabled because the grammar is incomplete by design,
        # which would lead to "unreachable rule" errors.
        self.grammar_config = self._compile_grammar_from_dict(config_dict, lint=False)

    def parse(self, text: str, start_rule: Optional[str] = None) -> dict:
        """
        Parses the input text using a structural-only version of the grammar
        with placeholders for subgrammars.

        :param text: The source text to parse.
        :param start_rule: An optional rule name to begin parsing from. If
                           not provided, the grammar's default `start_rule`
                           is used.
        """
        return self._parse_internal(text, self.grammar_config, start_rule)
    
    def validate(self, text: str) -> tuple[bool, str]:
        result = self.parse(text)
        if result['status'] == 'success':
            return True, 'success'
        else:
            return False, result['message']


class Parser(_ParserCore):
    """
    The main entry point that orchestrates the parsing process, including
    loading and resolving `includes` and `subgrammar` directives.
    """
    @classmethod
    def from_file(cls, filepath: str):
        """Loads a grammar from a main YAML file."""
        # Resolve the filepath to get an absolute path. This ensures that
        # subgrammars with relative paths are resolved correctly, regardless
        # of the current working directory.
        filepath_path = Path(filepath).resolve()
        with open(filepath_path, 'r') as f:
            raw = yaml.safe_load(f) or {}
            grammar_dict = sanitize_to_json_data(raw)
        # The base path for includes/subgrammars is relative to the grammar file.
        return cls(grammar_dict, base_path=filepath_path.parent)

    def __init__(self, grammar_dict: dict, base_path: Path = None):
        """
        Initializes the parser with a grammar dictionary.

        :param grammar_dict: The grammar definition as a dictionary.
        :param base_path: The base path for resolving relative `includes` and
                          `subgrammar` file paths. **Important**: If your grammar
                          uses `subgrammar` directives with relative paths, you
                          **must** provide the base path. The recommended way to do
                          this is to use `Parser.from_file("path/to/grammar.yaml")`,
                          which handles this automatically. If you load the grammar
                          manually, you must pass the path to its parent directory,
                          e.g., `Parser(my_grammar, base_path="path/to/")`.
                          If omitted, paths will be resolved relative to the
                          current working directory, which can lead to errors.
        """
        grammar_dict = sanitize_to_json_data(grammar_dict)

        if base_path is None:
            base_path = Path.cwd()
        else:
            # Ensure the provided base path is absolute to prevent ambiguity
            # when resolving subgrammar paths.
            base_path = Path(base_path).resolve()

        unified_grammar = self._build_unified_grammar(grammar_dict, base_path)
        self.full_grammar = self._compile_grammar_from_dict(unified_grammar)

    def _get_namespace(self, path: Path) -> str:
        if path.name == "_.yaml":
            return None # Main grammar has no namespace
        stem = path.stem
        return "".join(word.capitalize() for word in stem.replace('-', '_').split('_'))

    def _build_unified_grammar(self, initial_grammar_dict: dict, initial_base_path: Path) -> dict:
        # 1. Discover all grammars recursively.
        grammars = {}
        main_path_key = (initial_base_path / "_.yaml")
        queue = [(main_path_key, initial_grammar_dict)]
        processed_paths = set()

        while queue:
            current_path, grammar_content = queue.pop(0)
            if current_path in processed_paths: continue
            processed_paths.add(current_path)

            grammars[current_path] = grammar_content
            self._lint_leaf_subgrammar_conflict(grammar_content)
            deps = self._get_subgrammar_dependencies(grammar_content.get('rules', {}))

            for dep in deps:
                sub_file = dep['subgrammar']['file']
                # Subgrammars are resolved relative to the file they are defined in.
                sub_path = (current_path.parent / sub_file).resolve()
                if sub_path not in processed_paths:
                    with open(sub_path, 'r') as f:
                        raw = yaml.safe_load(f) or {}
                        content = sanitize_to_json_data(raw)
                        queue.append((sub_path, content))
        
        # Guard against duplicate namespaces across different files
        ns_to_path = {}
        for path in grammars.keys():
            ns = self._get_namespace(path)
            if not ns:
                continue
            prev = ns_to_path.get(ns)
            if prev and prev != path:
                raise ValueError(
                    f"Namespace collision: files '{prev}' and '{path}' resolve to the same namespace '{ns}'. "
                    "Please rename one of them to avoid rule name conflicts."
                )
            ns_to_path[ns] = path

        # 2. Collect all rules, namespacing subgrammars.
        unified_rules = {}
        all_local_rules = {}
        for path, content in grammars.items():
            namespace = self._get_namespace(path)
            rules_to_add = content.get('rules', {})
            all_local_rules[path] = set(rules_to_add.keys())
            if namespace:
                for rule_name, rule_def in rules_to_add.items():
                    unified_rules[f"{namespace}_{rule_name}"] = deepcopy(rule_def)
            else:
                unified_rules.update({k: deepcopy(v) for k, v in rules_to_add.items()})
        
        # 3. Rewrite all references now that all rules are collected.
        rules_copy = deepcopy(unified_rules)
        subgrammar_entry_points = set()
        # Iterate over a copy of keys to allow modification of the dictionary during iteration.
        for rule_name in list(rules_copy.keys()):
            rule_def = rules_copy[rule_name]
            original_path = None
            if rule_name in initial_grammar_dict.get('rules', {}):
                 original_path = main_path_key
            else:
                namespace_part = rule_name.split('_')[0]
                for p in grammars:
                    if self._get_namespace(p) == namespace_part:
                        original_path = p
                        break
            
            if original_path:
                local_rules = all_local_rules[original_path]
                current_namespace = self._get_namespace(original_path)
                self._rewrite_rule_references(rule_def, current_namespace, local_rules)
                rules_copy[rule_name] = self._rewrite_subgrammar_directives_in_place(rule_def, original_path.parent, subgrammar_entry_points)
        
        final_grammar = initial_grammar_dict.copy()
        final_grammar['rules'] = rules_copy
        
        # Collect all start rules from all grammars to treat them as valid entry points.
        all_start_rules = set()
        for path, content in grammars.items():
            if 'start_rule' in content:
                namespace = self._get_namespace(path)
                start_rule = content['start_rule']
                if namespace:
                    all_start_rules.add(f"{namespace}_{start_rule}")
                else:
                    all_start_rules.add(start_rule)

        all_external_refs = subgrammar_entry_points.union(self._get_all_qualified_references(rules_copy)).union(all_start_rules)
        final_grammar['_external_refs'] = list(all_external_refs)
        if 'start_rule' not in final_grammar:
             raise ValueError("The main grammar must have a 'start_rule'")
             
        return final_grammar

    def _rewrite_rule_references(self, node, namespace, local_rules):
        if isinstance(node, list):
            for i, item in enumerate(node):
                node[i] = self._rewrite_rule_references(item, namespace, local_rules)
        elif isinstance(node, dict):
            if 'rule' in node:
                ref_name = node['rule']
                if namespace and ref_name in local_rules:
                    node['rule'] = f"{namespace}_{ref_name}"

            for key, value in node.items():
                if key not in ['ast', 'subgrammar', 'transpile']:
                    node[key] = self._rewrite_rule_references(value, namespace, local_rules)
        return node

    def _rewrite_subgrammar_directives_in_place(self, node, base_path, subgrammar_entry_points):
        if isinstance(node, list):
            for i, item in enumerate(node):
                replacement = self._rewrite_subgrammar_directives_in_place(item, base_path, subgrammar_entry_points)
                if replacement is not item:
                    node[i] = replacement
        elif isinstance(node, dict):
            if 'subgrammar' in node:
                sub_config = node['subgrammar']
                sub_file_str = sub_config['file']
                sub_path = (base_path / sub_file_str).resolve()
                sub_namespace = self._get_namespace(sub_path)
                
                with open(sub_path, 'r') as f:
                    raw = yaml.safe_load(f) or {}
                    sub_content = sanitize_to_json_data(raw)

                start_rule = sub_config.get('rule') or sub_content.get('start_rule')
                if not start_rule:
                    raise ValueError(f"Subgrammar '{sub_file_str}' must have a 'start_rule' or a 'rule' must be specified.")
                
                qualified_start_rule = f"{sub_namespace}_{start_rule}"
                subgrammar_entry_points.add(qualified_start_rule)

                new_rule_ref = {'rule': qualified_start_rule}
                original_item = node.copy()
                del original_item['subgrammar']
                new_rule_ref.update(original_item)
                return new_rule_ref
            
            for key, value in node.items():
                if key not in ['ast', 'transpile']:
                    replacement = self._rewrite_subgrammar_directives_in_place(value, base_path, subgrammar_entry_points)
                    if replacement is not value:
                        node[key] = replacement
        return node

    def _get_all_qualified_references(self, rules_to_scan: dict):
        """Recursively finds all qualified rule references (e.g., Sub_rule)."""
        refs = set()
        visited_nodes = set()

        def find_refs(node):
            node_id = id(node)
            if node_id in visited_nodes: return
            visited_nodes.add(node_id)

            if isinstance(node, list):
                for item in node: find_refs(item)
            elif isinstance(node, dict):
                if 'rule' in node:
                    ref_name = node['rule']
                    if re.match(r'[A-Z][a-zA-Z0-9]*_', ref_name):
                        refs.add(ref_name)
                for key, value in node.items():
                    if key not in ['ast', 'transpile']:
                        find_refs(value)
        
        find_refs(rules_to_scan)
        return refs

    def _get_subgrammar_dependencies(self, rules_to_scan: dict):
        """Recursively finds all subgrammar directives in a set of rules."""
        subgrammar_items = []
        
        # A set to keep track of nodes we've already visited to avoid infinite loops
        # with self-referential rule structures (which are valid in Koine).
        visited_nodes = set()

        def find_subgrammars(node):
            # Use object ID to handle mutable dicts/lists correctly.
            node_id = id(node)
            if node_id in visited_nodes:
                return
            visited_nodes.add(node_id)

            if isinstance(node, list):
                for item in node:
                    find_subgrammars(item)
            elif isinstance(node, dict):
                if 'subgrammar' in node:
                    subgrammar_items.append(node)
                else:
                    for key, value in node.items():
                        # Don't descend into `ast` blocks.
                        if key not in ['ast', 'transpile']:
                            find_subgrammars(value)
        
        find_subgrammars(rules_to_scan)
        return subgrammar_items


    def parse(self, text: str, start_rule: Optional[str] = None) -> dict:
        """
        Parses the input text using the full grammar, resolving subgrammars.

        :param text: The source text to parse.
        :param start_rule: An optional rule name to begin parsing from. If
                           not provided, the grammar's default `start_rule`
                           is used.
        """
        return self._parse_internal(text, self.full_grammar, start_rule)

    def validate(self, text: str) -> tuple[bool, str]:
        result = self.parse(text)
        if result['status'] == 'success':
            return True, 'success'
        else:
            return False, result['message']
