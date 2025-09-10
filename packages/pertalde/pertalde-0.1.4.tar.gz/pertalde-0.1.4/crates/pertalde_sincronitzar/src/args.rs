use anyhow::{ensure, Context};

use super::EventInfo;

#[derive(clap::Args, Debug)]
pub struct Args {
    /// reference event used to syncronize the trace
    #[arg(short = 'e', long = "event", value_name = "TYPE:VALUE")]
    ref_event_str: Option<String>,

    #[clap(skip)]
    pub ref_event: Option<EventInfo>,

    /// use the N occurenve of the event
    #[arg(short = 'o', long = "occurence", value_name = "N", default_value = "1")]
    pub occurence: usize,

    /// compress the output traces with gzip
    #[arg(long = "compress", short = 'c')]
    pub compress: bool,

    /// the sufix to use for the new files.
    #[arg(long = "sufix", default_value = "sync")]
    pub sufix: String,
}

impl Args {
    pub fn build_reference_event(&mut self) -> anyhow::Result<()> {
        self.ref_event = self
            .ref_event_str
            .as_mut()
            .map(|event| {
                let mut split_event_str = event.split(':');
                let event_type = split_event_str
                    .next()
                    .context("parsing type from event")?
                    .parse()
                    .context("expected a u64 when parsing event type")?;
                let event_value = split_event_str
                    .next()
                    .context("parsing value from event")?
                    .parse()
                    .context("expected a u64 when parsing event value")?;

                ensure!(
                    split_event_str.next().is_none(),
                    "event does not follow TYPE:VALUE format"
                );
                Ok(EventInfo {
                    event_type,
                    event_value,
                })
            })
            .transpose()
            .context("building reference event")?;

        Ok(())
    }
}
