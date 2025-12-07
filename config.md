# Config
This is documentation for this add-on's configuration (stored in config.json within the add-on's folder), in *markdown* format.

## Examples:

### Default configuation values:

Displays preset as 5th column, uses the preset cog image, and applies default styling to right-align and truncate excessively long preset names

```json
{
    "presetColumnNumber": 100,
    "displayPresetCog": true,
    "presetStyle": "text-align: left; display: block; max-width: 300px; overflow: hidden; white-space: nowrap; text-overflow: ellipsis;",
    "presetHeaderAlign": "left",
    "presetHeaderStyle": "text-align: left; padding: 4px 12px;",
    "presetHeaderTitle": "Preset"
}
```

### Preset as leftmost column with right aligned text, hide preset cog image, only show first 100px of preset name, rename column to Option Set Name
```json
{
    "presetColumnNumber": 0,
    "displayPresetCog": false,
    "presetStyle": "text-align: right; display: block; max-width: 100px; overflow: hidden; white-space: nowrap; text-overflow: ellipsis;",
    "presetHeaderAlign": "right",
    "presetHeaderStyle": "text-align: right; padding: 4px 12px;",
    "presetHeaderTitle": "Option Set Name"
}
```

### Preset as leftmost column
Fields not provided in the JSON config for this add-on will revert to their default values. Column is zero-indexed (first column = 0).
```json
{
    "presetColumnNumber": 0
}
```