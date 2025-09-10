use std::borrow::Cow;

use std::any::Any;
use std::time::Duration;
use std::{thread, thread::JoinHandle};

// static STYLE_TEMPLATE: &str =
//     "{wide_msg:>40.bold.blue} [{bar:30}] {percent:>3}% [{elapsed_precise}, eta: {eta_precise}]";

static STYLE_TEMPLATE: &str =
    "{wide_msg:<.bold.blue} [{bar:>30}] {percent:>3}% [{elapsed_precise}]";

static FINISH_STYLE_TEMPLATE: &str =
    "{wide_msg:<.bold.green} [{bar:>30}] {percent:>3}% [{elapsed_precise}]";

static STYLE_BAR_CHARS: &str = "=> ";

pub struct ProgressBar<IntoCowStr>
where
    IntoCowStr: Into<Cow<'static, str>>,
{
    bar: indicatif::ProgressBar,
    max: u64,
    cur: u64,
    redraw_point: u64,
    end_message: IntoCowStr,
}

impl<IntoCowStr> ProgressBar<IntoCowStr>
where
    IntoCowStr: Into<Cow<'static, str>> + Clone,
{
    pub fn new(max: u64, start_message: IntoCowStr, end_message: IntoCowStr) -> Self {
        let style = indicatif::ProgressStyle::with_template(STYLE_TEMPLATE)
            .unwrap()
            .progress_chars(STYLE_BAR_CHARS);

        let bar = indicatif::ProgressBar::new(max)
            .with_message(start_message)
            .with_style(style);

        Self {
            bar,
            max,
            cur: 0,
            redraw_point: 0,
            end_message,
        }
    }

    pub fn set_position(&mut self, position: u64) {
        if position >= self.redraw_point || self.cur > position {
            self.bar.set_position(position);
            if self.cur > position {
                self.redraw_point = 0;
            }
            loop {
                self.redraw_point += self.max / 200;
                if self.redraw_point > position {
                    break;
                }
            }
        }
        self.cur = position;
    }

    pub fn finish(&mut self) {
        let progress_style = indicatif::ProgressStyle::with_template(FINISH_STYLE_TEMPLATE)
            .unwrap()
            .progress_chars(STYLE_BAR_CHARS);

        self.bar.set_style(progress_style);
        self.bar.finish_with_message(self.end_message.clone());
    }
}

pub struct ProgressSpinner<IntoCowStr>
where
    IntoCowStr: Into<Cow<'static, str>>,
{
    bar: indicatif::ProgressBar,
    end_message: Option<IntoCowStr>,
}

impl<IntoCowStr> ProgressSpinner<IntoCowStr>
where
    IntoCowStr: Into<Cow<'static, str>> + Clone,
{
    pub fn new(start_message: IntoCowStr, end_message: Option<IntoCowStr>) -> Self {
        let spinner = indicatif::ProgressBar::new_spinner();
        spinner.set_style(
            indicatif::ProgressStyle::default_spinner()
                .template("{spinner:.green} {msg}")
                .unwrap()
                .tick_strings(&["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]),
        );
        spinner.set_message(start_message);

        Self {
            bar: spinner,
            end_message,
        }
    }

    pub fn tick(&mut self) {
        self.bar.tick();
    }

    pub fn finish(&mut self) {
        if let Some(end_message) = &self.end_message {
            self.bar.finish_with_message(end_message.clone());
        } else {
            self.bar.finish_and_clear();
        }
    }

    pub fn wait_join_handle<T>(
        &mut self,
        join_handle: JoinHandle<T>,
    ) -> Result<T, Box<dyn Any + Send>> {
        while !join_handle.is_finished() {
            thread::sleep(Duration::from_millis(300));
            self.tick();
        }
        self.finish();
        join_handle.join()
    }
}
