# User Training Guide - Authentication & Permissions System

## Welcome to the Data Analysis System

This guide will help you understand your role, permissions, and how to use the system effectively.

---

## 🔐 **Getting Started - Login Process**

### **How to Log In:**
1. Open your web browser and go to the system URL
2. Click "Login" or go to `/api/auth/login/`
3. Enter your **email address** and **password**
4. Click "Sign In"

### **Login Security Features:**
- ✅ **Email-based authentication** (not username)
- ✅ **Secure password encryption**
- ✅ **Session tracking** with automatic logout
- ✅ **IP address logging** for security

### **Forgot Password:**
- Contact your system administrator
- They can reset your password through the admin panel

---

## 👥 **Understanding User Roles**

### **1. Admin Role** 👑
**What you can do:**
- ✅ **Full System Access** - All features and data
- ✅ **User Management** - Create, edit, delete user accounts
- ✅ **Data Control** - Upload, modify, delete all data
- ✅ **Reports** - Generate, print, send, delete any report
- ✅ **AI Features** - Use all artificial intelligence tools
- ✅ **Messaging** - Send messages to all users
- ✅ **Approvals** - Approve/reject data uploads

**What you cannot do:**
- ❌ Nothing - you have full access

**Daily Tasks:**
- Review and approve data uploads
- Manage user accounts and permissions
- Generate system reports
- Monitor system usage and security

---

### **2. Doctor Role** 👨‍⚕️
**What you can do:**
- ✅ **Dashboard Access** - View analytics and graphs
- ✅ **Data Analysis** - Use filters for period, bacteria, section
- ✅ **Reports** - Create, print, and email reports
- ✅ **AI Tools** - Use antibiotic recommendations and medical Q&A
- ✅ **Messaging** - Send messages to admin only

**What you cannot do:**
- ❌ Modify or delete raw data
- ❌ Delete reports (can only create/print/send)
- ❌ Upload data files
- ❌ Access user management

**Daily Tasks:**
- Review patient data and analytics
- Generate reports for your cases
- Use AI for antibiotic recommendations
- Communicate with admin for data requests

---

### **3. Lab/Data Entry Role** 🧪
**What you can do:**
- ✅ **Data Upload** - Upload Excel, PDF, or image files
- ✅ **Data Review** - View uploaded data after approval
- ✅ **Limited AI** - Basic AI features for data validation
- ✅ **Messaging** - Send messages to admin only

**What you cannot do:**
- ❌ Modify old data results
- ❌ Create official reports
- ❌ Delete any data
- ❌ Send messages to doctors

**Daily Tasks:**
- Upload new test results and data files
- Review your uploaded data
- Contact admin for data corrections
- Ensure data quality before submission

---

### **4. Viewer Role** 👁️
**What you can do:**
- ✅ **Login Access** - Access the system
- ✅ **Dashboard View** - View basic graphs and statistics
- ✅ **Read-Only** - View approved data and analytics

**What you cannot do:**
- ❌ Upload any files
- ❌ Modify any data
- ❌ Create reports
- ❌ Use AI features
- ❌ Send messages

**Daily Tasks:**
- Review system dashboards and statistics
- Monitor overall data trends
- Request access upgrades through admin

---

## 💬 **Internal Messaging System**

### **How Messaging Works:**
- **Doctors** can message **Admin** only
- **Lab staff** can message **Admin** only
- **Admin** can message **All users**
- **Viewers** cannot send messages

### **Sending a Message:**
1. Go to Messages section
2. Click "Compose" or "New Message"
3. Select recipient (based on your role)
4. Enter subject and message content
5. Click "Send"

### **Viewing Messages:**
- **Inbox** - Messages sent to you
- **Sent** - Messages you sent
- **Unread** - Messages you haven't read yet

### **Message Rules:**
- ❌ Messages cannot be deleted (permanent record)
- ✅ All messages are logged for audit purposes
- ✅ Read status is tracked

---

## 📊 **Data Upload & Approval Process**

### **For Lab Staff:**
1. **Upload File** - Submit Excel, PDF, or image files
2. **Status: Pending** - File awaits admin approval
3. **Admin Review** - Admin checks data quality
4. **Approval/Rejection** - File becomes available or is rejected
5. **Data Access** - View approved data in the system

### **For Admin:**
1. **Review Uploads** - Check pending files in admin panel
2. **Quality Check** - Verify data accuracy and completeness
3. **Approve/Reject** - Grant access or request corrections
4. **Audit Trail** - All approvals are logged

### **Upload Rules:**
- 📁 **File Types**: Excel (.xlsx), PDF, Images
- ⏳ **Approval Required**: No data enters analysis without admin approval
- 🔒 **No Direct Editing**: Lab cannot modify data after upload
- 📋 **Audit Logging**: All uploads and approvals tracked

