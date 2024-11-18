mod appstate;
mod handlers;
mod winit;

pub use appstate::CompxrState;

use smithay::reexports::{
    calloop::EventLoop,
    wayland_server::{Display, DisplayHandle},
};

pub struct CalloopData {
    state: CompxrState,
    display_handle: DisplayHandle,
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut event_loop: EventLoop<CalloopData> = EventLoop::try_new()?;

    let display: Display<CompxrState> = Display::new()?;
    let display_handle = display.handle();
    let state = CompxrState::new(&mut event_loop, display);


    
    let mut data = CalloopData {
        state,
        display_handle,
    };

    winit::init_winit(&mut event_loop, &mut data)?;

    event_loop.run(None, &mut data, move |_| {
        // empty loop because event driven
    })?;

    Ok(())
}
