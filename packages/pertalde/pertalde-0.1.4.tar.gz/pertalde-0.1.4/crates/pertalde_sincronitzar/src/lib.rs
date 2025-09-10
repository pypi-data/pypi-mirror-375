pub mod args;
pub use args::Args;

use pertalde_utils::{ProgressBar, ProgressSpinner, TraceFiles};
use prv::{get_prv_reader, get_prv_writer, Record, Records};

use anyhow::{anyhow, Context};

use std::{
    collections::HashMap,
    error::Error,
    io::{BufRead, Write},
    path::PathBuf,
    thread,
};

#[derive(thiserror::Error, Debug)]
#[error(transparent)]
pub struct PtdSincronitzarError(#[from] anyhow::Error);

pub fn run(args: Args, traces: Vec<PathBuf>) -> Result<(), Box<dyn Error>> {
    Ok(run_wrapper(args, traces).map_err(PtdSincronitzarError)?)
}

fn run_wrapper(mut args: Args, traces: Vec<PathBuf>) -> anyhow::Result<()> {
    args.build_reference_event()?;
    let args = args;

    for trace in traces {
        let mut trace_files_in = TraceFiles::try_from(&trace).context("creating trace files")?;
        let mut trace_files_out = trace_files_in.clone();

        //let mut trace_files_in = Arc::new(Mutex::new(trace_files_in));

        trace_files_out.push_extension(&args.sufix);
        if args.compress {
            trace_files_out.set_compressed(true);
        }

        let mpi_init = EventInfo {
            event_type: 50000003,
            event_value: 31,
        };
        let ref_event = args.ref_event.as_ref().unwrap_or(&mpi_init);

        let find_reference_event_thread = {
            let records =
                get_prv_reader(&trace_files_in).context("creating prv reader for event finding")?;
            let ref_event = ref_event.clone();
            let occurence = args.occurence.clone();
            thread::spawn(move || find_reference_event(records, &ref_event, occurence))
        };

        let mut find_reference_spinner_wait =
            ProgressSpinner::new("Finding reference event...", None);

        let event_times = find_reference_spinner_wait
            .wait_join_handle(find_reference_event_thread)
            .expect("Joining thread find reference event");

        // let event_times = find_reference_event(records, ref_event, args.occurence)
        //     .context("finding reference event")?;

        let latest_end = event_times
            .values()
            .map(
                |EventTime {
                     start_time,
                     duration,
                 }| start_time + duration,
            )
            .max()
            .context("finding earlier end time")?;

        let shift_info: HashMap<u64, u64> = event_times
            .into_iter()
            .map(|(task, event)| {
                let event_end_time = event.start_time + event.duration;
                let shift = latest_end - event_end_time;
                (task, shift)
            })
            .collect();

        let mut trace_file_in_prv_size = trace_files_in.prv_size()?;
        if trace_files_in.is_compressed() {
            trace_file_in_prv_size *= 3;
        }

        let mut progressbar = ProgressBar::new(
            trace_file_in_prv_size,
            format!("Syncronizing {}", trace_files_in.prv().to_string_lossy()),
            format!("{} done.", trace_files_out.prv().to_string_lossy()),
        );
        let mut written = 0;

        let records =
            get_prv_reader(&mut trace_files_in).context("creating prv reader for event finding")?;
        let mut output = get_prv_writer(&mut trace_files_out).context("creating prv writer")?;

        for record in records {
            let record = shift_record(record, &shift_info)?;
            let buf = format!("{record}\n");
            let buf = buf.as_bytes();
            written += buf.len() as u64;

            output.write_all(buf).context("writing record")?;

            progressbar.set_position(written);
        }

        progressbar.finish();

        std::fs::copy(trace_files_in.pcf(), trace_files_out.pcf()).context("copying pcf file")?;
        std::fs::copy(trace_files_in.row(), trace_files_out.row()).context("copying row file")?;
    }
    Ok(())
}

#[derive(Debug, Clone)]
pub struct EventTime {
    pub start_time: u64,
    pub duration: u64,
}

#[derive(Debug, Clone)]
pub struct EventInfo {
    pub event_type: u64,
    pub event_value: u64,
}

fn find_reference_event<B: BufRead>(
    records: Records<B>,
    ref_event: &EventInfo,
    occurences: usize,
) -> HashMap<u64, EventTime> {
    let mut occurences_left = HashMap::<u64, usize>::new();
    let mut start_time = HashMap::<u64, u64>::new();
    let mut shifts = HashMap::<u64, EventTime>::new();
    //let mut occurences_left = occurences;

    for record in records {
        if let Record::Events(event_list) = record {
            let event_task = event_list.object.task;
            if shifts.contains_key(&event_task) {
                continue;
            }
            for (t, v) in event_list.events {
                if t != ref_event.event_type {
                    continue;
                }
                if v == ref_event.event_value {
                    let task_event_occurences =
                        occurences_left.entry(event_task).or_insert(occurences);
                    *task_event_occurences -= 1;
                    if *task_event_occurences == 0 {
                        start_time.insert(event_task, event_list.time);
                    }
                } else if v == 0 {
                    if let Some(start_time) = start_time.remove(&event_task) {
                        let duration = event_list.time - start_time;
                        shifts.insert(
                            event_task,
                            EventTime {
                                start_time,
                                duration,
                            },
                        );
                    }
                }
            }
        }
    }

    shifts
}

fn get_shift_info(task: u64, shift_info: &HashMap<u64, u64>) -> anyhow::Result<u64> {
    let mut attempts = 10;
    let mut check_task = task;

    loop {
        if let Some(shift) = shift_info.get(&check_task) {
            return Ok(*shift);
        } else {
            check_task = check_task.saturating_sub(1);
            attempts -= 1;
            if attempts == 0 {
                break;
            }
        }
    }
    Err(anyhow!("error finding shift info for task: {task}"))
}

fn shift_record(record: Record, shift_info: &HashMap<u64, u64>) -> anyhow::Result<Record> {
    match record {
        Record::State(mut state) => {
            let shift = get_shift_info(state.object.task, shift_info)?;
            state.start += shift;
            state.end += shift;
            Ok(Record::State(state))
        }
        Record::Events(mut events) => {
            let shift = get_shift_info(events.object.task, shift_info)?;
            events.time += shift;
            Ok(Record::Events(events))
        }
        Record::Comm(mut comm) => {
            let shift = get_shift_info(comm.object_send.task, shift_info)?;
            comm.logic_send += shift;
            comm.physical_send += shift;

            let shift = get_shift_info(comm.object_recv.task, shift_info)?;
            comm.logic_recv += shift;
            comm.physical_recv += shift;
            Ok(Record::Comm(comm))
        }
        r @ Record::Other(_) => Ok(r),
    }
}
