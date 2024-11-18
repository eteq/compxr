use std::ffi::OsString;
use std::sync::Arc;

use smithay::reexports::{
    wayland_server::{DisplayHandle, Display},
    wayland_server::backend::{ClientData, ClientId, DisconnectReason},
    calloop::{EventLoop, LoopSignal, generic::Generic, Interest, Mode, PostAction},
};
use smithay::wayland::{
    socket::ListeningSocketSource,
    compositor::CompositorClientState,
};

use crate::CalloopData;

pub struct CompxrState {
    pub start_time: std::time::Instant,
    pub display_handle: DisplayHandle,
    pub event_loop_signal: LoopSignal,
    pub wayland_socket_name: OsString,
}
impl CompxrState {
    pub fn new(event_loop: &mut EventLoop<CalloopData>, display: Display<Self>) -> Self {
        let start_time = std::time::Instant::now();

        let display_handle = display.handle();

        let event_loop_signal = event_loop.get_signal();

        let wayland_socket_name = Self::init_wayland_listener(display, event_loop);

        Self {
            start_time,
            display_handle,
            event_loop_signal,
            wayland_socket_name
        }
    }

    fn init_wayland_listener(
        display: Display<CompxrState>,
        event_loop: &mut EventLoop<CalloopData>,
    ) -> OsString {
        // Creates a new listening socket, automatically choosing the next available `wayland` socket name.
        let listening_socket = ListeningSocketSource::new_auto().unwrap();

        // Get the name of the listening socket.
        // Clients will connect to this socket.
        let socket_name = listening_socket.socket_name().to_os_string();

        let handle = event_loop.handle();

        handle
            .insert_source(listening_socket, move |client_stream, _, state| {
                // Inside the callback, you should insert the client into the display.
                //
                // You may also associate some data with the client when inserting the client.
                state
                    .display_handle
                    .insert_client(client_stream, Arc::new(ClientState::default()))
                    .unwrap();
            })
            .expect("Failed to init the wayland event source.");

        // You also need to add the display itself to the event loop, so that client events will be processed by wayland-server.
        handle
            .insert_source(
                Generic::new(display, Interest::READ, Mode::Level),
                |_, display, state| {
                    // Safety: we don't drop the display
                    unsafe {
                        display.get_mut().dispatch_clients(&mut state.state).unwrap();
                    }
                    Ok(PostAction::Continue)
                },
            )
            .unwrap();

        socket_name
    }
}

#[derive(Default)]
pub struct ClientState {
    pub compositor_state: CompositorClientState,
}

impl ClientData for ClientState {
    fn initialized(&self, _client_id: ClientId) {}
    fn disconnected(&self, _client_id: ClientId, _reason: DisconnectReason) {}
}