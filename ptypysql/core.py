# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/00_core.ipynb (unless otherwise specified).

__all__ = ['MAIN_STATEMENTS', 'CAP_STATEMENTS', 'clean_query', 'preformat_statements', 'lowercase_query',
           'add_whitespaces_query', 'format_partition_by', 'remove_wrong_end_comma', 'format_case_when',
           'format_select', 'format_from', 'format_join', 'format_on', 'format_on', 'format_where',
           'format_filter_where', 'format_statement_line', 'format_statements', 'add_join_as',
           'format_multiline_comments', 'add_semicolon', 'format_simple_sql', 'format_sql']

# Cell
import re
from .utils import *

# Cell
MAIN_STATEMENTS = [
    "create.*?table",  # regex for all variants, e.g. CREATE OR REPLACE TABLE
    "create.*?view",  # regex for all variants, e.g. CREATE OR REPLACE VIEW
    "with",
    "select distinct",
    "select",
    "from",
    "(?:natural\s|full\s)?(?:left\s|right\s|inner\s|outer\s|cross\s)?join",
    "union",
    "intersect",
    "on",
    "where",
    "group by",
    "having",
    "order by",
    "over",  # special case: no newline, only capitalized
    "partition by",  # special case: no newline, only capitalized
    "limit",
]

CAP_STATEMENTS = [
    "between",
    "and",
    "or",
    "not",
    "case",
    "when",
    "else",
    "then",
    "end",
    "any",
    "all",
    "exists",
    "in",
    "filter",
    "offset",
    "as",
    "is",
    "like",
    "similar to",
    "null",
    "true",
    "false",
    "unknown",
    "asc",
    "desc"
]
    # "count(",
    # "sum(",
    # "avg(",
    # "min(",
    # "max(",
    # "least(",
    # "greatest(",
    # "date_trunc(",
    # "coalesce(",
    # "trunc(",
    # "sqrt(",
    # "abs(",
    # "cbrt(",
    # "ceil(",
    # "floor(",
    # "degrees(",
    # "div(",
    # "exp(",
    # "ln(",
    # "log(",
    # "mod(",
    # "pi()",
    # "power(",
    # "radians(",
    # "round(",
    # "sign(",
    # "width_bucket(",
    # "random()",
    # "setseed(",
    # "acos(",
    # "asin(",
    # "atan(",
    # "cos(",
    # "cot(",
    # "sin(",
    # "tan(",


# Cell
def clean_query(s):
    "Remove redundant whitespaces, mark comments boundaries and remove newlines afterwards in query `s`"
    s = add_whitespaces_after_comma(s)  # add whitespaces after comma but no in comments or quotes
    s = remove_redundant_whitespaces(s)  # remove too many whitespaces but no newlines
    s = mark_comments(s)  # mark comments with special tokens [C], [CS] and [CI]
    s = replace_newline_chars(s)  # remove newlines but not in the comments
    s = remove_whitespaces_newline(s)  # remove whitespaces after and before newline
    s = remove_whitespaces_comments(s)  # remove whitespaces after and before [C], [CS] and [CI]
    s = remove_whitespaces_parenthesis(s)  # remove whitespaces between parenthesis
    s = remove_redundant_whitespaces(s)  # remove too many whitespaces but no newlines
    return s

