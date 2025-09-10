pub mod record;

pub use crate::record::comm::Comm;
pub use crate::record::event::Event;
pub use crate::record::event::Events;
pub use crate::record::state::State;
pub use crate::record::Record;
pub use crate::record::Records;
pub use crate::record::TryRecords;

use pertalde_utils::TraceFiles;

use anyhow::Context;
use flate2::{read::GzDecoder, write::GzEncoder, Compression};

use std::{
    fs::File,
    io::{self, BufRead, BufReader, BufWriter, Write},
};

#[derive(thiserror::Error, Debug)]
pub enum PrvReaderError {
    #[error("file not found {0}")]
    FileNotFound(String),

    #[error(transparent)]
    Io(#[from] io::Error),

    #[error(transparent)]
    Anyhow(#[from] anyhow::Error),
}

fn get_bufreader_from_trace_files(
    trace: &TraceFiles,
) -> Result<Box<dyn BufRead + Send>, PrvReaderError> {
    if !std::fs::exists(trace.prv()).context("reading file metadata")? {
        return Err(PrvReaderError::FileNotFound(
            trace.prv().to_string_lossy().to_string(),
        ));
    }

    let file = File::open(trace.prv())?;

    let bufreader: Box<dyn BufRead + Send> = if trace.is_compressed() {
        let decoder = GzDecoder::new(file);
        let reader = BufReader::new(decoder);
        Box::new(reader)
    } else {
        Box::new(BufReader::new(file))
    };

    Ok(bufreader)
}

pub fn get_prv_reader(
    trace: &TraceFiles,
) -> Result<Records<Box<dyn BufRead + Send>>, PrvReaderError> {
    let bufreader = get_bufreader_from_trace_files(trace)?;
    Ok(Records::new(bufreader))
}

pub fn get_prv_try_reader(
    trace: &TraceFiles,
) -> Result<TryRecords<Box<dyn BufRead + Send>>, PrvReaderError> {
    let bufreader = get_bufreader_from_trace_files(trace)?;
    Ok(TryRecords::new(bufreader))
}

pub fn get_prv_writer(trace: &TraceFiles) -> anyhow::Result<Box<dyn Write + Send>> {
    let output_prv = File::create(trace.prv()).context("creating output prv file")?;
    let output_buf = BufWriter::new(output_prv);

    if trace.is_compressed() {
        Ok(Box::new(GzEncoder::new(output_buf, Compression::default())))
    } else {
        Ok(Box::new(output_buf))
    }
}
