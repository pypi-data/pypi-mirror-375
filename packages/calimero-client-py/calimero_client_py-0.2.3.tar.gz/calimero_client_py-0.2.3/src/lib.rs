//! Standalone Python bindings for Calimero client
//! 
//! This crate provides Python bindings that can be built independently
//! without requiring the full Calimero workspace.

// Re-export the Python bindings module
pub mod python;

// The main Python module function is defined in python.rs
// This lib.rs file serves as the entry point for the crate
