// SPDX-License-Identifier: GPL-3.0-only
//! Private directory and socket permissions, with kernel peer-UID verification.

use super::{AgentEndpoint, PeerIdentity};
use interprocess::local_socket::{
    GenericFilePath, ListenerOptions, Name, ToFsName,
    tokio::{Listener, Stream, prelude::*},
};
#[cfg(not(target_os = "macos"))]
use interprocess::os::unix::local_socket::ListenerOptionsExt;
use std::{
    fs, io,
    os::unix::fs::{DirBuilderExt, FileTypeExt, MetadataExt, PermissionsExt},
    path::{Path, PathBuf},
};

fn socket_path(database: &Path) -> io::Result<PathBuf> {
    let parent = database
        .parent()
        .ok_or_else(|| io::Error::other("missing profile directory"))?;
    Ok(parent.join("ipc").join(format!(
        "agent-{:016x}.sock",
        crate::instance::instance_identity(database)
    )))
}

pub(super) fn endpoint_name(path: &Path) -> io::Result<Name<'static>> {
    socket_path(path)?.to_fs_name::<GenericFilePath>()
}

fn effective_uid() -> u32 {
    // SAFETY: geteuid takes no pointers and has no failure mode.
    unsafe { libc::geteuid() }
}

pub(super) fn bind(endpoint: &AgentEndpoint) -> io::Result<Listener> {
    let socket = socket_path(&endpoint.database_path)?;
    let directory = socket
        .parent()
        .ok_or_else(|| io::Error::other("missing socket directory"))?;
    match fs::DirBuilder::new().mode(0o700).create(directory) {
        Ok(()) => {}
        Err(error) if error.kind() == io::ErrorKind::AlreadyExists => {}
        Err(error) => return Err(error),
    }
    let metadata = fs::symlink_metadata(directory)?;
    if !metadata.is_dir()
        || metadata.uid() != effective_uid()
        || metadata.permissions().mode() & 0o077 != 0
    {
        return Err(io::Error::new(
            io::ErrorKind::PermissionDenied,
            "IPC directory must be private and owned by the current user",
        ));
    }
    // The caller holds the current Agent profile lock, using the same stable
    // identity function as this socket name.
    // Remove only a stale socket owned by this user, never a symlink/regular file.
    match fs::symlink_metadata(&socket) {
        Ok(metadata) if metadata.file_type().is_socket() && metadata.uid() == effective_uid() => {
            fs::remove_file(&socket)?;
        }
        Ok(_) => {
            return Err(io::Error::new(
                io::ErrorKind::PermissionDenied,
                "unsafe IPC socket path",
            ));
        }
        Err(error) if error.kind() == io::ErrorKind::NotFound => {}
        Err(error) => return Err(error),
    }
    let options = ListenerOptions::new().name(endpoint.name()?);
    #[cfg(not(target_os = "macos"))]
    let options = options.mode(0o600);
    let listener = options.create_tokio()?;
    // Darwin rejects interprocess's pre-bind fchmod on the socket descriptor.
    // The already-verified owner-only directory prevents access by other users
    // while setting the filesystem socket mode, before returning the listener.
    // Peer UID verification remains mandatory on accepted and connected streams.
    #[cfg(target_os = "macos")]
    fs::set_permissions(&socket, fs::Permissions::from_mode(0o600))?;
    Ok(listener)
}

pub(super) fn verify_peer(stream: &Stream) -> io::Result<PeerIdentity> {
    let credentials = stream.peer_creds()?;
    if credentials.euid() != Some(effective_uid()) {
        return Err(io::Error::new(
            io::ErrorKind::PermissionDenied,
            "IPC peer is not the current user",
        ));
    }
    Ok(PeerIdentity {
        process_id: credentials.pid().and_then(|pid| u32::try_from(pid).ok()),
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::atomic::{AtomicUsize, Ordering};
    use tokio::io::{AsyncReadExt, AsyncWriteExt};

    static NEXT_PROFILE: AtomicUsize = AtomicUsize::new(0);

    struct Profile(PathBuf);

    impl Profile {
        fn new() -> Self {
            let nonce = std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_nanos();
            let serial = NEXT_PROFILE.fetch_add(1, Ordering::Relaxed);
            let root =
                std::env::temp_dir().join(format!("q-ipc-{}-{nonce}-{serial}", std::process::id()));
            fs::create_dir(&root).unwrap();
            Self(root)
        }

        fn endpoint(&self) -> AgentEndpoint {
            AgentEndpoint::for_database(&self.0.join("test.db")).unwrap()
        }
    }

    impl Drop for Profile {
        fn drop(&mut self) {
            let _ = fs::remove_dir_all(&self.0);
        }
    }

    #[tokio::test]
    async fn private_socket_permissions_and_authenticated_roundtrip() {
        let profile = Profile::new();
        let endpoint = profile.endpoint();
        let guard = crate::SingleInstanceCoordinator::claim(&endpoint.database_path).unwrap();
        let listener = guard.bind_agent_listener(&endpoint).unwrap();
        let socket = socket_path(&endpoint.database_path).unwrap();
        for (path, mode) in [(socket.parent().unwrap(), 0o700), (socket.as_path(), 0o600)] {
            let metadata = fs::symlink_metadata(path).unwrap();
            assert_eq!(metadata.permissions().mode() & 0o777, mode);
            assert_eq!(metadata.uid(), effective_uid());
        }
        tokio::time::timeout(std::time::Duration::from_secs(5), async {
            let (client, server) = tokio::join!(endpoint.connect(), listener.accept());
            let mut client = client.unwrap();
            let (mut server, _) = server.unwrap();
            client.write_all(b"ping").await.unwrap();
            let mut message = [0; 4];
            server.read_exact(&mut message).await.unwrap();
            assert_eq!(&message, b"ping");
            server.write_all(b"pong").await.unwrap();
            client.read_exact(&mut message).await.unwrap();
            assert_eq!(&message, b"pong");
        })
        .await
        .unwrap();
    }

    #[tokio::test]
    async fn rejects_non_private_directory_without_changing_its_permissions() {
        let profile = Profile::new();
        let endpoint = profile.endpoint();
        let directory = endpoint.database_path.parent().unwrap().join("ipc");
        fs::create_dir(&directory).unwrap();
        fs::set_permissions(&directory, fs::Permissions::from_mode(0o755)).unwrap();
        assert!(
            matches!(bind(&endpoint), Err(error) if error.kind() == io::ErrorKind::PermissionDenied)
        );
        assert_eq!(
            fs::metadata(&directory).unwrap().permissions().mode() & 0o777,
            0o755
        );
    }

    #[tokio::test]
    async fn refuses_to_replace_an_existing_non_socket_file() {
        let profile = Profile::new();
        let endpoint = profile.endpoint();
        let socket = socket_path(&endpoint.database_path).unwrap();
        fs::DirBuilder::new()
            .mode(0o700)
            .create(socket.parent().unwrap())
            .unwrap();
        fs::write(&socket, b"preserve this file").unwrap();
        assert!(
            matches!(bind(&endpoint), Err(error) if error.kind() == io::ErrorKind::PermissionDenied)
        );
        assert_eq!(fs::read(&socket).unwrap(), b"preserve this file");
    }
}
