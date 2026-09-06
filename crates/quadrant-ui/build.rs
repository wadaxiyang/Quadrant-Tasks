// SPDX-FileCopyrightText: Copyright (c) 2026 Quadrant contributors
// SPDX-License-Identifier: GPL-3.0-only
//! Builds Product UI using the pinned remote Kit source facade.

use std::collections::HashMap;

fn main() {
    let facade = quadrant_kit::slint_library_path();
    assert!(facade.is_file(), "Kit facade must be a file");
    let libraries = HashMap::from([(quadrant_kit::SLINT_LIBRARY_NAME.to_owned(), facade)]);
    let config = slint_build::CompilerConfiguration::new()
        .with_style("fluent".into())
        .with_library_paths(libraries)
        .embed_resources(slint_build::EmbedResourcesKind::EmbedFiles);
    slint_build::compile_with_config("../../ui/app.slint", config)
        .expect("failed to compile the Quadrant Slint UI");
}
