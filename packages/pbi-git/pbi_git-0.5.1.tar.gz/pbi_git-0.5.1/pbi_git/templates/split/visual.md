{% if visual.change_type != ChangeType.NO_CHANGE %}
### Visual: {{ visual.display_name() }}

{{ visual.to_markdown() }}
{% endif %}
