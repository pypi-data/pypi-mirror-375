

use std::fmt::{Display, Formatter};

use crate::{errors::DTTError, params::channel_params::Channel};

#[cfg(any(feature = "python", feature = "python-pipe"))]
use pyo3::{pyclass, pymethods};
#[cfg(not(any(feature = "python", feature = "python-pipe")))]
use dtt_macros::{new, staticmethod};
#[cfg(feature = "all")]
use pyo3_stub_gen::{
    derive::{gen_stub_pyclass_complex_enum, gen_stub_pymethods, },
};

/// This is the name of a result
/// Can be of the simple form "SomeChannelName"
/// Or the compound form "Name(OtherID1, OtherID2, ...)"
/// 
/// Structured to avoid unnecessary string parsing
#[derive(Clone, Hash, Debug, PartialEq, Eq)]
#[cfg_attr(feature = "all", gen_stub_pyclass_complex_enum)]
#[cfg_attr(any(feature = "python", feature = "python-pipe"), pyclass(frozen, str, eq, hash))]
pub enum AnalysisID {
    Compound{name: String, args: Vec<AnalysisID>},
    Simple{channel: Channel},
}

impl Display for AnalysisID
{
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::Compound{name, args} => {
                f.write_str(name)?;
                if !args.is_empty() {
                    let mut first = true;
                    f.write_str("(")?;   
                    for sub_id in args {
                        if first {
                            first = false;
                        } else {
                            f.write_str(", ")?;
                        }
                        f.write_str(&sub_id.to_string())?;
                    }         
                    f.write_str(")")?;
                }
            }   
            Self::Simple{channel} => {
                f.write_str(&channel.name)?;
            }         
        }
        Ok(())
    }
}

#[macro_export]
macro_rules! analysis_id {
    ($name:expr, $($args:expr), +) => {
        AnalysisID::Compound {
            name: $name.to_string(),
            args: vec!($($args.into()),+),
        }
    };
    ($channel:expr) => {
        AnalysisID::Simple{channel: Channel::from($channel)}
    }
}

impl Default for AnalysisID {
    fn default() -> Self {
        return Channel::default().into()
    }
}

#[cfg_attr(feature = "all", gen_stub_pymethods)]
#[cfg_attr(any(feature = "python", feature = "python-pipe"), pymethods)]
impl AnalysisID
{
    #[staticmethod]
    fn from_channel(channel: Channel) -> Self {
        AnalysisID::Simple{channel}
    }

    #[new]
    fn new(name: String, args: Vec<AnalysisID>) -> Self {
        AnalysisID::Compound{name, args}
    }

    /// get the first channel
    fn first_channel(&self) -> Result<Channel, DTTError>
    {
        //there's always one channel
        self.channels().next().ok_or(DTTError::CalcError("A result ID has no associated channel".to_string()))
    }
}

impl AnalysisID
{
    pub fn channels(&'_ self) -> ChannelIterator<'_> 
    {
        ChannelIterator::new(self)
    }
}

impl<T> From<T> for AnalysisID
where
    Channel: From<T>
{
    fn from(value: T) -> Self {
        let c: Channel = value.into();
        Self::from_channel(c)
    }
}

pub struct ChannelIterator<'a> {
    id: &'a AnalysisID,
    count: usize,
    sub_iterator: Option<Box<ChannelIterator<'a>>>,
    done: bool,
}

impl<'a> Iterator for ChannelIterator<'a> {
    type Item=Channel;

    /// depth-first iteration of all channels in the id
    fn next(&mut self) -> Option<Self::Item> {
        match self.id {
            AnalysisID::Simple{channel} => {
                if self.done {
                    None
                } else {
                    self.done = true;
                    Some(channel.clone())                    
                }
            }
            AnalysisID::Compound{name: _, args} => {
                if self.count < args.len() {
                    match &mut self.sub_iterator {
                        None => { 
                            self.sub_iterator = Some(Box::new(ChannelIterator::new(&args[self.count])));
                            self.next()
                        }
                        Some(sub) => {
                            match sub.next() {
                                Some(x) => Some(x),
                                None => {
                                    self.count += 1;
                                    self.sub_iterator = None;
                                    self.next()
                                }
                            }
                        }
                    }
                    
                } else {
                    None
                }
            }
        }
    }
}

impl<'a> ChannelIterator<'a> {
    fn new(id: &'a AnalysisID) -> Self
    {
        Self {
            id,
            count: 0,
            sub_iterator: None,
            done: false,            
        }
    }
}