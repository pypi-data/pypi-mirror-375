use pest::iterators::Pairs;
use pest_derive::Parser;

use anyhow::Context;
use itertools::Itertools;

#[derive(Parser)]
#[grammar = "pcf.pest"]
pub struct PcfParser;

use std::collections::{HashMap, HashSet};
use std::fmt;

#[derive(Debug, Clone)]
pub struct Color(u8, u8, u8);

#[derive(Debug, Clone)]
pub struct DefaultOptions {
    level: String,
    units: String,
    look_back: usize,
    speed: usize,
    flag_icons: String,
    num_of_state_colors: usize,
    ymax_scale: usize,
}

impl fmt::Display for DefaultOptions {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let level = self.level.as_str();
        let units = self.units.as_str();
        let look_back = self.look_back;
        let speed = self.speed;
        let flag_icons = self.flag_icons.as_str();
        let num_of_state_colors = self.num_of_state_colors;
        let ymax_scale = self.ymax_scale;

        write!(
            f,
            "DEFAULT_OPTIONS

LEVEL               {level}
UNITS               {units}
LOOK_BACK           {look_back}
SPEED               {speed}
FLAG_ICONS          {flag_icons}
NUM_OF_STATE_COLORS {num_of_state_colors}
YMAX_SCALE          {ymax_scale}
"
        )
    }
}

impl TryFrom<Pairs<'_, self::Rule>> for DefaultOptions {
    type Error = anyhow::Error;

    fn try_from(pairs: Pairs<'_, self::Rule>) -> anyhow::Result<Self> {
        let mut level = None;
        let mut units = None;
        let mut look_back = None;
        let mut speed = None;
        let mut flag_icons = None;
        let mut num_of_state_colors = None;
        let mut ymax_scale = None;

        for pair in pairs {
            match pair.as_rule() {
                Rule::level => level = Some(pair.into_inner().as_str()),
                Rule::units => units = Some(pair.into_inner().as_str()),
                Rule::look_back => {
                    look_back = Some(
                        pair.into_inner()
                            .as_str()
                            .parse()
                            .context("converting to integer")?,
                    )
                }
                Rule::speed => {
                    speed = Some(
                        pair.into_inner()
                            .as_str()
                            .parse()
                            .context("converting to integer")?,
                    )
                }
                Rule::flag_icons => flag_icons = Some(pair.into_inner().as_str()),
                Rule::num_of_state_colors => {
                    num_of_state_colors = Some(
                        pair.into_inner()
                            .as_str()
                            .parse()
                            .context("converting to integer")?,
                    )
                }
                Rule::ymax_scale => {
                    ymax_scale = Some(
                        pair.into_inner()
                            .as_str()
                            .parse()
                            .context("converting to integer")?,
                    )
                }
                _ => panic! {"Syntax error! While parsing DefaultOptions! "},
            }
        }

        Ok(DefaultOptions {
            level: level.context("default option has level")?.to_string(),
            units: units.context("default option has units")?.to_string(),
            look_back: look_back.context("default option has look back")?,
            speed: speed.context("default option has speed")?,
            flag_icons: flag_icons
                .context("default option has flag icons")?
                .to_string(),
            num_of_state_colors: num_of_state_colors
                .context("default option has num of state colors")?,
            ymax_scale: ymax_scale.context("default option has ymax scale")?,
        })
    }
}

#[derive(Debug, Clone)]
pub struct DefaultSemantic {
    thread_func: String,
}

impl fmt::Display for DefaultSemantic {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let thread_func = self.thread_func.as_str();

        write!(
            f,
            "DEFAULT_SEMANTIC

THREAD_FUNC         {thread_func}
            "
        )
    }
}

impl TryFrom<Pairs<'_, self::Rule>> for DefaultSemantic {
    type Error = anyhow::Error;

    fn try_from(pairs: Pairs<'_, self::Rule>) -> anyhow::Result<Self> {
        let mut thread_func = None;

        for pair in pairs {
            match pair.as_rule() {
                Rule::thread_func => thread_func = Some(pair.into_inner().as_str()),
                _ => panic! {"Syntax error! While parsing DefaultSemantic ! "},
            }
        }

        Ok(DefaultSemantic {
            thread_func: thread_func
                .context("default semantic has thread func")?
                .to_string(),
        })
    }
}

#[derive(Debug, Clone)]
pub struct State {
    pub semantic: String,
    pub color: Color,
}

impl fmt::Display for Color {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let Color(red, green, blue) = self;
        write!(f, "{{{red},{green},{blue}}}")
    }
}

#[derive(Debug, Clone, Default)]
pub struct EventGroup {
    pub types: HashMap<u64, EventType>,
    pub values: HashMap<u64, String>,
}

