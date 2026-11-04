import SwiftUI

/// Toont de tv-pagina's van de Solis-app schermvullend.
/// Links/rechts op de Siri Remote wisselt van pagina, Select ververst, Menu opent het menu.
struct ViewerView: View {
    let config: SolisConfig
    let openSetup: () -> Void

    @State private var pages: [String] = []
    @State private var index: Int = 0
    @State private var image: UIImage? = nil
    @State private var errorText: String? = nil
    @State private var showMenu: Bool = false
    @State private var requestID: Int = 0
    @State private var lastUpdate: Date? = nil
    @FocusState private var viewerFocused: Bool

    var body: some View {
        ZStack {
            viewerLayer
                .focusable(!showMenu)
                .focused($viewerFocused)
                .onMoveCommand { direction in
                    guard !showMenu else { return }
                    switch direction {
                    case .left: step(-1)
                    case .right: step(1)
                    default: break
                    }
                }
                .onTapGesture {
                    if !showMenu { Task { await refresh() } }
                }

            if showMenu {
                menuLayer
            }
        }
        // Menu-knop: eerst het menu, nog een keer drukken sluit de app (standaardgedrag van tvOS).
        .onExitCommand(perform: exitAction)
        .onChange(of: showMenu) { open in
            if !open { viewerFocused = true }
        }
        .onAppear { viewerFocused = true }
        .task(id: config) {
            await refresh()
            while !Task.isCancelled {
                try? await Task.sleep(nanoseconds: 30_000_000_000)
                if Task.isCancelled { break }
                await refresh()
            }
        }
    }

    // MARK: - Onderdelen

    private var viewerLayer: some View {
        ZStack {
            Color.black.ignoresSafeArea()

            if let image = image {
                Image(uiImage: image)
                    .resizable()
                    .scaledToFit()
                    .ignoresSafeArea()
            } else if errorText == nil {
                ProgressView("Laden…")
            }

            if let errorText = errorText {
                VStack {
                    Spacer()
                    Text(errorText)
                        .font(.headline)
                        .multilineTextAlignment(.center)
                        .padding(24)
                        .frame(maxWidth: 1400)
                        .background(Color.red.opacity(0.85))
                        .cornerRadius(16)
                        .padding(.bottom, 60)
                }
            }
        }
    }

    private var menuLayer: some View {
        ZStack {
            Color.black.opacity(0.75).ignoresSafeArea()
            VStack(spacing: 32) {
                Text("Solis")
                    .font(.largeTitle)
                    .bold()
                Text(updateText)
                    .foregroundColor(.secondary)
                Button("Doorgaan") { showMenu = false }
                Button("Ververs nu") {
                    showMenu = false
                    Task { await refresh() }
                }
                Button("Instellingen") {
                    showMenu = false
                    openSetup()
                }
                Text("Druk nog een keer op Menu om de app te sluiten.")
                    .font(.callout)
                    .foregroundColor(.secondary)
            }
            .padding(60)
        }
    }

    /// Menu-knop: alleen als het menu dicht is zelf afhandelen, anders doet tvOS het standaardgedrag (app sluiten).
    private var exitAction: (() -> Void)? {
        if showMenu { return nil }
        return { showMenu = true }
    }

    private var updateText: String {
        guard let lastUpdate = lastUpdate else { return "Nog niet bijgewerkt" }
        let f = DateFormatter()
        f.locale = Locale(identifier: "nl_NL")
        f.dateFormat = "HH:mm:ss"
        return "Laatst bijgewerkt om " + f.string(from: lastUpdate)
    }

    // MARK: - Gedrag

    private func step(_ delta: Int) {
        guard pages.count > 1 else { return }
        index = (index + delta + pages.count) % pages.count
        Task { await refresh(reloadPages: false) }
    }

    /// Haalt (eventueel de lijst met pagina's en) het plaatje van de huidige pagina op.
    /// Een oudere, nog lopende aanvraag wordt genegeerd zodra er een nieuwere is.
    @MainActor
    private func refresh(reloadPages: Bool = true) async {
        requestID += 1
        let myID = requestID
        let client = SolisClient(config: config)
        do {
            if reloadPages || pages.isEmpty {
                let list = try await client.pages()
                if myID != requestID { return }
                let current: String? = pages.indices.contains(index) ? pages[index] : nil
                pages = list
                if let current = current, let found = list.firstIndex(of: current) {
                    index = found
                } else {
                    index = min(index, list.count - 1)
                }
            }
            guard pages.indices.contains(index) else { return }
            let page = pages[index]
            let picture = try await client.image(for: page)
            if myID != requestID { return }
            image = picture
            errorText = nil
            lastUpdate = Date()
        } catch {
            if let e = error as? URLError, e.code == .cancelled { return }
            if error is CancellationError { return }
            if myID != requestID { return }
            errorText = SolisClient.describe(error)
        }
    }
}
