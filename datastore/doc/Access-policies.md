# Access Policies

## Overview

Our application uses a combination of roles and permissions to manage access
control. This system allows us to attribute specific roles to users, which
define their access to various features of the application. Additionally,
permissions are used to manage access to user-owned resources (Discretionary
access control).

## Roles

Roles are used to define the overall access level of a user within the
application. The roles are stored in the `roles` table (The name needs to be
plural because role is a reserved word in PostgrSQL) and include the following:

- **dev**: Developers with full access to all features.
- **admin**: Administrators with full access to all features except the dev
  menu.
- **team leader**: Users with elevated privileges to manage teams (groups).
- **inspector**: Users with limited access.

## Permissions

Permissions are used to manage access to user-owned resources called containers.
A user can manage who can see and upload content into their container. The
permissions are stored in the `permission` table and include the following:

- **read**: Permission to view content in a container.
- **write**: Permission to upload/delete content to a container.
- **owner**: Full control over the container, including managing permissions for
  other users.
