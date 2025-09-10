pub mod args;
pub use args::Args;

mod filter;

use filter::TraceFilter;

use pertalde_utils::{fs::rollback::Rollback, PathBuilder, ProgressBar, TraceFiles};
use prv::{get_prv_reader, PrvReaderError};

use anyhow::Context;
use colored::Colorize;
use log::{error, warn};

use std::error::Error;
use std::io;
use std::path::PathBuf;

#[derive(thiserror::Error, Debug)]
enum PtdSepararError {
    #[error(transparent)]
    CreatingDirectory(#[from] OutputFolderError),

    #[error(transparent)]
    ReadingParaverTrace(#[from] PrvReaderError),

    #[error(transparent)]
    CopyingAuxFiles(#[from] CopyAuxFilesError),

    #[error("creating the output directory: {0}")]
    Io(#[from] io::Error),

    #[error("handled error: {0}")]
    Anyhow(#[from] anyhow::Error),
}

pub fn run(args: Args, traces: Vec<PathBuf>) -> Result<(), Box<dyn Error>> {
    Ok(traces
        .into_iter()
        .try_for_each(|trace| run_trace(&args, trace))?)
}

fn run_trace(args: &Args, trace: PathBuf) -> Result<(), PtdSepararError> {
    let mut rb = Rollback::new();

    let original_trace = TraceFiles::try_from(&trace).context("crating trace files paths")?;

    let mut base_path: PathBuilder = original_trace
        .base_name()
        .file_name()
        .to_owned()
        .context("generating filtered folder path")?
        .into();
    base_path.push_extension(&args.sufix);

    try_prepare_output_folder(&mut rb, args, &base_path)?;

    let output_dir = base_path
        .file_name()
        .to_owned()
        .context("getting output dir path")?;

    let mut filtered_files = original_trace.clone();
    filtered_files.push_dir(output_dir);
    if args.compress {
        filtered_files.set_compressed(true);
    }

    let mut filters = args.build_profile_filters(&filtered_files)?;

    if let Some(threashold) = args.useful {
        filters.push(TraceFilter::by_state(
            format!("useful_{threashold}us"),
            &filtered_files,
            vec![1],
            threashold /* us */ * 1000, /* now in nanoseconds */
        )?);
    }

    let mut others_filter = args
        .keep_others
        .then_some(TraceFilter::keep_all(format!("others"), &filtered_files)?);

    let mut input = get_prv_reader(&original_trace)?;

    let mut original_trace_prv_size = original_trace.prv_size()?;
    if original_trace.is_compressed() {
        original_trace_prv_size *= 5;
    }

    let mut progressbar = ProgressBar::new(
        original_trace_prv_size,
        format!("Processing {}", original_trace.prv().to_string_lossy()),
        format!("{} done", base_path.as_path().to_string_lossy()),
    );

    let mut processed = 0;

    for record in &mut input {
        let reminder =
            filters
                .iter_mut()
                .try_fold(Some(record), |record, filter| -> anyhow::Result<_> {
                    if let Some(record) = record {
                        filter.filter_record(record)
                    } else {
                        Ok(None)
                    }
                })?;

        if let Some(ref mut others_filter) = others_filter {
            if let Some(reminder) = reminder {
                let _ = others_filter.filter_record(reminder)?;
            }
        }

        // I have measured an average of 30 bytes per record. And this is a best effort to advance
        // the progress bar based on the trace size.
        processed += 45;
        progressbar.set_position(processed);
    }
    progressbar.finish();

    input.report_unparsed_records()?;

    for filter in filters.iter_mut() {
        copy_or_remove(&mut rb, &original_trace, filter, || {
            let message = format!(
                "Info: {} contained no record. And was delted.",
                filter.name()
            );
            println!("{}", message.yellow().bold());
        })?;
    }

    if let Some(ref others_filter) = others_filter {
        copy_or_remove(&mut rb, &original_trace, others_filter, || {})?;
    }

    rb.commit()?;

    Ok(())
}

#[derive(thiserror::Error, Debug)]
enum OutputFolderError {
    #[error("output path exists: consider using --reuse, --force, or --sufix")]
    AlreadyExists,

    #[error("output path exists but its not a directory")]
    ItsNotADir,

    #[error("preparing output dir: {0}")]
    Io(#[from] io::Error),
}

fn try_prepare_output_folder(
    rb: &mut Rollback,
    args: &Args,
    files: &PathBuilder,
) -> Result<(), OutputFolderError> {
    let path = files.as_path_buf();

    if (&path).exists() {
        let metadata = std::fs::metadata(&path)?;

        if args.force {
            if metadata.is_file() {
                warn!("Output path exists but its a file");
                rb.remove_file(&path)?;
            } else {
                std::fs::remove_dir_all(&path)?;
            }
        } else if !args.reuse {
            return Err(OutputFolderError::AlreadyExists);
        } else if !metadata.is_dir() {
            return Err(OutputFolderError::ItsNotADir);
        } else {
            // Reuse is set and path is a directory
            return Ok(());
        }
    }
    rb.create_dir(&path)?;
    Ok(())
}

#[derive(thiserror::Error, Debug)]
#[error("copying auxiliary files (pcf, row)")]
struct CopyAuxFilesError(#[from] io::Error);

fn copy_or_remove<F>(
    rb: &mut Rollback,
    from: &TraceFiles,
    to: &TraceFilter,
    with_if_empty: F,
) -> Result<(), CopyAuxFilesError>
where
    F: FnOnce() -> (),
{
    if to.is_empty() {
        with_if_empty();
        rb.remove_file(to.files().prv())?;
    } else {
        rb.copy_file(from.pcf(), to.files().pcf())?;
        rb.copy_file(from.row(), to.files().row())?;
    }
    Ok(())
}
