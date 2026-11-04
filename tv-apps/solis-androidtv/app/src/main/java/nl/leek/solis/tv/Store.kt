package nl.leek.solis.tv

import android.content.Context

/** Onthoudt de instellingen op de tv. */
class Store(context: Context) {
    private val prefs = context.applicationContext.getSharedPreferences("solis", Context.MODE_PRIVATE)

    var host: String
        get() = prefs.getString("host", "") ?: ""
        set(value) {
            prefs.edit().putString("host", value.trim()).apply()
        }

    var port: Int
        get() = prefs.getInt("port", 8765)
        set(value) {
            prefs.edit().putInt("port", value).apply()
        }

    /** Automatisch doorbladeren aan of uit (in het gewone scherm). */
    var rotate: Boolean
        get() = prefs.getBoolean("rotate", false)
        set(value) {
            prefs.edit().putBoolean("rotate", value).apply()
        }

    /** Seconden per pagina bij doorbladeren. */
    var rotateSec: Int
        get() = prefs.getInt("rotateSec", 20)
        set(value) {
            prefs.edit().putInt("rotateSec", value).apply()
        }

    val configured: Boolean
        get() = host.isNotBlank()
}
