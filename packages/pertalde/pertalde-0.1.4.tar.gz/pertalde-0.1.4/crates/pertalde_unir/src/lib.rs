mod args;
pub use args::Args;

mod translate;
use translate::PrvTranslator;

use std::collections::HashMap;
use std::error::Error;
use std::fs::File;
use std::io::Write;
use std::path::PathBuf;
use std::thread;

use pcf::Data;
use pertalde_utils::TraceFiles;

use anyhow::Context;
use itertools::Itertools;
use pertalde_utils::ProgressSpinner;

#[derive(thiserror::Error, Debug)]
#[error(transparent)]
pub struct PtdUnirError(#[from] anyhow::Error);

pub fn run(args: Args, traces: Vec<PathBuf>) -> Result<(), Box<dyn Error>> {
    Ok(run_wrapper(args, traces).map_err(PtdUnirError)?)
}

fn run_wrapper(mut args: Args, traces: Vec<PathBuf>) -> anyhow::Result<()> {
    args.build_type_groups()?;
    let args = args;

    let mut trace_files_in: HashMap<usize, TraceFiles> = traces
        .iter()
        .map(|trace| TraceFiles::from(trace))
        .into_iter()
        .enumerate()
        .collect();

    let mut traces_files_out: HashMap<usize, TraceFiles> = trace_files_in
        .iter()
        .map(|(k, v)| (k.clone(), v.clone()))
        .map(|(k, mut files_in)| {
            files_in.pop_all_dirs().push_extension(&args.sufix);
            if args.compress {
                files_in.set_compressed(true);
            }
            (k, files_in)
        })
        .collect();

    let pcf_files = trace_files_in
        .iter_mut()
        .sorted_by_key(|(k, _)| *k)
        .map(|(id, trace_in)| (*id, trace_in.pcf().to_owned()))
        .collect();
    let (mut translations, mut pcfs) = join_pcf::run(&args, pcf_files)?;

    for (id, mut files_in) in trace_files_in {
        let mut files_out = traces_files_out
            .remove(&id)
            .context("did not generate output trace files for this trace")?;

        let value_translations = translations
            .remove(&id)
            .context("did not generate value translation table for this trace")?;

        let mut translator =
            PrvTranslator::build(&mut files_in, &mut files_out).context("Preparing translation")?;
        translator
            .run(value_translations)
            .context("Translating trace")?;

        let pcf = pcfs
            .remove(&id)
            .context("did not generate new pcf for this trace")
            .unwrap();

        let pcf_path = files_out.pcf().clone();
        let write_pcf_thread = { thread::spawn(move || write_pcf(pcf, &pcf_path)) };
        let mut spinner = ProgressSpinner::new("Writting pcf...", None);
        let _ = spinner.wait_join_handle(write_pcf_thread);

        let copy_row_thread = {
            thread::spawn(move || {
                std::fs::copy(files_in.row(), files_out.row()).context("copying row file")
            })
        };
        let mut spinner = ProgressSpinner::new("Writting row...", None);
        let _ = spinner.wait_join_handle(copy_row_thread);
    }

    Ok(())
}

mod join_pcf {
    use super::args::Args;
    use std::collections::{HashMap, HashSet};
    use std::fs;
    use std::ops::Not;
    use std::path::PathBuf;

    use pcf::{Data, EventGroup, PcfParser, Rule};

    use anyhow::Context;
    use itertools::Itertools;

    pub(super) fn run(
        args: &Args,
        pcfs: HashMap<usize, PathBuf>,
    ) -> anyhow::Result<(
        HashMap<usize, HashMap<(u64, u64), u64>>,
        HashMap<usize, Data>,
    )> {
        let pcf_contents = read_pcfs(pcfs)?;
        let mut pcfs = parse_pcfs(pcf_contents)?;
        let mut value_translations = HashMap::new();

        let profile_type_groups: Vec<_> = args
            .profile
            .iter()
            .cloned()
            .flat_map(|p| p.get_type_groups().into_iter())
            .collect();

        let type_groups: Vec<_> = profile_type_groups
            .is_empty()
            .not()
            .then_some(profile_type_groups)
            .or(args.type_groups.clone())
            .context("user should have selected some types with (--types or --profile)")?;

        let mut offset = 0;
        // Update every type_group for every trace available
        for type_group in type_groups.into_iter() {
            let base_group = create_base_event_group(type_group.clone(), args.use_pcf.clone())?;
            let (new_pcfs, event_groups) = extract_event_groups(type_group, pcfs)?;
            let (joint_group, new_value_translations) = join_pcfs(
                args.squash_values,
                args.use_pcf.is_some(),
                event_groups,
                value_translations,
                base_group,
                offset,
                args.sorted_by_name,
            )?;

            if args.no_overlap_groups {
                offset += TryInto::<u64>::try_into(joint_group.values.len()).unwrap();
            }

            pcfs = add_event_group_to_pcfs(new_pcfs, joint_group)?;
            value_translations = new_value_translations;
        }

        Ok((value_translations, pcfs))
    }

    fn read_pcfs(pcf_files: HashMap<usize, PathBuf>) -> anyhow::Result<HashMap<usize, String>> {
        pcf_files
            .iter()
            .map(|(id, pcf_path)| {
                Ok((
                    *id,
                    fs::read_to_string(&pcf_path).context("reading the pcf files")?,
                ))
            })
            .collect()
    }

    fn parse_pcfs(pcf_contents: HashMap<usize, String>) -> anyhow::Result<HashMap<usize, Data>> {
        pcf_contents
            .into_iter()
            .map(|(id, file_content)| {
                let parse = <PcfParser as pest::Parser<Rule>>::parse(Rule::pcf, &file_content)
                    .context("parssing the pcf file")?;
                Ok((id, Data::try_from(parse).context("converting pcf file")?))
            })
            .collect::<anyhow::Result<_>>()
    }

    fn create_base_event_group(
        selected_types: HashSet<u64>,
        base_pcf: Option<String>,
    ) -> anyhow::Result<Option<EventGroup>> {
        if let Some(ref base_pcf) = base_pcf {
            let pcf = fs::read_to_string(base_pcf).context("reading the base pcf files")?;
            let pcf = <PcfParser as pest::Parser<Rule>>::parse(Rule::pcf, &pcf)
                .context("parssing the base pcf file")?;
            let pcf = Data::try_from(pcf).context("converting base pcf file")?;

            let (_, groups) = pcf::generate_index(pcf, selected_types.clone())?;
            if groups.len() != 1 {
                //Err("").context("all types should be already grouped in the base pcf.")?;
            }
            Ok(Some(groups.first().unwrap().clone()))
        } else {
            Ok(None)
        }
    }

    fn extract_event_groups(
        selected_types: HashSet<u64>,
        pcfs_data: HashMap<usize, Data>,
    ) -> anyhow::Result<(HashMap<usize, Data>, HashMap<usize, Vec<EventGroup>>)> {
        let mut groups = HashMap::new();
        let mut pcfs_data_new = HashMap::new();

        for (id, pcf) in pcfs_data.into_iter() {
            let (pcf, group) = pcf::generate_index(pcf, selected_types.clone())?;
            groups.insert(id, group);
            pcfs_data_new.insert(id, pcf);
        }

        Ok((pcfs_data_new, groups))
    }

    fn join_pcfs(
        squash: bool,
        uses_base_pcf: bool,
        event_groups: HashMap<usize, Vec<EventGroup>>,
        mut value_translations: HashMap<usize, HashMap<(u64, u64), u64>>,
        base_group: Option<EventGroup>,
        offset: u64,
        sorted_by_name: bool,
    ) -> anyhow::Result<(EventGroup, HashMap<usize, HashMap<(u64, u64), u64>>)> {
        let mut joint_group = base_group.unwrap_or_default();

        // Initialize value_by_name map with base pcf values.
        let mut found_repeated_event = false;
        let mut value_by_name = HashMap::new();
        joint_group.values.iter().for_each(|(id, name)| {
            if value_by_name.insert(name.to_string(), *id).is_some() {
                found_repeated_event = true;
            }
        });
        if found_repeated_event {
            return Err(anyhow::anyhow!(
                "Fatal: Found repeated semantic in base pcf, last semantic will be used."
            ));
        }

        for (trace_id, event_groups) in event_groups {
            let value_translation = value_translations.entry(trace_id).or_default();
            for event_group in event_groups {
                for (event_id, event_type) in event_group.types.iter().sorted_by_key(|(k, _)| *k) {
                    joint_group
                        .types
                        .entry(*event_id)
                        .or_insert(event_type.clone());
                }
                value_by_name = join_events_groups(
                    squash,
                    uses_base_pcf,
                    value_by_name,
                    value_translation,
                    event_group,
                    offset,
                    sorted_by_name,
                )?;
            }
        }

        joint_group.values = value_by_name
            .into_iter()
            .map(|(name, id)| (id, name))
            .collect();

        Ok((joint_group, value_translations))
    }

    fn join_events_groups(
        squash: bool,
        uses_base_pcf: bool,
        mut value_by_name: HashMap<String, u64>,
        translations: &mut HashMap<(u64, u64), u64>,
        event_group: EventGroup,
        offset: u64,
        sorted_by_name: bool,
    ) -> anyhow::Result<HashMap<String, u64>> {
        for type_id in event_group.types.keys() {
            let event_group_values: Vec<_> = if sorted_by_name {
                event_group
                    .values
                    .iter()
                    .sorted_by_key(|(_, name)| name.to_string())
                    .collect()
            } else {
                event_group.values.iter().collect()
            };

            for (value_id, value_name) in event_group_values {
                // By default if we are not squashing values we are going to pick the value for a
                // specific semantic of the first time it appears.
                let mut new_value_id = *value_id;

                if squash {
                    // If we are squashing values and we don't have a base pcf then we can assuem that
                    // the size of the HashSet with the currently treatead values can be the id for
                    // this value.
                    let size: u64 = value_by_name.len().try_into().unwrap();
                    new_value_id = size + offset + 1u64; // Offset because we don't want to have values with

                    // If we are using a base pcf we have to check if this value_id is already used by
                    // another value.
                    if uses_base_pcf && event_group.values.contains_key(&new_value_id) {
                        return Err(anyhow::anyhow!("when using squash-values and base-pcf together, the base-pcf must be pre-squshed"));
                    }
                }

                let translation = value_by_name
                    .entry(value_name.to_string())
                    // We don't want to translate zeroes, therefore we'll select the first semantantic that appears for them
                    // but keep the value_id of 0.
                    .or_insert_with(|| if *value_id == 0 { 0 } else { new_value_id });

                // We don't translate zeros nor values that don't change don't need to be
                if *value_id != 0 && translation != value_id {
                    translations
                        .entry((*type_id, *value_id))
                        .or_insert(*translation);
                }
            }
        }

        Ok(value_by_name)
    }

    fn add_event_group_to_pcfs(
        mut pcfs: HashMap<usize, Data>,
        joint_group: EventGroup,
    ) -> anyhow::Result<HashMap<usize, Data>> {
        pcfs.iter_mut()
            .for_each(|(_, pcf)| pcf.event_groups.push(joint_group.clone()));
        Ok(pcfs)
    }
}

fn write_pcf(pcf: Data, pcf_path: &PathBuf) -> anyhow::Result<()> {
    let mut file = File::create(pcf_path).context("Creating pcf file: {pcf_path}")?;
    write!(file, "{pcf}").context("writing pcf")?;
    Ok(())
}
