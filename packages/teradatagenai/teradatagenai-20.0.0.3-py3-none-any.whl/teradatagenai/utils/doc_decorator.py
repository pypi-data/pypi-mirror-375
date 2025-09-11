"""
Unpublished work.
Copyright (c) 2025 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner: Sushant.Mhambrey@Teradata.com
               PankajVinod.Purandare@Teradata.com

This file implements the decorator to append common parameters to function docstrings.
"""

import inspect
import re
import textwrap
from functools import wraps
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
)

# -------------------------------------------------------------------
# Helpers for emitting structured parameter blocks & notes
# -------------------------------------------------------------------

_LIST_MARKER_RE = re.compile(r"^(\*|\+|\-|\d+\.|[a-zA-Z]\.)\s")
_SECTION_HEADER_RE = re.compile(r"^\s*([A-Z][A-Z _]+?)\s*:?\s*$", re.MULTILINE)


def _emit_structured_block(
    label: str,
    content: Any,
    description_indent: str,
) -> List[str]:
    """    
    DESCRIPTION:
        Internal function to build a properly indented block in the docstring
        for any "Label:" section where the content maybe a single value,
        multiline string, or a list of items.

    PARAMETERS:
        label:
            Required Argument.
            The label for the block (e.g., 'Default Value').
            Types: str

        content:
            Required Argument.
            The value or list to be formatted as a block.
            Types: Any

        description_indent:
            Required Argument.
            The indentation to use for the block's description lines.
            Types: str

    RETURNS:
        List of formatted lines for the docstring block.
        Types: List[str]

    RAISES:
        None.

    EXAMPLES:
        lines = _emit_structured_block('Default Value', '512', '    ')
    """

    lines: List[str] = []
    if not content:
        return lines

    # Normalize into list of lines
    if isinstance(content, (list, tuple, set)):
        raw_lines = [f"* {item}" for item in content]
    else:
        raw_lines = [ln for ln in str(content).splitlines() if ln.strip()]

    # Single-line simple content
    if len(raw_lines) == 1 and not _LIST_MARKER_RE.match(raw_lines[0]):
        lines.append(f"{description_indent}{label}: {raw_lines[0]}")
        return lines

    # Multi-line block
    lines.append(f"{description_indent}{label}:")
    block_indent = description_indent + " " * 4
    sub_indent = description_indent + " " * 8

    # Process each line, indenting bullets and preserving structure
    # for multiline content
    i = 0
    while i < len(raw_lines):
        raw = raw_lines[i].strip()
        is_bullet = bool(_LIST_MARKER_RE.match(raw))
        content = raw[2:].strip() if is_bullet else raw
        if ( not is_bullet and ":" in raw) or content.endswith(":"):
            lines.append(f"{block_indent}{content}")
            i += 1
        elif is_bullet:
            lines.append(f"{sub_indent}* {content}")
            i += 1
        else:
            # Not a bullet, just a regular line
            lines.append(f"{sub_indent} {content}")
            i += 1
        
    return lines

def _emit_notes_block(notes: str, description_indent: str) -> List[str]:
    """
    DESCRIPTION:
        Internal function that emits a free-form notes string into a
        'Note:' or 'Notes:' section with proper indentation and bullet 
        formatting for docstrings.
        Detects whether to use singular or plural header and preserves
        nested paragraphs.

    PARAMETERS:
        notes:
            Required Argument.
            The notes string to be formatted.
            Types: str

        description_indent:
            Required Argument.
            The indentation to use for the block's description lines.
            Types: str

    RETURNS:
        List of formatted lines for the notes block.
        Types: List[str]

    RAISES:
        None.

    EXAMPLES:
        lines = _emit_notes_block('Applicable only for file-based stores.', '    ')
    """
    lines: List[str] = []

    # Split and filter out blank lines
    raw = [ln.strip() for ln in notes.splitlines() if ln.strip()]
    if not raw:
        return lines

    # Determine if we need singular or plural header
    header = "Notes:" if len(raw) > 1 else "Note:"

    # Build lines with header
    lines.append(f"{description_indent}{header}")

    previous_was_bullet = False
    # For each line in raw, indent as bullet 
    # or paragraph line under last bullet
    # depending on whether it starts with a bullet marker
    for ln in raw:
        if _LIST_MARKER_RE.match(ln):
            lines.append(f"{description_indent}    {ln}")
            previous_was_bullet = True
        else:
            spacer = "      " if previous_was_bullet else "    "
            lines.append(f"{description_indent}{spacer}{ln}")
            previous_was_bullet = False

    return lines

#-------------------------------------------------------------------
# Section parsing & parameter-removal helpers
# -------------------------------------------------------------------

