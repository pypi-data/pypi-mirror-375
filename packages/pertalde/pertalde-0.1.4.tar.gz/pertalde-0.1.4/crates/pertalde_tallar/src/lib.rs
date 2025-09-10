pub mod args;
pub use args::Args;

use pertalde_utils::TraceFiles;
use prv::{get_prv_reader, get_prv_writer, Record};

use anyhow::Context;

use std::{error::Error, io::Write, ops::Not, path::PathBuf};

#[derive(thiserror::Error, Debug)]
#[error(transparent)]
pub struct PtdTallarError(#[from] anyhow::Error);

pub fn run(args: Args, traces: Vec<PathBuf>) -> Result<(), Box<dyn Error>> {
    Ok(traces
        .into_iter()
        .try_for_each(|trace| run_trace(&args, trace))
        .map_err(PtdTallarError)?)
}

fn run_trace(args: &Args, trace: PathBuf) -> anyhow::Result<()> {
    let trace_files_in = TraceFiles::try_from(&trace).context("creating trace files paths")?;
    let mut trace_files_out = trace_files_in.clone();
    trace_files_out.push_extension(&args.sufix);
    if args.compress {
        trace_files_out.set_compressed(true);
    }
    let trace_files_out = trace_files_out;

    let mut records =
        get_prv_reader(&trace_files_in).context("creating prv reader for event finding")?;
    let records = &mut records;
    let mut output = get_prv_writer(&trace_files_out).context("creating prv writer")?;

    records
        .filter_map(|record| -> Option<Record> {
            match record {
                Record::State(mut state) => {
                    if (args.start <= state.start && state.start <= args.end)
                        && (args.start <= state.end && state.end <= args.end)
                    {
                        Some(Record::State(state))
                    } else if (state.start < args.start)
                        && (args.start <= state.end && state.end <= args.end)
                    {
                        state.start = if args.break_state {
                            args.start
                        } else {
                            state.start
                        };
                        args.discard_first_state
                            .not()
                            .then_some(Record::State(state))
                    } else if (args.start <= state.start && state.start <= args.end)
                        && (state.end > args.end)
                    {
                        state.end = if args.break_state {
                            args.end
                        } else {
                            state.end
                        };
                        args.discard_last_state
                            .not()
                            .then_some(Record::State(state))
                    } else {
                        None
                    }
                }
                Record::Events(events) => (args.start <= events.time && events.time <= args.end)
                    .then_some(Record::Events(events)),
                Record::Comm(comm) => ((args.start <= comm.logic_send
                    && comm.logic_send <= args.end)
                    && (args.start <= comm.logic_recv && comm.logic_recv <= args.end))
                    .then_some(Record::Comm(comm)),
                r @ Record::Other(_) => Some(r),
            }
        })
        .map(|record| -> anyhow::Result<()> {
            let buf = format!("{record}\n");
            let buf = buf.as_bytes();
            output.write_all(buf).context("writing record")?;
            Ok(())
        })
        .collect::<anyhow::Result<()>>()?;

    output.flush().context("flushing prv file")?;

    records.report_unparsed_records()?;

    std::fs::copy(trace_files_in.pcf(), trace_files_out.pcf()).context("copying pcf file")?;
    std::fs::copy(trace_files_in.row(), trace_files_out.row()).context("copying row file")?;
    Ok(())
}
