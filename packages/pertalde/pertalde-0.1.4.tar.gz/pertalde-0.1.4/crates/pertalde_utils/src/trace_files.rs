use anyhow::Context;

use std::{
    convert::{AsRef, From},
    ffi::{OsStr, OsString},
    ops::Deref,
    os::unix::ffi::OsStrExt,
    path::PathBuf,
    sync::OnceLock,
};

#[derive(Debug, Clone)]
pub struct TraceFiles {
    base_name: PathBuilder,
    prv: OnceLock<PathBuf>,
    pcf: OnceLock<PathBuf>,
    row: OnceLock<PathBuf>,
    compressed_prv: bool,
}

impl<P: Into<PathBuilder>> From<P> for TraceFiles {
    // Note: Here we should implement TryFrom but we cannot because of the issue
    //       https://github.com/rust-lang/rust/issues/50133
    fn from(path: P) -> Self {
        let path: PathBuilder = path.into();

        // Check if trace is compressed
        let mut compressed_prv = false;
        if path.extension() == Some("gz") {
            compressed_prv = true;
        }

        // Remove the "gz" if compressed and afterwards "prv" to get the base name
        let mut base_name = path;
        if compressed_prv {
            base_name.pop_extension()
        } else {
            Some(&mut base_name)
        }
        .and_then(|p| p.pop_extension())
        .unwrap();
        //.context("could not remove extension to get base name from")?;

        TraceFiles {
            base_name,
            prv: OnceLock::new(),
            pcf: OnceLock::new(),
            row: OnceLock::new(),
            compressed_prv,
        }
    }
}

impl TraceFiles {
    pub fn base_name(&self) -> &PathBuilder {
        &self.base_name
    }

    pub fn prv(&self) -> &PathBuf {
        let ext = if self.compressed_prv { "prv.gz" } else { "prv" };
        self.prv.get_or_init(|| {
            let mut path = self.base_name.clone();
            path.push_extension(ext);
            path.as_path_buf().to_owned()
        })
    }

    pub fn prv_size(&self) -> anyhow::Result<u64> {
        let metadata = std::fs::metadata(self.prv())
            .with_context(|| format!("getting size of file {}", self.prv().to_string_lossy()))?;

        Ok(metadata.len())
    }

    pub fn pcf(&self) -> &PathBuf {
        self.pcf.get_or_init(|| {
            let mut path = self.base_name.clone();
            path.push_extension("pcf");
            path.as_path_buf().to_owned()
        })
    }

    pub fn row(&self) -> &PathBuf {
        self.row.get_or_init(|| {
            let mut path = self.base_name.clone();
            path.push_extension("row");
            path.as_path_buf().to_owned()
        })
    }

    pub fn is_compressed(&self) -> bool {
        self.compressed_prv
    }

    pub fn set_compressed(&mut self, compress: bool) {
        if self.compressed_prv != compress {
            self.prv = OnceLock::new();
        }
        self.compressed_prv = compress;
    }

    pub fn pop_extension(&mut self) -> &mut Self {
        // Remove the last sufix
        let mut base_name = self.base_name.clone();
        if base_name.pop_extension().is_none() {
            return self;
        }
        self.base_name = base_name;
        self.clear_caches();
        self
    }

    pub fn push_extension<S: AsRef<OsStr>>(&mut self, extension: S) -> &mut Self {
        // Add sufix
        self.base_name.push_extension(extension);
        self.clear_caches();
        self
    }

    pub fn push_dir<S: AsRef<OsStr>>(&mut self, dir: S) -> &mut Self {
        self.base_name.push_dir(&dir);
        self.clear_caches();
        self
    }

    pub fn pop_dir(&mut self) -> &mut Self {
        self.base_name.pop_dir();
        self.clear_caches();
        self
    }

    pub fn pop_all_dirs(&mut self) -> &mut Self {
        self.base_name.pop_all_dirs();
        self.clear_caches();
        self
    }

