pub mod comm;
pub mod event;
pub mod object;
pub mod state;

use std::fmt::Display;
use std::fs::OpenOptions;
use std::io::Write;

use anyhow::Context;
use colored::Colorize;

#[derive(Debug, Clone, PartialEq)]
pub enum Record {
    State(state::State),
    Events(event::Events),
    Comm(comm::Comm),
    Other(String),
}

use std::io::BufRead;

pub struct TryRecords<B> {
    reader: B,
}

impl<B> TryRecords<B> {
    pub fn new(reader: B) -> Self {
        Self { reader }
    }
}

#[derive(Debug)]
pub enum Reason {
    TooManyValues(usize),
    TooFewValues(usize),
    WrongType,
}

impl Display for Reason {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        let message = match self {
            Reason::TooManyValues(n) => format!("{n} value extra"),
            Reason::TooFewValues(n) => format!("{n} value missing"),
            Reason::WrongType => format!("non int value"),
        };

        write!(f, "{}", message)
    }
}

pub struct Records<B> {
    reader: TryRecords<B>,
    unparsed_records: Vec<(String, Reason)>,
}

impl<B> Records<B> {}

impl Display for Record {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Record::State(s) => write!(f, "{s}")?,
            Record::Events(e) => write!(f, "{e}")?,
            Record::Comm(c) => write!(f, "{c}")?,
            Record::Other(s) => write!(f, "{s}")?,
        };
        Ok(())
    }
}

impl<B> Records<B> {
    pub fn new(reader: B) -> Records<B> {
        Records {
            reader: TryRecords::new(reader),
            unparsed_records: vec![],
        }
    }

    pub fn get_unparsed_records(&self) -> &Vec<(String, Reason)> {
        &self.unparsed_records
    }

    pub fn report_unparsed_records(&self) -> anyhow::Result<()> {
        if self.unparsed_records.len() > 10 {
            let file_name = "pertalde_bad_records.out";
            let mut file = OpenOptions::new()
                .write(true)
                .create(true)
                .open(file_name)
                .context(format!("Opening error file: {file_name}"))?;

            println!(
                "{} {} {}",
                "Warning: several records could not be processes."
                    .bold()
                    .yellow(),
                "You can find a list of this records in:".bold().yellow(),
                file_name.bold().yellow()
            );

            for (record, reason) in self.unparsed_records.iter() {
                let buf = format!("{reason}: {record}\n");
                let buf = buf.as_bytes();
                file.write_all(buf)
                    .context("Writting record in pertalde_bad_records.out")?;
            }
        } else {
            for (record, reason) in self.unparsed_records.iter() {
                println!("{reason: <15}: {record}");
            }
        }
        Ok(())
    }
}

impl<B: BufRead> TryRecords<B> {
    fn next_line(&mut self) -> Option<String> {
        let mut buf = String::new();
        match self.reader.read_line(&mut buf) {
            Ok(0) => None,
            Ok(_n) => {
                if buf.ends_with('\n') {
                    buf.pop();
                    if buf.ends_with('\r') {
                        buf.pop();
                    }
                }
                Some(buf)
            }
            Err(_) => None,
        }
    }
}

impl<B: BufRead> Iterator for Records<B> {
    type Item = Record;

    fn next(&mut self) -> Option<Self::Item> {
        while let Some(record) = self.reader.next() {
            match record {
                Ok(record) => return Some(record),
                Err(record_and_reason) => self.unparsed_records.push(record_and_reason),
            }
        }
        None
    }
}

impl<B: BufRead> Iterator for TryRecords<B> {
    type Item = std::result::Result<Record, (String, Reason)>;

    fn next(&mut self) -> Option<Self::Item> {
        self.next_line()
            .map(|raw_record| parse_record(&raw_record).map_err(|reason| (raw_record, reason)))
    }
}

struct Wrapper<PrvRecords>(PrvRecords);
impl<PrvRecord: Iterator<Item = u64>> From<PrvRecord> for Wrapper<PrvRecord> {
    fn from(records: PrvRecord) -> Wrapper<PrvRecord> {
        Wrapper(records)
    }
}

fn parse_record(record: &str) -> std::result::Result<Record, Reason> {
    let first: String = record.chars().take_while(|c| *c != ':').collect();

    match first.as_str() {
        // For now we only parse those that are Events
        "1" | "2" | "3" => {
            let line = record.split(':');
            let line: Result<Vec<u64>, String> = line
                .map(|elem| elem.parse::<u64>().map_err(|_| record.to_string()))
                .collect();
            match line {
                Ok(line) => {
                    let mut line = line.into_iter();
                    let _remove_record_type = line.next().unwrap();

                    let line: Wrapper<_> = line.into();
                    match first.as_str() {
                        "1" => Ok(Record::State(line.try_into()?)),
                        "2" => Ok(Record::Events(line.try_into()?)),
                        "3" => Ok(Record::Comm(line.try_into()?)),
                        _ => unreachable!(),
                    }
                }
                Err(_) => Err(Reason::WrongType),
            }
        }
        _ => Ok(Record::Other(record.to_string())),
    }
}