impl fmt::Display for EventGroup {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        writeln!(f, "EVENT_TYPE")?;
        for (event_id, event_type) in self.types.clone().into_iter().sorted_by_key(|(k, _)| *k) {
            writeln!(
                f,
                "{} {} {}",
                event_type.gradient_id, event_id, event_type.name
            )?;
        }

        if !self.values.is_empty() {
            writeln!(f, "VALUES")?;
            for (value_id, value_name) in self.values.clone().into_iter().sorted_by_key(|(k, _)| *k)
            {
                writeln!(f, "{value_id}   {value_name}")?;
            }
        }

        Ok(())
    }
}

impl TryFrom<Pairs<'_, self::Rule>> for EventGroup {
    type Error = anyhow::Error;

    fn try_from(pairs: Pairs<'_, self::Rule>) -> anyhow::Result<Self> {
        let mut types = HashMap::new();
        let mut values = HashMap::new();

        for pair in pairs {
            match pair.as_rule() {
                Rule::event_types => {
                    let mut pair = pair.into_inner();
                    let gradient_id = pair
                        .next()
                        .context("Event type to have GradientID")?
                        .as_str();
                    let gradient_id = gradient_id.parse().context("converting to integer")?;

                    let type_id = pair.next().context("Event type to have TypeID")?.as_str();
                    let type_id = type_id.parse().context("converting to integer")?;

                    let name = pair.next().context("Event type to have Semantic")?.as_str();

                    types.insert(
                        type_id,
                        EventType {
                            gradient_id,
                            name: name.to_string(),
                        },
                    );
                }
                Rule::event_values => {
                    for (id, name) in pair.into_inner().tuples() {
                        let id = id.as_str().parse().context("converting to integer")?;
                        let name = name.as_str();
                        values.insert(id, name.to_string());
                    }
                }
                _ => panic! {"Syntax error! While parsing EventGroup ! "},
            }
        }

        Ok(EventGroup { types, values })
    }
}

#[derive(Debug, Clone)]
pub struct EventType {
    pub gradient_id: u64,
    pub name: String,
}

#[derive(Debug, Clone)]
pub struct Gradient {
    pub semantic: String,
    pub color: Color,
}

#[derive(Debug, Clone)]
pub struct Data {
    pub default_options: Option<DefaultOptions>,
    pub default_semantic: Option<DefaultSemantic>,

    pub states: HashMap<u64, State>,
    pub event_groups: Vec<EventGroup>,
    pub gradients: HashMap<u64, Gradient>,
}

impl fmt::Display for Data {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        if let Some(default_options) = self.default_options.clone() {
            write!(f, "{default_options}")?;
            write!(f, "\n\n")?;
        }

        if let Some(default_semantic) = self.default_semantic.clone() {
            write!(f, "{default_semantic}")?;
            write!(f, "\n\n")?;
        }

        if !self.states.is_empty() {
            writeln!(f, "STATES")?;
            for (state_id, state) in self.states.clone().iter().sorted_by_key(|(k, _)| *k) {
                writeln!(f, "{state_id} {}", state.semantic)?;
            }
            write!(f, "\n\n")?;

            writeln!(f, "STATES_COLOR")?;
            for (state_id, state) in self.states.clone().iter().sorted_by_key(|(k, _)| *k) {
                writeln!(f, "{state_id} {}", state.color)?;
            }
            write!(f, "\n\n")?;
        }

        if !self.gradients.is_empty() {
            writeln!(f, "GRADIENT_COLOR")?;
            for (gradient_id, gradient) in self.gradients.clone().iter().sorted_by_key(|(k, _)| *k)
            {
                writeln!(f, "{gradient_id} {}", gradient.color)?;
            }
            write!(f, "\n\n")?;

            writeln!(f, "GRADIENT_NAMES")?;
            for (gradient_id, gradient) in self.gradients.clone().iter().sorted_by_key(|(k, _)| *k)
            {
                writeln!(f, "{gradient_id} {}", gradient.semantic)?;
            }
            write!(f, "\n\n")?;
        }

        for event_group in self.event_groups.clone() {
            if event_group.types.is_empty() {
                continue;
            }
            write!(f, "{event_group}")?;
            write!(f, "\n\n")?;
        }

        Ok(())
    }
}

