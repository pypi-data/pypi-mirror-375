#[derive(clap::Args, Debug)]
pub struct Args {
    /// when enabled the program will check the whole trace and report all ill-formated records
    #[arg(long = "exhaustive", short = 'e')]
    pub exhaustive_check: bool,
}
