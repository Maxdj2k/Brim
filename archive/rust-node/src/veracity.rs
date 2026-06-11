use crate::{Entity, Role, Result, BrimError};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use uuid::Uuid;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Claim {
    id: Uuid,
    creator_id: Uuid,
    content: String,
    status: ClaimStatus,
    validations: Vec<Validation>,
    created_at: DateTime<Utc>,
    updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum ClaimStatus {
    Pending,
    Validated,
    Rejected,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Validation {
    validator_id: Uuid,
    is_valid: bool,
    comment: Option<String>,
    timestamp: DateTime<Utc>,
}

impl Claim {
    pub fn new(creator_id: Uuid, content: String) -> Self {
        let now = Utc::now();
        Self {
            id: Uuid::new_v4(),
            creator_id,
            content,
            status: ClaimStatus::Pending,
            validations: Vec::new(),
            created_at: now,
            updated_at: now,
        }
    }

    pub fn add_validation(&mut self, validator_id: Uuid, is_valid: bool, comment: Option<String>) -> Result<()> {
        let validation = Validation {
            validator_id,
            is_valid,
            comment,
            timestamp: Utc::now(),
        };

        // Check if validator has already validated this claim
        if self.validations.iter().any(|v| v.validator_id == validator_id) {
            return Err(BrimError::ValidationError("Validator has already validated this claim".to_string()));
        }

        self.validations.push(validation);
        self.update_status();
        self.updated_at = Utc::now();
        Ok(())
    }

    fn update_status(&mut self) {
        if self.validations.is_empty() {
            return;
        }

        let total = self.validations.len() as f64;
        let valid_votes = self.validations.iter().filter(|v| v.is_valid).count() as f64;
        let validation_ratio = valid_votes / total;

        self.status = if validation_ratio >= 0.66 {
            ClaimStatus::Validated
        } else if validation_ratio <= 0.33 {
            ClaimStatus::Rejected
        } else {
            ClaimStatus::Pending
        };
    }
}

impl Entity for Claim {
    fn id(&self) -> Uuid { self.id }
    fn created_at(&self) -> DateTime<Utc> { self.created_at }
    fn updated_at(&self) -> DateTime<Utc> { self.updated_at }
} 