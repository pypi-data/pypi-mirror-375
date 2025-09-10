#[derive(clap::Args, Debug)]
pub struct Args {
    #[arg(short = 'n', default_value = "20", value_name = "NUM")]
    /// show the first NUM distinct records with more counts
    pub number: usize,

    #[arg(long = "all")]
    /// show all distinct records
    pub show_all: bool,
}
