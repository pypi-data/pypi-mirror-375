{% if section.change_type != ChangeType.NO_CHANGE %}
## Section: {{ section.display_name() }}

{{ section.to_markdown() }}

{% endif  %}


## Visual Changes

| Visual Element | Change Type |
| -------------- | ----------- |
{% for visual in section.visuals -%}
{% if visual.change_type != ChangeType.NO_CHANGE -%}
| [{{ visual.display_name() }}](visuals/{{ visual.path_name() }}.md) | {{ visual.change_count() }} |
{% endif -%}
{% endfor %}