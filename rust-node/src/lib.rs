pub mod user;
pub mod veracity;

use thiserror::Error;
use uuid::Uuid;

#[derive(Error, Debug)]
pub enum BrimError {
    #[error("Authentication failed")]
    AuthError,
    #[error("Authorization failed: {0}")]
    AuthorizationError(String),
    #[error("Invalid input: {0}")]
    ValidationError(String),
    #[error("Resource not found: {0}")]
    NotFound(String),
    #[error("Internal error: {0}")]
    Internal(String),
}

pub type Result<T> = std::result::Result<T, BrimError>;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Role {
    GlobalAdmin,
    GroupAdmin,
    Validator,
    User,
}

pub trait Entity {
    fn id(&self) -> Uuid;
    fn created_at(&self) -> chrono::DateTime<chrono::Utc>;
    fn updated_at(&self) -> chrono::DateTime<chrono::Utc>;
} 