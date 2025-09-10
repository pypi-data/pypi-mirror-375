use anyhow::Context;
use clap::{ArgAction, ArgGroup, ValueEnum};

use std::collections::HashSet;

#[derive(clap::Args, Debug, Clone)]
#[clap(group(
        ArgGroup::new("mode")
        .required(true)
        .args(&["type_groups_str", "profile"]),
))]
pub struct Args {
    /// unify the event values of the event types listed in EVENT_TYPES.
    ///
    /// Every use of the flag will create a group of these types. If two groups overlap, this will
    /// result in a single, bigger group.
    #[arg(short = 't', long = "types", value_name = "EVENT_TYPES")]
    type_groups_str: Vec<String>,

    #[clap(skip)]
    pub type_groups: Option<Vec<HashSet<u64>>>,

    /// predefined groups of types made for specific tools
    #[arg(short, long, value_enum, conflicts_with = "type_groups_str")]
    pub profile: Vec<Profile>,

    /// ensure that types in different groups don't have overlapping values
    #[arg(long = "no-overlap-types", conflicts_with = "squash_values")]
    pub no_overlap_groups: bool,

    /// don't make the values of the selected types to be consecutive
    #[arg(long = "no-squash-values", action = ArgAction::SetFalse)]
    pub squash_values: bool,

    /// sort event values in the same grouyp by name
    #[arg(long = "sort-values-by-name", conflicts_with = "squash_values")]
    pub sorted_by_name: bool,

    /// compress the output traces with gzip
    #[arg(long = "compress", short = 'c')]
    pub compress: bool,

    /// use this pcf as the base
    ///
    /// when this option is used without the no-sqush-values option, its assumed that the pcf
    /// already has the values squashed. Otherwise the program will abort.
    #[arg(long = "base-pcf", value_name = ".pcf")]
    pub use_pcf: Option<String>,

    /// the sufix to use for the new files.
    #[arg(long = "sufix", default_value = "juntar")]
    pub sufix: String,
}

impl Args {
    pub fn build_type_groups(&mut self) -> anyhow::Result<()> {
        let mut type_groups = Vec::with_capacity(self.type_groups_str.len());
        for type_pattern in self.type_groups_str.iter() {
            type_groups.push(parse_range(type_pattern)?);
        }
        self.type_groups = Some(type_groups);
        Ok(())
    }
}

fn parse_range(input: &str) -> anyhow::Result<HashSet<u64>> {
    let error_message = "expects a list of integers (e.g. 1-100,80)";
    Ok(input
        .split(',')
        .map(|element| element.split_once('-').unwrap_or((element, element)))
        .map(|(start, end)| {
            let start: u64 = start.parse().context(error_message)?;
            let end: u64 = end.parse().context(error_message)?;
            Ok(start..=end)
        })
        .collect::<anyhow::Result<Vec<_>>>()?
        .into_iter()
        .flatten()
        .collect::<HashSet<u64>>())
}

#[derive(Debug, Copy, Clone, PartialEq, Eq, PartialOrd, Ord, ValueEnum)]
pub enum Profile {
    Nsys2prv,
    Nesmik,
}

impl Profile {
    pub fn get_type_groups(&self) -> Vec<HashSet<u64>> {
        match self {
            Self::Nsys2prv => todo!(),
            Self::Nesmik => vec![
                parse_range("81000-81999").expect("hardcoded event gorup range"),
                parse_range("82000").expect("hardcoded event gorup range"),
            ],
        }
    }
}
