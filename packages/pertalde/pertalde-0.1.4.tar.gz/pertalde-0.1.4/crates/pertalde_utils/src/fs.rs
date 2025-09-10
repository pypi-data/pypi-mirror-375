pub mod rollback {

    use log::{debug, error, info};

    use std::{
        collections::{HashMap, HashSet},
        fs::OpenOptions,
        io,
        ops::Drop,
        path::Path,
        path::PathBuf,
    };

    #[derive(Default)]
    pub struct Rollback {
        // this store we should rollback upon droping
        commited: bool,

        // this store the original file name and the backup file name
        changed_files: HashMap<PathBuf, PathBuf>,

        // this tracks paths to files that have been created
        created_files: HashSet<PathBuf>,

        // this tracks the files that have been deleted
        deleted_files: HashMap<PathBuf, PathBuf>,

        // this tracks directories that have been created
        created_directories: Vec<PathBuf>,
    }

    impl Rollback {
        pub fn new() -> Self {
            Self::default()
        }

        pub fn commit(&mut self) -> io::Result<()> {
            self.commited = true;

            // Replace original file with the temporary (updated) file
            for (name, temp) in self.changed_files.iter() {
                std::fs::rename(temp, name)?;
            }
            Ok(())
        }

        fn add_to_created_files<P: AsRef<Path>>(&mut self, path: P) {
            self.created_files.insert(path.as_ref().to_path_buf());
        }

        fn add_to_changed_files<P: AsRef<Path>, N: AsRef<Path>>(&mut self, path: P, new: N) {
            self.changed_files
                .insert(path.as_ref().to_path_buf(), new.as_ref().to_path_buf());
        }

        fn add_to_deleted_files<P: AsRef<Path>, N: AsRef<Path>>(&mut self, path: P, temp: N) {
            self.deleted_files
                .insert(path.as_ref().to_path_buf(), temp.as_ref().to_path_buf());
        }

        fn add_to_created_dirs<P: AsRef<Path>>(&mut self, path: P) {
            self.created_directories.push(path.as_ref().to_path_buf())
        }

        // Creates a temporary file name
        fn handle_truncate_file<P: AsRef<Path>>(&mut self, path: P) -> Option<PathBuf> {
            let path = path.as_ref().to_path_buf();
            if path.exists() && !self.created_files.contains(&path) {
                let temp = generate_temporary_file(&path);
                self.add_to_changed_files(&path, &temp);
                Some(temp)
            } else {
                self.add_to_created_files(path);
                None
            }
        }

        // Creates a temporary copy of the file to write in if path already it exists
        fn handle_modify_file<P: AsRef<Path>>(&mut self, path: P) -> io::Result<Option<PathBuf>> {
            if let Some(temp) = self.handle_truncate_file(&path) {
                std::fs::copy(&path, &temp)?;
                return Ok(Some(temp));
            }
            Ok(None)
        }

        pub fn create_write<P: AsRef<Path>>(&mut self, path: P) -> io::Result<std::fs::File> {
            if path.as_ref().exists() {
                return Err(io::Error::from(io::ErrorKind::AlreadyExists));
            }
            self.add_to_created_files(&path);
            OpenOptions::new().write(true).create(true).open(path)
        }

        pub fn create_write_append<P: AsRef<Path>>(
            &mut self,
            path: P,
        ) -> io::Result<std::fs::File> {
            let path = self
                .handle_modify_file(&path)?
                .unwrap_or(path.as_ref().to_path_buf());
            OpenOptions::new().append(true).create(true).open(path)
        }

        pub fn create_write_force<P: AsRef<Path>>(&mut self, path: P) -> io::Result<std::fs::File> {
            let path = self
                .handle_truncate_file(&path)
                .unwrap_or(path.as_ref().to_path_buf());
            OpenOptions::new().write(true).create(true).open(path)
        }

        pub fn create_dir<P: AsRef<Path>>(&mut self, path: P) -> io::Result<()> {
            self.add_to_created_dirs(&path);
            std::fs::create_dir(path)
        }

        pub fn copy_file<F: AsRef<Path>, T: AsRef<Path>>(
            &mut self,
            from: F,
            to: T,
        ) -> io::Result<u64> {
            let to = self
                .handle_truncate_file(&to)
                .unwrap_or(to.as_ref().to_path_buf());
            std::fs::copy(from, to)
        }

        pub fn remove_file<P: AsRef<Path>>(&mut self, file: P) -> io::Result<()> {
            let file = file.as_ref().to_path_buf();
            if self.created_files.remove(&file) {
                std::fs::remove_file(&file)?;
                return Ok(());
            }

            if let Some(temp) = self.changed_files.remove(&file) {
                std::fs::remove_file(&temp)?;
                return Ok(());
            }

            let temp = generate_temporary_file(&file);
            self.add_to_deleted_files(&file, &temp);
            std::fs::rename(&file, &temp)
        }
    }

    fn generate_temporary_file<P: AsRef<Path>>(path: P) -> PathBuf {
        let mut temp = path.as_ref().to_path_buf();
        temp.add_extension("temp");
        temp
    }

    impl Drop for Rollback {
        fn drop(&mut self) {
            if !self.commited {
                info!("Rollback: starting filesystem recovery");

                // Remove temporary files
                for (name, temp) in self.changed_files.iter() {
                    if std::fs::remove_file(&temp).is_err() {
                        error!(
                            "Rollback: Could not recover {} during rollback",
                            name.to_string_lossy()
                        );
                    } else {
                        debug!("Rollback: Discarded changes in {}", name.to_string_lossy());
                    }
                }

                // Recover deleted files
                for (name, temp) in self.deleted_files.iter() {
                    if std::fs::rename(&temp, &name).is_err() {
                        error!(
                            "Rollback: Could not recover {} during rollabck",
                            name.to_string_lossy()
                        );
                    } else {
                        debug!("Rollback: Recovered file {}", name.to_string_lossy());
                    }
                }

                // Remove created files
                for name in self.created_files.iter() {
                    match std::fs::remove_file(&name) {
                        // Sucessfully removed
                        Ok(()) => (),
                        // It was already gone
                        Err(e) if e.kind() == io::ErrorKind::NotFound => (),
                        // Something went wrong
                        Err(_) => {
                            error!(
                                "Rollback: Could not remove file {} during rollback",
                                name.to_string_lossy()
                            );
                            continue;
                        }
                    }
                    debug!("Rollback: Discarded file {}", name.to_string_lossy());
                }

                // Remove created
                self.created_directories.dedup();
                for dir in self.created_directories.iter().rev() {
                    match std::fs::remove_dir_all(&dir) {
                        // Sucessfully removed
                        Ok(()) => (),
                        // It was already gone
                        Err(e) if e.kind() == io::ErrorKind::NotFound => (),
                        // Something went wrong
                        Err(_) => {
                            error!(
                                "Rollback: Could not remove dir {} during rollback",
                                dir.to_string_lossy()
                            );
                            continue;
                        }
                    }
                    debug!("Rollback: Deleted directory {}", dir.to_string_lossy());
                }
                info!("Rollback: finalized");
            }
        }
    }

    #[cfg(test)]
    mod test {
        use super::*;

        struct DirCleanup(PathBuf);

        impl Drop for DirCleanup {
            fn drop(&mut self) {
                std::fs::remove_dir_all(&self.0).unwrap_or(());
            }
        }

        struct FileCleanup(PathBuf);

        impl Drop for FileCleanup {
            fn drop(&mut self) {
                std::fs::remove_file(&self.0).unwrap_or(());
            }
        }

        #[test]
        fn test_create_file_uncommited() {
            let path = PathBuf::from("test_create_file_uncommited.txt");
            let _path_cleanup = FileCleanup(path.clone());
            let mut fs_rollback = Rollback::new();
            fs_rollback.create_write(&path).unwrap();
            drop(fs_rollback);
            assert!(!path.exists());
        }

        #[test]
        fn test_create_file_commited() {
            let path = PathBuf::from("test_create_file_commited.txt");
            let _path_cleanup = FileCleanup(path.clone());

            // Create the file and check if exists after droping
            {
                let mut fs_rollback = Rollback::new();
                fs_rollback.create_write(&path).unwrap();
                fs_rollback.commit().unwrap();
            }
            assert!(path.exists());

            // Delete the file but recover it
            {
                let mut fs_rollback = Rollback::new();
                fs_rollback.remove_file(&path).unwrap();
            }
            assert!(path.exists());

            // Delete the file
            {
                let mut fs_rollback = Rollback::new();
                fs_rollback.remove_file(&path).unwrap();
                fs_rollback.commit().unwrap();
            }
            assert!(!path.exists());
        }

        #[test]
        fn test_dir_uncommited() {
            let path = PathBuf::from("test_dir_uncommited.dir");
            let _path_cleanup = DirCleanup(path.clone());
            let mut fs_rollback = Rollback::new();
            fs_rollback.create_dir(&path).unwrap();
            drop(fs_rollback);
            assert!(!path.exists());
        }

        #[test]
        fn test_files_in_dir_uncommited() {
            let path = PathBuf::from("test_files_in_dir_uncommited.dir");
            let _path_cleanup = DirCleanup(path.clone());
            let file = PathBuf::from("test_files_in_dir_uncommited.dir/file1");
            let _file_cleanup = FileCleanup(file.clone());

            let mut fs_rollback = Rollback::new();
            fs_rollback.create_dir(&path).unwrap();
            fs_rollback.create_write(&file).unwrap();
            drop(fs_rollback);
            assert!(!path.exists());
            assert!(!file.exists());
        }

        #[test]
        fn test_dir_in_dir_uncommited() {
            let path1 = PathBuf::from("test_dir_in_dir_uncommited.dir");
            let _path1_cleanup = DirCleanup(path1.clone());
            let path2 = PathBuf::from("test_dir_in_dir_uncommited.dir/dir");
            let _path2_cleanup = DirCleanup(path2.clone());

            let mut fs_rollback = Rollback::new();
            fs_rollback.create_dir(&path1).unwrap();
            fs_rollback.create_dir(&path2).unwrap();
            drop(fs_rollback);

            assert!(!path1.exists());
            assert!(!path2.exists());
        }
    }
}