# Cell
def preformat_statements(s):
    """Write a newline in `s` for all `statements` and
    uppercase them but not if they are inside a comment"""
    statements = MAIN_STATEMENTS
    s = clean_query(s)  # clean query and mark comments
    split_s = split_query(s)  # split by comment and non comment
    split_s = compress_dicts(split_s, ["comment", "select"])
    # compile regex before loop
    create_re = re.compile(r"\bcreate\b", flags=re.I)
    select_re = re.compile(r"\bselect\b", flags=re.I)
    for statement in statements:
        if create_re.match(statement):  # special case CREATE with AS capitalize as well
            create_sub = re.compile(rf"\s*({statement} )(.*) as\b", flags=re.I)
            split_s = [{
                "string": create_sub.sub(
                    lambda pat: "\n" + pat.group(1).upper() + pat.group(2) + " AS",
                    sdict["string"],
                    ) if not sdict["comment"] else sdict["string"],
                    "comment": sdict["comment"],
                    "select": sdict["select"]
                } for sdict in split_s]
        else:  # normal main statements
            non_select_region_re = re.compile(rf"\s*\b({statement})\b", flags=re.I)
            select_region_statement_re = re.compile(rf"\b({statement})\b", flags=re.I)
            split_s = [{
                "string": non_select_region_re.sub(lambda x: "\n" + x.group(1).upper(), sdict["string"])
                    if not sdict["comment"] and not sdict["select"]  # no comment, no select region
                    else non_select_region_re.sub(lambda x: "\n" + x.group(1).upper(), sdict["string"])
                    if not sdict["comment"] and sdict["select"] and select_re.match(statement) # no comment, select region and select statement
                    else select_region_statement_re.sub(lambda x: x.group(1).upper(), sdict["string"])
                    if not sdict["comment"] and sdict["select"] and not select_re.match(statement) # no comment, select region and no select statement
                    else sdict["string"],
                "comment": sdict["comment"],
                "select": sdict["select"]
                } for sdict in split_s]

    # capital common and important functional words
    cap_statements = CAP_STATEMENTS
    for statement in cap_statements:
        split_s = [{
            "string": re.sub(rf"\b({statement})\b", statement.upper(), sdict["string"], flags=re.I) if not sdict["comment"] else sdict["string"],
            "comment": sdict["comment"],
            "select": sdict["select"]
        }for sdict in split_s]

    s = "".join([sdict["string"] for sdict in split_s])
    s = s.strip()  # strip string
    s = remove_whitespaces_newline(s)  # remove whitespaces before and after newline


    return s

# Cell
def lowercase_query(s):
    "Lowercase query but let comments and text in quotes untouched"
    split_s = split_query(s)
    split_s = [
        d["string"]
        if d["comment"] or d["quote"]
        else d["string"].lower()
        for d in split_s
    ]
    s = "".join([s for s in split_s])
    return s

# Cell
def add_whitespaces_query(s):
    "Add whitespaces between symbols (=!<>) for query `s` but not for comments"
    split_s = split_comment_quote(s)  # split by comment / non-comment, quote / non-quote
    for d in split_s:
        if not d["comment"] and not d["quote"]:
            d["string"] = add_whitespaces_between_symbols(d["string"])
    s = "".join([d["string"] for d in split_s])
    return s

# Cell
def format_partition_by(s, base_indentation):
    "Format PARTITION BY line in SELECT (DISTINCT)"
    orderby_involved = bool(re.search("order by", s, flags=re.I))
    if orderby_involved:
        split_s = re.split("(partition by.*)(order by.*)", s, flags=re.I)  # split PARTITION BY
    else:
        split_s = re.split("(partition by.*)", s, flags=re.I)  # split PARTITION BY
    split_s = [sp for sp in split_s if sp != ""]
    begin_s = split_s[0]
    partition_by = split_s[1]
    indentation = base_indentation + 8
    # add newline after each comma (no comments) and indentation
    partition_by = add_newline_indentation(partition_by, indentation=indentation)
    # add new line and indentation after order by
    if orderby_involved:
        partition_by = "".join([partition_by, " "] + split_s[2:])
    partition_by = re.sub(
        r"\s(order by.*)", "\n" + " " * (base_indentation + 4) + r"\1",
        partition_by,
        flags=re.I
    )
    # combine begin of string with formatted partition by
    s = begin_s + "\n" + (base_indentation + 4) * " " + partition_by
    s = s.strip()
    # add newline and indentation before the last bracket
    s = re.sub(r"(\)\s*(?:as\s*)*[^\s\)]+)$", "\n" + " " * base_indentation + r"\1", s, flags=re.I)
    return s

# Cell
def remove_wrong_end_comma(split_s):
    """Remove mistakenly placed commas at the end of SELECT statement using `split_s` with keys
    "string", "comment" and "quote"
    """
    reversed_split_s = split_s[::-1]  # reversed split_s
    first_noncomment = True
    # compile regex before loop
    replace_comma_without_comment = re.compile(r"([\w\d]+)[,]+(\s*)$")
    replace_comma_with_comment = re.compile(r"([\w\d]+)[,]+(\s*)$")
    for i, d in enumerate(reversed_split_s):
        s_aux = d["string"]
        if not d["comment"] and not d["quote"] and d["string"] != "" and first_noncomment:
            if i == 0:  # if end of select (no comment afterwards) remove whitespaces
                s_aux = replace_comma_without_comment.sub(r"\1", s_aux)
            else:  # if not end of select (because comment afterwards) do not remove whitespaces
                s_aux = replace_comma_with_comment.sub(r"\1\2", s_aux)
            first_noncomment = False
        # remove whitespaces between newline symbols
        s_aux = remove_whitespaces_newline(s_aux)
        reversed_split_s[i]["string"] = s_aux
    split_s_out = reversed_split_s[::-1]
    return split_s_out

