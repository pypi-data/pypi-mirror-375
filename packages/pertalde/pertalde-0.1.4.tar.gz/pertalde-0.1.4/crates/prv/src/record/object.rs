use std::convert::TryFrom;
use std::fmt::Display;

#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct Object {
    pub cpu: u64,
    pub appl: u64,
    pub task: u64,
    pub thread: u64,
}

#[derive(Debug, PartialEq, Eq)]
pub struct ParseObjectErr;

impl Object {
    pub fn new(cpu: u64, appl: u64, task: u64, thread: u64) -> Self {
        Self {
            cpu,
            appl,
            task,
            thread,
        }
    }
}

use super::Reason;

use super::Wrapper;
impl<PrvRecord> TryFrom<&mut Wrapper<PrvRecord>> for Object
where
    PrvRecord: Iterator<Item = u64>,
{
    type Error = Reason;
    fn try_from(value: &mut Wrapper<PrvRecord>) -> Result<Self, Self::Error> {
        Ok(Self {
            cpu: value.0.next().ok_or(Reason::TooFewValues(4))?,
            appl: value.0.next().ok_or(Reason::TooFewValues(3))?,
            task: value.0.next().ok_or(Reason::TooFewValues(2))?,
            thread: value.0.next().ok_or(Reason::TooFewValues(1))?,
        })
    }
}

impl Display for Object {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "{}:{}:{}:{}",
            self.cpu, self.appl, self.task, self.thread
        )
    }
}
