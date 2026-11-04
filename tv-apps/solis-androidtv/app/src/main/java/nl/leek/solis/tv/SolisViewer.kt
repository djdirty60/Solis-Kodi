package nl.leek.solis.tv

import android.content.Context
import android.graphics.Color
import android.graphics.Typeface
import android.os.Handler
import android.os.Looper
import android.view.Gravity
import android.view.KeyEvent
import android.view.View
import android.widget.FrameLayout
import android.widget.ImageView
import android.widget.TextView
import java.net.ConnectException
import java.net.NoRouteToHostException
import java.net.SocketTimeoutException
import java.net.UnknownHostException
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors

/**
 * Het scherm met de Solis-pagina's. Wordt gebruikt door het gewone scherm en door de schermbeveiliging.
 *
 * dream = true: schermbeveiliging (blijft doorbladeren, geen hulpteksten, geen toetsen).
 */
class SolisViewer(
    private val context: Context,
    private val store: Store,
    private val dream: Boolean,
    private val onOpenSettings: (() -> Unit)? = null
) {
    val root = FrameLayout(context)

    private val image = ImageView(context)
    private val status = TextView(context)
    private val hint = TextView(context)
    private val main = Handler(Looper.getMainLooper())

    private var io: ExecutorService? = null
    private var pages: List<String> = emptyList()
    private var index = 0
    private var running = false
    private var generation = 0
    private var hasImage = false
    private var sinceRefresh = 0
    private var sinceRotate = 0
    private var autoRotate = false

    private val names = mapOf(
        "zon" to "Zon", "stroom" to "Stroom", "meer" to "Details", "inzicht" to "Inzicht",
        "overzicht" to "Overzicht", "dynamisch" to "Dynamisch", "verbruik" to "Verbruik", "slim" to "Slim",
        "instel" to "Opties", "spaarpot" to "Spaarpot", "vergelijk" to "Vergelijk", "kids" to "Kids"
    )

    private val hideHint = Runnable { hint.visibility = View.GONE }

    private val tick = object : Runnable {
        override fun run() {
            if (!running) return
            sinceRefresh++
            sinceRotate++
            if (autoRotate && pages.size > 1 && sinceRotate >= rotateSeconds()) {
                step(1, false)
            } else if (sinceRefresh >= 30) {
                refresh()
            }
            main.postDelayed(this, 1000)
        }
    }

    init {
        root.setBackgroundColor(Color.parseColor("#0E1220"))

        image.scaleType = ImageView.ScaleType.FIT_CENTER
        root.addView(image, FrameLayout.LayoutParams(FrameLayout.LayoutParams.MATCH_PARENT, FrameLayout.LayoutParams.MATCH_PARENT))

        status.setTextColor(Color.WHITE)
        status.textSize = 22f
        status.gravity = Gravity.CENTER
        status.setPadding(dp(32), dp(20), dp(32), dp(20))
        status.setBackgroundColor(Color.parseColor("#CC161B2E"))
        status.visibility = View.GONE
        root.addView(status, FrameLayout.LayoutParams(FrameLayout.LayoutParams.MATCH_PARENT, FrameLayout.LayoutParams.WRAP_CONTENT, Gravity.CENTER))

        hint.setTextColor(Color.WHITE)
        hint.textSize = 16f
        hint.typeface = Typeface.DEFAULT_BOLD
        hint.setPadding(dp(20), dp(10), dp(20), dp(10))
        hint.setBackgroundColor(Color.parseColor("#B0161B2E"))
        hint.visibility = View.GONE
        val hp = FrameLayout.LayoutParams(FrameLayout.LayoutParams.WRAP_CONTENT, FrameLayout.LayoutParams.WRAP_CONTENT, Gravity.BOTTOM or Gravity.END)
        hp.setMargins(dp(24), dp(24), dp(24), dp(24))
        root.addView(hint, hp)
    }

    private fun dp(v: Int): Int = (v * context.resources.displayMetrics.density).toInt()

    private fun rotateSeconds(): Int {
        val s = store.rotateSec
        return if (dream) maxOf(10, s) else maxOf(5, s)
    }

    private fun base(): String = Net.baseUrl(store.host, store.port)

    fun start() {
        if (running) return
        running = true
        io = Executors.newSingleThreadExecutor()
        autoRotate = dream || store.rotate
        sinceRefresh = 0
        sinceRotate = 0
        if (!hasImage) showStatus("Even laden...", false)
        if (!dream) flash("◀ ▶ pagina   OK vernieuwen   ▲ instellingen   ▼ doorbladeren aan/uit", 8000)
        loadPages()
        main.postDelayed(tick, 1000)
    }

    fun stop() {
        running = false
        generation++
        main.removeCallbacksAndMessages(null)
        io?.shutdownNow()
        io = null
    }

    /** Geeft true als de toets is verwerkt. */
    fun handleKey(keyCode: Int): Boolean {
        if (dream) return false
        when (keyCode) {
            KeyEvent.KEYCODE_DPAD_LEFT, KeyEvent.KEYCODE_MEDIA_PREVIOUS, KeyEvent.KEYCODE_CHANNEL_DOWN -> step(-1, true)
            KeyEvent.KEYCODE_DPAD_RIGHT, KeyEvent.KEYCODE_MEDIA_NEXT, KeyEvent.KEYCODE_CHANNEL_UP -> step(1, true)
            KeyEvent.KEYCODE_DPAD_CENTER, KeyEvent.KEYCODE_ENTER, KeyEvent.KEYCODE_NUMPAD_ENTER -> {
                flash("Vernieuwen...", 1500)
                refresh()
            }
            KeyEvent.KEYCODE_DPAD_UP, KeyEvent.KEYCODE_MENU -> onOpenSettings?.invoke()
            KeyEvent.KEYCODE_DPAD_DOWN -> {
                autoRotate = !autoRotate
                store.rotate = autoRotate
                sinceRotate = 0
                flash(if (autoRotate) "Doorbladeren aan (elke ${rotateSeconds()} s)" else "Doorbladeren uit", 2500)
            }
            else -> return false
        }
        return true
    }

    private fun loadPages() {
        val exec = io ?: return
        val myGen = generation
        try {
            exec.execute {
                try {
                    val list = Net.fetchPages(base())
                    main.post {
                        if (running && myGen == generation) {
                            pages = list
                            if (index >= pages.size) index = 0
                            showPage()
                        }
                    }
                } catch (e: Throwable) {
                    main.post { if (running && myGen == generation) onError(e) }
                }
            }
        } catch (e: Exception) {
            // de uitvoerder is al gestopt
        }
    }

    private fun refresh() {
        if (pages.isEmpty()) loadPages() else showPage()
    }

    private fun step(delta: Int, announce: Boolean) {
        if (pages.isEmpty()) {
            loadPages()
            return
        }
        index = ((index + delta) % pages.size + pages.size) % pages.size
        if (announce) {
            val p = pages[index]
            flash("${names[p] ?: p}  (${index + 1}/${pages.size})", 2000)
        }
        showPage()
    }

    private fun showPage() {
        val exec = io ?: return
        if (pages.isEmpty()) return
        sinceRefresh = 0
        sinceRotate = 0
        generation++
        val myGen = generation
        val page = pages[index]
        try {
            exec.execute {
                try {
                    val bmp = Net.fetchBitmap(base(), page)
                    main.post {
                        if (running && myGen == generation) {
                            image.setImageBitmap(bmp)
                            hasImage = true
                            status.visibility = View.GONE
                        }
                    }
                } catch (e: Throwable) {
                    main.post { if (running && myGen == generation) onError(e) }
                }
            }
        } catch (e: Exception) {
            // de uitvoerder is al gestopt
        }
    }

    private fun onError(e: Throwable) {
        val where = "${store.host}:${store.port}"
        val text = when (e) {
            is UnknownHostException ->
                "Ik kan '${store.host}' niet vinden.\nControleer het adres in de instellingen" + (if (dream) "." else " (druk op ▲).")
            is ConnectException, is NoRouteToHostException, is SocketTimeoutException ->
                "Geen verbinding met de Solis-app op $where.\nStaat de Homey aan en zit de tv op hetzelfde netwerk?\nIk probeer het zo opnieuw."
            is OutOfMemoryError ->
                "De tv heeft te weinig geheugen voor dit plaatje.\nIk probeer het zo opnieuw."
            else ->
                "Er ging iets mis: ${e.message ?: e.javaClass.simpleName}\nIk probeer het zo opnieuw."
        }
        showStatus(text, true)
        sinceRefresh = 20 // over ongeveer 10 seconden opnieuw proberen
    }

    private fun showStatus(text: String, error: Boolean) {
        status.text = text
        status.setBackgroundColor(Color.parseColor(if (error) "#E6B3261E" else "#CC161B2E"))
        val lp = status.layoutParams as FrameLayout.LayoutParams
        lp.gravity = if (hasImage) Gravity.BOTTOM else Gravity.CENTER
        status.layoutParams = lp
        status.visibility = View.VISIBLE
    }

    private fun flash(text: String, millis: Long) {
        if (dream) return
        hint.text = text
        hint.visibility = View.VISIBLE
        main.removeCallbacks(hideHint)
        main.postDelayed(hideHint, millis)
    }
}
