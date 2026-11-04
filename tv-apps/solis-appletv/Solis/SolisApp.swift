import SwiftUI

@main
struct SolisApp: App {
    var body: some Scene {
        WindowGroup {
            RootView()
        }
    }
}

/// Kiest tussen het instelscherm (eerste keer) en het scherm met de pagina's.
struct RootView: View {
    @AppStorage("host") private var host: String = "homey.local"
    @AppStorage("port") private var port: Int = 8765
    @AppStorage("configured") private var configured: Bool = false
    @State private var editing: Bool = false

    var body: some View {
        if configured && !editing {
            ViewerView(
                config: SolisConfig(host: host, port: port),
                openSetup: { editing = true }
            )
        } else {
            SetupView(
                initialHost: host,
                initialPort: port,
                canCancel: configured,
                onCancel: { editing = false },
                onSave: { newHost, newPort in
                    host = newHost
                    port = newPort
                    configured = true
                    editing = false
                }
            )
        }
    }
}
