# Authentication System Implementation TODO

## Phase 1: User Model Updates
- [x] Update User model ROLE_CHOICES to: admin, doctor, lab, viewer
- [x] Create database migration for role changes
- [x] Update default role to 'viewer'

## Phase 2: Authentication Updates
- [x] Update login to use email instead of username
- [x] Create custom authentication backend for email login
- [x] Update CustomTokenObtainPairView to use email
- [x] Implement logout endpoint with audit logging

## Phase 3: Permission System
- [x] Create api/permissions.py with role-based permission classes
- [ ] AdminPermissions - full access
- [ ] DoctorPermissions - dashboard, filters, reports, AI, messaging
- [ ] LabPermissions - upload data, view after approval, limited AI
- [ ] ViewerPermissions - login, view dashboard/graphs only

## Phase 4: Audit Logging System
- [x] Create audit app with models for:
  - LoginLog (user, login_time, ip_address)
  - UploadLog (user, file, upload_time, status)
  - ModificationLog (user, model, object_id, field, old_value, new_value, timestamp)
  - ReportLog (user, report_type, created_at)
  - AIUsageLog (user, query, response, timestamp)
- [x] Create audit/migrations
- [ ] Add audit logging to relevant views

## Phase 5: Internal Messaging System
- [ ] Create messaging app with Message model
- [ ] Message fields: sender, recipient, subject, content, timestamp, read_status
- [ ] Views for sending/receiving messages
- [ ] Permissions: doctors send to admin, admin to all, lab to admin

## Phase 6: Update View Permissions
- [ ] Update all API views with appropriate role permissions
- [ ] Implement upload approval workflow (pending -> approved)
- [ ] Add edit restrictions (admin only for historical data)
- [ ] Update report permissions (doctors can create/print/send, cannot delete)

## Phase 7: Update Serializers and URLs
- [x] Update UserSerializer to include role
- [x] Update RegisterSerializer for email validation
- [x] Add new URL patterns for logout, messaging, audit logs

## Phase 8: Testing and Migration
- [ ] Run database migrations
- [ ] Test authentication flow with different roles
- [ ] Test permission restrictions
- [ ] Verify audit logging
- [ ] Test messaging system
