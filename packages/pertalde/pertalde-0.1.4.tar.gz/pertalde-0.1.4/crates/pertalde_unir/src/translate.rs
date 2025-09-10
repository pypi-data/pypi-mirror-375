use pertalde_utils::{ProgressBar, ProgressSpinner};

use pertalde_utils::TraceFiles;
use prv::{get_prv_reader, get_prv_writer, Record, Records};

use anyhow::{Context, Result};

use std::{
    collections::HashMap,
    io::{BufRead, Write},
    sync::{Arc, Mutex},
    thread,
};

trait SeekableIterator: Iterator {}
impl<B> SeekableIterator for Records<B> where B: BufRead {}

pub struct PrvTranslator {
    input: Box<dyn SeekableIterator<Item = Record>>,
    output: Arc<Mutex<Box<dyn Write + Send>>>,
    progress: ProgressBar<String>,
    written: u64,
}

fn translate_record(map: &HashMap<(u64, u64), u64>, mut record: Record) -> Record {
    if let Record::Events(ref mut event_list) = record {
        for (t, ref mut v) in event_list.events.iter_mut() {
            if let Some(translated_value) = map.get(&(*t, *v)) {
                *v = *translated_value;
            }
        }
    }

    record
}

impl PrvTranslator {
    pub fn build(trace_in: &TraceFiles, trace_out: &TraceFiles) -> Result<Self> {
        let input_size = {
            let metadata = std::fs::metadata(&trace_in.prv()).with_context(
                || format! {"getting size of {}", trace_in.prv().to_string_lossy()},
            )?;
            let mut lenght = metadata.len();
            if trace_in.is_compressed() {
                // Assume a compression rate of 70% for the progress bar
                lenght *= 4;
                lenght /= 3
            }
            lenght
        };

        let prv_reader = get_prv_reader(trace_in).context("creating prv reader")?;

        let prv_writer = get_prv_writer(trace_out).context("creating prv writer")?;

        let mut stripped_trace_in = trace_in.clone();
        let stripped_trace_in = stripped_trace_in.pop_all_dirs();
        let progress = ProgressBar::new(
            input_size,
            format!("{}", stripped_trace_in.prv().to_string_lossy()),
            format!("{} done.", trace_out.prv().to_string_lossy()),
        );

        Ok(PrvTranslator {
            input: Box::new(prv_reader),
            output: Arc::new(Mutex::new(prv_writer)),
            progress,
            written: 0,
        })
    }

    pub fn run(&mut self, map: HashMap<(u64, u64), u64>) -> Result<()> {
        let mut output = self.output.lock().unwrap();

        // .map(|r| r.map_err(anyhow::Error::msg).context("Parsing record"))
        for record in self.input.by_ref() {
            let record = translate_record(&map, record);

            let buf = format!("{record}\n");
            let buf = buf.as_bytes();

            let written = buf.len();
            output.write_all(buf).context("Writing record")?;

            self.written += written as u64;
            self.progress.set_position(self.written);
        }
        self.progress.finish();

        Ok(())
    }
}

impl Drop for PrvTranslator {
    fn drop(&mut self) {
        let output = Arc::clone(&self.output);
        let flushing_thread = {
            thread::spawn(move || {
                let _ = output.lock().unwrap().flush();
                output
            })
        };

        let mut spinner = ProgressSpinner::new("Flusshing...", None);
        spinner
            .wait_join_handle(flushing_thread)
            .expect("Joining flush thread");
    }
}