# Cell
def format_case_when(s, max_len=99):
    "Format case when statement in line `s`"
    # compile regex
    when_else_re = re.compile(r"(?<!case) ((?:when|else).*?)", flags=re.I)
    case_and_or = re.compile(r"\b((?:and|or))\b", flags=re.I)
    case_then = re.compile(r"\b(then)\b", flags=re.I)
    case_end = re.compile(r"\b(end)\b", flags=re.I)
    indent_between_and_reset = re.compile(r"(\bbetween\b)\s+(\S*?)\s+(\band\b)", flags=re.I)
    indent_between_and_indent = re.compile(r"(\bbetween\b)\s(\S*?)\s(\band\b)", flags=re.I)
    # prepare string
    s_strip = s.strip()
    field_indentation = len(s) - len(s_strip)
    split_s = split_comment_quote(s)
    for d in split_s:
        if not d["quote"]:  # assumed no comments given by select function
            d["string"] = when_else_re.sub(
                r"\n" + " " * (field_indentation + 4) + r"\1",
                d["string"]
            )
            # if len(d["string"]) + field_indentation + 10 > max_len: # 10 for "case when "
            #     d["string"] = case_and_or.sub(
            #         "\n" + " " * (field_indentation + 8) + r"\1",
            #         d["string"]
            #     )
            d["string"] = case_then.sub(
                "\n" + " " * (field_indentation + 4) + r"\1",
                d["string"]
            )
            d["string"] = case_end.sub("\n" + " " * field_indentation + r"\1", d["string"])

    s_code = "".join([d["string"] for d in split_s])
    s_code = "\n".join([case_and_or.sub("\n" + " " * (field_indentation + 8) + r"\1", sp) if len(sp) > max_len else sp for sp in s_code.split("\n")])
    s_code = indent_between_and_reset.sub(r"\1 \2 \3", s_code)
    s_code = "\n".join([indent_between_and_indent.sub(r"\1 \2\n" + " " * 12 + r"\3", sp)
                        if len(sp) > max_len else sp for sp in s_code.split("\n")])

    return s_code

# Cell
def format_select(s, max_len=99):
    "Format SELECT statement line `s`. If line is longer than `max_len` then reformat line"
    # remove [C] at end of SELECT
    s = re.sub(r"\[C\]$", "", s)
    split_s = split_comment_quote(s)  # split by comment / non-comment, quote / non-quote
    # if comma is found at the end of select statement then remove comma
    split_s = remove_wrong_end_comma(split_s)
    # check whether there is a SELECT DISTINCT in the code (not comments, not text in quotes)
    s_code = "".join([d["string"] for d in split_s if not d["comment"] and not d["quote"]])
    # save the correct indentation: 16 for select distinct, 7 for only select
    indentation = 4
    # get only comment / non-comment
    split_comment = compress_dicts(split_s, ["comment"])
    # add newline after each comma and indentation (this is robust against quotes by construction)
    s = add_newline_indentation("".join([d["string"] for d in split_s if not d["comment"]]),
                                indentation=indentation)
    # split by newline
    split_s = s.split("\n")
    # format case when
    split_s = [
        format_case_when(sp, max_len)
        if identify_in_sql("case when", sp) != []
        else sp
        for sp in split_s
    ]
    # add AS if missing
    as_regex = re.compile(r"(\)(?<!\bAS\b)\s?|\w(?<!\bSELECT\b)(?<!\bSELECT DISTINCT\b)(?<!\bAS\b)\s)(\w+|\'.+\')(,?)$", flags=re.I)
    split_s = [as_regex.sub(lambda x: x.group(1).rstrip() + " AS " + x.group(2) + x.group(3), sp)
               for sp in split_s]
    # join by newline
    s = "\n".join(split_s)
    # format PARTITION BY
    begin_s = s[0:indentation]
    split_s = s[indentation:].split("\n" + (" " * indentation))
    partition_by_re = re.compile("partition by", flags=re.I)
    split_s = [
        format_partition_by(line, base_indentation=indentation)
        if partition_by_re.search(line) else line
        for line in split_s
    ]
    s = begin_s + ("\n" + (" " * indentation)).join(split_s)

    # depreciated: used to reformat too long line in select only, and cannot handle too long subquery
    # s = "\n".join([
    #     reformat_too_long_line(li, max_len=max_len)
    #     for li in s.split("\n")
    # ])
    # get comments and preceding string (non-comment)
    comment_dicts = []
    for i, d in enumerate(split_comment):
        if d["comment"]:
            comment_dicts.append({"comment": d["string"], "preceding": split_comment[i-1]["string"]})
    # assign comments to text
    s = assign_comment(s, comment_dicts)
    return s