impl TryFrom<Pairs<'_, self::Rule>> for Data {
    type Error = anyhow::Error;

    fn try_from(pairs: Pairs<'_, self::Rule>) -> anyhow::Result<Data> {
        let mut pairs = pairs;
        let pairs = pairs.next().context("parssing pcf")?.into_inner();

        let mut default_options: Option<DefaultOptions> = None;
        let mut default_semantic: Option<DefaultSemantic> = None;

        let mut states_color: HashMap<u64, Color> = HashMap::new();
        let mut states_names: HashMap<u64, String> = HashMap::new();

        let mut event_groups: Vec<EventGroup> = Vec::new();

        let mut gradient_color: HashMap<u64, Color> = HashMap::new();
        let mut gradient_names: HashMap<u64, String> = HashMap::new();

        for pair in pairs {
            match pair.as_rule() {
                Rule::default_options => {
                    default_options = Some(
                        pair.into_inner()
                            .try_into()
                            .context("parsing default options")?,
                    )
                }
                Rule::default_semantic => {
                    default_semantic = Some(
                        pair.into_inner()
                            .try_into()
                            .context("parsing default semantic")?,
                    )
                }
                Rule::state_colors => {
                    for state in pair.into_inner() {
                        let mut color_by_id = state.into_inner();
                        let id = color_by_id.next().context("state to have ID")?.as_str();
                        let id = id.parse().context("converting to integer")?;

                        let color = color_by_id.next().context("state to have Name")?;
                        let mut color = color.into_inner();

                        let red = color.next().context("Color to have Red")?.as_str();
                        let red = red.parse().context("converting to integer")?;

                        let green = color.next().context("Color to have Green")?.as_str();
                        let green = green.parse().context("convergin to integer")?;

                        let blue = color.next().context("Color to have Blue")?.as_str();
                        let blue = blue.parse().context("converting to integer")?;

                        let color = Color(red, green, blue);

                        states_color.insert(id, color);
                    }
                }

                Rule::states => {
                    for state in pair.into_inner() {
                        let mut name_by_id = state.into_inner();
                        let id = name_by_id.next().context("state to have ID")?.as_str();
                        let id = id.parse().context("converting to integer")?;
                        let name = name_by_id.next().context("state to have Name")?.as_str();

                        states_names.insert(id, name.to_string());
                    }
                }
                Rule::gradient_colors => {
                    for gradient in pair.into_inner() {
                        let mut color_by_id = gradient.into_inner();
                        let id = color_by_id.next().context("state to have ID")?.as_str();
                        let id = id.parse().context("converting to integer")?;
                        let color = color_by_id.next().context("state to have Name")?;
                        let mut color = color.into_inner();

                        let red = color.next().context("Color to have Red")?.as_str();
                        let red = red.parse().context("converting to integer")?;

                        let green = color.next().context("Color to have Red")?.as_str();
                        let green = green.parse().context("converting to integer")?;

                        let blue = color.next().context("Color to have Red")?.as_str();
                        let blue = blue.parse().context("converting to integer")?;

                        let color = Color(red, green, blue);

                        gradient_color.insert(id, color);
                    }
                }
                Rule::gradient_names => {
                    for gradient in pair.into_inner() {
                        let mut name_by_id = gradient.into_inner();
                        let id = name_by_id.next().context("state to have ID")?.as_str();
                        let id = id.parse().context("converting integer")?;
                        let name = name_by_id.next().context("state to have Name")?.as_str();

                        gradient_names.insert(id, name.to_string());
                    }
                }
                Rule::event => {
                    event_groups.push(pair.into_inner().try_into().context("parsing event grup")?)
                }
                rule => {
                    panic! {"Syntax error! Unknow rule: {rule:?}"};
                }
            }
        }

        let default_options = default_options;
        let default_semantic = default_semantic;

        let states: HashMap<u64, State> = states_names
            .into_iter()
            .map(|(id, name)| {
                Ok::<(u64, State), anyhow::Error>((
                    id,
                    State {
                        semantic: name.to_string(),
                        color: states_color
                            .remove(&id)
                            .context(format! {"state with name ({id}, {name}) to have Color"})?,
                    },
                ))
            })
            .collect::<anyhow::Result<_>>()?;

        let gradients: HashMap<u64, Gradient> = gradient_names
            .into_iter()
            .map(|(id, name)| {
                Ok::<(u64, Gradient), anyhow::Error>((
                    id,
                    Gradient {
                        semantic: name.to_string(),
                        color: gradient_color
                            .remove(&id)
                            .context(format! {"gradient with name ({id}, {name}) to have Color"})?,
                    },
                ))
            })
            .collect::<anyhow::Result<_>>()?;

        Ok(Data {
            default_options,
            default_semantic,
            states,
            event_groups,
            gradients,
        })
    }
}

pub fn generate_index(
    pcf: Data,
    selected_types: HashSet<u64>,
) -> anyhow::Result<(Data, Vec<EventGroup>)> {
    let mut pcf = pcf;
    let mut groups = vec![];

    for group_id in (0..pcf.event_groups.len()).rev() {
        if pcf.event_groups[group_id]
            .types
            .keys()
            .any(|key| selected_types.contains(key))
        {
            let group = pcf.event_groups.remove(group_id);
            groups.push(group);
        }
    }

    Ok((pcf, groups))
}
