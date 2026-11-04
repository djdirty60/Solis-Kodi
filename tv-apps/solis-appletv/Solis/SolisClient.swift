import Foundation
import UIKit

/// Adres van de Solis-app op de Homey.
struct SolisConfig: Hashable {
    var host: String
    var port: Int

    /// Maakt van "homey.local", "192.168.1.5:8765" of "http://homey.local/" een bruikbaar adres.
    var baseURL: URL? {
        var h = host.trimmingCharacters(in: .whitespacesAndNewlines)
        let lower = h.lowercased()
        if lower.hasPrefix("http://") { h = String(h.dropFirst(7)) }
        else if lower.hasPrefix("https://") { h = String(h.dropFirst(8)) }
        while h.hasSuffix("/") { h.removeLast() }
        if h.isEmpty { return nil }
        let text = h.contains(":") ? "http://\(h)" : "http://\(h):\(port)"
        return URL(string: text)
    }
}

enum SolisError: Error {
    case geenAdres
    case serverFout(Int)
    case geenPaginas
    case geenPlaatje
}

private struct PagesResponse: Decodable {
    let pages: [String]
}

/// Haalt de lijst met pagina's en de plaatjes op, precies zoals de Kodi-add-on dat doet.
struct SolisClient {
    let config: SolisConfig

    private static let session: URLSession = {
        let c = URLSessionConfiguration.ephemeral
        c.timeoutIntervalForRequest = 8
        c.timeoutIntervalForResource = 20
        c.requestCachePolicy = .reloadIgnoringLocalAndRemoteCacheData
        c.waitsForConnectivity = false
        return URLSession(configuration: c)
    }()

    private func data(for path: String, query: [URLQueryItem] = []) async throws -> Data {
        guard let base = config.baseURL else { throw SolisError.geenAdres }
        var url = base.appendingPathComponent(path)
        if !query.isEmpty, var comps = URLComponents(url: url, resolvingAgainstBaseURL: false) {
            comps.queryItems = query
            if let u = comps.url { url = u }
        }
        var request = URLRequest(url: url)
        request.cachePolicy = .reloadIgnoringLocalAndRemoteCacheData
        let (body, response) = try await SolisClient.session.data(for: request)
        if let http = response as? HTTPURLResponse, http.statusCode != 200 {
            throw SolisError.serverFout(http.statusCode)
        }
        return body
    }

    /// De pagina's, bijvoorbeeld ["zon", "stroom", "meer"].
    func pages() async throws -> [String] {
        let body = try await data(for: "beeld/pages.json")
        let decoded = try JSONDecoder().decode(PagesResponse.self, from: body)
        let ids = decoded.pages.filter { id in
            !id.isEmpty && id.allSatisfy { $0.isLetter && $0.isLowercase && $0.isASCII }
        }
        if ids.isEmpty { throw SolisError.geenPaginas }
        return ids
    }

    /// Het plaatje (1920x1080 PNG) van een pagina.
    func image(for page: String, query: [URLQueryItem] = []) async throws -> UIImage {
        let body = try await data(for: "beeld/page/\(page).png", query: query)
        // PNG begint altijd met deze vier bytes
        let magic: [UInt8] = [0x89, 0x50, 0x4E, 0x47]
        guard body.count > 1000, Array(body.prefix(4)) == magic, let image = UIImage(data: body) else {
            throw SolisError.geenPlaatje
        }
        return image
    }

    /// Nederlandse uitleg bij een fout.
    static func describe(_ error: Error) -> String {
        if let e = error as? SolisError {
            switch e {
            case .geenAdres:
                return "Er is geen geldig adres ingevuld. Open de instellingen en vul het adres van je Homey in."
            case .serverFout(let code):
                return "De Solis-app gaf een foutmelding (\(code)). Probeer het over een minuut opnieuw."
            case .geenPaginas:
                return "De Solis-app gaf geen pagina's terug. Is de app op je Homey bijgewerkt?"
            case .geenPlaatje:
                return "Het antwoord van de Solis-app was geen geldig plaatje."
            }
        }
        if let e = error as? URLError {
            switch e.code {
            case .cannotFindHost, .dnsLookupFailed:
                return "Homey niet gevonden. Controleer het adres en of Apple TV en Homey op hetzelfde wifi-netwerk zitten."
            case .timedOut:
                return "Homey antwoordt niet op tijd. Controleer of Homey aan staat en op hetzelfde netwerk zit."
            case .cannotConnectToHost, .networkConnectionLost:
                return "Geen verbinding met de Solis-app. Staat het dashboard aan in de instellingen van de app, en klopt de poort?"
            case .notConnectedToInternet:
                return "Apple TV heeft geen netwerkverbinding."
            case .appTransportSecurityRequiresSecureConnection:
                return "Deze Apple TV staat geen onbeveiligde lokale verbinding toe."
            default:
                return "Verbinding mislukt (\(e.localizedDescription))."
            }
        }
        if error is DecodingError {
            return "Het antwoord van de Solis-app is niet te lezen. Klopt het adres?"
        }
        return "Er ging iets mis: \(error.localizedDescription)"
    }
}
