# BRD Authentication System Implementation Plan

## 🎯 Objective
Implement the Login and Authorization Management System according to the BRD specifications, replacing the current Django-based system with a custom database schema.

## 📊 Current vs BRD Analysis

### Current System
- Uses Django's AbstractUser with simple role field
- Extensive audit logging with multiple log types
- Hardcoded permissions in code
- Self-registration possible

### BRD Requirements
- Custom User table with specific fields
- Separate Roles, Permissions, Role_Permissions tables
- Simplified Audit_Log table
- Database-driven RBAC
- Admin-only user creation
- No self-registration

## 🏗 Implementation Plan

### Phase 1: Database Schema Updates
1. **Update User Model** (`users/models.py`)
   - Replace AbstractUser with custom fields
   - Add: user_id, full_name, email, password_hash, role_id, status, created_at, last_login
   - Remove: username, first_name, last_name, etc.

2. **Create Roles Model** (`users/models.py`)
   - role_id (PK)
   - role_name (Admin/Doctor/Lab/Viewer)
   - description

3. **Create Permissions Model** (`users/models.py`)
   - permission_id (PK)
   - permission_name
   - description

4. **Create Role_Permissions Model** (`users/models.py`)
   - role_id (FK)
   - permission_id (FK)
   - Composite PK

5. **Update Audit_Log Model** (`audit/models.py`)
   - Simplify to: log_id, user_id, action_type, timestamp, ip_address
   - Remove complex logging types

### Phase 2: Authentication Backend
1. **Update Authentication Backend** (`users/backends.py`)
   - Modify to work with custom User model
   - Support email-based authentication

2. **Update Login View** (`api/views.py`)
   - Adapt CustomTokenObtainPairView for new User model
   - Update audit logging

### Phase 3: RBAC System
1. **Create Permission Management** (`api/permissions.py`)
   - Replace hardcoded permissions with database queries
   - Implement dynamic RBAC checking

2. **Update Permission Classes**
   - AdminPermissions, DoctorPermissions, etc.
   - Query database for permissions

### Phase 4: Admin Panel Updates
1. **User Management Views**
   - Admin-only user creation
   - Role assignment
   - User status management

2. **Remove Self-Registration**
   - Disable RegisterView or make admin-only

### Phase 5: Data Migration
1. **Create Migration Scripts**
   - Migrate existing users to new schema
   - Create default roles and permissions
   - Migrate audit logs

### Phase 6: Testing & Validation
1. **Update Test Scripts**
   - Adapt to new schema
   - Test RBAC functionality
   - Validate audit logging

## 🔄 Dependencies
- Django migrations for schema changes
- Update all imports and references to User model
- Frontend may need updates for user fields

## ⚠️ Breaking Changes
- User model changes will affect all user-related functionality
- Audit logging simplified
- Permission system completely rewritten

## ✅ Success Criteria
- Users table matches BRD specification
- RBAC works with database-driven permissions
- Admin-only user creation enforced
- Audit logs capture required fields
- Login system functional with new schema
