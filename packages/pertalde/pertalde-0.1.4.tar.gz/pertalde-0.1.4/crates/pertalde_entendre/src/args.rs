use clap::Parser;
use std::path::PathBuf;

#[derive(Debug, Parser)]
pub struct Args {
    /// The file to translate
    pub csv_file: PathBuf,

    /// The event type to use for the translation
    pub event_type: u64,
}