def _split_sections(docstring: str) -> List[Tuple[str, List[str]]]:
    """
    DESCRIPTION:
        Internal function to split a docstring into named sections based
        on headers like 'DESCRIPTION:', 'PARAMETERS:', etc.
        Leading text before the first recognized header is considered 'BODY'.

    PARAMETERS:
        docstring:
            Required Argument.
            The docstring to split into sections.
            Types: str

    RETURNS:
        List of (header, lines) tuples representing docstring sections.
        Types: List[Tuple[str, List[str]]]

    RAISES:
        None.

    EXAMPLES:
        sections = _split_sections('''DESCRIPTION:...PARAMETERS:...''')
    """
    if not docstring:
        return []

    sections: List[Tuple[str, List[str]]] = []
    last_header = "BODY"
    last_index = 0

    # Find all section headers
    # and split the docstring into blocks
    for match in _SECTION_HEADER_RE.finditer(docstring):
        header = match.group(1).strip().upper()
        block_text = docstring[last_index : match.start()].rstrip("\n")
        
        # split into lines and strip out any leading/trailing blank lines
        lines = block_text.splitlines()
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
        sections.append((last_header, lines))
        
        #sections.append((last_header, block_text.splitlines()))
        # update for next section with last header and last index
        last_header = header
        last_index = match.end()

    # final block
    final_block = docstring[last_index:].rstrip("\n")
    
    lines = final_block.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    sections.append((last_header, lines))

    # drop the very first BODY if empty
    if sections and not any(line.strip() for line in sections[0][1]):
        sections.pop(0)

    return sections

def _remove_excluded_parameters(
    parameter_lines: List[str],
    excluded_argument_names: set[str],
) -> List[str]:
    """
    DESCRIPTION:
        Removes parameter entry blocks from a PARAMETERS section whose name is 
        in excluded_argument_names.

    PARAMETERS:
        parameter_lines:
            Required Argument.
            The lines of the PARAMETERS section to filter.
            Types: List[str]

        excluded_argument_names:
            Required Argument.
            Set of parameter names to exclude from the PARAMETERS section.
            Types: set[str]

    RETURNS:
        Filtered list of parameter lines.
        Types: List[str]

    RAISES:
        None.

    EXAMPLES:
        param_lines = [
            "    chunk_size:",
            "       Optional Argument.",
            "   nv_ingestor:",
            "       Optional Argument."
            ]
        filtered = _remove_excluded_parameters(param_lines , {"nv_ingestor"})
    """
    cleaned_lines: List[str] = []
    skipping = False
    param_indent_level = None

    # Iterate through all lines under PARAMETERS
    # and remove blocks for excluded parameters
    for line in parameter_lines:
        # Detect start of each param block
        name_match = re.match(r"^(\s*)(\w+):\s*$", line)
        if name_match:
            indent, param_name = name_match.groups()
            if param_name in excluded_argument_names:
                skipping = True
                param_indent_level = len(indent)
                continue
            else:
                skipping = False

        if skipping:
            # if we encounter a line that's at or above the original param indent,
            # it means the block ended
            current_indent = len(line) - len(line.lstrip())
            if current_indent <= (param_indent_level or 0):
                skipping = False
            else:
                continue

        if not skipping:
            cleaned_lines.append(line)

    # Clean up consecutive blank lines left after removing parameters
    result = []
    prev_blank = False
    for line in cleaned_lines:
        is_blank = not line.strip()
        if not (is_blank and prev_blank):  # Avoid consecutive blank lines
            result.append(line)
        prev_blank = is_blank
    
    # Remove trailing blank lines
    while result and not result[-1].strip():
        result.pop()
    
    return result

# -------------------------------------------------------------------
# The unified decorator
# -------------------------------------------------------------------

