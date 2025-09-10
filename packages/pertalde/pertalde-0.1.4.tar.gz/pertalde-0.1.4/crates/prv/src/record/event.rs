use super::object::Object;

use std::convert::TryFrom;
use std::fmt::Display;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Event {
    pub object: Object,
    pub time: u64,
    pub event_type: u64,
    pub event_value: u64,
}

#[derive(Debug, Default, PartialEq, Eq)]
pub struct ParseEventErr;

#[derive(Debug, Clone, PartialEq)]
pub struct Events {
    pub object: Object,
    pub time: u64,
    pub events: Vec<(u64, u64)>,
}

impl Events {
    pub fn new(object: Object, time: u64, events: Vec<(u64, u64)>) -> Self {
        Self {
            object,
            time,
            events,
        }
    }
}

use super::Reason;

use super::Wrapper;
impl<PrvRecord> TryFrom<Wrapper<PrvRecord>> for Events
where
    PrvRecord: Iterator<Item = u64>,
{
    type Error = Reason;
    fn try_from(mut value: Wrapper<PrvRecord>) -> Result<Self, Self::Error> {
        let object: Object = (&mut value).try_into().map_err(|reason| match reason {
            Reason::TooFewValues(n) => Reason::TooFewValues(n + 3),
            _ => unreachable!(), // only TooFewValues can be returned from object
        })?;

        let value = &mut value.0;
        let time = value.next().ok_or(Reason::TooFewValues(3))?;

        let mut events = Vec::with_capacity(8);
        loop {
            match (value.next(), value.next()) {
                (Some(event_type), Some(event_value)) => events.push((event_type, event_value)),
                (None, None) => break,
                (Some(_), None) => return Err(Reason::TooFewValues(1)),
                (None, Some(_)) => unreachable!(), // once PrvRecord yields None it should be empty
            }
        }

        Ok(Self {
            object,
            time,
            events,
        })
    }
}

impl Display for Events {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "2:{}:{}", self.object, self.time)?;
        for (event_type, event_value) in self.events.iter() {
            write!(f, ":{event_type}:{event_value}")?;
        }
        Ok(())
    }
}
