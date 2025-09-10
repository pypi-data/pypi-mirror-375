use clap::{Parser, Subcommand, ValueHint};
use colored::Colorize;
use std::error::Error;

use std::path::PathBuf;
use std::process::{ExitCode, Termination};

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
        allow_hyphen_values = false,
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

    /// Count the ammount of apearences each record type has and estimates disk ussage.
    Comptar(pertalde_comptar::Args),
}

enum TerminationWrapper {
    Err(Box<dyn Error>),
    Ok,
}

impl From<Result<(), Box<dyn Error>>> for TerminationWrapper {
    fn from(value: Result<(), Box<dyn Error>>) -> Self {
        match value {
            Err(value) => TerminationWrapper::Err(value),
            Ok(()) => TerminationWrapper::Ok,
        }
    }
}

impl Termination for TerminationWrapper {
    fn report(self) -> ExitCode {
        match self {
            TerminationWrapper::Err(e) => {
                eprintln!("{} {}", "error:".red().bold(), e);
                1.into()
            }
            TerminationWrapper::Ok => 0.into(),
        }
    }
}

fn main() -> TerminationWrapper {
    std::panic::set_hook(Box::new(|panic_info| {
        eprint!("{}", "internal error at".red().bold());
        if let Some(location) = panic_info.location() {
            eprintln!(
                "{} {}:{}",
                ":".red().bold(),
                location.file(),
                location.line()
            );
        } else {
            eprintln!("{}", "!".red().bold());
        }

        if let Some(s) = panic_info.payload().downcast_ref::<&str>() {
            eprintln!("{}", "reason:".bold());
            eprintln!("\t{s}");
        } else if let Some(s) = panic_info.payload().downcast_ref::<String>() {
            eprintln!("{}", "reason:".bold());
            eprintln!("\t{s}");
        } else {
            println!("panic occured, but could not read deal with payload")
        }

        eprintln!();
        let report_at = format!(
            "{}\n{}",
            "Ups, perdó! Even though we disappointed you, please show kindness and report the bug at:".cyan(),
            "https://gitlab.pm.bsc.es/beppp/parajuntar/-/issues/new".cyan()
        );
        eprintln!("{report_at}");

        let how_to_report = format!(
            "\t{}{}\n\t{}{}",
            "1.".green().bold(),
            "Try to run with RUST_LOG=debug".green(),
            "2.".green().bold(),
            "Provide the whole program log".green(),
        );
        eprintln!("{how_to_report}");
    }));

    let cli = Cli::parse();

    env_logger::Builder::from_env(env_logger::Env::default().default_filter_or("warn")).init();

    match cli.command {
        Command::Unir(cmd) => pertalde_unir::run(cmd, cli.traces),
        Command::Entendre(cmd) => pertalde_entendre::run(cmd, cli.traces),
        Command::Comprovar(cmd) => pertalde_comprovar::run(cmd, cli.traces),
        Command::Sincronitzar(cmd) => pertalde_sincronitzar::run(cmd, cli.traces),
        Command::Tallar(cmd) => pertalde_tallar::run(cmd, cli.traces),
        Command::Separar(cmd) => pertalde_separar::run(cmd, cli.traces),
        Command::Comptar(cmd) => pertalde_comptar::run(cmd, cli.traces),
    }
    .into()
}
