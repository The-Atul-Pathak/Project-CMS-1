SELECT * FROM platform_admins;

SELECT * FROM platform_sessions;

SELECT * FROM plans;

select * from features;

SELECT * from company_subscriptions;

SELECT * from company_features;

SELECT * FROM platform_activity_logs ORDER BY created_at DESC;

SELECT * FROM audit_logs ORDER BY timestamp DESC;

SELECT * from users;

Select * from user_sessions;

select * from roles;

select * from roles_features;

select * from feature_bundle_pages;

UPDATE feature_bundle_pages
SET route = '/user_management'
WHERE id = 1;

select * from role_permissions;

select * from user_roles;

select * from company_activity_logs

SELECT id, company_name, status
FROM companies;


Select * from companies;

