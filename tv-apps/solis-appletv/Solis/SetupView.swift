import SwiftUI

/// Instelscherm: adres en poort van de Homey. Wordt de eerste keer getoond.
struct SetupView: View {
    let canCancel: Bool
    let onCancel: () -> Void
    let onSave: (String, Int) -> Void

    @State private var host: String
    @State private var portText: String
    @State private var testResult: String = ""
    @State private var testing: Bool = false

    init(initialHost: String, initialPort: Int, canCancel: Bool,
         onCancel: @escaping () -> Void, onSave: @escaping (String, Int) -> Void) {
        self.canCancel = canCancel
        self.onCancel = onCancel
        self.onSave = onSave
        _host = State(initialValue: initialHost)
        _portText = State(initialValue: String(initialPort))
    }

    private var port: Int {
        let n = Int(portText) ?? 8765
        return (1...65535).contains(n) ? n : 8765
    }

    var body: some View {
        VStack(spacing: 36) {
            Text("Solis")
                .font(.largeTitle)
                .bold()
            Text("Vul het adres in van je Homey, waarop de Solis-app draait. Meestal is dat homey.local en poort 8765. Apple TV en Homey moeten op hetzelfde wifi-netwerk zitten.")
                .multilineTextAlignment(.center)
                .frame(maxWidth: 1100)

            VStack(spacing: 24) {
                TextField("Adres van Homey (bijvoorbeeld homey.local)", text: $host)
                    .autocorrectionDisabled(true)
                TextField("Poort (standaard 8765)", text: $portText)
                    .autocorrectionDisabled(true)
                    .onChange(of: portText) { newValue in
                        let digits = newValue.filter { $0.isNumber }
                        if digits != newValue { portText = digits }
                    }
            }
            .frame(maxWidth: 900)

            HStack(spacing: 40) {
                Button("Test verbinding") {
                    Task { await runTest() }
                }
                .disabled(testing)

                Button("Opslaan en starten") {
                    let cleanHost = host.trimmingCharacters(in: .whitespacesAndNewlines)
                    onSave(cleanHost.isEmpty ? "homey.local" : cleanHost, port)
                }

                if canCancel {
                    Button("Terug", action: onCancel)
                }
            }

            Text(testing ? "Even testen…" : testResult)
                .multilineTextAlignment(.center)
                .frame(maxWidth: 1100, minHeight: 80)
        }
        .padding(60)
    }

    @MainActor
    private func runTest() async {
        testing = true
        testResult = ""
        let cleanHost = host.trimmingCharacters(in: .whitespacesAndNewlines)
        let client = SolisClient(config: SolisConfig(host: cleanHost.isEmpty ? "homey.local" : cleanHost, port: port))
        do {
            let list = try await client.pages()
            testResult = "Gelukt: \(list.count) pagina's gevonden."
        } catch {
            testResult = SolisClient.describe(error)
        }
        testing = false
    }
}
