# Layout Changes

{{layout_changes.to_markdown()}}


## Updated Pages

| Page | Change Count |
| ---- | ------------ |
{% for section in layout_changes.sections -%}
| [{{ section.display_name() }}]({{section.path_name()}}/main.md) | {{ section.change_count() }} |
{% endfor %}