pub mod args;
pub use args::Args;

use pcf::{Data, PcfParser, Rule};
use pertalde_utils::TraceFiles;
use prv::Record;

use anyhow::Context;
use log::warn;

use std::collections::HashMap;
use std::error::Error;
use std::fs;
use std::ops::Not;
use std::path::PathBuf;

#[derive(thiserror::Error, Debug)]
enum PtdComptarError {
    #[error("error: {0}")]
    Anyhow(#[from] anyhow::Error),
}

pub fn run(args: Args, traces: Vec<PathBuf>) -> Result<(), Box<dyn Error>> {
    Ok(traces
        .into_iter()
        .try_for_each(|trace| run_trace(&args, trace))?)
}

#[derive(Hash, PartialEq, Eq, Clone, Copy)]
enum RecordKind {
    State,
    Event,
    Communication,
}

fn run_trace(args: &Args, trace: PathBuf) -> Result<(), PtdComptarError> {
    let trace = TraceFiles::from(&trace);

    let limit = args
        .show_all
        .not() // explicitly show all
        .then_some(args.number);

    let pcf_data = get_pcf_data(&trace);
    if pcf_data.is_none() {
        warn!("no semantics will be available")
    }

    let mut map = HashMap::new();
    let prv = prv::get_prv_reader(&trace).context("opening prv")?;
    for record in prv {
        match record {
            Record::State(s) => {
                let size = format!("{s}").bytes().len();
                let entry = map.entry((RecordKind::State, s.state)).or_insert((0, 0));
                entry.0 += 1;
                entry.1 += size;
            }
            Record::Events(events) => {
                if events.events.len() == 1 {
                    let (etype, _value) = events.events.first().unwrap();
                    let entry = map.entry((RecordKind::Event, *etype)).or_insert((0, 0));
                    entry.0 += 1;
                    let size = format!("{events}").bytes().len();
                    entry.1 += size;
                } else {
                    for (etype, value) in events.events.iter() {
                        let entry = map.entry((RecordKind::Event, *etype)).or_insert((0, 0));
                        entry.0 += 1;
                        let size = format!("{etype}:{value}").bytes().len();
                        entry.1 += size;
                    }
                }
            }
            Record::Comm(comm) => {
                let entry = map.entry((RecordKind::Communication, 0)).or_insert((0, 0));
                entry.0 += 1;
                let size = format!("{comm}").bytes().len();
                entry.1 += size;
            }
            _ => {}
        }
    }

    let mut ordered_by_size: Vec<_> = map
        .into_iter()
        .map(|((kind, id), (count, size))| (kind, id, count, size))
        .collect();
    ordered_by_size.sort_by(|a, b| b.3.cmp(&a.3));
    if let Some(limit) = limit {
        ordered_by_size.truncate(limit);
    }

    let mut tabled_builder = tabled::builder::Builder::new();
    tabled_builder.push_record(["Record", "Name", "Occurrences", "Size"]);
    for (kind, id, count, size) in ordered_by_size {
        // Get a name from the id
        let name = translate_record_id(&pcf_data, kind, id);

        let kind = match kind {
            RecordKind::State => "State",
            RecordKind::Event => "Event",
            RecordKind::Communication => "Comms",
        };

        let size = humansize::format_size(size, humansize::DECIMAL);

        tabled_builder.push_record([kind, &name, &count.to_string(), &size]);
        // println!("{:>10}{:>10}{:>10}{:>10}", kind, id, count, size);
    }

    let prv_name = trace.prv().as_path().to_string_lossy();

    let table_style = tabled::settings::Style::ascii_rounded().horizontals([
        (1, tabled::settings::style::HorizontalLine::filled('=').left('|').right('|')),
        (2, tabled::settings::style::HorizontalLine::filled('-').left('|').right('|')),
    ]);

    let mut table = tabled_builder.build();
    table
        .with(table_style)
        .with(tabled::settings::Alignment::right())
        .with(tabled::settings::panel::Header::new(prv_name))
        .with(
            tabled::settings::Modify::new(tabled::settings::object::Rows::first())
                .with(tabled::settings::Alignment::center()),
        )
        .with(
            tabled::settings::Modify::new(tabled::settings::object::Rows::new(1..=1))
                .with(tabled::settings::Alignment::center()),
        );
    println!("{table}");

    Ok(())
}

fn get_pcf_data(trace: &TraceFiles) -> Option<pcf::Data> {
    let pcf_filename = trace.pcf();
    let pcf_file_str = match fs::read_to_string(pcf_filename) {
        Ok(str) => str,
        Err(err) => {
            warn!(
                "error reading pcf file ({}): {err}",
                pcf_filename.as_path().to_string_lossy()
            );
            return None;
        }
    };

    let pcf_parser = match <PcfParser as pest::Parser<Rule>>::parse(Rule::pcf, &pcf_file_str) {
        Ok(parsed) => parsed,
        Err(err) => {
            warn!(
                "error parsing pcf ({}): {err}",
                pcf_filename.as_path().to_string_lossy()
            );
            return None;
        }
    };

    let pcf_data = match Data::try_from(pcf_parser) {
        Ok(data) => data,
        Err(err) => {
            warn!(
                "error parsing pcf ({}): {err}",
                pcf_filename.as_path().to_string_lossy()
            );
            return None;
        }
    };

    Some(pcf_data)
}

fn translate_record_id(pcf_data: &Option<pcf::Data>, kind: RecordKind, id: u64) -> String {
    match kind {
        RecordKind::State => pcf_data
            .as_ref()
            .and_then(|pcf| find_state(pcf, id))
            .unwrap_or(format!("{id} (Unknown)")),
        RecordKind::Event => pcf_data
            .as_ref()
            .and_then(|pcf| find_event(pcf, id))
            .unwrap_or(format!("{id} (Unknown)")),
        RecordKind::Communication => "-".to_string(),
    }
}

fn find_state(pcf: &pcf::Data, id: u64) -> Option<String> {
    pcf.states.get(&id).map(|s| s.semantic.to_string())
}

fn find_event(pcf: &pcf::Data, id: u64) -> Option<String> {
    for group in pcf.event_groups.iter() {
        let type_name = group.types.get(&id).map(|e| e.name.to_string());
        if type_name.is_some() {
            return type_name;
        }
    }
    None
}