# Cell
def format_from(s, **kwargs):
    "Format FROM statement line `s`"
    split_s = split_comment_quote(s)
    split_comment = compress_dicts(split_s, ["comment"])
    # define regex before loop
    indentation = 4
    s = add_newline_indentation("".join([d["string"] for d in split_s if not d["comment"]]),
                                indentation=indentation)
    split_s = s.split("\n")
    # add AS if no AS exists but with custom name
    as_regex = re.compile(r"(\)(?<!\bAS\b)\s?|\w(?<!\bFROM\b)(?<!\bAS\b)\s)(\w+|\'.+\')(,?)$", flags=re.I)
    split_s = [as_regex.sub(lambda x: x.group(1).rstrip() + " AS " + x.group(2) + x.group(3), sp)
               for sp in split_s]
    s = "\n".join(split_s)

    comment_dicts = []
    for i, d in enumerate(split_comment):
        if d["comment"]:
            comment_dicts.append({"comment": d["string"], "preceding": split_comment[i-1]["string"]})
    # assign comments to text
    s = assign_comment(s, comment_dicts)
    return s

# Cell
def format_join(s, **kwargs):
    "Format JOIN statement line `s`"
    s = re.sub(  # add indentation
        r"\b((?:natural\s|full\s)?(?:left\s|right\s|inner\s|outer\s|cross\s)?join)\b",
        r"    \1",
        s,
        flags=re.I
    )
    return s

# Cell
def format_on(s, max_len = 82):
    "Format ON statement line `s`"
    indentation = 8
    s = " " * indentation + s  # add indentation
    split_s = split_comment_quote(s)
    # define regex before loop
    indent_and_or = re.compile(r"\s*\b(and|or)\b", flags=re.I)
    indent_between_and_reset = re.compile(r"(\bbetween\b)\s+(\S*?)\s+(\band\b)", flags=re.I)
    indent_between_and_indent = re.compile(r"(\bbetween\b)\s(\S*?)\s(\band\b)", flags=re.I)
    for d in split_s:
        if not d["comment"] and not d["quote"]:
            s_aux = d["string"]
            s_aux = indent_and_or.sub(lambda x: "\n" + " " * 8 + x.group(1), s_aux)  # add newline and indentation for and ,or
            d["string"] = s_aux
    # get split comment / non comment
    split_comment = compress_dicts(split_s, ["comment"])
    s_code = "".join([d["string"] for d in split_s if not d["comment"]])
    # add newline and indentation for between_and (experimental) if too long
    s_code = indent_between_and_reset.sub(r"\1 \2 \3", s_code)
    s_code = "\n".join([indent_between_and_indent.sub(r"\1 \2\n" + " " * 12 + r"\3", sp)
                        if len(sp) > max_len else sp for sp in s_code.split("\n")])

    # strip lines of code from the right
    s_code = "\n".join([sp.rstrip() for sp in s_code.split("\n")])
    # get comments and preceding string (non-comment)
    comment_dicts = []
    for i, d in enumerate(split_comment):
        if d["comment"]:
            comment_dicts.append({"comment": d["string"], "preceding": split_comment[i-1]["string"]})
    # assign comments to text
    s = assign_comment(s_code, comment_dicts)
    return s