    fn clear_caches(&mut self) {
        self.prv = OnceLock::new();
        self.pcf = OnceLock::new();
        self.row = OnceLock::new();
    }
}

#[derive(Clone, Debug)]
pub struct PathBuilder {
    buf: PathBuf,
}

impl<P: AsRef<OsStr>> From<P> for PathBuilder {
    fn from(path: P) -> Self {
        //path.as_ref().to_path_buf().into()
        Self {
            buf: (&path).into(),
        }
    }
}

impl Deref for PathBuilder {
    type Target = PathBuf;
    fn deref(&self) -> &Self::Target {
        &self.buf
    }
}

impl PathBuilder {
    pub fn extension(&self) -> Option<&str> {
        self.buf.extension()?.to_str()
    }

    pub fn pop_extension(&mut self) -> Option<&mut Self> {
        self.buf.set_extension("").then_some(self)
    }

    pub fn push_extension<S: AsRef<OsStr>>(&mut self, extension: S) -> &mut Self {
        let extension = extension.as_ref();

        // If the provided extension is empty, we do nothing and return self
        if extension.is_empty() {
            return self;
        }

        let capacity = extension.as_bytes().len()
            + self
                .buf
                .extension()
                .map(|current| current.as_bytes().len() + 1)
                .unwrap_or(0);

        let mut new_extension = OsString::with_capacity(capacity);

        if let Some(current_extension) = self.buf.extension() {
            new_extension.push(current_extension);
            new_extension.push(".");
        }

        new_extension.push(extension);
        self.buf.set_extension(new_extension);

        self
    }

    pub fn push_dir<S: AsRef<OsStr>>(&mut self, dir: S) -> &mut Self {
        let file_name = self
            .buf
            .file_name()
            .expect("path has been sanitazed in PathBuilder construction")
            .to_owned();

        let _ = self.buf.pop();
        self.buf.push(dir.as_ref());
        self.buf.push(file_name);
        self
    }

    pub fn pop_dir(&mut self) -> &mut Self {
        let _ = self.buf.pop();
        self
    }

    pub fn pop_all_dirs(&mut self) -> &mut Self {
        self.buf = PathBuf::from(self.buf.file_name().unwrap());
        self
    }

    pub fn as_path_buf(&self) -> &PathBuf {
        &self.buf
    }
}

#[cfg(test)]
mod test {

    use super::TraceFiles;
    use std::{assert, assert_eq, path::Path};

    #[test]
    fn test_create_trace_files() {
        let _ = TraceFiles::from("test.prv".to_string());
    }

    #[test]
    fn test_paraver_files() {
        let path = TraceFiles::try_from("test.prv").unwrap();

        assert_eq! {path.prv().as_os_str().to_str().unwrap(), "test.prv"};
        assert_eq! {path.pcf().as_os_str().to_str().unwrap(), "test.pcf"};
        assert_eq! {path.row().as_os_str().to_str().unwrap(), "test.row"};
    }

    #[test]
    fn test_paraver_files_compressed() {
        let path = TraceFiles::try_from("test.prv.gz").unwrap();

        assert!(path.compressed_prv);
        assert_eq! {path.prv().as_os_str().to_str().unwrap(), "test.prv.gz"};
        assert_eq! {path.pcf().as_os_str().to_str().unwrap(), "test.pcf"};
        assert_eq! {path.row().as_os_str().to_str().unwrap(), "test.row"};
    }

    #[test]
    fn test_paraver_files_with_sufix() {
        let mut path = TraceFiles::try_from(Path::new("test.prv.gz")).unwrap();

        path.push_extension("sufix");
        assert_eq! {path.prv().as_os_str().to_str().unwrap(), "test.sufix.prv.gz"};
        assert_eq! {path.pcf().as_os_str().to_str().unwrap(), "test.sufix.pcf"};
        assert_eq! {path.row().as_os_str().to_str().unwrap(), "test.sufix.row"};
    }
}
