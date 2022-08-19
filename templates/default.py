#!/usr/bin/env python3
import sys
sys.setrecursionlimit(10 ** 9)


INF = float('INF')
{% if is_yes_str %}
YES = '{{ yes_str }}'
{%- endif %}
{%- if is_no_str %}
NO = '{{ no_str }}'
{%- endif %}


def solve({{ solve_argument }}):
    {%- if is_no_str %}
    print(NO)
    {%- elif is_yes_str %}
    print(YES)
    {%- else %}
    return
    {%- endif %}


def main():
    {%- if extract_success %}
    def stdin_iter():
        for stdin in sys.stdin:
            for item_str in stdin.split():
                yield item_str
    iter_var = stdin_iter()
    {%- endif %}
    {{ input_process }}
    solve({{ solve_argument }})


if __name__ == '__main__':
    main()
