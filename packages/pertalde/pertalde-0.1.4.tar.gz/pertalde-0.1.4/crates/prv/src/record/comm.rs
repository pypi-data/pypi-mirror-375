use super::object::Object;
use std::convert::TryFrom;
use std::fmt::Display;

#[derive(Debug, Clone, PartialEq)]
pub struct Comm {
    pub logic_send: u64,
    pub physical_send: u64,
    pub object_send: Object,

    pub logic_recv: u64,
    pub physical_recv: u64,
    pub object_recv: Object,

    pub size: u64,
    pub tag: u64,
}

use super::Reason;
use super::Wrapper;
impl<PrvRecord> TryFrom<Wrapper<PrvRecord>> for Comm
where
    PrvRecord: Iterator<Item = u64>,
{
    type Error = Reason;
    fn try_from(mut value: Wrapper<PrvRecord>) -> Result<Self, Self::Error> {
        let object_send: Object = (&mut value).try_into().map_err(|reason| match reason {
            Reason::TooFewValues(n) => Reason::TooFewValues(n + 10),
            _ => unreachable!(), // only TooFewValues can be returned from object
        })?;
        let logic_send = value.0.next().ok_or(Reason::TooFewValues(10))?;
        let physical_send = value.0.next().ok_or(Reason::TooFewValues(9))?;

        let object_recv: Object = (&mut value).try_into().map_err(|reason| match reason {
            Reason::TooFewValues(n) => Reason::TooFewValues(n + 4),
            _ => unreachable!(), // only TooFewValues can be returned from object
        })?;
        let logic_recv = value.0.next().ok_or(Reason::TooFewValues(4))?;
        let physical_recv = value.0.next().ok_or(Reason::TooFewValues(3))?;

        let size = value.0.next().ok_or(Reason::TooFewValues(2))?;
        let tag = value.0.next().ok_or(Reason::TooFewValues(1))?;

        let extra_values = value.0.count();
        if extra_values > 0 {
            return Err(Reason::TooManyValues(extra_values));
        }

        Ok(Self {
            object_send,
            logic_send,
            physical_send,

            object_recv,
            logic_recv,
            physical_recv,

            size,
            tag,
        })
    }
}

impl Display for Comm {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "3:{}:{}:{}:{}:{}:{}:{}:{}",
            self.object_send,
            self.logic_send,
            self.physical_send,
            self.object_recv,
            self.logic_recv,
            self.physical_recv,
            self.size,
            self.tag
        )
    }
}
