// Create database and user
db = db.getSiblingDB('n8n_clone');

// Create a user for the application
db.createUser({
  user: 'app_user',
  pwd: 'app_password',
  roles: [
    {
      role: 'readWrite',
      db: 'n8n_clone'
    }
  ]
});

// Create collections
db.createCollection('users');
db.createCollection('workflows');
db.createCollection('workflow_executions');
db.createCollection('node_templates');
db.createCollection('workflow_checkpoints');

print('MongoDB initialized successfully');