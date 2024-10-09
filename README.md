# ailab-datastore

## Overview

This monorepo contains the code for the AI Lab Datastore project. The project
aims to provide a data store with metadata for images and other data types
related to different projects. The datastore folder contains common code for
projects used by Nachet and Fertiscan projects.

## Monorepo Structure

The monorepo consists of three main folders: `datastore`, `fertiscan`, and
`nachet`. Here's an overview:

- **datastore**: This is the shared codebase used by both Nachet and Fertiscan
  projects. Common features that are relevant to both projects are implemented
  here.
- **fertiscan**: This folder contains the code and configurations specific to
  the Fertiscan project. Fertiscan is dependent on the datastore for shared
  functionality. The backend for this project is located at
  [fertiscan-backend](https://github.com/ai-cfia/fertiscan-backend). It
  references the datastore package from `requirements.txt` using a tag like
  `git+https://github.com/ai-cfia/ailab-datastore.git@v1.0.0-fertiscan-datastore`.
- **nachet**: This folder contains the code and configurations specific to the
  Nachet project. Nachet is also dependent on the datastore. The backend for
  this project is located at
  [nachet-backend](https://github.com/ai-cfia/nachet-backend), and it references
  the datastore package similarly via `nachet-datastore
  @git+https://github.com/ai-cfia/ailab-datastore.git@v1.0.0-nachet-datastore`.

Additionally, there is a common `tests` folder that aggregates tests for all
three folders (datastore, fertiscan, and nachet). All project-specific tests
should be placed in their respective folders under `./tests`.

## Package Release Workflow

The monorepo has a CI/CD pipeline in place that automates the release process
for both Nachet and Fertiscan packages. Here's how it works:

1. **Version Bump Check**:
   - The pipeline checks if changes are made in the `nachet`, `fertiscan`, or
     `datastore` folders when a pull request is created.
   - If changes are made to `datastore`, the pipeline validates the version
     bumps for both the `nachet_pyproject.toml` and `fertiscan_pyproject.toml`
     files.
   - If changes are made to the `nachet` folder, it triggers version bump
     validation for `nachet_pyproject.toml`. Similarly, changes to the
     `fertiscan` folder trigger validation for `fertiscan_pyproject.toml`.
   - A pull request (PR) that modifies any of these areas must update the
     respective version in the corresponding `pyproject.toml`.

2. **PR Merge and Release**:
   - Once a PR is merged into `main`, the pipeline runs again and enters the
     package release stage.
   - The pipeline creates a new release based on the bumped version and project.
     For example, if changes were made to the `nachet` folder, the
     `nachet-datastore` package will be released, tagged with the new version.
   - Backend projects (e.g., `fertiscan-backend` and `nachet-backend`) can then
     update their dependencies to point to the new release version.
   - Renovate will automatically detect the new version and open a PR in the
     backend repository to update the package.

3. **Release Handling**:
   - Releases are versioned with tags like `v1.0.0-nachet-datastore` or
     `v1.0.0-fertiscan-datastore`.
   - If a release with the same tag already exists, the pipeline will fail. In
     such cases, you can delete the existing release if necessary to retry the
     process.

For detailed information on the specific workflows and configurations, please
refer to the respective README files in the `nachet` and `fertiscan` folders.
