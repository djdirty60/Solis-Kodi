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
    @FocusState private var menuFocus: MenuItem?

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
                GeometryReader { geo in
                    Image(uiImage: image)
                        .resizable()
                        .aspectRatio(contentMode: .fill)
                        .frame(width: geo.size.width, height: geo.size.height)
                        .clipped()
                }
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
            Color.black.opacity(0.88).ignoresSafeArea()
            VStack(spacing: 40) {
                Text("Solis")
                    .font(.system(size: 80, weight: .bold))
                    .foregroundColor(.white)
                Text(updateText)
                    .font(.system(size: 34))
                    .foregroundColor(Color.white.opacity(0.85))
                VStack(spacing: 28) {
                    Button { showMenu = false } label: { MenuButtonLabel(title: "Doorgaan") }
                        .buttonStyle(.plain)
                        .focused($menuFocus, equals: .continueItem)
                    Button {
                        showMenu = false
                        Task { await refresh() }
                    } label: { MenuButtonLabel(title: "Ververs nu") }
                        .buttonStyle(.plain)
                        .focused($menuFocus, equals: .refresh)
                    Button {
                        showMenu = false
                        openSetup()
                    } label: { MenuButtonLabel(title: "Instellingen") }
                        .buttonStyle(.plain)
                        .focused($menuFocus, equals: .settings)
                }
                Text("Druk nog een keer op Menu om de app te sluiten.")
                    .font(.system(size: 30))
                    .foregroundColor(Color.white.opacity(0.75))
            }
            .padding(80)
            .background(RoundedRectangle(cornerRadius: 36).fill(Color(white: 0.14)))
        }
        .onAppear {
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) { menuFocus = .continueItem }
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


/// Keuzes in het menu (voor de focus met de Siri Remote).
enum MenuItem: Hashable {
    case continueItem, refresh, settings
}

/// Grote, goed leesbare menuknop: wit op donker, de gekozen knop is wit met zwarte tekst.
struct MenuButtonLabel: View {
    let title: String
    @Environment(\.isFocused) private var isFocused

    var body: some View {
        Text(title)
            .font(.system(size: 42, weight: .semibold))
            .foregroundColor(isFocused ? Color.black : Color.white)
            .frame(width: 640)
            .padding(.vertical, 22)
            .background(RoundedRectangle(cornerRadius: 22).fill(isFocused ? Color.white : Color.white.opacity(0.2)))
            .scaleEffect(isFocused ? 1.06 : 1.0)
            .animation(.easeOut(duration: 0.15), value: isFocused)
    }
}