---

## 📋 **Report Generation & Sharing**

### **Report Permissions by Role:**

| Action | Admin | Doctor | Lab | Viewer |
|--------|-------|--------|-----|--------|
| Create Report | ✅ | ✅ | ❌ | ❌ |
| Print Report | ✅ | ✅ | ❌ | ❌ |
| Email Report | ✅ | ✅ | ❌ | ❌ |
| Delete Report | ✅ | ❌ | ❌ | ❌ |

### **Creating Reports:**
1. Go to Reports section
2. Select data filters (period, bacteria, section)
3. Choose report type
4. Generate and review
5. Print, email, or save

### **Report Types:**
- **Patient Reports** - Individual case analysis
- **Trend Reports** - Data over time periods
- **Summary Reports** - Department/section overviews
- **AI Reports** - Antibiotic recommendations

---

## 🤖 **AI Features & Usage**

### **AI Permissions by Role:**

| Feature | Admin | Doctor | Lab | Viewer |
|---------|-------|--------|-----|--------|
| Antibiotic Recommendations | ✅ | ✅ | ❌ | ❌ |
| Medical Q&A | ✅ | ✅ | ❌ | ❌ |
| Data Analysis | ✅ | ✅ | ✅ | ❌ |
| Interpretations | ✅ | ✅ | ❌ | ❌ |

### **Using AI Features:**
1. Navigate to AI section
2. Select appropriate tool
3. Input your query or data
4. Review AI recommendations
5. Apply to patient care or data analysis

### **AI Usage Logging:**
- ✅ All AI interactions logged
- ✅ User identification tracked
- ✅ Query and response stored
- ✅ Audit trail maintained

---

## 🔒 **Security & Best Practices**

### **Password Security:**
- Use strong passwords (8+ characters, mixed case, numbers, symbols)
- Never share your password
- Change password regularly
- Contact admin for password resets

### **Session Management:**
- Always log out when finished
- Don't leave sessions unattended
- System auto-logs out inactive sessions
- Use "Logout" button, don't just close browser

### **Data Handling:**
- Only access data you need for your role
- Don't share sensitive patient information inappropriately
- Report security concerns to admin immediately
- Follow HIPAA/data protection guidelines

---

## 🚨 **Common Issues & Solutions**

### **Can't Log In:**
- Check email address is correct
- Verify password (case-sensitive)
- Contact admin if account locked
- Check internet connection

### **Access Denied Errors:**
- Verify you have correct permissions for the action
- Check your user role with admin
- Some features require admin approval
- Contact admin for permission upgrades

### **Upload Issues:**
- Check file format (Excel, PDF, images only)
- Ensure file is not corrupted
- Contact admin if upload fails
- Wait for admin approval before data is visible

### **Messaging Problems:**
- Check recipient permissions (role restrictions apply)
- Verify message content doesn't violate policies
- Contact admin for messaging issues

---

## 📞 **Getting Help**

### **Who to Contact:**
- **Technical Issues**: System Administrator
- **Permission Questions**: Your Department Head or Admin
- **Data Questions**: Lab Supervisor or Admin
- **Training Needs**: HR or System Administrator

### **Support Channels:**
- **Internal Messaging**: Use system messaging for non-urgent issues
- **Email**: Contact admin directly for urgent matters
- **Phone**: Call IT support for technical emergencies
- **Documentation**: Refer to this guide and API documentation

---

## 📈 **System Monitoring & Logs**

### **What Gets Logged:**
- ✅ User login/logout times and IP addresses
- ✅ File uploads and approval actions
- ✅ Data modifications and changes
- ✅ Report generation and sharing
- ✅ AI feature usage
- ✅ Messages sent and received

### **Why Logging Matters:**
- **Security**: Track unauthorized access attempts
- **Compliance**: Meet regulatory requirements
- **Auditing**: Verify system usage and data changes
- **Troubleshooting**: Debug issues and system problems

---

## 🎯 **Quick Reference Guide**

### **Role Permission Summary:**

```
Admin:    Full access to everything
Doctor:   Dashboard, analytics, reports, AI, messaging(admin)
Lab:      Upload data, view approved data, limited AI, messaging(admin)
Viewer:   Dashboard view only, no modifications
```

### **Key URLs:**
- Login: `/api/auth/login/`
- Dashboard: `/api/dashboard/`
- Reports: `/api/reports/`
- Messages: `/api/messaging/messages/`
- Uploads: `/api/uploads/`

### **Emergency Contacts:**
- System Admin: [Admin Email/Phone]
- IT Support: [IT Email/Phone]
- Security Issues: Report immediately to admin

---

**Remember**: Your role permissions are designed to protect patient data and ensure system security. Always follow your role guidelines and report any unusual activity to your administrator.

**Welcome to the team!** 👋
