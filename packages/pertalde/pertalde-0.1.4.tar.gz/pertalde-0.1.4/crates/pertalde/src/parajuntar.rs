use clap::{Parser, ValueHint};
use colored::Colorize;

use std::error::Error;
use std::path::PathBuf;

#[derive(Parser, Debug)]
#[command(
    name = "parajuntar",
    version,
    about = "Join event values among traces and types by semantic",
    trailing_var_arg = false
)]
struct Cli {
    #[command(flatten)]
    pub cmd: pertalde_unir::Args,

    /// the traces to process
    #[arg(
        global = true,
        value_name = "TRACE",
        num_args = 1,
        allow_hyphen_values = true,
        value_hint = ValueHint::FilePath
    )]
    pub traces: Vec<PathBuf>,
}

fn main() -> Result<(), Box<dyn Error>> {
    println!(
        "{}\n{}\n{}\n{}\n{}\n",
        "!!!\nWarning: This command is beeing deprecated and will be removed in the furure!"
            .yellow()
            .bold(),
        "You can use instead:",
        "\tptd unir --help".bold(),
        "This new version also includes other command line tools which you can check by:",
        "\tptd --help".bold()
    );

    let cli = Cli::parse();
    pertalde_unir::run(cli.cmd, cli.traces)
}
