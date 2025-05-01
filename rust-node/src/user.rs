use crate::{Entity, Role, Result, BrimError};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use uuid::Uuid;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct User {
    id: Uuid,
    username: String,
    password_hash: String,
    role: Role,
    groups: Vec<Uuid>,
    created_at: DateTime<Utc>,
    updated_at: DateTime<Utc>,
}

impl User {
    pub fn new(username: String, password: String, role: Role) -> Self {
        let now = Utc::now();
        Self {
            id: Uuid::new_v4(),
            username,
            password_hash: Self::hash_password(&password),
            role,
            groups: Vec::new(),
            created_at: now,
            updated_at: now,
        }
    }

    fn hash_password(password: &str) -> String {
        use sha2::{Sha256, Digest};
        let mut hasher = Sha256::new();
        hasher.update(password.as_bytes());
        hex::encode(hasher.finalize())
    }

    pub fn verify_password(&self, password: &str) -> bool {
        self.password_hash == Self::hash_password(password)
    }

    pub fn add_to_group(&mut self, group_id: Uuid) {
        if !self.groups.contains(&group_id) {
            self.groups.push(group_id);
            self.updated_at = Utc::now();
        }
    }
}

impl Entity for User {
    fn id(&self) -> Uuid { self.id }
    fn created_at(&self) -> DateTime<Utc> { self.created_at }
    fn updated_at(&self) -> DateTime<Utc> { self.updated_at }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Group {
    id: Uuid,
    name: String,
    admin_id: Uuid,
    members: Vec<Uuid>,
    created_at: DateTime<Utc>,
    updated_at: DateTime<Utc>,
}

impl Group {
    pub fn new(name: String, admin_id: Uuid) -> Self {
        let now = Utc::now();
        Self {
            id: Uuid::new_v4(),
            name,
            admin_id,
            members: vec![admin_id],
            created_at: now,
            updated_at: now,
        }
    }

    pub fn add_member(&mut self, user_id: Uuid) -> Result<()> {
        if !self.members.contains(&user_id) {
            self.members.push(user_id);
            self.updated_at = Utc::now();
            Ok(())
        } else {
            Err(BrimError::ValidationError("User already in group".to_string()))
        }
    }
}

impl Entity for Group {
    fn id(&self) -> Uuid { self.id }
    fn created_at(&self) -> DateTime<Utc> { self.created_at }
    fn updated_at(&self) -> DateTime<Utc> { self.updated_at }
} 