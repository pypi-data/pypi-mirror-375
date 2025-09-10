use pertalde_utils::TraceFiles;

use clap::ValueEnum;

#[derive(clap::Args, Debug)]
pub struct Args {
    /// compress the output traces with gzip
    #[arg(long = "compress", short = 'c')]
    pub compress: bool,

    /// lower bound threashold to filter useful records in microseconds
    #[arg(long = "useful", short = 'u', value_name = "DURATION")]
    pub useful: Option<u64>,

    #[arg(long = "force", short = 'f', conflicts_with = "reuse")]
    pub force: bool,

    #[arg(long = "reuse", conflicts_with = "force")]
    pub reuse: bool,

    /// is a comma separated list of the different even profiles selected
    #[arg(long = "profile", short = 'p', value_delimiter = ',')]
    pub profiles: Vec<EventProfile>,

    /// will generate a trace with unfiltered events
    #[arg(long = "keep-others")]
    pub keep_others: bool,

    #[clap(skip)]
    pub profiles_filter: Option<Vec<TraceFilter>>,

    /// the sufix to use for the new files.
    #[arg(long = "sufix", default_value = "partials")]
    pub sufix: String,
}

impl Args {
    pub fn build_profile_filters(
        &self,
        trace_files: &TraceFiles,
    ) -> anyhow::Result<Vec<TraceFilter>> {
        self.profiles
            .iter()
            .map(|p| p.into_filter(trace_files))
            .collect()
    }
}

#[derive(Debug, Clone, Copy, ValueEnum)]
pub enum EventProfile {
    Nesmik,
    Mpi,
    OpenMP,
    Flushing,
    Counters,
}

use crate::filter::TraceFilter;

impl EventProfile {
    fn into_filter(&self, trace_files: &TraceFiles) -> anyhow::Result<TraceFilter> {
        use EventProfile::*;
        let (name, event_list) = match self {
            Nesmik => ("nesmik", vec![(81000, 82000)]),
            Mpi => ("mpi", vec![(50000000, 59000000)]),
            OpenMP => ("omp", vec![(60000000, 69999999)]),
            Flushing => ("flushing", vec![(40000003, 40000003)]),
            Counters => ("counters", vec![(41999999, 42999999)]),
        };
        TraceFilter::by_event(name.to_string(), trace_files, event_list)
    }
}
