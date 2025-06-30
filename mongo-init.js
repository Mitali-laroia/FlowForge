// Create database and collections
db = db.getSiblingDB('flowforge');

// Create collections for workflow states
db.createCollection('workflow_states');
db.createCollection('checkpoints');

// Create indexes for better performance
db.workflow_states.createIndex({ "thread_id": 1 }, { unique: true });
db.checkpoints.createIndex({ "thread_id": 1 });
db.checkpoints.createIndex({ "timestamp": 1 });

print('MongoDB initialized for FlowForge');