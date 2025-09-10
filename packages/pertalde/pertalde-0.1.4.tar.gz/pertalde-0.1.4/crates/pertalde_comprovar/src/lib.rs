pub mod args;
pub use args::Args;

use anyhow::Context;
use std::error::Error;
use std::fs;

use pcf::{Data, PcfParser, Rule};
use pertalde_utils::TraceFiles;
use prv::get_prv_try_reader;

use std::path::PathBuf;

#[derive(thiserror::Error, Debug)]
#[error(transparent)]
pub struct PtdComprovarError(#[from] anyhow::Error);

pub fn run(args: Args, traces: Vec<PathBuf>) -> Result<(), Box<dyn Error>> {
    Ok(run_wrapper(args, traces).map_err(PtdComprovarError)?)
}

fn run_wrapper(args: Args, traces: Vec<PathBuf>) -> anyhow::Result<()> {
    for trace in traces {
        let mut trace_files_in =
            TraceFiles::try_from(&trace).context("getting input trace files")?;

        let records = get_prv_try_reader(&mut trace_files_in).context("generating trace reader")?;

        let mut valid: bool = true;
        for record in records {
            if let Err((record, reason)) = record {
                println!("{reason: >20}: {record}");
                valid = false;
                if !args.exhaustive_check {
                    break;
                }
            }
        }

        // Validate PCF
        let pcf = trace_files_in.pcf();
        let pcf_content = fs::read_to_string(pcf.clone()).context("Reading pcf file")?;
        let parse = <PcfParser as pest::Parser<Rule>>::parse(Rule::pcf, &pcf_content)
            .context("Error parsing pcf")?;
        let _ = Data::try_from(parse).context("Parsing pcf file")?;

        if args.exhaustive_check && !valid {
            std::process::exit(1);
        }
    }

    Ok(())
}
