pub mod args;
pub use args::Args;

use pcf::{Data, PcfParser, Rule};
use pertalde_utils::TraceFiles;

use anyhow::{bail, Context};
use serde_derive::{Deserialize, Serialize};

use std::{collections::HashMap, error::Error, fs, fs::File, path::PathBuf};

#[derive(thiserror::Error, Debug)]
#[error(transparent)]
pub struct PtdEntendreError(#[from] anyhow::Error);

pub fn run(args: Args, traces: Vec<PathBuf>) -> Result<(), Box<dyn Error>> {
    Ok(run_wrapper(args, traces).map_err(PtdEntendreError)?)
}

#[derive(Debug, Deserialize)]
struct Record {
    ordering: u64,
    values: Vec<f64>,
}

#[derive(Debug, Serialize)]
struct SemanticRecord {
    ordering: u64,
    values: Vec<String>,
}

fn run_wrapper(args: Args, traces: Vec<PathBuf>) -> anyhow::Result<()> {
    if traces.len() != 1 {
        bail!("Not suported with multiple traces");
    }
    let trace = TraceFiles::try_from(traces[0].clone()).context("creating trace files")?;

    let event_translation_map = {
        let pcf_content = fs::read_to_string(trace.pcf()).context("reading the pcf file")?;
        let parse = <PcfParser as pest::Parser<Rule>>::parse(Rule::pcf, &pcf_content)
            .context("parssing the pcf file")?;
        let pcf = Data::try_from(parse).context("processing pcf file")?;
        get_translation_map(pcf, args.event_type)
            .context("getting event translation map for event")?
    };

    let mut rdr = {
        let input = File::open(&args.csv_file)
            .with_context(|| format!("Opening csv file: {}", "file.csv"))?;
        csv::ReaderBuilder::new()
            .delimiter(b'\t')
            .has_headers(false)
            .from_reader(input)
    };

    let mut wrt = {
        let mut csv_output = args.csv_file.clone();
        csv_output.set_extension("entender.csv");
        let output = File::create(csv_output)
            .with_context(|| format!("Creating csv output file: {}", "file.entender.csv"))?;
        csv::WriterBuilder::new()
            .delimiter(b',')
            .has_headers(false)
            .from_writer(output)
    };

    if let Some(header) = rdr.records().next() {
        let header = header.context("Reading csv header")?.clone();
        wrt.write_record(&header).context("writting header")?;
    } else {
        anyhow::bail! {"No header line"};
    }

    for record in rdr.deserialize::<Record>() {
        let record: Record = record.context("Parsing csv record")?;

        let semantic_record = SemanticRecord {
            ordering: record.ordering,
            values: translate_values(&event_translation_map, record.values)
                .context("Translating record")?,
        };

        wrt.serialize(semantic_record).context("Writting record")?;
    }

    Ok(())
}

fn get_translation_map(pcf: Data, event_type: u64) -> anyhow::Result<HashMap<u64, String>> {
    pcf.event_groups
        .iter()
        .find_map(|eg| {
            eg.types
                .contains_key(&event_type)
                .then_some(eg.values.clone())
        })
        .context("finding event type in pcf")
}

fn translate_values(
    event_value_map: &HashMap<u64, String>,
    records: Vec<f64>,
) -> anyhow::Result<Vec<String>> {
    records
        .into_iter()
        .map(|r| {
            if (r as u64) == 0 {
                return Ok("-".to_string());
            }
            event_value_map
                .get(&(r as u64))
                .cloned()
                .context("translating value")
        })
        .collect()
}
