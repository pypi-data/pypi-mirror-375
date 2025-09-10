#[derive(clap::Args, Debug)]
pub struct Args {
    /// compress the output traces with gzip
    #[arg(long = "compress", short = 'c')]
    pub compress: bool,

    /// the sufix to use for the new files.
    #[arg(long = "sufix", default_value = "chop")]
    pub sufix: String,

    /// start time of the cutter
    #[arg(long = "start", short = 's')]
    pub start: u64,

    /// end time of the cutter
    #[arg(long = "end", short = 'e')]
    pub end: u64,

    /// break state or not
    #[arg(long = "break-state")]
    pub break_state: bool,

    ///
    #[arg(long = "discard-first-state")]
    pub discard_first_state: bool,

    ///
    #[arg(long = "discard-last-state")]
    pub discard_last_state: bool,

    #[arg(long = "discard_boundary_events")]
    pub discard_boundary_events: bool,
}
