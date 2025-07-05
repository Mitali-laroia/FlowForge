// Create the database and user
db = db.getSiblingDB('n8n_clone');

db.createUser({
  user: 'n8n_user',
  pwd: 'n8n_password',
  roles: [
    {
      role: 'readWrite',
      db: 'n8n_clone'
    }
  ]
});

// Create collections with initial indexes
db.users.createIndex({ "username": 1 }, { unique: true });
db.users.createIndex({ "email": 1 }, { unique: true });
db.workflows.createIndex({ "owner_id": 1 });
db.workflow_executions.createIndex({ "workflow_id": 1 });
db.workflow_executions.createIndex({ "status": 1 });