# Cell
def format_on(s, max_len = 82):
    "Format ON statement line `s`"
    indentation = 8
    s = " " * indentation + s  # add indentation
    split_s = split_comment_quote(s)
    # define regex before loop
    indent_and_or = re.compile(r"\s*\b(and|or)\b", flags=re.I)
    indent_between_and_reset = re.compile(r"(\bbetween\b)\s+(\S*?)\s+(\band\b)", flags=re.I)
    indent_between_and_indent = re.compile(r"(\bbetween\b)\s(\S*?)\s(\band\b)", flags=re.I)
    for d in split_s:
        if not d["comment"] and not d["quote"]:
            s_aux = d["string"]
            s_aux = indent_and_or.sub(lambda x: "\n" + " " * 8 + x.group(1), s_aux)  # add newline and indentation for and ,or
            d["string"] = s_aux
    # get split comment / non comment
    split_comment = compress_dicts(split_s, ["comment"])
    s_code = "".join([d["string"] for d in split_s if not d["comment"]])
    # add newline and indentation for between_and (experimental) if too long
    s_code = indent_between_and_reset.sub(r"\1 \2 \3", s_code)
    s_code = "\n".join([indent_between_and_indent.sub(r"\1 \2\n" + " " * 12 + r"\3", sp)
                        if len(sp) > max_len else sp for sp in s_code.split("\n")])

    # strip lines of code from the right
    s_code = "\n".join([sp.rstrip() for sp in s_code.split("\n")])
    # get comments and preceding string (non-comment)
    comment_dicts = []
    for i, d in enumerate(split_comment):
        if d["comment"]:
            comment_dicts.append({"comment": d["string"], "preceding": split_comment[i-1]["string"]})
    # assign comments to text
    s = assign_comment(s_code, comment_dicts)
    return s

# Cell
def format_where(s, max_len = 82):
    "Format WHERE statement line `s`"
    #s = re.sub(r"(where )", r"\1 ", s, flags=re.I)  # add indentation after WHERE
    # split by comment / non comment, quote / non-quote
    split_s = split_comment_quote(s)
    # define regex before loop
    indent_and_or = re.compile(r"\s*\b(and|or)\b", flags=re.I)
    indent_between_and_reset = re.compile(r"(\bbetween\b)\s+(\S*?)\s+(\band\b)", flags=re.I)
    indent_between_and_indent = re.compile(r"(\bbetween\b)\s(\S*?)\s(\band\b)", flags=re.I)
    for d in split_s:
        if not d["comment"] and not d["quote"]:
            s_aux = d["string"]
            s_aux = indent_and_or.sub(lambda x: "\n" + " " * 4 + x.group(1), s_aux)  # add newline and indentation for and ,or
            d["string"] = s_aux
    # get split comment / non comment
    split_comment = compress_dicts(split_s, ["comment"])
    s_code = "".join([d["string"] for d in split_s if not d["comment"]])
    # add newline and indentation for between_and (experimental) if too long
    s_code = indent_between_and_reset.sub(r"\1 \2 \3", s_code)
    s_code = "\n".join([indent_between_and_indent.sub(r"\1 \2\n" + " " * 8 + r"\3", sp)
                        if len(sp) > max_len else sp for sp in s_code.split("\n")])

    # strip from the right each code line
    s_code = "\n".join([sp.rstrip() for sp in s_code.split("\n")])
    # get comments and preceding string (non-comment)
    comment_dicts = []
    for i, d in enumerate(split_comment):
        if d["comment"]:
            comment_dicts.append({"comment": d["string"], "preceding": split_comment[i-1]["string"]})
    # assign comments to text
    s = assign_comment(s_code, comment_dicts)
    return s

# Cell
def format_filter_where(s, **kwargs):
    "Format WHERE statement line `s`"
    s = re.sub(r"(filter)\s+\((where)\s+", r"\1 (\n\2 ", s, flags=re.I)  # add indentation after WHERE
    return s

# Cell
def format_statement_line(s, **kwargs):
    "Format statement line `s`"
    statement_funcs = {
        r"^select": format_select,
        r"^from": format_from,
        r"^\w*\s?\w*\s?join": format_join,
        r"^on": format_on,
        r"filter \(where": format_filter_where,
        r"^where": format_where,
        r"\(\nwhere": format_where,
    }
    for key, format_func in statement_funcs.items():
        if re.search(key, s, flags=re.I):
            s = format_func(s, **kwargs)
    return s

# Cell
def format_statements(s, **kwargs):
    "Format statements lines `s`"
    statement_lines = s.split("\n")
    formatted_lines = [
        format_statement_line(line, **kwargs) for line in statement_lines
    ]
    formatted_s = "\n".join(formatted_lines)
    return formatted_s

