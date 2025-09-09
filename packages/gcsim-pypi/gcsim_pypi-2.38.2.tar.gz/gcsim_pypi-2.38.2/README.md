# gcsim Binary for PyPI

This document provides guidelines for releasing the [gcsim](https://github.com/genshinsim/gcsim) binary to PyPI.

## Release Methods

There are three primary methods to release a new version of the gcsim binary to PyPI:

1. **Automated Weekly Releases**: The release workflow is automatically executed every Sunday.
2. **Manual Workflow Trigger**: You can manually initiate the release workflow as needed.
3. **Creating a Release**: Opt to create a release through GitHub, which triggers the release process.

## Important Considerations

Before manually and locally publishing a release, it's crucial to run the `scripts.py` file to ensure all necessary preparations are complete. Use the following command:

```
python scripts.py
```