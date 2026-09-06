// SPDX-FileCopyrightText: Copyright (c) 2026 Quadrant contributors
// SPDX-License-Identifier: GPL-3.0-only
//! Captures three synthetic native windows without starting Agent or storage.

use quadrant_ui::{MainWindow, QuickAddWindow, TaskEditorWindow, ThemeMode};
use slint::{ComponentHandle, LogicalSize};
use std::{fs::File, io::BufWriter, path::Path, time::Duration};

fn capture(window: &slint::Window, path: &Path) -> Result<(), Box<dyn std::error::Error>> {
    let pixels = window.take_snapshot()?;
    if pixels.width() == 0 || pixels.height() == 0 {
        return Err("empty native snapshot".into());
    }
    let mut png = png::Encoder::new(
        BufWriter::new(File::create(path)?),
        pixels.width(),
        pixels.height(),
    );
    png.set_color(png::ColorType::Rgba);
    png.set_depth(png::BitDepth::Eight);
    png.write_header()?.write_image_data(pixels.as_bytes())?;
    Ok(())
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let output = std::path::PathBuf::from(
        std::env::args_os()
            .nth(1)
            .ok_or("output directory required")?,
    );
    std::fs::create_dir_all(&output)?;
    let dark = std::env::args().nth(2).as_deref() == Some("dark");
    let theme = if dark {
        ThemeMode::Dark
    } else {
        ThemeMode::Light
    };
    let main = MainWindow::new()?;
    main.set_agent_connected(true);
    main.set_application_version("Synthetic integration probe".into());
    if std::env::args().nth(3).as_deref() == Some("focus") {
        main.set_current_route(2);
    }
    main.invoke_apply_theme(theme, dark);
    main.window().set_size(LogicalSize::new(1100.0, 720.0));
    let quick = QuickAddWindow::new()?;
    quick.set_title_text("Verify shared controls".into());
    quick.set_destination(2);
    quick.invoke_apply_theme(theme, dark);
    let editor = TaskEditorWindow::new()?;
    editor.set_task_id("synthetic-only".into());
    editor.set_title_text("Review remote Kit integration".into());
    editor.set_notes_text("No Agent, IPC or database is used by this probe.".into());
    editor.invoke_set_theme_mode(theme);
    main.show()?;
    quick.show()?;
    editor.show()?;
    let weak_main = main.as_weak();
    let weak_quick = quick.as_weak();
    let weak_editor = editor.as_weak();
    slint::Timer::single_shot(Duration::from_millis(1500), move || {
        let result = (|| -> Result<(), Box<dyn std::error::Error>> {
            capture(
                weak_main.upgrade().ok_or("main closed")?.window(),
                &output.join("main.png"),
            )?;
            capture(
                weak_quick.upgrade().ok_or("quick add closed")?.window(),
                &output.join("quick-add.png"),
            )?;
            capture(
                weak_editor.upgrade().ok_or("editor closed")?.window(),
                &output.join("task-editor.png"),
            )?;
            Ok(())
        })();
        if let Err(error) = result {
            eprintln!("native Product probe failed: {error}");
            std::process::exit(2);
        }
        drop(slint::quit_event_loop());
    });
    slint::run_event_loop()?;
    Ok(())
}
