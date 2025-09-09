# mkdocs-search-izsam

This MkDocs plugin enhances the native search functionality by:

* Enabling local search without CORS issues
* Indexing YAML metadata from Markdown files for improved search capabilities

## Local Search Functionality

The plugin generates two JavaScript files—one for `config` and one for `docs`—which can be included in your theme as follows:

```html
<script src="{{ 'search/search_config.js'|url }}"></script>
<script src="{{ 'search/search_docs.js'|url }}"></script>
```

This approach eliminates CORS issues typically encountered with `loadJSON` and the native `worker.js` model.

#### Important

To leverage these JavaScript files and bypass the native search worker, set the `search_index_only` option to `true` in your theme configuration:

```yaml
theme:
  name: null
  custom_dir: your_custom_theme
  include_search_page: true
  search_index_only: true
```

## Search Metadata YAML Support

The plugin indexes YAML metadata defined in your Markdown files, making these fields searchable. To exclude specific metadata keys from the search index, add an `exclude_meta_keys` entry to your file's metadata, listing the keys to ignore. For example:

```yaml
exclude_meta_keys:
  - sections.type
  - sections.data.link
```

## Setup

Install the plugin using pip:

`pip install mkdocs-izsam-search`

Activate the plugin in `mkdocs.yml`:

```yaml
plugins:
  - izsam-search
```

It is possible to use same config options of the native search plugin:

```yaml
- izsam-search:
        lang: en
```

You can then implement search using your preferred JavaScript library (for example, `lunr.js`). For more details, see the [MkDocs documentation on search and themes](https://www.mkdocs.org/dev-guide/themes/#search-and-themes).

## See Also

[mkdocs-plugins]: http://www.mkdocs.org/user-guide/plugins/
[mkdocs-template]: https://www.mkdocs.org/user-guide/custom-themes/#template-variables
[mkdocs-block]: https://www.mkdocs.org/user-guide/styling-your-docs/#overriding-template-blocks
