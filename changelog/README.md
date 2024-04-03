# Changelog

## General Information

Changes in the changelog are divided into six groups in the following order:
- **Features**
- **Changes**
- **Fixes**
- **Breaking Changes**
- **Chores**
- **Documentation**

Apart from **Breaking Changes**, all of these correspond to pull request titles. Breaking changes are defined separately, as anything that present a change that could be breaking for users.

## Writing the Changelog Entries

Details about the changes in each pull request must be added to all pull requests. In order to keep the changelogs clean and uniform, changelog entries must be written in the following template:

```json
{
  "pr_number": 0,
  "changes": [
    {
      "change": "Features | Changes | Fixes | Breaking Changes | Chores | Documentation",
      "description": "A description of the change you've made."
    }
  ]
}
```

There can be multiple entries in one pull request, but it's recommended to keep pull reuqests small and related to a single change. Of course, this doesn't necessarily work in practice at all times, but this is generally the ideal. Keep it in mind when making changes.
