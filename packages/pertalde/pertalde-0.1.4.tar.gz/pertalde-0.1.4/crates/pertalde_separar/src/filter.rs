use pertalde_utils::TraceFiles;
use prv::{get_prv_writer, Events, Record};

use anyhow::Context;
use enum_dispatch::enum_dispatch;

use std::io::Write;
use std::ops::Not;
use std::{fmt, fmt::Debug};

#[derive(Debug, Clone)]
#[enum_dispatch(RecordFilter)]
enum RecordFiltererProcessor {
    State(StateFilter),
    Event(EventFilter),
    Communication(CommunicationFilter),
    Keep(KeepFilter),
}

#[enum_dispatch]
trait RecordFilter {
    fn filter_record(&self, record: Record) -> (Option<Record>, Option<Record>);
}

#[derive(Debug, Clone)]
struct StateFilter {
    allow_list: Vec<u64>,
    duration_threshold: u64,
}

impl RecordFilter for StateFilter {
    fn filter_record(&self, record: Record) -> (Option<Record>, Option<Record>) {
        if let Record::State(ref s) = record {
            // Check the allow list
            if self
                .allow_list
                .iter()
                .find(|&&kind| kind == s.state)
                .is_none()
            {
                return (None, Some(record));
            }

            // Check the minimum duration
            if s.duration() < self.duration_threshold {
                return (None, Some(record));
            }

            (Some(record), None)
        } else {
            (None, Some(record))
        }
    }
}

#[derive(Debug, Clone)]
struct EventFilter {
    event_ranges: Vec<(u64, u64)>,
}

impl RecordFilter for EventFilter {
    // #![feature(extract_if)]
    fn filter_record(&self, mut record: Record) -> (Option<Record>, Option<Record>) {
        if let Record::Events(ref mut e) = record {
            let filtered_event_list: Vec<_> = e
                .events
                .extract_if(.., |(event_type, _event_value)| {
                    self.event_ranges
                        .iter()
                        .any(|&(lower, higer)| lower <= *event_type && *event_type <= higer)
                })
                .collect();

            let taken = filtered_event_list
                .is_empty()
                .not()
                .then_some(Record::Events(Events::new(
                    e.object.clone(),
                    e.time,
                    filtered_event_list,
                )));
            let remaining = e.events.is_empty().not().then_some(record);

            (taken, remaining)
        } else {
            (None, Some(record))
        }
    }
}

#[allow(dead_code)]
#[derive(Debug, Clone)]
struct CommunicationFilter {}

impl RecordFilter for CommunicationFilter {
    fn filter_record(&self, _record: Record) -> (Option<Record>, Option<Record>) {
        todo!()
    }
}

#[derive(Debug, Clone)]
struct KeepFilter;

impl RecordFilter for KeepFilter {
    fn filter_record(&self, record: Record) -> (Option<Record>, Option<Record>) {
        (Some(record), None)
    }
}

pub struct TraceFilter {
    name: String,
    trace_files: TraceFiles,
    filter: RecordFiltererProcessor,
    empty: bool,
    output: Box<dyn Write + Send>,
}

impl Debug for TraceFilter {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.debug_struct("TraceFilter")
            .field("trace_files", &self.trace_files)
            .field("filter", &self.filter)
            .field("empty", &self.empty)
            .finish()
    }
}

impl TraceFilter {
    fn build(
        name: String,
        trace_files: &TraceFiles,
        filter: RecordFiltererProcessor,
    ) -> anyhow::Result<Self> {
        let mut trace_files = trace_files.clone();
        trace_files.push_extension(&name);
        let output = get_prv_writer(&trace_files).context("creating prv writer")?;
        Ok(Self {
            name,
            trace_files,
            filter,
            empty: true,
            output,
        })
    }

    pub fn keep_all(name: String, trace_files: &TraceFiles) -> anyhow::Result<Self> {
        Self::build(name, trace_files, RecordFiltererProcessor::Keep(KeepFilter))
    }

    pub fn by_state(
        name: String,
        trace_files: &TraceFiles,
        states: Vec<u64>,
        threshold: u64,
    ) -> anyhow::Result<Self> {
        Self::build(
            name,
            trace_files,
            RecordFiltererProcessor::State(StateFilter {
                allow_list: states,
                duration_threshold: threshold,
            }),
        )
    }

    pub fn by_event(
        name: String,
        trace_files: &TraceFiles,
        events: Vec<(u64, u64)>,
    ) -> anyhow::Result<Self> {
        Self::build(
            name,
            trace_files,
            RecordFiltererProcessor::Event(EventFilter {
                event_ranges: events,
            }),
        )
    }

    #[allow(dead_code)]
    pub fn by_communication(_trace_files: TraceFiles) -> anyhow::Result<Self> {
        todo!()
    }

    fn write_record(&mut self, record: &Record) -> anyhow::Result<()> {
        let buf = format!("{record}\n");
        let buf = buf.as_bytes();
        self.output.write_all(buf).context("writting record")?;
        Ok(())
    }

    pub fn filter_record(&mut self, record: Record) -> anyhow::Result<Option<Record>> {
        match record {
            Record::Other(_) => {
                self.write_record(&record)?;
                Ok(Some(record))
            }
            record => {
                let (to_write, reminder) = self.filter.filter_record(record);

                if let Some(record) = to_write {
                    self.empty = false;
                    self.write_record(&record)?;
                }

                Ok(reminder)
            }
        }
    }

    pub fn is_empty(&self) -> bool {
        self.empty
    }

    pub fn files(&self) -> &TraceFiles {
        &self.trace_files
    }

    pub fn name(&self) -> &str {
        &self.name
    }
}