def docstring_handler(
    inherit_from: Optional[Union[Type, Callable]] = None,
    replace_sections: Sequence[str] = ("EXAMPLES",),
    common_params: Optional[Dict[str, Dict[str, Any]]] = None,
    exclude_params: Optional[List[str]] = None,
) -> Callable[[Callable], Callable]:
    """
    DESCRIPTION:
        Decorator to inherit parent method's docstring, override specified sections,
        append shared parameters, and remove excluded parameters.

    PARAMETERS:
        inherit_from:
            Optional Argument.
            Class or function to inherit the parent method's docstring from.
            Types: class or function

        replace_sections:
            Optional Argument.
            Sequence of section headers the child should override in the docstring.
            Types: sequence of str

        common_params:
            Optional Argument.
            Mapping of parameter-key to spec-dict to append into PARAMETERS.
            Types: dict

        exclude_params:
            Optional Argument.
            List of parameter keys (or argument_names) to remove from both inherited PARAMETERS and injected common_params.
            Types: list of str

    RETURNS:
        Decorated function with updated docstring.
        Types: Callable[[Callable], Callable]

    RAISES:
        None.

    EXAMPLES:
        @docstring_handler(inherit_from=BaseClass, common_params=PARAMS)
        def my_func(...):
            ...
    """
    excluded_keys = set(exclude_params or [])

    if isinstance(replace_sections, str):
        headers_to_replace = {replace_sections.upper()}
    else:
        headers_to_replace = {h.upper() for h in replace_sections}

    def decorator(method: Callable) -> Callable:
        # 1) Fetch and split parent doc if requested
        parent_sections: List[Tuple[str, List[str]]] = []
        if inherit_from:
            parent_method = getattr(inherit_from, method.__name__)
            raw_parent_doc = inspect.getdoc(parent_method) or ""
            parent_sections = _split_sections(raw_parent_doc)

        # 2) Split the child’s own doc
        raw_child_doc = inspect.getdoc(method) or ""
        child_sections = dict(_split_sections(raw_child_doc))

        # 3) Merge sections
        if inherit_from:
            merged_sections: List[Tuple[str, List[str]]] = []
            parent_headers = [hdr for hdr, _ in parent_sections]

            for header, block_lines in parent_sections:
                if header in headers_to_replace and header in child_sections:
                    merged_sections.append((header, child_sections[header]))
                else:
                    merged_sections.append((header, block_lines))

            # Append any child-only sections
            for header, block_lines in _split_sections(raw_child_doc):
                if header not in parent_headers and header != "BODY":
                    merged_sections.append((header, block_lines))

        else:
            # No inheritance: start with child's sections only
            merged_sections = _split_sections(raw_child_doc)
        
        # Ensure each section exists
        section_canonical_names = ["DESCRIPTION", "PARAMETERS", "RETURNS", "RAISES", "EXAMPLES"]
        existing = [hdr for hdr, _ in merged_sections ]
        block_indent_auto = " " * 4

        for section in section_canonical_names:
            if section not in existing:
                # DESCRIPTION gets a default line, others can just say "None"
                
                if section == "DESCRIPTION":
                    default_block = [f"{block_indent_auto}Auto generated description."]
                
                elif section == "PARAMETERS" and common_params:
                    default_block = []
                else:
                    default_block = [f"{block_indent_auto}None"]

                # Figure out what to insert next so order stays as section_canonical_names
                insert_at = next(
                    (i for i, (hdr, _) in enumerate(merged_sections)
                    if hdr in section_canonical_names
                        and section_canonical_names.index(hdr) > section_canonical_names.index(section)),
                    len(merged_sections),
                )
                merged_sections.insert(insert_at, (section, default_block))

        # 4) Inject or update PARAMETERS block
        if common_params:
            # find or create PARAMETERS section
            param_index = next(
                (i for i, (hdr, _) in enumerate(merged_sections) if hdr == "PARAMETERS"),
                None,
            )
            header, existing_param_lines = merged_sections[param_index]

            # remove excluded params
            # also map keys → argument_name for exclusion
            excluded_argument_names = {
                common_params[key].get("argument_name", key)
                for key in excluded_keys
                if key in common_params
            }
            excluded_argument_names |= excluded_keys

            cleaned_param_lines = _remove_excluded_parameters(
                existing_param_lines,
                excluded_argument_names,
            )

            # Which args are already present
            existing_param_names = {
                m.group(1)
                for line in cleaned_param_lines
                if (m := re.match(r"^\s*(\w+):\s*$", line))
            }

            # build new param lines
            base_indent = " " * 4
            description_indent = base_indent + " " * 4
            injected_lines: List[str] = []
            for param_key, spec in common_params.items():
                # Only exclude by excluded keys in the injection loop, not by argument_name.
                if param_key in excluded_keys:
                    continue
                
                argument_name = spec.get("argument_name", param_key)

                if argument_name in existing_param_names:
                    # If already exists, skip adding it again
                    continue

                # name:
                injected_lines.append(f"{base_indent}{argument_name}:")
                # required
                if spec.get("required"):
                    injected_lines.append(f"{description_indent}{spec['required']}.")
                # description
                if spec.get("description"):
                    for i, desc_line in enumerate(spec["description"].splitlines()):
                        indent = description_indent if i else description_indent
                        injected_lines.append(f"{indent}{desc_line.strip()}")
                # notes, default, permitted, types
                injected_lines += _emit_notes_block(
                    spec.get("notes", ""), description_indent
                )
                injected_lines += _emit_structured_block(
                    "Default Value", spec.get("default_values"), description_indent
                )
                injected_lines += _emit_structured_block(
                    "Permitted Values", spec.get("permitted_values"), description_indent
                )
                if spec.get("types"):
                    injected_lines.append(
                        f"{description_indent}Types: {spec['types']}"
                    )
                injected_lines.append("")  # blank line

            # merge old + blank separator + new
            if cleaned_param_lines and injected_lines:
                if cleaned_param_lines[-1].strip():
                    cleaned_param_lines.append("")
            merged_param_block = cleaned_param_lines + injected_lines

            # replace in merged_sections
            merged_sections[param_index] = (header, merged_param_block)


        # 5) Reconstruct final docstring
        final_blocks: List[str] = []
        for header, block_lines in merged_sections:
            if header == "BODY":
                if block_lines:
                    final_blocks.append("\n".join(block_lines).rstrip())
            else:
                # final_blocks.append(f"{header}:")
                # if block_lines:
                #     final_blocks.append("\n".join(block_lines).rstrip())
                if block_lines:
                    block = f"{header}:\n" + "\n".join(block_lines).rstrip()
                else:
                    block = f"{header}:"
                final_blocks.append(block)

        final_doc = "\n\n".join(final_blocks).rstrip() + "\n"
        method.__doc__ = textwrap.dedent(final_doc)
        #method.__doc__ = final_doc

        return method

    return decorator