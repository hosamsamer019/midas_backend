# Messaging System Enhancement TODO

## Backend Enhancements

### 1. Update Message Model
- [x] Add GenericForeignKey fields (content_type, object_id, content_object) for contextual linking
- [x] Add message_type field (direct, contextual, broadcast)
- [x] Add is_archived field (instead of delete)
- [x] Add department field for filtering
- [x] Add date_range_start, date_range_end for time-based context

### 2. Create MessageAttachment Model
- [x] Model with message FK, file field, uploaded_at
- [x] Support PDF, images, etc.

### 3. Update Permissions
- [x] Create MessagingPermissions class
- [x] Admin: send/receive/broadcast
- [x] Doctor: send to admins/doctors, receive
- [x] Lab: send to admins, receive
- [x] Viewer: receive only

### 4. Enhance Views
- [x] Add search action (by sender, date, keyword, message_type)
- [x] Add broadcast action for admins
- [x] Add contextual_messages action (filter by linked entity)
- [x] Update permissions in views
- [x] Add archive/unarchive actions

### 5. Update Serializers
- [x] Add fields for new model fields
- [x] Add attachment serializer
- [x] Handle GenericForeignKey serialization

### 6. Create Migration
- [x] Generate and run migration for model changes

## Frontend Enhancements

### 7. Update Messages Component
- [ ] Add contextual messaging UI (link to reports, bacteria, etc.)
- [ ] Add attachment upload in compose
- [ ] Add search bar
- [ ] Add broadcast option for admins
- [ ] Add archive functionality
- [ ] Update message display to show linked context

### 8. Add Notification System
- [ ] Badge for unread count
- [ ] In-system notifications
- [ ] Optional email notifications (future)

## Testing

### 9. Test Backend
- [x] Test permissions
- [x] Test contextual linking
- [x] Test attachments
- [x] Test search

### 10. Test Frontend
- [ ] Test UI updates
- [ ] Test integration with backend

## Documentation

### 11. Update API Documentation
- [ ] Document new endpoints
- [ ] Document message types and linking
