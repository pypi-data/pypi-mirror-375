use super::object::Object;
use std::convert::TryFrom;
use std::fmt::Display;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct State {
    pub object: Object,
    pub state: u64,
    pub start: u64,
    pub end: u64,
}

impl State {
    pub fn duration(&self) -> u64 {
        self.end.checked_sub(self.start).unwrap_or(0)
        // .expect("state constructor must guarantee positive duration")
    }
}

#[derive(Debug, Default, PartialEq, Eq)]
pub struct ParseError;

use super::Reason;

use super::Wrapper;
impl<PrvRecord> TryFrom<Wrapper<PrvRecord>> for State
where
    PrvRecord: Iterator<Item = u64>,
{
    type Error = Reason;

    fn try_from(mut value: Wrapper<PrvRecord>) -> Result<Self, Self::Error> {
        let object: Object = (&mut value).try_into().map_err(|reason| match reason {
            Reason::TooFewValues(n) => Reason::TooFewValues(n + 3),
            _ => unreachable!(), // only TooFewValues can be returned from object
        })?;

        let mut value = value.0;

        let start = value.next().ok_or(Reason::TooFewValues(3))?;
        let end = value.next().ok_or(Reason::TooFewValues(2))?;
        let state = value.next().ok_or(Reason::TooFewValues(1))?;

        let extra_values = value.count();
        if extra_values > 0 {
            return Err(Reason::TooManyValues(extra_values));
        }

        Ok(Self {
            object,
            start,
            end,
            state,
        })
    }
}

impl Display for State {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "1:{}:{}:{}:{}",
            self.object, self.start, self.end, self.state
        )
    }
}
