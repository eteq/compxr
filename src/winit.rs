
use crate::CalloopData;
use smithay::reexports::calloop::EventLoop;
use smithay::backend::renderer::gles::GlesRenderer;
use smithay::backend::winit;
use smithay::output::Mode;

pub fn init_winit(
    event_loop: &mut EventLoop<CalloopData>,
    data: &mut CalloopData
) -> Result<(), Box<dyn std::error::Error>>{

    let (mut backend, winit) = winit::init()?;

    let mode = Mode {
        size: backend.window_size(),
        refresh:60000,
    };

    Ok(())
}