aq# IRD Document Implementation TODO

## Information Gathered
- Current User model has most fields but missing `create_by` (FK to self).
- Role model has 'Presenter' instead of 'Viewer'.
- Permission and RolePermission models exist and match.
- AuditLog model needs update to match BRD: record_id, action_type, performed_by, timestamp, details.
- Admin_Email_Control model is missing.
- UserManager needs update to handle create_by in account creation.

## Plan
1. Update users/models.py:
   - Add create_by field to User model.
   - Change Role choices from 'Presenter' to 'Viewer'.
   - Update UserManager to set create_by when creating users.
2. Add Admin_Email_Control model to users/models.py.
3. Update audit/models.py:
   - Change AuditLog to match BRD fields.
4. Create migrations for changes.
5. Update any dependent code if needed.

## Dependent Files to be edited
- Data_Analysis_Project/users/models.py
- Data_Analysis_Project/audit/models.py

## Followup steps
- Run migrations.
- Test the models.
- Update any views or serializers if needed.

## Completed Tasks
- [x] Updated Role choices to 'Viewer'
- [x] Added create_by field to User model
- [x] Added pass_hash field to User model
- [x] Changed status choices to include 'Suspended'
- [x] Renamed fields to match BRD (role_id, create_at)
- [x] Added AdminEmailControl model
- [x] Updated UserManager to handle created_by
- [x] Updated AuditLog model to match BRD
- [x] Created migration files for users and audit apps