# Cell
def add_join_as(s, **kwargs):
    as_on_regex = re.compile(r"(\)(?<!\bAS\b)\s?|\w(?<!\bJOIN\b)(?<!\bAS\b)\s)(\w+|\'.+\')(\s+\bON\b)")
    s = as_on_regex.sub(lambda x: x.group(1).rstrip() + " AS " + x.group(2) + x.group(3), s)
    return s

# Cell
def format_multiline_comments(s):
    "Format multiline comments by replacing multiline comment [CI] by newline and adding indentation"
    split_s = s.split("\n")
    split_out = []
    for sp in split_s:  # loop on query lines
        if re.search(r"\[CI\]", sp):
            indentation = re.search(r"\/\*", sp).start() + 3
            sp_indent = re.sub(r"\[CI\]", "\n" + " " * indentation, sp)
            split_out.append(sp_indent)
        else:
            split_out.append(sp)
    s = "\n".join(split_out)
    return s

# Cell
def add_semicolon(s):
    "Add a semicolon at the of query `s`"
    split_s = s.split("\n")
    last_line = split_s[-1]
    split_c = split_comment(last_line)
    if len(split_c) == 1:
        split_s[-1] = last_line + ";"
    else:
        split_c[0]["string"] = re.sub("(.*[\w\d]+)(\s*)$", r"\1;\2", split_c[0]["string"])
        split_s[-1] = "".join([d["string"] for d in split_c])
    return "\n".join(split_s)

# Cell
def format_simple_sql(s, semicolon=False, max_len=99):
    "Format a simple SQL query without subqueries `s`"
    s = lowercase_query(s)  # everything lowercased but not the comments
    s = preformat_statements(s)  # add breaklines for the main statements
    s = add_whitespaces_query(s)  # add whitespaces between symbols in query
    s = format_statements(s, max_len=max_len)  # format statements
    s = add_join_as(s) # special handling for JOIN ... AS ... ON
    s = re.sub(r"\[C\]", "", s)  # replace remaining [C]
    s = re.sub(r"\[CS\]", "\n", s)  # replace remaining [CS]
    s = re.sub(r"\s+\n", "\n", s)  # replace redundant whitespaces before newline
    s = format_multiline_comments(s)  # format multline comments
    s = s.strip()  # strip query
    if semicolon:
        s = add_semicolon(s)
    return s

# Cell
def format_sql(s, semicolon=False, max_len=99):
    "Format SQL query with subqueries `s`"
    s = format_simple_sql(s, semicolon=semicolon, max_len=max_len)  # basic query formatting
    # get first outer subquery positions
    subquery_pos = extract_outer_subquery(s)
    # loop over subqueries
    while subquery_pos is not None:
        # get split
        split_s = [
            s[0:subquery_pos[0]+2],
            s[subquery_pos[0]+2:(subquery_pos[1]+1)],
            s[(subquery_pos[1]+1):]
        ]
        # format subquery (= split_s[1])
        split_s[1] = format_subquery(split_s[1], split_s[0])
        # join main part and subquery
        s = "".join(split_s)

        # get first outer subquery positions
        subquery_pos = extract_outer_subquery(s)

    # format too long string
    split_s = split_comment_quote(s)
    split_comment = compress_dicts(split_s, ["comment"])

    # separate comment and the code since the length of comment is not considered
    s_code = "".join([d["string"] for d in split_s if not d["comment"]])
    s_code = s_code.split("\n")
    # loop for each line, reformat it if it is too long
    s_id = 0
    while s_id < len(s_code):
        sp = s_code[s_id]
        if len(sp) > max_len:
            sp_code = "\n".join(s_code[s_id:])
            if split_index := extract_outer_subquery_too_long(sp_code, max_len):
                zip_split = zip([-1] + split_index, split_index + [len(s)])
                ss = [sp_code[i+1:j+1] for i,j in zip_split]
                for i in range(1, len(ss) - 1):
                    ss[i] = "\n" + format_subquery_too_long(ss[i].strip(), ss[0])
                sp_code = "".join(ss)
                s_code = s_code[:s_id] + sp_code.split("\n")

        s_id += 1

    s_code = "\n".join([ss.rstrip() for ss in s_code])
    comment_dicts = []
    for i, d in enumerate(split_comment):
        if d["comment"]:
            comment_dicts.append({"comment": d["string"], "preceding": split_comment[i-1]["string"]})
    # assign comments to text
    s = assign_comment(s_code, comment_dicts)
    return s