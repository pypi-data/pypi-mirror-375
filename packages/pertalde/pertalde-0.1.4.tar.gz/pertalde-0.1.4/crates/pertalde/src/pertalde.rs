use clap::{Parser, Subcommand, ValueHint};
use colored::Colorize;

use std::error::Error;
use std::path::PathBuf;

#[derive(Parser, Debug)]
#[command(
    name = "pertalde",
    version,
    about = "A set of tools to manipulate paraver traces.",
    subcommand_required = true,
    trailing_var_arg = true
)]
struct Cli {
    #[command(subcommand)]
    command: Command,

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

#[derive(Subcommand, Debug)]
enum Command {
    /// Join event values among traces and types by semantic.
    #[command(visible_alias = "u")]
    Unir(pertalde_unir::Args),

    /// Translate values from a csv file based on pcf information.
    #[command(visible_alias = "e")]
    Entendre(pertalde_entendre::Args),

    /// Check that a trace is not ill-formated.
    #[command(visible_alias = "c")]
    Comprovar(pertalde_comprovar::Args),

    /// Synchonize paraver traces based on a reference event.
    #[command(visible_alias = "sync")]
    Sincronitzar(pertalde_sincronitzar::Args),

    /// Chop a trace with a start and end time.
    #[command(visible_aliases = ["t", "chop" ])]
    Tallar(pertalde_tallar::Args),

    /// Apply several filters to a trace with only one pass.
    #[command(visible_aliases = [ "s", "filter" ])]
    Separar(pertalde_separar::Args),
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

    match cli.command {
        Command::Unir(cmd) => pertalde_unir::run(cmd, cli.traces),
        Command::Entendre(cmd) => pertalde_entendre::run(cmd, cli.traces),
        Command::Comprovar(cmd) => pertalde_comprovar::run(cmd, cli.traces),
        Command::Sincronitzar(cmd) => pertalde_sincronitzar::run(cmd, cli.traces),
        Command::Tallar(cmd) => pertalde_tallar::run(cmd, cli.traces),
        Command::Separar(cmd) => pertalde_separar::run(cmd, cli.traces),
    }
}
